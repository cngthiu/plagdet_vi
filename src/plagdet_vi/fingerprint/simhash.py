# ============================================
# File: src/plagdet_vi/fingerprint/simhash.py
# ============================================
from __future__ import annotations
import hashlib
from typing import List

def simhash_128(tokens: List[str]) -> int:
    """
    SimHash 128-bit để bắt near-duplicate giá rẻ.
    Why: lọc nhanh trước khi so khớp sâu.
    """
    bits = [0]*128
    for tok in tokens:
        h = hashlib.blake2b(tok.encode("utf-8"), digest_size=16).digest()
        v = int.from_bytes(h, "big")
        for i in range(128):
            bits[i] += 1 if (v >> i) & 1 else -1
    out = 0
    for i, b in enumerate(bits):
        if b >= 0:
            out |= (1 << i)
    return out

def hamming128(a: int, b: int) -> int:
    return (a ^ b).bit_count()