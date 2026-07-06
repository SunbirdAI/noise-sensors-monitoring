import logging
import os

from .prompt import build_messages

logger = logging.getLogger(__name__)


def call_openai(features, lang, audience):
    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=15)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=build_messages(features, lang, audience),
            temperature=0.4,
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception:
        logger.exception("Noise Advisor OpenAI generation failed.")
        return None
