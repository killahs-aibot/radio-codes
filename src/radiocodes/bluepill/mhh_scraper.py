# -*- coding: utf-8 -*-
"""
BluePill MHH Scraper — authenticated scraping of MHH AUTO RadioCodeDatabase thread

Uses DrissionPage (Chromium) to scrape the authenticated session.
Thread: https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all
Pages: 703 (as of 2026-03-20)
Each page: ~9 posts, some contain serial+code pairs

Usage:
  python -m radiocodes.bluepill.mhh_scraper --start-page 1 --end-page 703 --output /path/to/output.csv
"""

import re
import sys
import json
import time
import argparse
import csv
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger("mhh_scraper")


@dataclass
class RadioPair:
    serial: str
    code: str
    brand: str
    model: str
    source_page: int
    source_post: int
    author: str


BRAND_KEYWORDS = {
    "Blaupunkt": "blaupunkt", "BP": "blaupunkt", "AUZ": "audi", "VWZ": "vw",
    "SKZ": "skoda", "SEZ": "seat", "GM0": "opel", "GM0203": "opel", "GM0204": "opel",
    "GM0300": "opel", "GM0400": "opel", "GM0600": "opel", "GM0700": "opel",
    "GM0800": "opel", "Peugeot": "peugeot", "Citroen": "citroen", "Fiat": "fiat",
    "Ford": "ford", "Renault": "renault", "Nissan": "nissan", "Honda": "honda",
    "Toyota": "toyota", "Opel": "opel", "Vauxhall": "vauxhall", "VW": "vw",
    "Audi": "audi", "Seat": "seat", "Skoda": "skoda", "Alfa": "alfa-romeo",
    "Chrysler": "chrysler", "Jaguar": "jaguar", "BMW": "bmw", "Mercedes": "mercedes",
}


def normalize_serial(s: str) -> str:
    return re.sub(r"[\s\-\.]", "", s.upper())


def is_likely_serial(s: str) -> bool:
    s = normalize_serial(s)
    if len(s) < 3 or len(s) > 25:
        return False
    alnum = sum(c.isalnum() for c in s)
    return alnum >= 3


def is_likely_code(s: str) -> bool:
    s = s.strip()
    if not re.fullmatch(r"\d{3,6}", s):
        return False
    # First digit usually not 0 for 4-digit codes
    return True


def detect_brand(text: str) -> str:
    text_upper = text.upper()
    for keyword, brand in BRAND_KEYWORDS.items():
        if keyword.upper() in text_upper:
            return brand
    return "unknown"


