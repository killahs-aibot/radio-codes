# -*- coding: utf-8 -*-
"""
BluePill Scraper — MHH AUTO RadioCodeDatabase thread scraper

MHH AUTO (mhhauto.com) has a thread "RadioCodeDatabase-Free-for-all"
with thousands of serial+code pairs across dozens of brands.
This scraper fetches and parses it.

Target URL: https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
"""

import re
import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://mhhauto.com"
THREAD_PATH = "/Thread-RadioCodeDatabase-Free-for-all"
USER_AGENT = "Mozilla/5.0 (compatible; RadioUnlockBot/0.1; research)"

# Known Blaupunkt serial prefixes
BP_PREFIXES = [
    "BP",      # Blaupunkt standard
    "AUZ",     # Audi VW Blaupunkt (e.g. AUZ1Z1...)
    "VWZ",     # VW Blaupunkt
    "GM0",     # GM/Blaupunkt (Opel/Vauxhall)
    "SEZ",     # Seat
    "SKZ",     # Skoda
    "F0",      # Ford Blaupunkt
    "7",       # Siemens/Blaupunkt
]

# Brand tags used in MHH AUTO posts
BRAND_TAGS = {
    "Blaupunkt": "blaupunkt",
    "BP": "blaupunkt",
    "Peugeot": "peugeot",
    "Citroen": "citroen",
    "VW": "vw",
    "Audi": "audi",
    "Seat": "seat",
    "Skoda": "skoda",
    "Opel": "opel",
    "Vauxhall": "vauxhall",
    "Ford": "ford",
    "Renault": "renault",
    "Nissan": "nissan",
    "Honda": "honda",
    "Toyota": "toyota",
    "Alfa": "alfa",
    "Fiat": "fiat",
    "Chrysler": "chrysler",
    "Jaguar": "jaguar",
}


@dataclass
class SerialCodePair:
    serial: str
    code: str
    brand: str
    model: str = ""
    source_url: str = ""
    source_post: int = 0
    line_raw: str = ""

    def to_csv_row(self) -> str:
        return f"{self.brand},{self._esc(self.serial)},{self.code},{self._esc(self.model)},{self._esc(self.source_url)}"

    def _esc(self, s: str) -> str:
        if not s:
            return ""
        if "," in s or '"' in s or "\n" in s:
            return f'"{s.replace("\"","\"\"")}"'
        return s


