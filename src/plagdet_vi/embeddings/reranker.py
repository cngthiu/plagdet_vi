# ============================================
# File: src/plagdet_vi/embeddings/reranker.py
# ============================================

from __future__ import annotations
from typing import List, Tuple, Optional
try:
    from sentence_transformers import CrossEncoder
except Exception:
    CrossEncoder = None  # type: ignore

_RERANKER = None

def _pick_device(device: str) -> str:
    if device in ("cpu","cuda"): return device
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

def load_reranker(model_name: Optional[str], device: str):
    if not model_name or CrossEncoder is None: return None
    global _RERANKER
    if _RERANKER is None:
        dev = _pick_device(device)
        _RERANKER = CrossEncoder(model_name, device=dev)
    return _RERANKER

def rerank_pairs(reranker, pairs: List[Tuple[str, str]]) -> List[float]:
    if reranker is None or not pairs: return [0.0]*len(pairs)
    return [float(x) for x in reranker.predict(pairs)]