def extract_pairs_from_post(post_text: str, page_num: int, post_idx: int, author: str) -> list:
    """Extract serial+code pairs from a single post's text.
    
    The post may be one long line or multiple paragraphs.
    Radio code data comes in formats like:
      - "VWZ- s/n +code 340480 poz" (split on 'poz')
      - "BP123456789 / 4321" (slash separated)
      - "Serial: VWZ1234 Code: 1234" 
    """
    pairs = []

    # ── Pre-split on sentence boundaries to create analyzable chunks ──
    # The forum posts are often one long line; split on meaningful delimiters
    raw_chunks = post_text.split('poz')

    # Also split on double-space sentence boundaries
    refined_chunks = []
    for chunk in raw_chunks:
        for sub in chunk.split('  '):
            stripped = sub.strip()
            if stripped:
                refined_chunks.append(stripped)

    # Process each chunk
    for line in refined_chunks:
        line = line.strip()
        if len(line) < 6:
            continue

        # Skip quotes and boilerplate
        if re.match(r"^\(.*\)\s*(Wrote:|Thanks|Report|$)", line):
            continue
        if "api-ms-win" in line.lower() or "dll" in line.lower():
            continue
        if "paypal" in line.lower() or "donate" in line.lower():
            continue
        if "off('click')" in line or "$('#" in line:
            continue
        if "can calculate" in line.lower() or "can i have" in line.lower() or "help me" in line.lower():
            continue  # User requests, not answers

        # ── Pattern 0: "Serial: XXXXX Thank" (single serial, no code in post) ──
        if re.match(r"^Serial:\s*[\w]{5,20}\s*Thank", line, re.I):
            continue

        # ── Pattern 1: Serial / Code (slash-separated) ──
        for m in re.finditer(
            r"(?P<serial>[\w]{4,22})\s*/\s*(?P<code>\d{3,6})",
            line
        ):
            serial = normalize_serial(m.group("serial"))
            code = m.group("code").lstrip("0") or "0"
            if is_likely_serial(serial) and is_likely_code(code):
                brand = detect_brand(line)
                pairs.append(RadioPair(
                    serial=serial, code=code, brand=brand,
                    model="", source_page=page_num,
                    source_post=post_idx, author=author
                ))

        # ── Pattern 2: Serial → Code or Serial = Code ──
        for m in re.finditer(
            r"(?P<serial>[\w]{4,22})\s*[→=\-|:]\s*(?P<code>\d{3,6})",
            line
        ):
            serial = normalize_serial(m.group("serial"))
            code = m.group("code").lstrip("0") or "0"
            if is_likely_serial(serial) and is_likely_code(code):
                brand = detect_brand(line)
                pairs.append(RadioPair(
                    serial=serial, code=code, brand=brand,
                    model="", source_page=page_num,
                    source_post=post_idx, author=author
                ))

        # ── Pattern 3: "Serial: XXXXX Code: YYYY" ──
        for m in re.finditer(
            r"(?:serial|part|serial no|part number)[^\w]*(?P<serial>[\w]{4,20})[^\d]*(?:code|pass|pin)[^\w]*(?P<code>\d{3,6})",
            line, re.IGNORECASE
        ):
            serial = normalize_serial(m.group("serial"))
            code = m.group("code").lstrip("0") or "0"
            if is_likely_serial(serial) and is_likely_code(code):
                brand = detect_brand(line)
                pairs.append(RadioPair(
                    serial=serial, code=code, brand=brand,
                    model="", source_page=page_num,
                    source_post=post_idx, author=author
                ))

        # ── Pattern 4: "SERIAL s/n +code CODE" or "SERIAL s/n +code CODE poz" ──
        # e.g. "VWZ- s/n +code 340480" or "AUZ- s/n +code 129460 poz"
        for m in re.finditer(
            r"(?P<serial>(?:VWZ|AUZ|SEZ|SKZ|GM0\d+|BP|RCD)\-?\w{0,18})\s+s\/n\s+\+\s*code[^\d]*(?P<code>\d{3,6})",
            line, re.IGNORECASE
        ):
            serial = normalize_serial(m.group("serial"))
            code = m.group("code").lstrip("0") or "0"
            if is_likely_serial(serial) and is_likely_code(code):
                brand = detect_brand(line)
                pairs.append(RadioPair(
                    serial=serial, code=code, brand=brand,
                    model="", source_page=page_num,
                    source_post=post_idx, author=author
                ))

        # ── Pattern 5: "SERIAL CODE" (two adjacent words, serial first) ──
        # e.g. "BP123456789 1234" or "VWZ1234567 5678"
        for m in re.finditer(
            r"\b(?P<serial>(?:BP|VWZ|AUZ|SEZ|SKZ|GM0\d+|RCD)[A-Z0-9\-]{3,15})\s+(?P<code>\d{4,6})\b",
            line
        ):
            serial = normalize_serial(m.group("serial"))
            code = m.group("code").lstrip("0") or "0"
            if is_likely_serial(serial) and is_likely_code(code):
                brand = detect_brand(line)
                pairs.append(RadioPair(
                    serial=serial, code=code, brand=brand,
                    model="", source_page=page_num,
                    source_post=post_idx, author=author
                ))

    return pairs


def parse_page(html: str, page_num: int) -> tuple[list[RadioPair], int]:
    """Parse a page of the thread. Returns (pairs, total_posts_on_page)."""
    pairs = []

    # Split by post_head divs (space-separated class names: class="col x12 post_head nopad")
    chunks = re.split(r'<div class="col x12 post_head nopad">', html)
    if len(chunks) < 2:
        return pairs, 0

    # Find authors (may appear before post_head in each chunk)
    authors = re.findall(
        r'<a[^>]+href=["\'][^"\']*member\.php\?action=profile[^"\']*["\'][^>]*>([^<]+)<',
        html
    )

    for post_idx, chunk in enumerate(chunks[1:], 1):
        # Extract text content
        text = re.sub(r'<[^>]+>', ' ', chunk)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&\w+;", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text or len(text) < 10:
            continue

        author = authors[post_idx - 1].strip() if post_idx <= len(authors) else "unknown"
        post_pairs = extract_pairs_from_post(text, page_num, post_idx, author)
        pairs.extend(post_pairs)

    return pairs, len(chunks) - 1


def _reconnect_browser(addr: str = '127.0.0.1:9222', timeout: int = 30):
    """Reconnect to an existing Chrome debug session."""
    from DrissionPage import ChromiumPage
    return ChromiumPage(addr_or_opts=addr, timeout=timeout)


