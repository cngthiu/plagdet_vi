# ============================================
# File: src/plagdet_vi/report/highlight.py
# ============================================
from __future__ import annotations
from typing import List, Tuple
from ..scoring.aggregate import MatchSpan

def _spans_by_window(spans: List[MatchSpan], side: str) -> dict[int, List[Tuple[int,int]]]:
    """
    Gom spans theo cửa sổ (a_idx hoặc b_idx).
    Why: tô sáng token-level theo từng window.
    """
    by = {}
    for m in spans:
        idx = m.a_idx if side=="a" else m.b_idx
        s, e = (m.a_span if side=="a" else m.b_span)
        if e <= s: continue
        by.setdefault(idx, []).append((s, e))
    # hợp nhất chồng lấn
    for k, lst in by.items():
        lst.sort()
        merged = []
        for s,e in lst:
            if not merged or s > merged[-1][1]:
                merged.append([s,e])
            else:
                merged[-1][1] = max(merged[-1][1], e)
        by[k] = [(s,e) for s,e in merged]
    return by

def highlight_html(paras: List[str], spans: List[MatchSpan], side: str) -> str:
    """
    Sinh HTML toàn văn đã tô sáng. 
    Why: xem tổng quan vùng bị nghi trong tài liệu A/B.
    """
    by = _spans_by_window(spans, side)
    parts = []
    for i, p in enumerate(paras):
        toks = p.split()
        if i not in by:
            parts.append(f"<p>{p}</p>")
            continue
        cursor = 0; buf = []
        for (s,e) in by[i]:
            s = max(0, min(s, len(toks))); e = max(0, min(e, len(toks)))
            if s > cursor:
                buf.append(" ".join(toks[cursor:s]))
            buf.append(f"<mark>{' '.join(toks[s:e])}</mark>")
            cursor = e
        if cursor < len(toks):
            buf.append(" ".join(toks[cursor:]))
        parts.append(f"<p>{' '.join(buf)}</p>")
    return "\n".join(parts)