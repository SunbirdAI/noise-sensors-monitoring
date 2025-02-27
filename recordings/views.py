import contextlib

from rest_framework import parsers, viewsets
from rest_framework.response import Response

from devices.models import Device
from devices.serializers import RecordingSerializer

from .models import Recording
from .serializers import UploadRecordingSerializer


class UpdateAudioViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    http_method_names = ["patch"]
    lookup_field = "id"

    def partial_update(self, request, *args, **kwargs):
        instance = self.queryset.get(id=kwargs.get("id"))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ReceiveAudioViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = UploadRecordingSerializer
    # parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    parser_classes = [parsers.FileUploadParser]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        # FileUploadParser puts the raw file in request.data["file"].
        # Your serializer expects 'audio', so map it:
        if "file" in request.data and "audio" not in request.data:
            request.data["audio"] = request.data["file"]
        return super().create(request, *args, **kwargs)


    # def perform_create(self, serializer):
    #     if device_id := self.request.data.get('device', None):
    #         with contextlib.suppress(Device.DoesNotExist):
    #             device = Device.objects.get(device_id=device_id)
    #             device.update_last_seen()
    #     serializer.save()

    # def finalize_response(self, request, response, *args, **kwargs):
    #     if response.status_code != 201:
    #         print(response.data)
    #         response.data = {"Failed"}
    #     return super(ReceiveAudioViewSet, self).finalize_response(request, response, *args, **kwargs)
