# Cleaning summary

- Input rows: 295
- Output rows: 204
- Removed exact duplicates: 45
- Removed same-email duplicates: 27
- Removed near-duplicates (name+company fuzzy >= 92, or same initial + same phone): 19
- Flagged (kept): email issues 5 ({'email looks fake': 1, 'email disposable': 2, 'email invalid': 2}), missing company/location 4

## Near-duplicate examples (kept ← removed, score)

- Liam Anderson  ←  Mia Anderson  @ Soylent Corp  (94.11764705882354)
- Ethan Anderson  ←  Yui Anderson  @ Vandelay Industries  (93.33333333333333)
- Liam Anderson  ←  Yui Anderson  @ Vandelay Industries  (93.33333333333333)
- Ava Anderson  ←  Sophia Anderson  @ Wonka Industries  (92.5925925925926)
- Mia Davis  ←  Sophia Davis  @ Vandelay Industries  (92.5925925925926)
- Mia Davis  ←  Liam Davis  @ Vandelay Industries  (94.91525423728814)
- Mia Garcia  ←  Mason Garcia  @ Stark Industries  (92.85714285714286)
- Sophia Garcia  ←  Mia Garcia  @ Wayne Enterprises  (92.3076923076923)
- Mia Garcia  ←  Hana Garcia  @ Wayne Enterprises  (92.3076923076923)
- Mia Garcia  ←  Emma Garcia  @ Wayne Enterprises  (92.3076923076923)
- Mia Garcia  ←  Haruto Garcia  @ Wayne Enterprises  (92.3076923076923)
- Ren Johnson  ←  Sophia Johnson  @ Stark Industries  (92.3076923076923)
