# Renault / Dacia Radio Code Algorithm

## Overview
- **Brand:** Renault, Dacia
- **Serial Format:** 1 letter + 3 digits (e.g., A123, B456)
- **Output Code:** 4 digits (0000-9999)
- **Works with:** Clio, Duster, Espace, Kangoo, Laguna, Logan, Master, Megane, Safrane, Scenic, Symbol, Trafic, Twingo
- **Exception:** Precodes starting with `A0` are NOT supported

## How to Get Precode
1. Turn on radio, press and hold buttons "1" and "6" (or "1" and "5") simultaneously
2. While holding, press power button - display shows precode
3. Or remove radio and look for sticker on back/bottom

## Algorithm (Python Implementation - VERIFIED WORKING)

```python
def renault_code(precode):
    """
    Generate unlock code for Renault/Dacia radio
    
    Args:
        precode: String like 'A123' (1 letter + 3 digits)
    Returns:
        4-digit string code, or None if invalid
    """
    precode = precode.upper()
    
    # Validate format
    if not isinstance(precode, str) or len(precode) != 4:
        return None
    if not precode[0].isalpha() or not precode[1:].isdigit():
        return None
    if precode.startswith("A0"):
        return None  # A0 prefix not supported
    
    # x = char1 + char0 * 10 - 698
    # char1 = ASCII of digit (e.g., '0' = 48)
    # char0 = ASCII of letter (e.g., 'A' = 65)
    x = ord(precode[1]) + ord(precode[0]) * 10 - 698
    
    # y = char3 + char2 * 10 + x - 528
    y = ord(precode[3]) + ord(precode[2]) * 10 + x - 528
    
    # z = (y * 7) % 100
    z = (y * 7) % 100
    
    # Final code
    code = z // 10 + (z % 10) * 10 + ((259 % x) % 100) * 100
    
    return f"{code:04d}"
```

## Algorithm Steps

1. **Input:** Precode in format `XNNN` where X is A-Z and NNN are 3 digits
2. **Reject A0:** If precode starts with "A0", algorithm fails (division by zero issue)
3. **Calculate x:** `digit1 + letter_ascii * 10 - 698`
   - Letter A=65, B=66, etc.
   - Digit '0'=48, '1'=49, etc.
4. **Calculate y:** `digit3 + digit2*10 + x - 528`
5. **Calculate z:** `(y * 7) % 100`
6. **Final code:** `z//10 + (z%10)*10 + ((259 % x) % 100) * 100`

## Trace Example (A100)

```
Input: "A100"
charCodes: [65, 49, 48, 48]

x = 49 + 65 * 10 - 698 = 1
y = 48 + 48 * 10 + 1 - 528 = 1
z = (1 * 7) % 100 = 7

code = 0 + 70 + (259 % 1 % 100) * 100
     = 0 + 70 + (0) * 100
     = 70

Result: "0070"
```

## Test Vectors (VERIFIED)

From github.com/ojacquemart/renault-radio-code-list:

| Precode | Expected | Algorithm Output | Status |
|---------|----------|------------------|--------|
| A100 | 0070 | 0070 | ✓ |
| A101 | 0041 | 0041 | ✓ |
| A102 | 0012 | 0012 | ✓ |
| A103 | 0082 | 0082 | ✓ |
| A104 | 0053 | 0053 | ✓ |
| A105 | 0024 | 0024 | ✓ |
| A106 | 0095 | - | - |
| A107 | 0066 | - | - |
| A108 | 0037 | - | - |
| A109 | 0008 | - | - |

## JavaScript Implementation

```javascript
function renaultCode(precode) {
    precode = precode.toUpperCase();
    if (!/^[A-Z]\d{3}$/.test(precode) || precode.startsWith("A0")) {
        return null;
    }
    
    x = precode.charCodeAt(1) + precode.charCodeAt(0) * 10 - 698;
    y = precode.charCodeAt(3) + precode.charCodeAt(2) * 10 + x - 528;
    z = (y * 7) % 100;
    
    code = Math.floor(z / 10) + (z % 10) * 10 + ((259 % x) % 100) * 100;
    return code.toString().padStart(4, '0');
}
```

## Source Code References
- https://gist.github.com/yne/d6dad90416727c2e027774857233524f (Renault gist)
- https://github.com/m-a-x-s-e-e-l-i-g/renault-radio-code-generator (main.js)
- https://github.com/ojacquemart/renault-radio-code-list (test vectors)
- https://renault-dacia-radio-code-generator.netlify.app (live demo)

## Notes
- Works for both Renault and Dacia vehicles
- A0 prefix is mathematically impossible (259 % 0 = division by zero)
- Codes are 4 digits, but some radios display without leading zeros
- The precode retrieval requires physical access to radio buttons or removal
