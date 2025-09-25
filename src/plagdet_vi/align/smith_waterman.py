# ============================================
# File: src/plagdet_vi/align/smith_waterman.py
# ============================================
from __future__ import annotations
from typing import List, Tuple

def smith_waterman(tokens_a: List[str], tokens_b: List[str], match: int = 2, mismatch: int = -1, gap: int = -1) -> Tuple[int, Tuple[int,int,int,int]]:
    """
    SW trên token để xác định span tốt nhất.
    Why: highlight chính xác vùng trùng.
    """
    m, n = len(tokens_a), len(tokens_b)
    if m == 0 or n == 0:
        return 0, (0,0,0,0)
    H = [[0]*(n+1) for _ in range(m+1)]
    max_score, max_pos = 0, (0,0)
    for i in range(1, m+1):
        ai = tokens_a[i-1]
        for j in range(1, n+1):
            bj = tokens_b[j-1]
            s = match if ai == bj else mismatch
            H[i][j] = max(0, H[i-1][j-1]+s, H[i-1][j]+gap, H[i][j-1]+gap)
            if H[i][j] > max_score:
                max_score, max_pos = H[i][j], (i, j)
    i, j = max_pos
    ai1, bj1 = i, j
    while i > 0 and j > 0 and H[i][j] > 0:
        if H[i][j] == H[i-1][j-1] + (match if tokens_a[i-1]==tokens_b[j-1] else mismatch):
            i -= 1; j -= 1
        elif H[i][j] == H[i-1][j] + gap:
            i -= 1
        else:
            j -= 1
    ai0, bj0 = i, j
    return max_score, (ai0, ai1, bj0, bj1)