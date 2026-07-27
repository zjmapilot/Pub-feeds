# Scraper

Pulls specials from each venue in `venues.py`, extracts them with Claude, and writes
them to Postgres.

## One-time setup

```bash
pip install -r requirements.txt
playwright install chromium   # downloads the headless browser used for JS-rendered sites
```

Copy `.env.example` (in the repo root) to `.env` and fill in:
- `ANTHROPIC_API_KEY` — from console.anthropic.com/settings/keys
- `DATABASE_URL` — from Railway's Postgres service (Connect tab → Postgres Connection URL)

Then run the schema once against your database:

```bash
psql "$DATABASE_URL" -f ../db/schema.sql
```

## Running it

```bash
python run.py --dry-run   # scrape + extract, just print results, don't touch the database
python run.py              # the real thing — writes to Postgres
```

Start with `--dry-run` on a fresh setup so you can eyeball the extracted specials
before anything hits the database.

## Known limitations (carried over from manual research)

- **Zetland Hotel**: specials are posted as image/PDF flyers with no extractable text.
  This pipeline doesn't do OCR yet, so this venue will always come back empty until
  that's added.
- **Abbots Hotel**: site hasn't been updated since 2020. Whatever gets extracted
  should be treated as unreliable — flagged accordingly in `venues.py`.
- **The Alex (Merivale)**: needs the Playwright fallback since the site is fully
  JS-rendered; the plain HTTP fetch returns an empty shell.
- New venues without a `site_url` (or with `socials_only: True`) are skipped
  automatically — there's nothing to scrape.

## Adding more venues

Add an entry to `VENUES` in `venues.py`. You only need `name`, `suburb`, `address`,
and `site_url` — `lat`/`lng` will be geocoded automatically on first run if omitted
(the script will print the resolved coordinates so you can hardcode them and skip
geocoding on future runs).
