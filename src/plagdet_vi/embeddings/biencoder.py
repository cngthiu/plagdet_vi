# ============================================
# File: src/plagdet_vi/embeddings/biencoder.py
# ============================================
from __future__ import annotations
import os
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL = None

def _device_from_env(device: str) -> str:
    if device in ("cpu", "cuda"): 
        return device
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

def load_biencoder(model_name: str, device: str = "auto") -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(model_name, device=_device_from_env(device))
    return _MODEL

def embed_texts(texts: List[str], model_name: str, device: str = "auto", batch_size: int = 64) -> np.ndarray:
    m = load_biencoder(model_name, device=device)
    return m.encode(texts, batch_size=batch_size, convert_to_numpy=True, normalize_embeddings=True)