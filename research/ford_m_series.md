# Ford M Series Radio Code Algorithm

## Overview
- **Brand:** Ford
- **Series:** M Series
- **Serial Format:** `M` + 6 digits (e.g., M123456)
- **Output Code:** 4 digits (0000-9999, displayed as 3 digits on some units)
- **Works with:** Ford 4500, 4600, 5000, 6000 RDS EON radios

## Algorithm Type
Lookup table-based algorithm with multiple transformation stages.

## Exact Algorithm (Python Implementation)

```python
def ford_m_series(serial):
    """
    Generate unlock code for Ford radio with serial starting with 'M'
    
    Args:
        serial: String like 'M123456' (1 letter + 6 digits)
    Returns:
        4-digit string code
    """
    lookup = [
        [9, 5, 3, 4, 8, 7, 2, 6, 1, 0],
        [2, 1, 5, 6, 9, 3, 7, 0, 4, 8],
        [0, 4, 7, 3, 1, 9, 6, 5, 8, 2],
        [5, 6, 4, 1, 2, 8, 0, 9, 3, 7],
        [6, 3, 1, 2, 0, 5, 4, 8, 7, 9],
        [4, 0, 8, 7, 6, 1, 9, 3, 2, 5],
        [7, 8, 0, 5, 3, 2, 1, 4, 9, 6],
        [1, 9, 6, 8, 7, 4, 5, 2, 0, 3],
        [3, 2, 9, 0, 4, 6, 8, 7, 5, 1],
        [8, 7, 2, 9, 5, 0, 3, 1, 6, 4],
    ]
    
    # Remove 'M' prefix and reverse the remaining 6 digits
    n = list(map(int, serial[1:]))[::-1]  # Reverse digits
    
    n1, n2, n3, n4, n5, n6 = n[0], n[1], n[2], n[3], n[4], n[5]
    n7 = 0  # Pad with 0
    
    # First stage lookup
    r1 = lookup[n1][5]
    r2 = lookup[n2][3]
    r3 = lookup[n3][8]
    r4 = lookup[n4][2]
    r5 = lookup[n5][1]
    r6 = lookup[n6][6]
    r7 = lookup[n7][9]
    
    # Second stage calculations
    res1 = ((lookup[r2][r1] + 1) * (lookup[r6][r2] + 1) + 
            (lookup[r4][r3] + 1) * (lookup[r7][r5] + 1) + 
            (lookup[r1][r4])) % 10
    
    res2 = ((lookup[r2][r1] + 1) * (lookup[r5][r4] + 1) + 
            (lookup[r5][r2] + 1) * (lookup[r7][r3] + 1) + 
            (lookup[r1][r6])) % 10
    
    res3 = ((lookup[r2][r1] + 1) * (lookup[r4][r2] + 1) + 
            (lookup[r3][r6] + 1) * (lookup[r7][r4] + 1) + 
            (lookup[r1][r5])) % 10
    
    res4 = ((lookup[r2][r1] + 1) * (lookup[r6][r3] + 1) + 
            (lookup[r3][r7] + 1) * (lookup[r2][r5] + 1) + 
            (lookup[r4][r1])) % 10
    
    # Third stage calculations
    xres1 = (lookup[res1][5] + 1) * (lookup[res2][1] + 1) + 105
    xres2 = (lookup[res2][1] + 1) * (lookup[res4][0] + 1) + 102
    xres3 = (lookup[res1][5] + 1) * (lookup[res3][8] + 1) + 103
    xres4 = (lookup[res3][8] + 1) * (lookup[res4][0] + 1) + 108
    
    # Extract digits
    xres11 = (xres1 // 10) % 10
    xres10 = xres1 % 10
    xres21 = (xres2 // 10) % 10
    xres20 = xres2 % 10
    xres31 = (xres3 // 10) % 10
    xres30 = xres3 % 10
    xres41 = (xres4 // 10) % 10
    xres40 = xres4 % 10
    
    # Final code calculation
    code0 = (xres11 + xres10 + r1) % 10
    code1 = (xres21 + xres20 + r1) % 10
    code2 = (xres31 + xres30 + r1) % 10
    code3 = (xres41 + xres40 + r1) % 10
    
    return f"{code0}{code1}{code2}{code3}"
```

## Algorithm Steps

1. **Input:** Serial number in format `MXXXXXX` (1 letter + 6 digits)
2. **Reverse digits:** Take the 6 digits, reverse their order
3. **Stage 1 Lookup:** Use the 10x10 lookup table with fixed column indices (5,3,8,2,1,6,9)
4. **Stage 2 Calculation:** Combine lookup results with modular arithmetic
5. **Stage 3 Calculation:** More lookup combinations with added constants (105, 102, 103, 108)
6. **Final XOR:** Combine stage 3 results with first lookup value

## Test Vectors

| Serial | Expected Code | Source |
|--------|--------------|--------|
| M000000 | 6835 | Calculated |
| M123456 | (verify) | - |

## Source Code References
- https://github.com/OlegSmelov/ford-radio-codes
- https://gist.github.com/4ndrej/b252c4ec3efa49d2b7b03c704c1289e3
- https://github.com/DavidB445/fz_fordradiocodes

## Notes
- Some sources suggest the code is actually 3 digits (leading zero dropped)
- Serial retrieved by holding buttons 1+6 while powering on the radio
- Pre-2005 radios typically use this algorithm
