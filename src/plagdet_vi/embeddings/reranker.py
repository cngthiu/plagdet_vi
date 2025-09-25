# ============================================
# File: src/plagdet_vi/embeddings/reranker.py
# ============================================
from __future__ import annotations
from typing import List, Tuple, Optional

# Cross-Encoder; có thể thiếu nếu chưa cài sentence-transformers
try:
    from sentence_transformers import CrossEncoder
except Exception:
    CrossEncoder = None  # type: ignore

_RERANKER = None

def load_reranker(model_name: Optional[str], device: str = "auto"):
    """
    Trả về None nếu không cấu hình hoặc thư viện thiếu.
    Why: đảm bảo pipeline vẫn chạy được.
    """
    global _RERANKER
    if not model_name or CrossEncoder is None:
        return None
    if _RERANKER is None:
        # CE tự chọn device nếu không truyền; tuỳ chọn pass device.
        kwargs = {}
        if device in ("cpu", "cuda"):
            kwargs["device"] = device
        _RERANKER = CrossEncoder(model_name, **kwargs)
    return _RERANKER

def rerank_pairs(reranker, pairs: List[Tuple[str, str]]) -> List[float]:
    if reranker is None or not pairs:
        return [0.0]*len(pairs)
    scores = reranker.predict(pairs)
    return [float(x) for x in scores]