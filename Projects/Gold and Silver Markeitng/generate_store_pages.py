#!/usr/bin/env python3
"""
Generate per-store landing page HTML for all 4 categories
(gold, silver, coins, jewelry) by substituting tokens in the master templates.

Run from project root: python3 generate_store_pages.py
Output: store-instances/{category}/{slug}.html
"""

import os
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
OUTPUT_DIR = ROOT / "store-instances"
OUTPUT_DIR.mkdir(exist_ok=True)

CATEGORIES = [
    {"slug": "gold",    "template": "master-landing-page-template.html"},
    {"slug": "silver",  "template": "master-silver-template.html"},
    {"slug": "coins",   "template": "master-coins-template.html"},
    {"slug": "jewelry", "template": "master-jewelry-template.html"},
]

STORES = [
    {
        "STORE_ID": "culpeper",
        "STORE_CITY": "Culpeper",
        "STORE_CITY_LOWER": "culpeper",
        "STORE_PHONE_DISPLAY": "(540) 445-5510",
        "STORE_PHONE_RAW": "15404455510",
        "STORE_PHONE_RAW_NO1": "5404455510",
        "STORE_ADDRESS_STREET": "571 James Madison Highway",
        "STORE_ADDRESS_ZIP": "22701",
        "STORE_HOURS_LINE": "Monday–Saturday, 10:00 AM – 6:00 PM · Closed Sunday",
        "STORE_MAPS_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Culpeper+VA",
        "STORE_GBP_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Culpeper+VA",
        "STORE_NEARBY_ZIPS": "22701, 22714, 22729, 22735, 22737, 22741, 22727, 22732, 22747, 22942, 22960",
        "STORE_NEARBY_TOWNS": "Culpeper, Brandy Station, Madison, Reva, Stevensburg, Rixeyville, Mitchells, Orange, and Sperryville",
        "STORE_OPEN_DAYS_SCHEMA": '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]',
    },
    {
        "STORE_ID": "waynesboro",
        "STORE_CITY": "Waynesboro",
        "STORE_CITY_LOWER": "waynesboro",
        "STORE_PHONE_DISPLAY": "(540) 221-6346",
        "STORE_PHONE_RAW": "15402216346",
        "STORE_PHONE_RAW_NO1": "5402216346",
        "STORE_ADDRESS_STREET": "1321 West Broad Street",
        "STORE_ADDRESS_ZIP": "22980",
        "STORE_HOURS_LINE": "Mon, Tue, Thu, Fri & Sat 10:00 AM – 6:00 PM · Closed Wednesday & Sunday",
        "STORE_MAPS_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Waynesboro+VA",
        "STORE_GBP_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Waynesboro+VA",
        "STORE_NEARBY_ZIPS": "22980, 22939, 24477, 24431, 22952, 24401, 22920, 22922, 24440",
        "STORE_NEARBY_TOWNS": "Waynesboro, Fishersville, Stuarts Draft, Crimora, Lyndhurst, Staunton, Afton, and Greenville",
        "STORE_OPEN_DAYS_SCHEMA": '["Monday","Tuesday","Thursday","Friday","Saturday"]',
    },
    {
        "STORE_ID": "harrisonburg",
        "STORE_CITY": "Harrisonburg",
        "STORE_CITY_LOWER": "harrisonburg",
        "STORE_PHONE_DISPLAY": "(540) 574-4500",
        "STORE_PHONE_RAW": "15405744500",
        "STORE_PHONE_RAW_NO1": "5405744500",
        "STORE_ADDRESS_STREET": "1790 East Market Street",
        "STORE_ADDRESS_ZIP": "22801",
        "STORE_HOURS_LINE": "Mon, Tue, Thu, Fri & Sat 10:00 AM – 6:00 PM · Closed Wednesday & Sunday",
        "STORE_MAPS_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Harrisonburg+VA",
        "STORE_GBP_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Harrisonburg+VA",
        "STORE_NEARBY_ZIPS": "22801, 22802, 22812, 22821, 22815, 22840, 22841, 22846, 22853, 22827, 22824, 22842, 22835",
        "STORE_NEARBY_TOWNS": "Harrisonburg, Bridgewater, Dayton, Broadway, McGaheysville, Mt. Crawford, Penn Laird, Timberville, Elkton, and Linville",
        "STORE_OPEN_DAYS_SCHEMA": '["Monday","Tuesday","Thursday","Friday","Saturday"]',
    },
    {
        "STORE_ID": "lexington",
        "STORE_CITY": "Lexington",
        "STORE_CITY_LOWER": "lexington",
        "STORE_PHONE_DISPLAY": "(540) 461-8349",
        "STORE_PHONE_RAW": "15404618349",
        "STORE_PHONE_RAW_NO1": "5404618349",
        "STORE_ADDRESS_STREET": "125 Walker Street",
        "STORE_ADDRESS_ZIP": "24450",
        "STORE_HOURS_LINE": "Mon, Tue, Thu, Fri & Sat 10:00 AM – 6:00 PM · Closed Wednesday & Sunday",
        "STORE_MAPS_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Lexington+VA",
        "STORE_GBP_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Lexington+VA",
        "STORE_NEARBY_ZIPS": "24450, 24416, 24555, 24578, 24435, 24472, 24439, 24483, 24579",
        "STORE_NEARBY_TOWNS": "Lexington, Buena Vista, Glasgow, Natural Bridge, Fairfield, Raphine, Goshen, and the greater Rockbridge County area",
        "STORE_OPEN_DAYS_SCHEMA": '["Monday","Tuesday","Thursday","Friday","Saturday"]',
    },
    {
        "STORE_ID": "roanoke",
        "STORE_CITY": "Roanoke",
        "STORE_CITY_LOWER": "roanoke",
        "STORE_PHONE_DISPLAY": "(540) 562-0776",
        "STORE_PHONE_RAW": "15405620776",
        "STORE_PHONE_RAW_NO1": "5405620776",
        "STORE_ADDRESS_STREET": "2362 Peters Creek Road, Suite C",
        "STORE_ADDRESS_ZIP": "24017",
        "STORE_HOURS_LINE": "Mon, Tue, Thu, Fri & Sat 10:00 AM – 6:00 PM · Closed Wednesday & Sunday",
        "STORE_MAPS_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Roanoke+VA",
        "STORE_GBP_URL": "https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Roanoke+VA",
        "STORE_NEARBY_ZIPS": "24017, 24012, 24013, 24014, 24015, 24016, 24018, 24019, 24153, 24179, 24083, 24175, 24070, 24090",
        "STORE_NEARBY_TOWNS": "Roanoke, Salem, Vinton, Daleville, Troutville, Hollins, Cave Spring, Catawba, and Cloverdale",
        "STORE_OPEN_DAYS_SCHEMA": '["Monday","Tuesday","Thursday","Friday","Saturday"]',
    },
]


