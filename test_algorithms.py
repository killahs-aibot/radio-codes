#!/usr/bin/env python3
"""Test radio code algorithms"""

# Ford M Series Algorithm
def ford_m_series(serial):
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
    
    n = list(map(int, serial[1:]))[::-1]
    n1, n2, n3, n4, n5, n6 = n[0], n[1], n[2], n[3], n[4], n[5]
    n7 = 0
    
    r1 = lookup[n1][5]
    r2 = lookup[n2][3]
    r3 = lookup[n3][8]
    r4 = lookup[n4][2]
    r5 = lookup[n5][1]
    r6 = lookup[n6][6]
    r7 = lookup[n7][9]
    
    res1 = ((lookup[r2][r1] + 1) * (lookup[r6][r2] + 1) + (lookup[r4][r3] + 1) * (lookup[r7][r5] + 1) + (lookup[r1][r4])) % 10
    res2 = ((lookup[r2][r1] + 1) * (lookup[r5][r4] + 1) + (lookup[r5][r2] + 1) * (lookup[r7][r3] + 1) + (lookup[r1][r6])) % 10
    res3 = ((lookup[r2][r1] + 1) * (lookup[r4][r2] + 1) + (lookup[r3][r6] + 1) * (lookup[r7][r4] + 1) + (lookup[r1][r5])) % 10
    res4 = ((lookup[r2][r1] + 1) * (lookup[r6][r3] + 1) + (lookup[r3][r7] + 1) * (lookup[r2][r5] + 1) + (lookup[r4][r1])) % 10
    
    xres1 = (lookup[res1][5] + 1) * (lookup[res2][1] + 1) + 105
    xres2 = (lookup[res2][1] + 1) * (lookup[res4][0] + 1) + 102
    xres3 = (lookup[res1][5] + 1) * (lookup[res3][8] + 1) + 103
    xres4 = (lookup[res3][8] + 1) * (lookup[res4][0] + 1) + 108
    
    code0 = (xres1 // 10 % 10 + xres1 % 10 + r1) % 10
    code1 = (xres2 // 10 % 10 + xres2 % 10 + r1) % 10
    code2 = (xres3 // 10 % 10 + xres3 % 10 + r1) % 10
    code3 = (xres4 // 10 % 10 + xres4 % 10 + r1) % 10
    
    return f"{code0}{code1}{code2}{code3}"

# Renault Algorithm (FIXED)
def renault_code(precode):
    """
    Generate unlock code for Renault/Dacia radio
    Based on JavaScript implementation from:
    https://gist.github.com/yne/d6dad90416727c2e027774857233524f
    """
    precode = precode.upper()
    if not isinstance(precode, str) or len(precode) != 4:
        return None
    if not precode[0].isalpha() or not precode[1:].isdigit():
        return None
    if precode.startswith("A0"):
        return None  # A0 prefix not supported
    
    # charCodeAt gives ASCII values
    # A=65, B=66, etc.
    char0 = ord(precode[0])  # Letter
    char1 = ord(precode[1])  # First digit
    char2 = ord(precode[2])  # Second digit
    char3 = ord(precode[3])  # Third digit
    
    # This matches the JS: x = char1 + char0 * 10 - 698
    x = char1 + char0 * 10 - 698
    
    # y = char3 + char2 * 10 + x - 528
    y = char3 + char2 * 10 + x - 528
    
    # z = (y * 7) % 100
    z = (y * 7) % 100
    
    # code = Math.floor(z / 10) + (z % 10) * 10 + ((259 % x) % 100) * 100
    code = z // 10 + (z % 10) * 10 + ((259 % x) % 100) * 100
    
    return f"{code:04d}"

# Alternative Renault formula (from main.js gist)
def renault_code_alt(precode):
    """
    Alternative implementation
    """
    precode = precode.upper()
    if not isinstance(precode, str) or len(precode) != 4:
        return None
    if not precode[0].isalpha() or not precode[1:].isdigit():
        return None
    if precode.startswith("A0"):
        return None
    
    # x = char1 + char0*10 - 698
    x = ord(precode[1]) + ord(precode[0]) * 10 - 698
    # y = char3 + char2*10 + x - 528
    y = ord(precode[3]) + ord(precode[2]) * 10 + x - 528
    # z = (y*7) % 100
    z = (y * 7) % 100
    
    # code = floor(z/10) + (z%10)*10 + ((259 % x) % 100) * 100
    code = z // 10 + (z % 10) * 10 + ((259 % x) % 100) * 100
    
    return f"{code:04d}"

# Test Ford M Series
print("=== Ford M Series Tests ===")
test_cases_m = [
    ("M000000", "8551"),
]
for serial, expected in test_cases_m:
    code = ford_m_series(serial)
    print(f"  {serial} -> {code}")

# Test Renault with CORRECTED algorithm
print("\n=== Renault Tests (FIXED) ===")
test_cases_r = [
    ("A100", "0070"),  # From github.com/ojacquemart/renault-radio-code-list
    ("A101", "0041"),
    ("A102", "0012"),
    ("A103", "0082"),
    ("A104", "0053"),
    ("A105", "0024"),
]
for precode, expected in test_cases_r:
    code = renault_code(precode)
    status = "✓" if code == expected else "✗"
    print(f"  {precode} -> {code} (expected {expected}) {status}")

# Trace through A100
print("\n=== A100 Trace ===")
precode = "A100"
print(f"  charCodes: {[ord(c) for c in precode]}")
x = ord(precode[1]) + ord(precode[0]) * 10 - 698
print(f"  x = {ord(precode[1])} + {ord(precode[0])} * 10 - 698 = {x}")
y = ord(precode[3]) + ord(precode[2]) * 10 + x - 528
print(f"  y = {ord(precode[3])} + {ord(precode[2])} * 10 + {x} - 528 = {y}")
z = (y * 7) % 100
print(f"  z = ({y} * 7) % 100 = {z}")
code = z // 10 + (z % 10) * 10 + ((259 % x) % 100) * 100
print(f"  code = {z//10} + {z%10}*10 + (259%{x}%100)*100 = {code}")

