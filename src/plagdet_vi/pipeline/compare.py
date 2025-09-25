# ============================================
# File: src/plagdet_vi/pipeline/compare.py
# ============================================
from __future__ import annotations
from typing import List, Tuple
import numpy as np

from ..config.settings import Settings
from ..io.extract_pdf import read_pdf_text
from ..io.extract_docx import read_docx_text
from ..preprocess.segment import build_blocks, window_paragraphs
from ..preprocess.normalize import lower_nodiac
from ..fingerprint.shingles import shingles_hashes, jaccard
from ..fingerprint.simhash import simhash_128, hamming128
from ..embeddings.biencoder import embed_texts
from ..embeddings.reranker import load_reranker, rerank_pairs
from ..align.smith_waterman import smith_waterman
from ..scoring.aggregate import MatchSpan, ScoreReport, aggregate
from ..report.html import save_report

def _read_any(path: str, use_ocr: bool) -> str:
    p = path.lower()
    if p.endswith(".pdf"): return read_pdf_text(path, ocr=use_ocr)
    if p.endswith(".docx"): return read_docx_text(path)
    raise ValueError(f"Unsupported file type: {path}")

def _prepare_windows(text: str, cfg: Settings) -> tuple[list[str], list[str]]:
    blocks = build_blocks(text, strip_refs=cfg.strip_refs)
    wins = window_paragraphs(blocks["paras"], cfg.win_min_tokens, cfg.win_max_tokens, cfg.win_overlap_pct)
    return wins, [lower_nodiac(w) for w in wins]

def compare_paths(path_a: str, path_b: str, out_dir: str, cfg: Settings) -> dict:
    text_a = _read_any(path_a, cfg.use_ocr)
    text_b = _read_any(path_b, cfg.use_ocr)

    paras_a, paras_a_nd = _prepare_windows(text_a, cfg)
    paras_b, paras_b_nd = _prepare_windows(text_b, cfg)
    if not paras_a or not paras_b:
        return {"verdict":"Benign","score":0.0,"coverage":0.0,"mean_cos":0.0,"report_path":save_report(out_dir, ScoreReport(), [], [])}

    # Fingerprints
    j5_a = [shingles_hashes(x, n=5) for x in paras_a_nd]
    j5_b = [shingles_hashes(x, n=5) for x in paras_b_nd]
    j7_a = [shingles_hashes(x, n=7) for x in paras_a_nd]
    j7_b = [shingles_hashes(x, n=7) for x in paras_b_nd]
    s_a = [simhash_128(p.split()) for p in paras_a_nd]
    s_b = [simhash_128(p.split()) for p in paras_b_nd]

    # Embeddings
    E_a = embed_texts(paras_a, cfg.embed_model, device=cfg.device)
    E_b = embed_texts(paras_b, cfg.embed_model, device=cfg.device)
    sim = np.clip(E_a @ E_b.T, -1.0, 1.0)

    # Candidate mining
    pairs: List[Tuple[int,int,float]] = []
    for i in range(sim.shape[0]):
        row = sim[i]
        idx = np.argwhere(row >= cfg.cosine_candidate).reshape(-1)
        for j in idx: pairs.append((i, int(j), float(row[int(j)])))

    # Rerank
    rr_model = load_reranker(cfg.reranker_model, cfg.device) if cfg.use_reranker else None
    if rr_model is not None and pairs:
        rr_scores = rerank_pairs(rr_model, [(paras_a[i], paras_b[j]) for (i,j,_) in pairs])
        pairs_rr = [(i,j,cos,rr) for (rr,(i,j,cos)) in zip(rr_scores, pairs) if rr >= cfg.rerank_min]
        pairs_rr.sort(key=lambda x: (x[3], x[2]), reverse=True)
        pairs = pairs_rr
    else:
        pairs.sort(key=lambda x: -x[2])
        pairs = [(i,j,cos,0.0) for (i,j,cos) in pairs]

    # Refine + alignment
    spans: List[MatchSpan] = []
    for (i, j, cos, rr) in pairs:
        jac5 = jaccard(j5_a[i], j5_b[j]); jac7 = jaccard(j7_a[i], j7_b[j])
        hamm = hamming128(s_a[i], s_b[j])
        if (cos < cfg.cosine_strict and jac5 < 0.2 and hamm > cfg.simhash_hamming_loose and rr < max(cfg.rerank_min, 0.6)):
            continue
        a_toks = paras_a[i].split(); b_toks = paras_b[j].split()
        sw, (ai0, ai1, bj0, bj1) = smith_waterman(a_toks, b_toks)
        if ai1 - ai0 < cfg.min_span_tokens or bj1 - bj0 < cfg.min_span_tokens:
            continue
        spans.append(MatchSpan(
            a_idx=i, b_idx=j, a_span=(ai0, ai1), b_span=(bj0, bj1),
            cos=cos, jac5=jac5, jac7=jac7, simhash_hamm=hamm, sw_score=sw, rerank=rr
        ))

    rep: ScoreReport = aggregate(paras_a, spans)
    # Sinh HTML full-text highlight
    from ..report.highlight import highlight_html
    rep.html_full_a = highlight_html(paras_a, spans, side="a")
    rep.html_full_b = highlight_html(paras_b, spans, side="b")
    path = save_report(out_dir, rep, paras_a, paras_b)
    return {"verdict": rep.verdict, "score": rep.score_0_100, "coverage": rep.coverage_ratio, "mean_cos": rep.mean_cos, "report_path": path}