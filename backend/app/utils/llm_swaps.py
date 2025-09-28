import os
import logging
from typing import Optional, Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)

# Read API key from environment; do NOT commit keys to source control.
_API_KEY = os.environ.get("OPENAI_API_KEY")
if not _API_KEY:
    logger.warning("OPENAI_API_KEY is not set. suggest_swap will not be able to call the API until it is configured.")

# Create client if key is present. If no key, create without explicitly passing a key so other
# library mechanisms (e.g. shared config) can be used; avoid hardcoding any secret here.
client = OpenAI(api_key=_API_KEY) if _API_KEY else OpenAI()


def suggest_swap(item_name: str, category: str, co2e_100g: float) -> Optional[Tuple[str, str]]:
    """Suggest a lower-carbon substitute for a food item.

    Returns a tuple (item_name, reason) or (None, None) on failure.
    """

    model = os.environ.get("LLM_SWAP_MODEL", "gpt-4o-mini")
    prompt = f"""
    I have a food item: {item_name} (category: {category}, CO₂e per 100g: {co2e_100g}).
    Suggest a lower-carbon-footprint substitute. Explain why it’s better.
    Only respond in the format: "item_name; reason".
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        # Defensive checks for response shape
        choices = getattr(response, "choices", None)
        if not choices:
            logger.debug("No choices returned from LLM response: %r", response)
            return None, None

        # safest path to content
        message = getattr(choices[0], "message", None)
        answer = None
        if message and hasattr(message, "content"):
            answer = message.content.strip()
        else:
            # fallback to dict-like access
            try:
                answer = response.choices[0]["message"]["content"].strip()
            except Exception:
                logger.debug("Could not extract content from response: %r", response)
                return None, None

    except Exception as exc:
        # Log exception details but never print or write API keys
        logger.exception("suggest_swap API call failed: %s", exc)
        return None, None

    # Parse the expected "item; reason" format
    if not answer:
        return None, None

    if ";" in answer:
        to_item, why = answer.split(";", 1)
        return to_item.strip().strip('"\''), why.strip().strip('"\'')

    # If the model did not follow the format, return None so caller can handle it.
    logger.debug("LLM returned unexpected format for suggest_swap: %s", answer)
    return None, None