import logging
import time
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from devices.models import Device
from device_metrics.history import get_timezone

from .features import build_features
from .openai_client import call_openai
from .serializers import AdvisorInsightResponseSerializer

logger = logging.getLogger(__name__)

LANGUAGES = {"en", "lug"}
AUDIENCES = {"resident", "official"}
MIN_READINGS_FOR_INSIGHT = 20
NEGATIVE_CACHE_SECONDS = 300
LOCK_SECONDS = 30
LOCK_WAIT_SECONDS = 6
LOCK_POLL_SECONDS = 0.5


class AdvisorInsightView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="device_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Public device ID.",
            ),
            OpenApiParameter(
                name="lang",
                type=OpenApiTypes.STR,
                enum=["en", "lug"],
                location=OpenApiParameter.QUERY,
                description="Response language. Defaults to en.",
            ),
            OpenApiParameter(
                name="audience",
                type=OpenApiTypes.STR,
                enum=["resident", "official"],
                location=OpenApiParameter.QUERY,
                description="Audience framing. Defaults to resident.",
            ),
        ],
        responses={
            200: AdvisorInsightResponseSerializer,
            400: OpenApiResponse(description="Invalid lang or audience parameter."),
            404: OpenApiResponse(description="Device not found."),
        },
        examples=[
            OpenApiExample(
                "Ready insight",
                value={
                    "device_id": "SB1006",
                    "lang": "en",
                    "audience": "resident",
                    "insight": "This location was moderately noisy...",
                    "status": "ready",
                    "cached": False,
                    "generated_at": "2026-07-06T12:00:00+03:00",
                    "range": {
                        "start_date": "2026-06-29T12:00:00+03:00",
                        "end_date": "2026-07-06T12:00:00+03:00",
                    },
                },
                response_only=True,
            )
        ],
        description=(
            "Return a plain-language Noise Advisor insight for a device. "
            "Insights are generated synchronously on cache miss and cached."
        ),
    )
    def get(self, request, device_id):
        lang = request.query_params.get("lang", "en")
        audience = request.query_params.get("audience", "resident")

        if lang not in LANGUAGES:
            return Response({"lang": "Supported values are en and lug."}, status=400)
        if audience not in AUDIENCES:
            return Response(
                {"audience": "Supported values are resident and official."},
                status=400,
            )

        device = get_object_or_404(Device, device_id=device_id)
        tz = _device_timezone(device)
        start, end = _last_seven_days(tz)
        range_data = _range_data(start, end, tz)
        cache_key = _cache_key(device_id, lang, audience)
        cached = cache.get(cache_key)
        if cached is not None:
            return _cached_response(device_id, lang, audience, cached, range_data)

        lock_key = f"{cache_key}:lock"
        if not cache.add(lock_key, 1, timeout=LOCK_SECONDS):
            cached = _wait_for_cache(cache_key)
            if cached is not None:
                return _cached_response(device_id, lang, audience, cached, range_data)
            return _response(
                device_id,
                lang,
                audience,
                insight=None,
                status="generating",
                cached=False,
                generated_at=None,
                range_data=range_data,
            )

        try:
            return _generate_response(device, device_id, lang, audience, start, end, tz)
        finally:
            cache.delete(lock_key)


def _generate_response(device, device_id, lang, audience, start, end, tz):
    range_data = _range_data(start, end, tz)
    cache_key = _cache_key(device_id, lang, audience)

    try:
        features = build_features(device, start, end, tz)
        range_data = features["range"]
        if (features.get("readings") or 0) < MIN_READINGS_FOR_INSIGHT:
            payload = _cache_payload("empty", None, None, range_data)
            cache.set(cache_key, payload, timeout=NEGATIVE_CACHE_SECONDS)
            return _response(
                device_id,
                lang,
                audience,
                insight=None,
                status="empty",
                cached=False,
                generated_at=None,
                range_data=range_data,
            )

        insight = call_openai(features, lang, audience)
        if insight is None:
            payload = _cache_payload("unavailable", None, None, range_data)
            cache.set(cache_key, payload, timeout=NEGATIVE_CACHE_SECONDS)
            return _response(
                device_id,
                lang,
                audience,
                insight=None,
                status="unavailable",
                cached=False,
                generated_at=None,
                range_data=range_data,
            )

        generated_at = timezone.now().astimezone(tz).isoformat()
        payload = _cache_payload("ready", insight, generated_at, range_data)
        cache.set(
            cache_key,
            payload,
            timeout=getattr(settings, "INSIGHT_TTL_SECONDS", 43200),
        )
        return _response(
            device_id,
            lang,
            audience,
            insight=insight,
            status="ready",
            cached=False,
            generated_at=generated_at,
            range_data=range_data,
        )
    except Exception:
        logger.exception("Noise Advisor request generation failed.")
        payload = _cache_payload("unavailable", None, None, range_data)
        cache.set(cache_key, payload, timeout=NEGATIVE_CACHE_SECONDS)
        return _response(
            device_id,
            lang,
            audience,
            insight=None,
            status="unavailable",
            cached=False,
            generated_at=None,
            range_data=range_data,
        )


def _cached_response(device_id, lang, audience, cached, fallback_range):
    return _response(
        device_id,
        lang,
        audience,
        insight=cached.get("insight"),
        status=cached.get("status", "ready"),
        cached=True,
        generated_at=cached.get("generated_at"),
        range_data=cached.get("range") or fallback_range,
    )


def _response(
    device_id,
    lang,
    audience,
    insight,
    status,
    cached,
    generated_at,
    range_data,
):
    return Response(
        {
            "device_id": device_id,
            "lang": lang,
            "audience": audience,
            "insight": insight,
            "status": status,
            "cached": cached,
            "generated_at": generated_at,
            "range": range_data,
        }
    )


def _wait_for_cache(cache_key):
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    while time.monotonic() < deadline:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        time.sleep(LOCK_POLL_SECONDS)
    return None


def _cache_payload(status, insight, generated_at, range_data):
    return {
        "status": status,
        "insight": insight,
        "generated_at": generated_at,
        "range": range_data,
    }


def _cache_key(device_id, lang, audience):
    return f"advisor:{device_id}:{lang}:{audience}"


def _device_timezone(device):
    timezone_value = getattr(device, "timezone", None)
    timezone_name = getattr(timezone_value, "zone", None) or getattr(
        timezone_value, "key", None
    )
    if timezone_name is None and isinstance(timezone_value, str):
        timezone_name = timezone_value
    return get_timezone(timezone_name or settings.TIME_ZONE)


def _last_seven_days(tz):
    end = timezone.now().astimezone(tz)
    start = end - timedelta(days=7)
    return start, end


def _range_data(start, end, tz):
    return {
        "start_date": start.astimezone(tz).isoformat(),
        "end_date": end.astimezone(tz).isoformat(),
    }
