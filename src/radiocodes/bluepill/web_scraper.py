# -*- coding: utf-8 -*-
"""
BluePill Web Scraper — carstereocode.com scraper

Site uses: unlock.php?mk={brand_id}
mk IDs (from list.php dropdown):
  1=Alfa Romeo, 2=Audi, 3=BMW, 4=Citroen, 5=Fiat, 6=Ford, 7=Honda,
  8=Jaguar, 9=Lancia, 10=Land Rover, 11=Mercedes, 12=Mini, 13=Nissan,
  14=Opel, 15=Peugeot, 16=Renault, 17=Seat, 18=Skoda, 19=Toyota,
  20=VW, 21=Volvo, 22=Chrysler, 28=Blaupunkt, 29=Other

Page format: serial / model-name - code  OR  serial / code
Many pages have 200-400+ pairs each.
"""

import re
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.carstereocode.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL + "/",
}

# Brand name → mk ID mapping
MK_MAP: Dict[str, int] = {
    "alfa": 1, "alfa-romeo": 1,
    "audi": 2,
    "bmw": 3,
    "citroen": 4,
    "fiat": 5,
    "ford": 6,
    "honda": 7,
    "jaguar": 8,
    "lancia": 9,
    "landrover": 10, "land rover": 10,
    "mercedes": 11,
    "mini": 12,
    "nissan": 13,
    "opel": 14,
    "peugeot": 15,
    "renault": 16,
    "seat": 17,
    "skoda": 18,
    "toyota": 19,
    "vw": 20, "volkswagen": 20,
    "volvo": 21,
    "chrysler": 22,
    "blaupunkt": 28,
    "other": 29,
}

MK_TO_BRAND: Dict[int, str] = {v: k for k, v in MK_MAP.items()}

# Known serial prefixes per brand (to classify or filter pairs)
BRAND_PREFIXES: Dict[str, List[str]] = {
    "blaupunkt": ["BP", "AUZ", "VWZ", "GM0", "SEZ", "SKZ", "F0", "GM"],
    "peugeot":   ["BP", "815", "7"],
    "citroen":   ["BP", "815", "6"],
    "opel":      ["GM0", "GM1", "GM2", "GM", "CM01"],
    "vauxhall":  ["GM0", "GM1", "GM2", "GM", "CM01"],
    "vw":        ["VWZ", "AUZ", "LPZ", "VVZ"],
    "audi":      ["AUZ", "VWZ"],
    "ford":      ["M", "V", "F"],
    "renault":   ["LP", "CL", "R", "D"],
    "nissan":    ["BP", "B7", "PN"],
    "honda":     ["U", "L"],
    "toyota":    [],
    "fiat":      ["BP", "5K", "FK"],
    "alfa":      ["BP", "AR"],
    "chrysler":  ["BP", "CH"],
    "jaguar":    ["BP", "JA", "JAG"],
}


@dataclass
class StereoCodePair:
    serial: str
    code: str
    brand: str
    model: str = ""
    source: str = ""
    line_raw: str = ""

    def to_csv_row(self) -> str:
        m = f'"{self.model.replace("\"","\"\"")}"' if "," in self.model else self.model
        s = f'"{self.serial.replace("\"","\"\"")}"' if "," in self.serial else self.serial
        return f"{self.brand},{s},{self.code},{m},{self.source}"

    def _esc(self, s: str) -> str:
        if not s:
            return ""
        if "," in s or '"' in s or "\n" in s:
            return f'"{s.replace("\"","\"\"")}"'
        return s


