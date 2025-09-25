# ============================================
# File: src/plagdet_vi/fingerprint/shingles.py
# ============================================
from __future__ import annotations
import hashlib
from typing import Iterable, Set

def char_ngrams(s: str, n: int) -> Iterable[str]:
    s = (s or "").replace("\n", " ")
    if len(s) < n: 
        return []
    return (s[i:i+n] for i in range(len(s)-n+1))

def hash64(x: str) -> int:
    return int(hashlib.blake2b(x.encode("utf-8"), digest_size=8).hexdigest(), 16)

def shingles_hashes(text: str, n: int = 5, limit: int = 20000) -> Set[int]:
    hs: Set[int] = set()
    for i, g in enumerate(char_ngrams(text, n)):
        if i >= limit:
            break
        hs.add(hash64(g))
    return hs

def jaccard(a: Set[int], b: Set[int]) -> float:
    if not a and not b: 
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter/union if union else 0.0