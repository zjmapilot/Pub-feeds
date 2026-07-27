"""Fetching venue pages — the part that has to deal with the mess we found by hand:
plain HTML pages, JS-rendered single-page apps (like Merivale), and PDF menus.

Strategy: try a cheap static HTTP fetch first. If the visible text comes back
suspiciously short, assume the page is JS-rendered and fall back to a real
headless browser (Playwright). This mirrors exactly what we found testing
these 10 venues by hand — most sites work with the cheap path, a couple need
the expensive one.
"""

import io
import re

import pdfplumber
import requests
from playwright.sync_api import sync_playwright

USER_AGENT = "Mozilla/5.0 (compatible; WhatsPouringScraper/1.0)"
JS_RENDERED_THRESHOLD = 300  # chars — below this, assume the page needs JS to render


def fetch_static_html_text(url, timeout=15):
    """Cheap path: plain HTTP GET, strip tags, return visible text."""
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    text = re.sub(r"<script[^<]*(?:(?!</script>)<[^<]*)*</script>", " ", resp.text, flags=re.I)
    text = re.sub(r"<style[^<]*(?:(?!</style>)<[^<]*)*</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_rendered_html_text(url, timeout_ms=20000):
    """Expensive path: real headless browser, for JS-rendered sites (e.g. Merivale)."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(url, timeout=timeout_ms, wait_until="networkidle")
        text = page.inner_text("body")
        browser.close()
        return text


def fetch_pdf_text(url, timeout=15):
    """Download a PDF (e.g. a linked menu) and extract its text, page by page."""
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    parts = []
    with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
    return "\n".join(parts)


def fetch_venue_text(venue):
    """Best-effort fetch for one venue dict from venues.py.
    Returns (combined_text, method_used) where method_used is one of
    'html', 'rendered', 'pdf', or 'unavailable'.
    """
    if venue.get("socials_only") or not venue.get("site_url"):
        return "", "unavailable"

    texts = []
    method = "html"

    try:
        text = fetch_static_html_text(venue["site_url"])
        if len(text) < JS_RENDERED_THRESHOLD:
            text = fetch_rendered_html_text(venue["site_url"])
            method = "rendered"
        texts.append(text)
    except Exception as e:
        print(f"  ! failed to fetch site_url for {venue['name']}: {e}")

    if venue.get("pdf_url"):
        try:
            pdf_text = fetch_pdf_text(venue["pdf_url"])
            texts.append(pdf_text)
            method = "pdf"
        except Exception as e:
            print(f"  ! failed to fetch pdf_url for {venue['name']}: {e}")

    combined = "\n\n".join(t for t in texts if t)
    if not combined:
        return "", "unavailable"
    return combined, method
