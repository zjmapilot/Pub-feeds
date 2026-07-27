-- Pub Feeds — database schema
-- Run this once against a fresh Postgres database to set up tables.

CREATE TABLE IF NOT EXISTS venues (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    suburb          TEXT NOT NULL,
    address         TEXT NOT NULL,
    lat             DOUBLE PRECISION NOT NULL,
    lng             DOUBLE PRECISION NOT NULL,
    site_url        TEXT,                      -- NULL if venue has no website (socials only)
    socials_only    BOOLEAN NOT NULL DEFAULT FALSE,
    flagged_note    TEXT,                       -- e.g. "site hasn't updated since 2020"
    last_scraped_at TIMESTAMPTZ,                -- when we last successfully pulled this venue
    scrape_source   TEXT,                       -- 'html' | 'pdf' | 'manual' | 'unavailable'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS specials (
    id          SERIAL PRIMARY KEY,
    venue_id    INTEGER NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    days        TEXT[] NOT NULL,               -- e.g. ARRAY['Monday','Tuesday']
    start_time  TIME,                          -- NULL if unconfirmed/unknown
    end_time    TIME,                          -- NULL if unconfirmed/unknown
    display_time TEXT NOT NULL,                -- human-readable, e.g. "5–9pm" or "from 5pm"
    title       TEXT NOT NULL,
    price       TEXT,                          -- kept as text: "$12", "$79pp", "from $14" etc.
    description TEXT,
    category    TEXT[] NOT NULL,               -- subset of {'food','drink','event'}
    confidence  TEXT NOT NULL DEFAULT 'confirmed', -- 'confirmed' | 'unconfirmed'
    source_note TEXT,                          -- e.g. "mentioned in a customer review, not the venue's site"
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_specials_venue_id ON specials(venue_id);
CREATE INDEX IF NOT EXISTS idx_venues_suburb ON venues(suburb);

-- Each scraper run replaces a venue's specials wholesale (delete + reinsert)
-- rather than trying to diff old vs new — simpler and avoids stale leftover rows.
-- last_scraped_at + scrape_source let the site (or an admin view) flag venues
-- that haven't successfully updated in a while.


-- ============================================================
-- SECURITY: Row Level Security (RLS)
-- ============================================================
-- Why this matters: without these rules, Supabase's default public API key
-- (the one the website uses) would be able to read AND write every row.
-- These policies lock it down to READ-ONLY for the public. Only the
-- scraper — using a separate, secret "service role" key that bypasses RLS
-- entirely — can write. If the website's public key ever leaked, the worst
-- case is someone reading data that's already public, not deleting anything.

ALTER TABLE venues ENABLE ROW LEVEL SECURITY;
ALTER TABLE specials ENABLE ROW LEVEL SECURITY;

-- Anyone (the website, using the public "anon" key) can read.
CREATE POLICY "Public can read venues"
    ON venues FOR SELECT
    USING (true);

CREATE POLICY "Public can read specials"
    ON specials FOR SELECT
    USING (true);

-- Deliberately no INSERT/UPDATE/DELETE policies for the public "anon" role.
-- This means the public key literally cannot write, full stop — not "we
-- trust the app not to," but "the database itself refuses." The scraper
-- writes using Supabase's service_role key instead, which bypasses RLS by
-- design and must be kept secret (server-side / Railway env vars only —
-- never in the Next.js frontend code, and never committed to GitHub).

