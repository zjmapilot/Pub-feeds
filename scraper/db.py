"""Database writes — upserting venues and replacing their specials each run.

We fully replace a venue's specials on every run (delete + reinsert) rather than
trying to diff old vs new. Simpler, and avoids stale rows lingering if a special
gets removed from a venue's site.
"""

import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import execute_values


@contextmanager
def get_connection():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def upsert_venue(conn, venue, scrape_source):
    """Insert or update a venue (matched by name + suburb). Returns venue_id."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM venues WHERE name = %s AND suburb = %s",
                     (venue["name"], venue["suburb"]))
        row = cur.fetchone()

        if row:
            venue_id = row[0]
            cur.execute("""
                UPDATE venues SET
                    address = %s, lat = %s, lng = %s, site_url = %s,
                    socials_only = %s, flagged_note = %s,
                    last_scraped_at = now(), scrape_source = %s, updated_at = now()
                WHERE id = %s
            """, (
                venue["address"], venue["lat"], venue["lng"], venue.get("site_url"),
                venue.get("socials_only", False), venue.get("flagged_note"),
                scrape_source, venue_id
            ))
        else:
            cur.execute("""
                INSERT INTO venues
                    (name, suburb, address, lat, lng, site_url, socials_only,
                     flagged_note, last_scraped_at, scrape_source)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s, now(), %s)
                RETURNING id
            """, (
                venue["name"], venue["suburb"], venue["address"], venue["lat"], venue["lng"],
                venue.get("site_url"), venue.get("socials_only", False),
                venue.get("flagged_note"), scrape_source
            ))
            venue_id = cur.fetchone()[0]

        return venue_id


def replace_specials(conn, venue_id, specials):
    """Delete all existing specials for this venue and insert the freshly extracted set."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM specials WHERE venue_id = %s", (venue_id,))

        if not specials:
            return

        rows = [(
            venue_id,
            s["days"],
            s.get("start_time"),
            s.get("end_time"),
            s["display_time"],
            s["title"],
            s.get("price"),
            s.get("description"),
            s["category"],
            s.get("confidence", "confirmed"),
            s.get("source_note"),
        ) for s in specials]

        execute_values(cur, """
            INSERT INTO specials
                (venue_id, days, start_time, end_time, display_time,
                 title, price, description, category, confidence, source_note)
            VALUES %s
        """, rows)
