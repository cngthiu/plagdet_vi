# ================================
# File: src/plagdet_vi/preprocess/segment.py
# ================================
from __future__ import annotations
from math import floor
from .normalize import normalize_text, strip_tail_sections, lower_nodiac, split_paragraphs, split_sentences

def build_blocks(text: str, strip_refs: bool) -> dict:
    # Gọi tham số VỊ TRÍ để tránh lỗi keyword khi phiên bản cũ còn lưu cache
    kept, _ = strip_tail_sections(normalize_text(text), strip_refs)
    paras = split_paragraphs(kept)
    return {
        "text_clean": kept,
        "text_nodiac": lower_nodiac(kept),
        "paras": paras,
        "paras_nodiac": [lower_nodiac(p) for p in paras],
        "sents": split_sentences(kept),
    }

def window_paragraphs(paras: list[str], min_tok: int, max_tok: int, overlap_pct: float) -> list[str]:
    def tok(s: str) -> int: return len(s.split())
    joined, cur, cur_tok = [], [], 0
    for p in paras:
        t = tok(p)
        if t == 0:
            continue
        if cur_tok + t > max_tok and cur_tok >= min_tok:
            joined.append("\n".join(cur)); cur, cur_tok = [], 0
        cur.append(p); cur_tok += t
    if cur:
        joined.append("\n".join(cur))
    if not joined:
        return []
    # Tạo bản chồng lấn
    out = []
    for w in joined:
        out.append(w)
        toks = w.split()
        sb = max(1, floor(len(toks) * overlap_pct))
        if len(toks) > min_tok and sb > 0:
            out.append(" ".join(toks[sb:]))
    return out