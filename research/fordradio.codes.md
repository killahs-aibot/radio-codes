# FordRadio.codes Research Report

## Source
- **URL:** https://www.fordradio.codes/
- **Scraped:** 2026-03-20
- **robots.txt:** Barely anything — only `Disallow:` (empty) + Sitemap. No real scraping restrictions.

---

## Supported Models & Serial Formats

The site supports **8 radio product types**, each with a regex pattern and example:

| ID | Name | Serial Pattern | Example |
|----|------|---------------|---------|
| 2 | Ford V-Series | `^V[0-9]{6}$` | `V123456` |
| 3 | Ford M-Series | `^M[0-9]{6}$` | `M123456` |
| 4 | Blaupunkt Radio | `^BP[0-9]{4}[0-9A-Z][0-9]{7}$` | `BP1234A1234567` |
| 5 | Ford Figo Radio | `^VC(O|0)A[A-Z]{2}[0-9]{8}$` | `VCOAAB12345678` |
| 6 | Ford EcoSport Radio | `^[A-Z]{3}[0-9]{6}$` | `ABC123456` |
| 7 | Sanyo Radio | `^[0-9]{12}$` | `123456789012` |
| 9 | Ford SONY CD | `(S)(O|0)(CD)\\w{3}(V)[0-9]{6}` | `SOCDABCV123456` |
| 10 | TravelPilot | `^[0-9A-F]{1,4}[FA][0-9]{4}[A-Z0-9][0-9]{7}$` | `1234F1234A1234567` |

**Note on Ford 6000 CD / 4500 RDS EON:** These are **not separate product entries** — they appear to use the same serial format as V-Series or M-Series. The site says "6000 CD, 4500 RDS EON, or Sony models" all display serial on screen, meaning their serials follow V/M patterns.

**Vehicle-specific pages found in sitemap:**
- Ford Focus radio code
- Ford Fiesta radio code
- Ford Transit radio code
- (Plus all of the above translated into 10+ languages: ES, FR, DE, RO, TR, PL, HU, IT, CS, PT, SV, NL)

---

## Algorithm / Code Generation

**Key finding: This is NOT a purely algorithmic generator.** Evidence:

1. The `submitSerial()` JS function POSTs to `/api/create_payment.php` with `{ serial, product_id }` and gets back a `pid` (payment ID), then redirects to `/result?id={pid}`. This means the backend **looks up** the code in a database or calculates it server-side — no pure client-side algorithm.

2. The JavaScript only handles:
   - **Serial format detection** (regex matching against the 8 PRODUCTS)
   - **Partial match scoring** (fuzzy prefix matching for UX feedback)
   - UI state management (valid/partial/invalid badge)

3. **No code calculation logic exists in client-side JS.** The actual code generation is on the server.

4. The API endpoint `/api/create_payment.php` returns `{"error": "Invalid serial"}` when called without a valid serial — it's a real backend, not a static page.

**Partial match algorithm:**
- Scores character-by-character from the start against the example serial
- Adds +2 bonus if the input matches a "start pattern" (prefix regex) for that product
- Max score capped at 95 (not 100) for partial matches

---

## Serial/Code Pairs Database

**None found in HTML or JS.** The code generation is server-side only. No pre-computed serial→code pairs are exposed in the client.

The `/result?id=XXX` page (where the actual code is shown) was not analyzed — it likely requires a valid payment/redirect flow.

---

## API Assessment

| Endpoint | Method | Purpose | Usable? |
|----------|--------|---------|---------|
| `/api/create_payment.php` | POST | Creates payment session, returns redirect to result | ❌ Requires real serial matching backend DB |
| `/result?id=` | GET | Shows the actual radio code | ❌ Needs valid `pid` from create_payment |

**No public/free API.** The code is only revealed after the payment flow. Despite marketing "free and instant," the JS shows the flow goes through a payment PHP endpoint before showing results.

---

## Key Technical Findings

### Serial Detection Logic (client-side)
Located in inline `<script>` blocks on each page:
- `detectProduct(serial)` — regex matches serial against 8 product patterns
- `calculatePartialMatch(input, product)` — fuzzy prefix scoring
- `updateUI(result)` — shows/hides detection badge
- `submitSerial()` — POSTs to `/api/create_payment.php` then redirects

### Supported Serials Summary
- **V-Series:** `V` + 6 digits (e.g. `V019200`)
- **M-Series:** `M` + 6 digits
- **Blaupunkt:** `BP` + 4 digits + 1 alphanumeric + 7 digits
- **Figo:** `VCO`/`VC0` + `A` + 2 letters + 8 digits
- **EcoSport:** 3 letters + 6 digits
- **Sanyo:** 12 digits
- **SONY CD:** `SOCD`/`SO0CD`/`SCD` + 3 chars + `V` + 6 digits
- **TravelPilot:** hex-like pattern with `F` or `A` at position 4-5

### Where to Find Serial
- **SONY / 6000 CD:** Hold buttons 1+6 to display on screen
- **4500 RDS EON:** Displayed on screen
- **Other models:** Remove radio, sticker on side with serial starting with `V` or `M`

### Code Entry Method
- Use preset buttons 1-4 to enter each digit (press number times = digit value)
- Button 5 (or `*` for SONY CD) to confirm

---

## Recommendations for Our Radio Code Database

1. **Add V-Series (`^V[0-9]{6}$`) and M-Series (`^M[0-9]{6}$`)** — these are the most common Ford formats
2. **Add Ford SONY CD format** — `(S)(O|0)(CD)\w{3}(V)[0-9]{6}`
3. **The Blaupunkt pattern** (`^BP[0-9]{4}[0-9A-Z][0-9]{7}$`) is also Ford-specific and common
4. **No algorithm** can be reverse-engineered from this site — codes appear to come from a server-side database
5. **No API access** — can't query their backend directly
6. **The "free" claim is misleading** — the code flow goes through a payment endpoint; the "free" likely refers to their monetization model (affiliate/lead Gen) rather than truly free access

---

## Files Analyzed
- `https://www.fordradio.codes/` — main page
- `https://www.fordradio.codes/ford-focus-radio-code` — Focus-specific page
- `https://www.fordradio.codes/ford-fiesta-radio-code` — Fiesta-specific page
- `https://www.fordradio.codes/media/js/master.js` — UI JS (menus, modal, language — no code gen)
- `https://www.fordradio.codes/robots.txt` — permissive
- `https://www.fordradio.codes/sitemap.xml` — vehicle-specific pages listed
- `https://www.fordradio.codes/api/create_payment.php` — backend API endpoint
