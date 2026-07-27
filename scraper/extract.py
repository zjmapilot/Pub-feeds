"""Turns messy scraped text into structured specials using the Claude API.
This is the step that replaces what I was doing by hand in chat — reading a
venue's page and pulling out 'Tuesday: $18 schnitzel' style entries.
"""

import json
import os

from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

EXTRACTION_PROMPT = """You are extracting recurring FOOD and DRINK specials from a pub or bar's \
website or menu text. Only extract RECURRING weekly specials (things that happen every week on \
specific days) — ignore one-off dated events or promotions.

For each special found, output a JSON object with these exact fields:
- days: array of day names from ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
- start_time: 24-hour "HH:MM" if the start time is clearly stated, else null
- end_time: 24-hour "HH:MM" if the end time is clearly stated, else null
- display_time: short human-readable string, e.g. "5–9pm" or "from 5pm"
- title: short name of the special, e.g. "Schnitzel night"
- price: price as shown, e.g. "$18", or null if not stated
- description: one short sentence, or null
- category: array containing any of "food", "drink", "event" (event = trivia/bingo/live music/quiz)
- confidence: "confirmed" if clearly and explicitly stated, "unconfirmed" if inferred or ambiguous

Respond with ONLY a JSON array of these objects — no preamble, no markdown fences, nothing else.
If no recurring specials are found in the text, respond with exactly: []

TEXT TO ANALYZE:
"""


def extract_specials(raw_text, max_chars=15000):
    """Call Claude to extract specials. Returns a list of dicts (possibly empty)."""
    if not raw_text.strip():
        return []

    trimmed = raw_text[:max_chars]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT + trimmed}],
    )

    reply = response.content[0].text.strip()

    # Guard against the model wrapping output in markdown fences despite instructions
    if reply.startswith("```"):
        reply = reply.strip("`")
        if reply.lower().startswith("json"):
            reply = reply[4:]
        reply = reply.strip()

    try:
        specials = json.loads(reply)
        if not isinstance(specials, list):
            print("WARNING: model output wasn't a JSON array, discarding")
            return []
        return specials
    except json.JSONDecodeError:
        print(f"WARNING: could not parse model output as JSON:\n{reply[:500]}")
        return []
