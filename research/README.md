# Car Radio Code Algorithms - Research Summary

This directory contains research on car radio unlock code algorithms for various vehicle brands.

## Files

| File | Brand | Algorithm Status |
|------|-------|-----------------|
| `ford_m_series.md` | Ford M Series | ✅ FULLY REVERSED |
| `ford_v_series.md` | Ford V Series | ⚠️ DATABASE REQUIRED |
| `renault_dacia.md` | Renault/Dacia | ✅ FULLY REVERSED |
| `vw_rcd.md` | Volkswagen RCD | ❌ NOT REVERSED |
| `opel_vauxhall.md` | Opel/Vauxhall | ❌ NOT REVERSED |
| `peugeot_citroen.md` | Peugeot/Citroen | ❌ NOT FULLY REVERSED |
| `fiat.md` | Fiat | ⚠️ PARTIAL (VP1/VP2 only) |
| `nissan.md` | Nissan | ❌ NOT REVERSED |
| `honda.md` | Honda | ❌ NOT REVERSED |
| `toyota_erc.md` | Toyota ERC | ❌ NOT REVERSED |
| `open_source_projects.md` | All | 📋 PROJECT LIST |

## Quick Reference - Working Algorithms

### Ford M Series
```python
# Input: Serial like "M123456"
# Output: 4-digit code
# Source: github.com/OlegSmelov/ford-radio-codes
```

### Renault/Dacia
```python
# Input: Precode like "A123"
# Output: 4-digit code
# Source: github.com/m-a-x-s-e-e-l-i-g/renault-radio-code-generator
```

## Key Findings

1. **Only Ford M and Renault/Dacia have fully reversed algorithms**
2. **Ford V requires a pre-computed database (2 million entries)**
3. **Most brands use proprietary algorithms NOT publicly reversed**
4. **PELock commercial SDK covers many brands (paid)**
5. **EEPROM reading is often the only offline option**

## Recommended Approach for Bot

### Tier 1: Fully Working
- Ford M Series → Direct implementation
- Renault/Dacia → Direct implementation

### Tier 2: Database Lookup
- Ford V Series → Include radiocodes.bin or online API
- VW → Use forum database or online API

### Tier 3: External Services
- All other brands → Redirect to official services or paid APIs

## Sources Checked
- GitHub (repositories, gists)
- Car audio forums
- MHH AUTO forum
- teej.ca (mentioned but not accessible)
- radiocodesaver forums
- Various automotive forums

## Last Updated
2026-03-20