def main():
    total = 0
    for cat in CATEGORIES:
        template_path = ROOT / cat["template"]
        if not template_path.exists():
            print(f"  ✗ Missing template: {cat['template']}")
            continue

        master = template_path.read_text(encoding="utf-8")

        if re.search(r"dixie", master, re.IGNORECASE):
            raise SystemExit(f"FAILED: {cat['template']} contains 'Dixie' reference.")
        if re.search(r"firearm|\bgun\b|pistol|rifle", master, re.IGNORECASE):
            raise SystemExit(f"FAILED: {cat['template']} contains firearm reference.")

        cat_out_dir = OUTPUT_DIR / cat["slug"]
        cat_out_dir.mkdir(exist_ok=True)

        print(f"\n[{cat['slug'].upper()}]")
        for store in STORES:
            page = master
            for token, value in store.items():
                page = page.replace("{{" + token + "}}", value)

            remaining = re.findall(r"\{\{[A-Z_]+\}\}", page)
            if remaining:
                print(f"  WARNING: {store['STORE_ID']} has un-substituted tokens: {set(remaining)}")

            out_path = cat_out_dir / f"sell-{cat['slug']}-{store['STORE_ID']}.html"
            out_path.write_text(page, encoding="utf-8")
            print(f"  ✓ {out_path.relative_to(ROOT)} ({len(page):,} bytes)")
            total += 1

    print(f"\nGenerated {total} pages across {len(CATEGORIES)} categories × {len(STORES)} stores")


if __name__ == "__main__":
    main()
