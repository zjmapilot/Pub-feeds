"""Run the full scraping pipeline for every venue in venues.py:

    fetch -> extract -> (geocode if needed) -> write to database

Usage:
    python run.py            # scrape everything, write to the database
    python run.py --dry-run  # scrape and extract, but print results instead of writing

Requires a .env file (copy .env.example) with ANTHROPIC_API_KEY and DATABASE_URL set,
and `playwright install chromium` run once after pip installing requirements.txt.
"""

import argparse
import json
import sys

from dotenv import load_dotenv

load_dotenv()

from venues import VENUES
from fetch import fetch_venue_text
from extract import extract_specials
from geocode import geocode_address
import db


def run(dry_run=False):
    print(f"Starting scrape of {len(VENUES)} venues" + (" (dry run)" if dry_run else ""))

    if dry_run:
        _run_venues(VENUES, conn=None, dry_run=True)
    else:
        with db.get_connection() as conn:
            _run_venues(VENUES, conn=conn, dry_run=False)

    print("\nDone.")


def _run_venues(venues, conn, dry_run):
    for venue in venues:
        print(f"\n-> {venue['name']} ({venue['suburb']})")

        # Fill in coordinates for any venue that doesn't already have them hardcoded
        if venue.get("lat") is None or venue.get("lng") is None:
            print("  geocoding address...")
            coords = geocode_address(f"{venue['address']}, {venue['suburb']} NSW, Australia")
            if coords:
                venue["lat"], venue["lng"] = coords["lat"], coords["lng"]
                print(f"  resolved to {coords['lat']}, {coords['lng']} "
                      f"— consider hardcoding this in venues.py to skip geocoding next run")
            else:
                print("  ! could not geocode this address, skipping venue")
                continue

        text, method = fetch_venue_text(venue)

        if method == "unavailable":
            print(f"  no scrapeable source ({venue.get('flagged_note', 'no site_url set')})")
            specials = []
        else:
            print(f"  fetched via '{method}', {len(text)} chars — extracting specials...")
            specials = extract_specials(text)
            print(f"  extracted {len(specials)} specials")

        if dry_run:
            print(json.dumps(specials, indent=2))
            continue

        venue_id = db.upsert_venue(conn, venue, scrape_source=method)
        db.replace_specials(conn, venue_id, specials)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                         help="Scrape and extract, but don't write to the database")
    args = parser.parse_args()

    try:
        run(dry_run=args.dry_run)
    except KeyError as e:
        print(f"Missing environment variable: {e}. Did you copy .env.example to .env?")
        sys.exit(1)