class MHHMHFScraper:
    """Scrapes MHH AUTO RadioCodeDatabase thread for serial+code pairs."""

    def __init__(self, cookies: Optional[dict] = None, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        if cookies:
            self.session.cookies.update(cookies)
        self.pairs: List[SerialCodePair] = []
        self.seen: Set[str] = set()

    def _normalize_serial(self, serial: str) -> str:
        """Uppercase, strip whitespace and dashes."""
        return re.sub(r"[\s\-]", "", serial.upper())

    def _is_likely_serial(self, s: str) -> bool:
        """Heuristic: serials are 4-20 alphanumeric chars."""
        s = s.upper()
        if len(s) < 4 or len(s) > 20:
            return False
        # Must have at least 2 alphanumeric
        alnum = sum(c.isalnum() for c in s)
        if alnum < 4:
            return False
        return True

    def _is_likely_code(self, code: str) -> bool:
        """Heuristic: codes are 3-6 digits, first digit not usually 0."""
        code = code.strip()
        if not re.fullmatch(r"\d{3,6}", code):
            return False
        return True

    def _detect_brand(self, context: str) -> str:
        """Detect brand from surrounding text context."""
        context_upper = context.upper()
        for tag, brand in BRAND_TAGS.items():
            if tag.upper() in context_upper:
                return brand
        return "unknown"

    def _parse_post(self, post_text: str, post_id: int) -> List[SerialCodePair]:
        """Extract serial+code pairs from a forum post."""
        pairs = []
        lines = post_text.split("\n")

        for i, line in enumerate(lines):
            # Clean the line
            raw = line.strip()
            if not raw or len(raw) < 4:
                continue

            # Skip quote lines
            if raw.startswith(">"):
                continue
            # Skip URL-only lines
            if raw.startswith("http"):
                continue
            # Skip empty brackets
            if re.match(r"^\[.*\]$", raw):
                continue

            # ── Pattern 1: "Serial: XXXXX  Code: YYYY" ──
            for m in re.finditer(
                r"(?:serial|part|partnumber|serial no|serial number|pn|p\/n|part no)[^\w\d]*(?P<serial>[\w]{4,20})[^\d]*(?:code|cod|pass|key|unlock)[^\w\d]*(?P<code>\d{3,6})",
                raw, re.IGNORECASE
            ):
                ctx = post_text[max(0, i-2):i+3]
                brand = self._detect_brand(ctx)
                s = self._normalize_serial(m.group("serial"))
                if s not in self.seen and self._is_likely_serial(s):
                    self.seen.add(s)
                    pairs.append(SerialCodePair(
                        serial=s, code=m.group("code").lstrip("0") or "0",
                        brand=brand, source_post=post_id, line_raw=raw,
                        source_url=f"{BASE_URL}{THREAD_PATH}#post{post_id}"
                    ))

            # ── Pattern 2: "XXXXX → YYYY" or "XXXXX = YYYY" ──
            for m in re.finditer(
                r"(?P<serial>[\w]{4,20})\s*[→=:\-\|]+\s*(?P<code>\d{3,6})",
                raw
            ):
                s = self._normalize_serial(m.group("serial"))
                if s not in self.seen and self._is_likely_serial(s):
                    ctx = post_text[max(0, i-2):i+3]
                    brand = self._detect_brand(ctx)
                    self.seen.add(s)
                    pairs.append(SerialCodePair(
                        serial=s, code=m.group("code").lstrip("0") or "0",
                        brand=brand, source_post=post_id, line_raw=raw,
                        source_url=f"{BASE_URL}{THREAD_PATH}#post{post_id}"
                    ))

            # ── Pattern 3: "MODEL: XXXXX  CODE: YYYY" (Blaupunkt style) ──
            for m in re.finditer(
                r"(?:BP|AUZ|VWZ|GM0|SEZ|SKZ|F0|7)[\w\-]{3,18}\s*(?P<code>\d{3,6})",
                raw
            ):
                s = self._normalize_serial(m.group(0).rsplit(None, 1)[0])
                code = m.group("code")
                if s not in self.seen:
                    ctx = post_text[max(0, i-2):i+3]
                    brand = self._detect_brand(ctx)
                    self.seen.add(s)
                    pairs.append(SerialCodePair(
                        serial=s, code=code.lstrip("0") or "0",
                        brand=brand, source_post=post_id, line_raw=raw,
                        source_url=f"{BASE_URL}{THREAD_PATH}#post{post_id}"
                    ))

            # ── Pattern 4: "XXXXX YYYY" (two adjacent words, code looks like number) ──
            for m in re.finditer(
                r"(?<![a-zA-Z0-9])(?P<code>\d{3,6})(?=\s|$|[^\s\d])",
                raw
            ):
                # Only if preceded by something that looks like a serial
                # Look at last 30 chars before the number for context
                before = raw[max(0, m.start()-30):m.start()]
                if self._is_likely_serial(before.strip()):
                    s = self._normalize_serial(before.strip())
                    code = m.group("code")
                    if s not in self.seen:
                        ctx = post_text[max(0, i-2):i+3]
                        brand = self._detect_brand(ctx)
                        self.seen.add(s)
                        pairs.append(SerialCodePair(
                            serial=s, code=code.lstrip("0") or "0",
                            brand=brand, source_post=post_id, line_raw=raw,
                            source_url=f"{BASE_URL}{THREAD_PATH}#post{post_id}"
                        ))

        return pairs

    def fetch_thread_pages(self, max_pages: int = 20) -> int:
        """Fetch pages of the thread and extract pairs. Returns total pairs found."""
        page = 1
        total = 0

        while page <= max_pages:
            if page == 1:
                url = f"{BASE_URL}{THREAD_PATH}"
            else:
                url = f"{BASE_URL}{THREAD_PATH}/page{page}"

            try:
                r = self.session.get(url, timeout=15)
                r.raise_for_status()
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch page {page}: {e}")
                break

            # MHH AUTO uses vBulletin, pages may have post list
            # Extract post content blocks (vBulletin post class)
            post_blocks = re.findall(
                r'<div class="[^"]*postbody[^"]*"[^>]*>(.*?)</div>\s*<div class="[^"]*postdetails',
                r.text, re.DOTALL | re.IGNORECASE
            )

            if not post_blocks:
                logger.info(f"No post blocks found on page {page}, trying alt selector")
                # Try alternate vBulletin 5 pattern
                post_blocks = re.findall(
                    r'<article[^>]*>(.*?)</article>', r.text, re.DOTALL
                )
                if not post_blocks:
                    logger.info(f"Page {page} has no extractable posts, stopping.")
                    break

            for post_id, block in enumerate(post_blocks, start=(page-1)*20+1):
                # Strip HTML
                text = re.sub(r"<[^>]+>", " ", block)
                text = re.sub(r"&[a-z]+;", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
                pairs = self._parse_post(text, post_id)
                self.pairs.extend(pairs)
                total += len(pairs)

            logger.info(f"Page {page}: {len(post_blocks)} posts, {total} total pairs")
            page += 1
            time.sleep(1.5)  # Be polite

        return total

    def filter_blaupunkt(self) -> List[SerialCodePair]:
        """Return only pairs where serial starts with known BP prefixes."""
        bp = []
        for p in self.pairs:
            for prefix in BP_PREFIXES:
                if p.serial.startswith(prefix):
                    bp.append(p)
                    break
        return bp

    def save_csv(self, path: Path, brand_filter: Optional[str] = None):
        """Save all pairs (optionally filtered by brand) to CSV."""
        rows = [SerialCodePair("", "", "").to_csv_row().replace(",,,", "brand,serial,code,model,source_url").rstrip(",")]
        if brand_filter:
            filtered = [p for p in self.pairs if p.brand == brand_filter]
        else:
            filtered = self.pairs

        # CSV header
        rows[0] = "brand,serial,code,model,source_url"

        for p in filtered:
            rows.append(p.to_csv_row())

        path.write_text("\n".join(rows) + "\n")
        logger.info(f"Saved {len(rows)-1} pairs to {path}")
