"""
Post 9 — VesselFinder name scraper (public data only, respectful rate).

PURPOSE: Get vessel_name for each IMO. That's it. Only public info, no login needed.
         (Owner/Manager is behind paywall — we don't touch that.)

RESPECT:
- 8-12s random delay between requests (~5-7 req/min)
- Standard User-Agent
- Session cookies maintained
- Backoff on 429 (rate limit) errors
- Incremental save (crash-safe)
- Zero attempt to bypass any protection

USAGE:
    python scripts/scrape_vessel_names.py --test    # 5 IMOs test
    python scripts/scrape_vessel_names.py           # all pending IMOs
"""

import os
import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None

# =============================================================================
# Config
# =============================================================================

_script_dir = Path(__file__).resolve().parent
if (_script_dir.parent / "data" / "imos_to_lookup.csv").exists():
    DATA_DIR = _script_dir.parent / "data"
elif (_script_dir.parent.parent / "Data" / "post9" / "imos_to_lookup.csv").exists():
    DATA_DIR = _script_dir.parent.parent / "Data" / "post9"
else:
    DATA_DIR = _script_dir.parent / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_CSV = DATA_DIR / "imos_to_lookup.csv"
OUTPUT_CSV = DATA_DIR / "vessel_names.csv"

BASE_URL = "https://www.vesselfinder.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Respectful delays — 8-12s per request → ~5-7 req/min
DELAY_MIN = 8.0
DELAY_MAX = 12.0

# Backoff on rate limit / block
BACKOFF_SHORT = 60      # 1 min if 429
BACKOFF_LONG = 600      # 10 min if repeated

# =============================================================================
# CLI
# =============================================================================

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args = parser.parse_args()

# =============================================================================
# Load IMOs
# =============================================================================

print("=" * 70)
print("Post 9 — VesselFinder name scraper")
print("=" * 70)

df_input = pd.read_csv(INPUT_CSV, sep=";", encoding="utf-8-sig")
imos_all = df_input["imo"].astype(int).tolist()
print(f"\n[Input] Total IMOs: {len(imos_all):,}")

if OUTPUT_CSV.exists():
    df_done = pd.read_csv(OUTPUT_CSV, sep=";", encoding="utf-8-sig")
    imos_done = set(df_done["imo"].astype(int).tolist())
    print(f"[Resume] Already done: {len(imos_done):,}")
else:
    imos_done = set()
    pd.DataFrame(columns=[
        "imo", "vessel_name", "vessel_type", "flag", "scraped_at", "status"
    ]).to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8-sig")

imos_todo = [imo for imo in imos_all if imo not in imos_done]
if args.test:
    imos_todo = imos_todo[:5]

print(f"[Scope] To process: {len(imos_todo):,}")

# Time estimate
est_min = len(imos_todo) * ((DELAY_MIN + DELAY_MAX) / 2 + 1) / 60
print(f"[Estimate] ~{est_min:.0f} minutes ({est_min/60:.1f} hours)")

if not imos_todo:
    print("Nothing to do.")
    sys.exit(0)


# =============================================================================
# Scraper
# =============================================================================

def scrape_one(session, imo):
    """Scrape vessel name from VesselFinder public page."""
    url = f"{BASE_URL}/vessels/details/{imo}"
    result = {
        "imo": imo,
        "vessel_name": "",
        "vessel_type": "",
        "flag": "",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "status": "OK",
    }

    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        result["status"] = f"HTTP_ERROR: {type(e).__name__}"
        return result, None

    if resp.status_code == 429:
        result["status"] = "RATE_LIMITED"
        return result, "backoff"

    if resp.status_code == 404:
        result["status"] = "NOT_FOUND"
        return result, None

    if resp.status_code != 200:
        result["status"] = f"HTTP_{resp.status_code}"
        return result, None

    # Parse vessel name from <title> or h1
    soup = BeautifulSoup(resp.text, "html.parser")

    # VesselFinder title format: "VESSEL NAME, Type - Details and current position - IMO XXXX - VesselFinder"
    title = soup.find("title")
    if title:
        title_text = title.get_text(strip=True)
        # Extract vessel name (before first comma)
        if "," in title_text:
            result["vessel_name"] = title_text.split(",")[0].strip()
            # Extract type (after first comma, before " -")
            after_comma = title_text.split(",", 1)[1]
            if " -" in after_comma:
                result["vessel_type"] = after_comma.split(" -")[0].strip()

    # Fallback: h1
    if not result["vessel_name"]:
        h1 = soup.find("h1")
        if h1:
            result["vessel_name"] = h1.get_text(strip=True)[:100]

    # Extract flag if visible in the details section
    # VesselFinder typically has "IMO / MMSI" section with flag
    for label in ["AIS Flag", "Flag"]:
        idx = resp.text.find(label)
        if idx > 0:
            # Look for country name in next 200 chars
            snippet = resp.text[idx:idx + 200]
            # Very naive extraction; skip if not obvious
            break

    if not result["vessel_name"]:
        result["status"] = "NAME_NOT_PARSED"

    return result, None


def append_result(row):
    df_row = pd.DataFrame([row])
    df_row.to_csv(OUTPUT_CSV, sep=";", index=False, encoding="utf-8-sig",
                  header=False, mode="a")


# =============================================================================
# Main loop
# =============================================================================

def main():
    session = requests.Session()

    n_ok = 0
    n_fail = 0
    n_backoff = 0
    start_time = time.time()

    for i, imo in enumerate(imos_todo, 1):
        row, action = scrape_one(session, imo)
        append_result(row)

        if row["status"] == "OK":
            n_ok += 1
        else:
            n_fail += 1

        # Handle rate limit
        if action == "backoff":
            n_backoff += 1
            backoff = BACKOFF_LONG if n_backoff > 2 else BACKOFF_SHORT
            print(f"  [!] Rate limited. Backing off {backoff}s...", flush=True)
            time.sleep(backoff)
            # Reset backoff counter after successful sleep
            n_backoff = max(0, n_backoff - 1)

        elapsed = time.time() - start_time
        rate = i / elapsed if elapsed > 0 else 0
        eta_min = (len(imos_todo) - i) / rate / 60 if rate > 0 else 0

        log_every = 1 if args.test else 20
        if i % log_every == 0 or i == len(imos_todo):
            name_short = row["vessel_name"][:30] if row["vessel_name"] else ""
            print(f"  [{i:>4}/{len(imos_todo)}] IMO {imo} | {row['status'][:12]:12} | "
                  f"{name_short:30} | OK={n_ok} FAIL={n_fail} | ETA={eta_min:.0f}min",
                  flush=True)

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    elapsed_min = (time.time() - start_time) / 60
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    print(f"  Processed: {len(imos_todo)}")
    print(f"  OK:        {n_ok}")
    print(f"  Failed:    {n_fail}")
    print(f"  Elapsed:   {elapsed_min:.1f} min ({elapsed_min/60:.1f}h)")
    print(f"  Output:    {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
