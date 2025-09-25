# ============================================
# File: src/plagdet_vi/scoring/aggregate.py
# ============================================
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np

@dataclass
class MatchSpan:
    a_idx: int
    b_idx: int
    a_span: Tuple[int, int]
    b_span: Tuple[int, int]
    cos: float
    jac5: float
    jac7: float
    simhash_hamm: int
    sw_score: int
    rerank: float = 0.0

@dataclass
class ScoreReport:
    matches: List[MatchSpan] = field(default_factory=list)
    coverage_ratio: float = 0.0
    mean_cos: float = 0.0
    max_cos: float = 0.0
    mean_jaccard: float = 0.0
    verdict: str = "Benign"
    score_0_100: float = 0.0

def aggregate(paras_a: List[str], spans: List[MatchSpan]) -> ScoreReport:
    if not spans:
        return ScoreReport()
    covered = set()
    tok_offsets = []
    flat_tokens = []
    for p in paras_a:
        tok_offsets.append(len(flat_tokens))
        flat_tokens.extend(p.split())
    for m in spans:
        base = tok_offsets[m.a_idx]
        for t in range(base + m.a_span[0], base + m.a_span[1]):
            covered.add(t)
    coverage = len(covered) / max(1, len(flat_tokens))
    cs = np.array([x.cos for x in spans])
    j5 = np.array([x.jac5 for x in spans])
    rr = np.array([x.rerank for x in spans])
    # Ưu tiên precision: kết hợp cosine + max jaccard + rerank (nếu có)
    raw = 0.45*cs.mean() + 0.45*min(1.0, float(j5.max())) + 0.10*(rr.mean() if rr.size else 0.0)
    score = float(np.clip(100*raw, 0, 100))
    verdict = "Benign"
    if coverage >= 0.15 and (cs.mean() >= 0.86 or j5.max() >= 0.8):
        verdict = "Paraphrase/Strong"
    if coverage >= 0.30 and (j5.max() >= 0.9):
        verdict = "Exact/Copy-Paste"
    return ScoreReport(
        matches=spans,
        coverage_ratio=coverage,
        mean_cos=float(cs.mean()),
        max_cos=float(cs.max()),
        mean_jaccard=float(j5.mean()),
        verdict=verdict,
        score_0_100=score,
    )