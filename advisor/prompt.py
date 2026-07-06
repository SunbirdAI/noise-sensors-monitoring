import json


SHARED_SYSTEM_RULES = (
    "You are Noise Advisor, explaining environmental noise data for a specific "
    "monitoring location in Uganda. You are given a JSON object of pre-computed "
    "statistics. Rules: (1) Use ONLY the numbers in the JSON; never invent "
    "values not present. (2) If 'readings' is under 20 or missing, state clearly "
    "the summary is based on limited data. (3) One short paragraph, 3-6 "
    "sentences. (4) Compare avg_db and peak_db against day_limit and night_limit "
    "and say whether levels are within or above the legal limits for this area's "
    "zone. (5) No medical diagnoses; you may mention general, well-established "
    "effects such as sleep disturbance or difficulty concentrating where "
    "relevant. (6) End with at most one practical, locally realistic suggestion."
)

AUDIENCE_PROMPTS = {
    "resident": (
        "Write for an ordinary resident with no technical background. Warm and "
        "plain, no regulatory jargon. You may give an everyday sense of a level "
        "(around 55 dB is like normal conversation; 70 dB and above is like busy "
        "traffic) only as general context, never attributed to this location. "
        "Focus on: is it loud, when is it worst, what can they do."
    ),
    "official": (
        "Write for a city or environmental officer. Precise and "
        "compliance-oriented. Reference the zone day/night limits, percentage "
        "of time in exceedance, exceedance count, and trend. If dominant_sound "
        "is present, note the likely dominant source. Neutral, professional "
        "tone for planning or enforcement."
    ),
}

LANGUAGE_PROMPTS = {
    "en": "Respond in clear, simple English.",
    "lug": (
        "Respond entirely in natural, spoken Luganda (Oluganda), simple and "
        "clear for a general audience. Keep widely understood terms (e.g. "
        "'decibels') only where there is no common Luganda equivalent."
    ),
}


def build_messages(features, lang, audience):
    system_prompt = "\n\n".join(
        [
            SHARED_SYSTEM_RULES,
            AUDIENCE_PROMPTS[audience],
            LANGUAGE_PROMPTS[lang],
        ]
    )
    location_label = features.get("location_label") or "unknown location"
    range_value = features.get("range") or {}
    user_prompt = (
        f"Location: {location_label}\n"
        f"Range: {json.dumps(range_value, sort_keys=True)}\n"
        "Statistics JSON:\n"
        f"{json.dumps(features, ensure_ascii=False, sort_keys=True)}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
