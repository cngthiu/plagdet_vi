# ============================================
# File: src/plagdet_vi/config/settings.py
# ============================================
from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os, yaml

class Settings(BaseSettings):
    embed_model: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    reranker_model: Optional[str] = Field(default=None)
    use_ocr: bool = False
    use_reranker: bool = False
    device: str = "auto"  # auto|cpu|cuda

    cosine_candidate: float = 0.82
    cosine_strict: float = 0.86
    jaccard5_heavy: float = 0.80
    simhash_hamming_loose: int = 16
    min_span_tokens: int = 20
    rerank_min: float = 0.50

    win_min_tokens: int = 120
    win_max_tokens: int = 500

    class Config:
        env_prefix = "PLAGDET_"

def load_settings(config_path: str | None = None) -> Settings:
    data = {}
    path = config_path or os.environ.get("PLAGDET_CONFIG", "configs/default.yaml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            y = yaml.safe_load(f) or {}
        data.update({
            "embed_model": y.get("model", {}).get("biencoder"),
            "reranker_model": y.get("model", {}).get("reranker"),
            # "model_biencoder": y.get("model", {}).get("biencoder"),
            # "model_reranker": y.get("model", {}).get("reranker"),
            "use_ocr": y.get("runtime", {}).get("use_ocr", False),
            "use_reranker": y.get("runtime", {}).get("use_reranker", False),
            "device": y.get("runtime", {}).get("device", "auto"),
            "cosine_candidate": y.get("thresholds", {}).get("cosine_candidate", 0.82),
            "cosine_strict": y.get("thresholds", {}).get("cosine_strict", 0.86),
            "jaccard5_heavy": y.get("thresholds", {}).get("jaccard5_heavy", 0.80),
            "simhash_hamming_loose": y.get("thresholds", {}).get("simhash_hamming_loose", 16),
            "min_span_tokens": y.get("thresholds", {}).get("min_span_tokens", 20),
            "rerank_min": y.get("thresholds", {}).get("rerank_min", 0.50),
            "win_min_tokens": y.get("windowing", {}).get("min_tokens", 120),
            "win_max_tokens": y.get("windowing", {}).get("max_tokens", 500),
        })
    return Settings(**{k:v for k,v in data.items() if v is not None})