# -*- coding: utf-8 -*-
"""
RadioUnlock Lookup Engine.
Ingests forum_pairs.csv and provides instant free lookups by brand + serial.
Skips entries where code is XXXX or empty.
"""

import csv
import os
from pathlib import Path
from typing import Optional, Dict

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DEFAULT_CSV = DATA_DIR / "forum_pairs.csv"

# In-memory lookup: {(brand, serial): {"code": str, "model": str, "source": str}}
_LOOKUP_EXACT: Dict = {}
# Prefix lookup: {(brand, prefix): {"code": str, ...}}  (prefix length as key)
_LOOKUP_PREFIX: Dict = {}
_LOADED = False

def load_csv(csv_path=None) -> int:
    """Load forum pairs into memory. Skips XXXX codes."""
    global _LOOKUP_EXACT, _LOOKUP_PREFIX, _LOADED
    _LOOKUP_EXACT = {}
    _LOOKUP_PREFIX = {}
    _LOADED = True

    path = csv_path or DEFAULT_CSV
    if not os.path.exists(path):
        return 0

    count = 0
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            brand = row[0].strip().lower()
            serial_raw = row[1].strip()
            code = row[2].strip() if len(row) > 2 else ""
            model = row[3].strip() if len(row) > 3 else ""
            source = row[4].strip() if len(row) > 4 else ""

            if not brand or not serial_raw or not code:
                continue
            if code.upper() == "XXXX" or code == "0000":
                continue  # Skip unknown/invalid codes

            serial = serial_raw.upper().replace(" ", "").replace("-", "")
            if len(serial) < 4:
                continue

            info = {"code": code, "model": model, "source": source}

            # Exact match (full serial)
            key = (brand, serial)
            _LOOKUP_EXACT[key] = info

            # Prefix matches (for serials where we only know a prefix)
            for pl in range(4, len(serial)):
                prefix = serial[:pl]
                pkey = (brand, prefix)
                # Keep longest prefix match
                if pkey not in _LOOKUP_PREFIX or len(prefix) > len(_LOOKUP_PREFIX.get(pkey, {}).get("_prefix", "")):
                    _LOOKUP_PREFIX[pkey] = {**info, "_prefix": prefix}

            count += 1

    return count

def lookup(brand: str, serial: str) -> Optional[Dict]:
    """Find code by exact serial match."""
    if not _LOADED:
        load_csv()
    serial = serial.upper().replace(" ", "").replace("-", "")
    brand_key = brand.lower()
    return _LOOKUP_EXACT.get((brand_key, serial))

def prefix_lookup(brand: str, serial: str, min_length: int = 8) -> Optional[Dict]:
    """Find code by prefix match. Returns best (longest) match."""
    if not _LOADED:
        load_csv()
    serial = serial.upper().replace(" ", "").replace("-", "")
    brand_key = brand.lower()

    # Find all matching prefixes
    best = None
    best_len = 0
    for (b, prefix), info in _LOOKUP_PREFIX.items():
        if b == brand_key and serial.startswith(prefix) and len(prefix) >= min_length:
            if len(prefix) > best_len:
                best = info
                best_len = len(prefix)

    return best

def get_stats() -> Dict:
    """Return stats about loaded data."""
    if not _LOADED:
        load_csv()
    brands = {}
    for (brand, serial), info in _LOOKUP_EXACT.items():
        brands[brand] = brands.get(brand, 0) + 1
    return {"total_pairs": len(_LOOKUP_EXACT), "brands": brands}
