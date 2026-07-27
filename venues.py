# Starting venue list — the same 10 we researched by hand for the Alexandria/Waterloo
# prototype. Add more venues here as you expand suburb by suburb; each one just needs
# a name, suburb, address, and a URL to scrape (site_url, and optionally pdf_url if the
# specials specifically live in a linked PDF rather than the page itself).
#
# lat/lng can be left as None for new venues — run.py will geocode them automatically
# on first run and the script will print the resolved coordinates so you can hardcode
# them here afterwards (saves a Nominatim lookup on every future run).

VENUES = [
    {
        "name": "The Cauliflower Hotel", "suburb": "Waterloo", "address": "123 Botany Rd",
        "lat": -33.898883, "lng": 151.200268,
        "site_url": "https://cauliflowerhotel.com.au/",
        "pdf_url": "https://cauliflowerhotel.com.au/wp-content/uploads/cauliflower-hotel-summer-menu-final.pdf",
    },
    {
        "name": "Glenroy Hotel", "suburb": "Alexandria", "address": "246 Botany Rd",
        "lat": -33.9023667, "lng": 151.2014472,
        "site_url": None,
        "socials_only": True,
        "flagged_note": "No official website — specials live on Facebook/Instagram only.",
    },
    {
        "name": "Iron Duke Hotel", "suburb": "Alexandria", "address": "220 Botany Rd",
        "lat": -33.901641, "lng": 151.2011,
        "site_url": "https://www.ironduke.com.au/",
    },
    {
        "name": "Abbots Hotel", "suburb": "Waterloo", "address": "47 Botany Rd",
        "lat": -33.8965211, "lng": 151.1994528,
        "site_url": "https://www.abbottshotel.com.au/",
        "flagged_note": "Site hasn't been updated since 2020 — treat any extracted specials as unconfirmed.",
    },
    {
        "name": "The Redfern", "suburb": "Redfern", "address": "106 George St",
        "lat": -33.8927057, "lng": 151.2019012,
        "site_url": "https://www.theredfern.com.au/",
    },
    {
        "name": "Lord Raglan Hotel", "suburb": "Alexandria", "address": "12 Henderson Rd",
        "lat": -33.8969888, "lng": 151.1986439,
        "site_url": "https://www.lordraglan.com.au/",
    },
    {
        "name": "The Alex", "suburb": "Alexandria", "address": "35 Henderson Rd",
        "lat": -33.8970092, "lng": 151.1971657,
        "site_url": "https://merivale.com/venues/the-alex/",
        "flagged_note": "Merivale's site is JS-rendered — the fetch step needs the Playwright fallback, not the plain HTTP path.",
    },
    {
        "name": "The Mitch", "suburb": "Alexandria", "address": "50–52 Mitchell Rd",
        "lat": -33.9003963, "lng": 151.1939020,
        "site_url": "https://themitch.com.au/",
    },
    {
        "name": "Parkview Hotel", "suburb": "Alexandria", "address": "178–180 Mitchell Rd",
        "lat": -33.9030403, "lng": 151.1914364,
        "site_url": "https://pvhalexandria.com.au/",
    },
    {
        "name": "Zetland Hotel", "suburb": "Zetland", "address": "936 Bourke St",
        "lat": -33.9044364, "lng": 151.2052488,
        "site_url": "https://zetlandhotel.com.au/whats-on/",
        "flagged_note": "Specials are posted as image/PDF flyers, not extractable text — needs an OCR/vision step this pipeline doesn't have yet.",
    },
]
