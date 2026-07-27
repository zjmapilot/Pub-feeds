"""Free geocoding via OpenStreetMap's Nominatim — no API key needed.

Only used for venues where lat/lng isn't already hardcoded in venues.py.
Nominatim's usage policy asks for max 1 request/second and a real
identifying User-Agent, which this respects.
"""

import time
import requests

USER_AGENT = "WhatsPouringScraper/1.0"


def geocode_address(address):
    """Look up an address and return {"lat": ..., "lng": ...}, or None if not found."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    time.sleep(1)  # be polite — respects Nominatim's rate limit

    if not results:
        return None
    return {"lat": float(results[0]["lat"]), "lng": float(results[0]["lon"])}
