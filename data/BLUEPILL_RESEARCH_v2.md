# BluePill Research Findings — Session 2

**Date:** 2026-03-20
**Researcher:** Tam (sub-agent)
**Goal:** Continue searching for Blaupunkt + Opel/Vauxhall pairs

---

## 🔍 What Was Attempted

### 1. Tavily API Searches
- **Result:** FAILED - "This request exceeds your plan's set usage limit"
- All 4 parallel searches returned quota exceeded error

### 2. Web Search (Brave/Ollama)
- **Result:** FAILED - Brave API key missing, Ollama needs authentication

### 3. Web Fetch (Direct URL Access)
| URL | Result |
|-----|--------|
| carstereocode.com (Opel IDs) | ✅ Accessible but PAYWALLED (only serial prefixes shown, no codes) |
| radiocode.net | ✅ Accessible but requires serial input + payment |
| radiocode.net Opel page | ✅ Page loads but no free codes visible |
| ecoustics.com | ❌ 404 (search pages removed) |
| nairaland.com | ❌ Cloudflare blocked |
| unlockforum.com | ❌ Cloudflare blocked |

### 4. Browser Automation (DrissionPage)
| Target | Result |
|--------|--------|
| ecoustics.com | ✅ Loads, but forum content redirect to MHH AUTO |
| MHH AUTO thread | ✅ Accessible, but Cloudflare/bot detection limits scraping |
| radiocode.net | ✅ Loads, but site requires JavaScript + payment |
| carstereocode.com | ⚠️ Disconnects frequently |

### 5. Ford Radiocodes.bin
- **Result:** ❌ The file is actually GitHub HTML, NOT a binary database
- Was likely a failed download of a GitHub page

---

## 📊 New Data Found

### New Pairs Found This Session
| Serial | Code | Brand | Source | Notes |
|--------|------|-------|--------|-------|
| 89FJJWB182595085 | 6752 | volvo | digital-kaos.co.uk | Delphi Electronics truck radio |

### Total: 1 new pair

---

## 🔒 Access Status Summary

### Sources That WORK
1. **carstereocode.com** - Has serial prefixes for Opel/Vauxhall/Blaupunkt models (~26k entries in local CSV), but **PAYWALLED** - no free codes
2. **digital-kaos.co.uk** - Has some free codes (found 1 this session)
3. **GitHub RadioUnlock repo** - Readme shows project status and verified pairs

### Sources That DON'T WORK
1. **Tavily API** - Quota exhausted
2. **Brave/Ollama web search** - No API keys configured
3. **MHH AUTO** - Bot detection, Cloudflare
4. **unlockforum.com** - Cloudflare
5. **nairaland.com** - Cloudflare
6. **ecoustics.com** - Pages removed/404
7. **radiocode.net** - Payment required

---

## 🎯 Key Findings

### 1. Blaupunkt BP Serials (from carstereocode_all_serials.csv)
The local CSV has **1,733 Blaupunkt entries** and **162 Opel/Vauxhall entries** with serial prefixes like:
- `BP3301`, `BP9376`, `BP6301` - Blaupunkt model codes
- `GM0203`, `GM0300`, `GM0202` - Opel/Vauxhall serial prefixes

**BUT:** No actual unlock codes - these are paywalled.

### 2. Conflicting Codes in Existing Data
| Serial | Code 1 | Code 2 | Sources |
|--------|--------|--------|---------|
| BP8146Y5935543 | 2040 | 3116 | ecoustics (different threads) |
| BP723346696293 | 1232 | 117844 | radiocodes.co (alfa/fiat vs nissan) |
| BP2774S7838642 | 7139 | 2774 | forum_pairs vs ecoustics |

**⚠️ WARNING:** Multiple codes for same serial suggests either:
- Different radio models sharing same serial format
- User errors in forum posts
- Different unlock methods

### 3. Ford Bin File Corruption
The `ford_radiocodes.bin` file contains GitHub HTML, not binary data. Should be re-downloaded or removed.

---

## 📈 Current Dataset Status

### forum_pairs.csv
- **539 total pairs** across 40+ brands
- **23 Opel pairs** (GM0xxx serial format)
- **7 Vauxhall pairs** (same format)
- **13 Blaupunkt pairs** (BP serials)

### carstereocode_all_serials.csv
- **5,018 entries** with serial prefixes
- **1,733 Blaupunkt entries**
- **162 Opel/Vauxhall entries**
- **0 actual codes** (all paywalled)

### bluepill_crawl.csv (this session)
- **1 new pair** added: `89FJJWB182595085 -> 6752`

---

## 🔮 Recommendations for Future Research

### High Priority
1. **Use DrissionPage for MHH AUTO** - Need to handle Cloudflare challenges properly
2. **Try other forum mirrors** - Maybe cached versions or archives
3. **Check Reddit API** - r/carAV, r/carsterios might have free pairs
4. **Direct email to unlockforum** - Some users share codes via email

### Medium Priority
1. **Parse carstereocode serials more carefully** - Maybe codes are hidden in JavaScript
2. **Try archive.org** - Historical forum snapshots might have free codes
3. **Check YouTube comments** - People sometimes post codes in video descriptions

### Low Priority
1. **Find alternative paid API** - Not really "free" research
2. **EEPROM dump analysis** - Would need physical radio access

---

## 📊 Session Summary

| Metric | Value |
|--------|-------|
| New pairs found | 1 |
| Sources accessed | 12 |
| Sources with free data | 1 |
| Tavily searches | 4 (all failed - quota) |
| Pages scraped | ~20 |
| Time spent | ~45 minutes |

**Bottom line:** Most radio code sources are paywalled. Free data is extremely scarce. The best approach is continuing to scrape accessible forums, but most are blocked by Cloudflare/bot protection.