def scrape_thread(pages: range, output_path: Path, checkpoint_path: Path,
                  every_n_pages: int = 1) -> int:
    """
    Scrape MHH AUTO thread pages using DrissionPage.
    Returns total pairs found.
    """
    from DrissionPage.errors import ContextLostError, PageDisconnectedError, WaitTimeoutError

    total_pairs = 0
    seen_serials = set()
    all_pairs = []

    # Load checkpoint if exists
    if checkpoint_path.exists():
        try:
            data = json.loads(checkpoint_path.read_text())
            seen_serials = set(data.get("seen_serials", []))
            all_pairs = [RadioPair(**p) for p in data.get("pairs", [])]
            total_pairs = len(all_pairs)
            logger.info(f"Resuming from checkpoint: {total_pairs} pairs, {len(seen_serials)} seen serials")
        except (json.JSONDecodeError, KeyError):
            logger.warning("Checkpoint corrupted, starting fresh")

    browser = _reconnect_browser()
    logger.info("Connected to Chrome debug session")

    # Open thread
    browser.get(
        'https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all',
        timeout=60
    )
    time.sleep(6)

    for page_num in pages:
        retry = 0
        page_pairs = []
        while retry < 3:
            try:
                # Navigate to page
                if page_num > 1:
                    url = f'https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all?page={page_num}'
                    browser.get(url, timeout=20)
                    time.sleep(3)
                else:
                    time.sleep(1)

                html = browser.html
                if len(html) < 500:
                    raise RuntimeError(f"Page {page_num} returned tiny HTML ({len(html)} bytes)")

                page_pairs, post_count = parse_page(html, page_num)
                break  # success

            except (ContextLostError, PageDisconnectedError, WaitTimeoutError, RuntimeError) as e:
                retry += 1
                logger.warning(f"Page {page_num} attempt {retry} failed: {type(e).__name__}: {e}")
                time.sleep(2 * retry)
                if retry >= 3:
                    logger.error(f"Page {page_num} failed after 3 retries, skipping")
                    break
                # Reconnect and reload thread page to revive browser
                try:
                    browser.quit()
                except Exception:
                    pass
                browser = _reconnect_browser()
                time.sleep(3)
                browser.get('https://mhhauto.com/Thread-RadioCodeDatabase-Free-for-all', timeout=30)
                time.sleep(5)

        # Filter to new pairs
        new_pairs = [p for p in page_pairs if p.serial not in seen_serials]
        for p in new_pairs:
            seen_serials.add(p.serial)
            all_pairs.append(p)

        total_pairs += len(new_pairs)

        if page_num % 10 == 0 or new_pairs:
            logger.info(
                f"Page {page_num}: {len(page_pairs)} pairs found, {len(new_pairs)} new "
                f"(total: {total_pairs}, checkpoint saved)"
            )

        # Save checkpoint every N pages
        if page_num % every_n_pages == 0:
            checkpoint_path.write_text(json.dumps({
                "seen_serials": list(seen_serials),
                "pairs": [asdict(p) for p in all_pairs],
            }, indent=2))

        time.sleep(1.5)  # Be polite

    # Final save
    checkpoint_path.write_text(json.dumps({
        "seen_serials": list(seen_serials),
        "pairs": [asdict(p) for p in all_pairs],
    }, indent=2))

    # Export to CSV
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["brand","serial","code","model","author","source_page","source_post"])
        writer.writeheader()
        for p in all_pairs:
            writer.writerow(asdict(p))

    try:
        browser.quit()
    except Exception:
        pass

    logger.info(f"Done! Total pairs: {len(all_pairs)} → {output_path}")
    return len(all_pairs)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    ap = argparse.ArgumentParser(description="MHH AUTO RadioCodeDatabase Scraper")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=703)
    ap.add_argument("--step", type=int, default=1, help="Scrape every N pages")
    ap.add_argument("--output", default="/home/killahbot/.openclaw/workspace/radio-codes/data/mhh_radiocodes.csv")
    ap.add_argument("--checkpoint", default="/home/killahbot/.openclaw/workspace/radio-codes/data/mhh_checkpoint.json")
    args = ap.parse_args()

    output_path = Path(args.output)
    checkpoint_path = Path(args.checkpoint)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Scraping pages {args.start}-{args.end}, step={args.step}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Checkpoint: {checkpoint_path}")

    total = scrape_thread(
        range(args.start, args.end + 1, args.step),
        output_path,
        checkpoint_path,
        every_n_pages=5,
    )
    print(f"\n✅ Done! {total} unique pairs saved to {output_path}")


if __name__ == "__main__":
    main()
