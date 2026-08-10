#!/usr/bin/env python3
"""
One-time offline job: fetch a poster image URL for every anime in anime.csv
directly from TMDB, using the existing `anime_id` column (which is a TMDB
id) - no fuzzy title matching, no cross-service id guessing. Since the id
already comes from TMDB, this is a guaranteed exact match.

Run this ONCE (and again only when you add new anime to the CSV).
Your Streamlit app should NOT call any API at runtime - it just reads
the image_url column directly.

Setup:
    1. Get a free TMDB API key: https://www.themoviedb.org/settings/api
    2. Either set it as an environment variable:
           export TMDB_API_KEY=your_key_here
       or pass it with --api-key

Usage:
    pip install requests
    python fetch_posters_tmdb.py anime.csv anime.csv --api-key YOUR_KEY

Notes:
- Most anime entries on TMDB are catalogued as TV shows, so this tries
  the /tv/{id} endpoint first. If that 404s (a handful of anime films
  are catalogued as movies), it retries against /movie/{id}.
- Image size defaults to w500 (good for a 150px display width with room
  to spare on retina screens). Change POSTER_SIZE if you want larger.
- Progress is cached in poster_cache.json so it's safe to interrupt and
  re-run. IDs with no match are logged to failed_ids.txt.
"""

import argparse
import csv
import json
import os
import sys
import time

import requests

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_SIZE = "w500"  # options: w92, w154, w185, w342, w500, w780, original
IMAGE_BASE = f"https://image.tmdb.org/t/p/{POSTER_SIZE}"

CACHE_FILE = "poster_cache.json"
FAILED_LOG = "failed_ids.txt"

REQUEST_DELAY = 0.05  # TMDB's limit is generous (~50 req/sec), but be polite
MAX_RETRIES = 4


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def _get(url, api_key):
    backoff = 1.0
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params={"api_key": api_key}, timeout=15)
        except requests.RequestException:
            time.sleep(backoff)
            backoff *= 2
            continue

        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return None
        if resp.status_code == 429:
            wait = float(resp.headers.get("Retry-After", backoff))
            time.sleep(wait)
            backoff *= 2
            continue
        # other transient errors
        time.sleep(backoff)
        backoff *= 2
    return None


def fetch_poster(tmdb_id, api_key):
    """Try /tv/{id} first (most anime), then /movie/{id} as fallback."""
    for kind in ("tv", "movie"):
        data = _get(f"{TMDB_BASE}/{kind}/{tmdb_id}", api_key)
        if data and data.get("poster_path"):
            return IMAGE_BASE + data["poster_path"]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    parser.add_argument("--api-key", default=os.environ.get("TMDB_API_KEY"))
    args = parser.parse_args()

    if not args.api_key:
        print("Error: provide a TMDB API key via --api-key or TMDB_API_KEY env var.")
        sys.exit(1)

    cache = load_cache()
    failed_ids = []

    with open(args.input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if "anime_id" not in fieldnames or "image_url" not in fieldnames:
        print("Error: CSV must contain 'anime_id' and 'image_url' columns.")
        sys.exit(1)

    total = len(rows)
    for i, row in enumerate(rows, 1):
        tmdb_id = row["anime_id"]

        if tmdb_id in cache:
            new_url = cache[tmdb_id]
        else:
            new_url = fetch_poster(tmdb_id, args.api_key)
            cache[tmdb_id] = new_url
            if i % 25 == 0:
                save_cache(cache)
            time.sleep(REQUEST_DELAY)

        if new_url:
            row["image_url"] = new_url
        else:
            failed_ids.append(tmdb_id)

        if i % 50 == 0 or i == total:
            print(f"Processed {i}/{total} (tmdb_id={tmdb_id})")

    save_cache(cache)

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if failed_ids:
        with open(FAILED_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(failed_ids))
        print(f"\nDone. {len(failed_ids)} id(s) had no poster; "
              f"see {FAILED_LOG} (original URLs kept for those rows).")
    else:
        print("\nDone. All rows updated successfully.")

    print(f"Output written to: {args.output_csv}")


if __name__ == "__main__":
    main()