class CarStereoCodeScraper:
    """Scrapes carstereocode.com for serial+code pairs."""

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(HEADERS)
        self.pairs: List[StereoCodePair] = []
        self.seen: Set[str] = set()
        self.stats: Dict[str, int] = {}

    def _norm(self, s: str) -> str:
        return re.sub(r"[\s\-\.]", "", s.upper())

    def _is_serial(self, s: str) -> bool:
        s = s.upper()
        if len(s) < 4 or len(s) > 20:
            return False
        alnum = sum(c.isalnum() for c in s)
        return alnum >= 4

    def _detect_brand(self, serial: str) -> str:
        s = serial.upper()
        for brand, prefixes in BRAND_PREFIXES.items():
            for pre in prefixes:
                if s.startswith(pre):
                    return brand
        return ""

    def fetch_brand_page(self, brand: str) -> int:
        """Fetch carstereocode.com page for a brand. Returns pair count."""
        mk_id = MK_MAP.get(brand.lower())
        if mk_id is None:
            logger.warning(f"Unknown brand: {brand}")
            return 0

        url = f"{BASE_URL}/unlock.php?mk={mk_id}"
        try:
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch mk={mk_id} ({brand}): {e}")
            return 0

        html = r.text
        pairs_found = self._parse_page(html, brand, url)
        self.stats[brand] = len(pairs_found)
        logger.info(f"mk={mk_id} ({brand}): {len(pairs_found)} pairs")
        return len(pairs_found)

    def _parse_page(self, html: str, brand: str, url: str) -> List[StereoCodePair]:
        """Parse the unlock.php page for serial+code pairs."""
        pairs = []

        # The page content is mostly raw text separated by <br> and newlines
        # Strip HTML tags, keep structure
        text = re.sub(r"<br[^>]*>", "\n", html)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&\w+;", " ", text)
        text = re.sub(r"\s+", " ", text)
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if len(line) < 6:
                continue

            # ── Format 1: "SERIAL / MODEL - CODE" or "SERIAL / CODE" ──
            # Split on " / " to separate serial from rest
            parts = re.split(r"\s*/\s*", line)
            if len(parts) < 2:
                continue

            serial_raw = parts[0].strip()
            rest = " / ".join(parts[1:])

            # Extract code: last group of 3-6 digits at end of rest
            code_match = re.search(r"\b(\d{3,6})\b\s*$", rest)
            if not code_match:
                continue
            code = code_match.group(1).lstrip("0") or "0"

            # Extract model name: everything between serial and code
            model = ""
            model_and_code = rest[:code_match.start()].strip()
            if model_and_code:
                # Remove trailing dashes/hyphens
                model = re.sub(r"\s*-\s*$", "", model_and_code).strip()

            # Normalize serial
            serial = self._norm(serial_raw)
            if not self._is_serial(serial):
                # Maybe it's the code that's the serial and serial is somewhere else
                # Try: look for serial pattern anywhere in line
                serial_candidates = re.findall(r"\b([A-Z0-9]{6,18})\b", serial_raw)
                if serial_candidates:
                    serial = self._norm(serial_candidates[0])
                    if not self._is_serial(serial):
                        continue
                else:
                    continue

            if serial in self.seen:
                continue
            self.seen.add(serial)

            # Auto-detect brand from prefix
            detected_brand = self._detect_brand(serial)
            final_brand = detected_brand if detected_brand else brand

            pairs.append(StereoCodePair(
                serial=serial,
                code=code,
                brand=final_brand,
                model=model,
                source=url,
                line_raw=line[:100],
            ))

        return pairs

    def scrape_all(self) -> Dict[str, int]:
        """Scrape all known brands. Returns {brand: count}."""
        results = {}
        for brand in MK_MAP:
            if brand in ("other",):
                continue
            n = self.fetch_brand_page(brand)
            results[brand] = n
            self.pairs.extend(self._parse_page("", brand, "") or [])
            # Actually fetch_brand_page already parses, no need to call _parse_page again
            time.sleep(0.5)

        # Fix: pairs already added in fetch_brand_page
        return results

    def save_csv(self, path: Path, brand_filter: Optional[str] = None):
        if brand_filter:
            filtered = [p for p in self.pairs if p.brand == brand_filter]
        else:
            filtered = self.pairs

        rows = ["brand,serial,code,model,source_url"]
        for p in filtered:
            rows.append(p.to_csv_row())

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(rows) + "\n")
        logger.info(f"Saved {len(filtered)} pairs → {path}")
