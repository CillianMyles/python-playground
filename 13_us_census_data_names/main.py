#!/usr/bin/env python3
"""
Build 3k unique first names (50/50 male/female) and 3k unique last names
from U.S. Census 1990 name files, then generate all 9,000,000 combinations.

Outputs:
data/first_names_male.txt
data/first_names_female.txt
data/first_names_3000.txt        (combined, 3000 unique)
data/last_names_3000.txt         (3000 unique)
data/name_pairs.csv.gz           (9,000,000 rows: first,last)
"""

import csv
import gzip
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from itertools import product

BASE_PAGE = "https://www.census.gov/topics/population/genealogy/data/1990_census/1990_census_namefiles.html"
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

ALPHA_RE = re.compile(r"^[A-Z]+$")


def fetch_census_1990_file_links() -> dict:
    """
    Scrape the Census 1990 names page to discover the three raw file URLs.
    Returns dict with keys: male, female, last
    """
    resp = requests.get(BASE_PAGE, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    links = {"male": None, "female": None, "last": None}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = (a.get_text() or "").strip().lower()
        # The page labels are 'dist.male.first', 'dist.female.first', 'dist.all.last'
        # hrefs are hosted on https://www2.census.gov/...
        if "dist.male.first" in href or "dist.male.first" in text:
            links["male"] = a["href"]
        if "dist.female.first" in href or "dist.female.first" in text:
            links["female"] = a["href"]
        if "dist.all.last" in href or "dist.all.last" in text:
            links["last"] = a["href"]

    # Normalize to absolute URLs if they are relative
    for k, v in links.items():
        if v and v.startswith("/"):
            links[k] = "https://www.census.gov" + v
        # most likely these are already absolute to www2.census.gov
    if not all(links.values()):
        raise RuntimeError(f"Could not locate all required file links: {links}")
    return links


def download_text(url: str) -> List[str]:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    # these files are plain text; split by lines
    return r.text.splitlines()


def parse_census_name_file(lines: List[str]) -> List[Tuple[str, float, float, int]]:
    """
    Each line: NAME <freq%> <cum%> <rank>
    Return list of tuples (NAME, freq, cum, rank)
    """
    records = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 4:
            continue
        name = parts[0].upper()
        try:
            freq = float(parts[1])
            cum = float(parts[2])
            rank = int(parts[3])
        except ValueError:
            continue
        records.append((name, freq, cum, rank))
    # sort by rank (ascending)
    records.sort(key=lambda x: x[3])
    return records


def pick_top_unique(
    records: List[Tuple[str, float, float, int]], n: int, exclude: set = None
) -> List[str]:
    """
    Take names in rank order, keep only alphabetic names, enforce uniqueness,
    and skip any names present in 'exclude' (case-insensitive).
    """
    out = []
    seen = set()
    exclude_lower = {e.lower() for e in (exclude or set())}
    for name, *_ in records:
        if not ALPHA_RE.match(name):
            continue
        if name.lower() in seen or name.lower() in exclude_lower:
            continue
        seen.add(name.lower())
        out.append(name.title())  # Title Case for output
        if len(out) == n:
            break
    if len(out) < n:
        raise RuntimeError(f"Only gathered {len(out)} names, needed {n}.")
    return out


def write_list(path: Path, items: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for x in items:
            f.write(x + "\n")


def generate_pairs_gzip(
    first_names: List[str], last_names: List[str], out_path: Path
) -> None:
    """
    Stream 9,000,000 rows to a gzipped CSV: 'first,last'
    """
    total = len(first_names) * len(last_names)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out_path, "wt", encoding="utf-8", newline="") as gz:
        writer = csv.writer(gz)
        writer.writerow(["first", "last"])
        # TQDM on last_names to keep the progress bar moving every outer loop
        for ln in tqdm(
            last_names,
            total=len(last_names),
            desc="Writing combinations (outer: last names)",
        ):
            for fn in first_names:
                writer.writerow([fn, ln])


def main():
    print("Discovering file links on census.gov …")
    links = fetch_census_1990_file_links()
    print("Links found:")
    for k, v in links.items():
        print(f"  {k}: {v}")

    print("\nDownloading source files …")
    male_lines = download_text(links["male"])
    female_lines = download_text(links["female"])
    last_lines = download_text(links["last"])

    print("Parsing files …")
    male_records = parse_census_name_file(male_lines)
    female_records = parse_census_name_file(female_lines)
    last_records = parse_census_name_file(last_lines)

    print("Selecting 1,500 male + 1,500 female first names with no overlap …")
    male_first_1500 = pick_top_unique(male_records, n=1500)
    female_first_1500 = pick_top_unique(
        female_records, n=1500, exclude=set(male_first_1500)
    )

    # Combine to 3,000 unique first names (preserving balance)
    all_first_3000 = male_first_1500 + female_first_1500

    print("Selecting 3,000 last names …")
    last_3000 = pick_top_unique(last_records, n=3000)

    # Save the picks
    write_list(DATA_DIR / "first_names_male.txt", male_first_1500)
    write_list(DATA_DIR / "first_names_female.txt", female_first_1500)
    write_list(DATA_DIR / "first_names_3000.txt", all_first_3000)
    write_list(DATA_DIR / "last_names_3000.txt", last_3000)

    print("\nGenerating all 9,000,000 combinations (gzipped CSV) …")
    out_csv_gz = DATA_DIR / "name_pairs.csv.gz"
    generate_pairs_gzip(all_first_3000, last_3000, out_csv_gz)

    print("\nDone!")
    print(f"- First names (male):    {DATA_DIR / 'first_names_male.txt'}")
    print(f"- First names (female):  {DATA_DIR / 'first_names_female.txt'}")
    print(f"- First names (3000):    {DATA_DIR / 'first_names_3000.txt'}")
    print(f"- Last names (3000):     {DATA_DIR / 'last_names_3000.txt'}")
    print(f"- All pairs (CSV.GZ):    {out_csv_gz}")
    print("\nTip: To preview: zcat data/name_pairs.csv.gz | head")


if __name__ == "__main__":
    # Light dependency guardrails
    try:
        import requests  # noqa
        import bs4  # noqa
        import tqdm  # noqa
    except Exception as e:
        print(
            "Missing dependency. Install with:\n  pip install requests beautifulsoup4 tqdm\n",
            file=sys.stderr,
        )
        raise
    main()
