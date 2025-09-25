# ================================
# File: src/plagdet_vi/config/settings.py
# ================================
from __future__ import annotations
from typing import Optional
import os, yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Profiles & models
    profile: str = Field(default="default")
    embed_model: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    reranker_model: Optional[str] = Field(default="cross-encoder/ms-marco-MiniLM-L-12-v2")

    # Runtime
    device: str = "auto"         # auto|cpu|cuda
    use_ocr: bool = False
    use_reranker: bool = True
    strip_refs: bool = True

    # Thresholds
    cosine_candidate: float = 0.82
    cosine_strict: float = 0.86
    rerank_min: float = 0.50
    jaccard5_heavy: float = 0.80
    simhash_hamming_loose: int = 16
    min_span_tokens: int = 20

    # Windowing
    win_min_tokens: int = 120
    win_max_tokens: int = 500
    win_overlap_pct: float = 0.25

    # Pydantic v2 config (không dùng class Config)
    model_config = SettingsConfigDict(
        env_prefix="PLAGDET_",
        protected_namespaces=("settings_",)
    )

def _merge_dict(base: dict, upd: dict) -> dict:
    out = {**base}
    for k, v in (upd or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)
        else:
            out[k] = v
    return out

def _apply_profile(cfg: dict) -> dict:
    prof = (cfg.get("profile") or "default").lower()
    presets = {
        "recall": {
            "thresholds": {
                "cosine_candidate": 0.75, "cosine_strict": 0.82, "rerank_min": 0.45,
                "jaccard5_heavy": 0.70, "simhash_hamming_loose": 24, "min_span_tokens": 12,
            },
            "windowing": {"min_tokens": 60, "max_tokens": 300, "overlap_pct": 0.30},
            "runtime": {"strip_refs": False},
        },
        "strict": {
            "thresholds": {
                "cosine_candidate": 0.84, "cosine_strict": 0.88, "rerank_min": 0.70,
                "jaccard5_heavy": 0.85, "simhash_hamming_loose": 12, "min_span_tokens": 24,
            },
            "windowing": {"min_tokens": 140, "max_tokens": 520, "overlap_pct": 0.20},
            "runtime": {"strip_refs": True},
        },
        "default": {}
    }
    return _merge_dict(cfg, presets.get(prof, {}))

def load_settings(config_path: str | None = None) -> Settings:
    """Load YAML → apply profile → build Settings (env có thể override)."""
    y = {}
    path = config_path or os.environ.get("PLAGDET_CONFIG", "configs/default.yaml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            y = yaml.safe_load(f) or {}
    y = _apply_profile(y)
    data = {
        "profile": y.get("profile", "default"),
        "embed_model": y.get("model", {}).get("embed_model"),
        "reranker_model": y.get("model", {}).get("reranker_model"),
        "device": y.get("runtime", {}).get("device", "auto"),
        "use_ocr": y.get("runtime", {}).get("use_ocr", False),
        "use_reranker": y.get("runtime", {}).get("use_reranker", True),
        "strip_refs": y.get("runtime", {}).get("strip_refs", True),
        "cosine_candidate": y.get("thresholds", {}).get("cosine_candidate", 0.82),
        "cosine_strict": y.get("thresholds", {}).get("cosine_strict", 0.86),
        "rerank_min": y.get("thresholds", {}).get("rerank_min", 0.50),
        "jaccard5_heavy": y.get("thresholds", {}).get("jaccard5_heavy", 0.80),
        "simhash_hamming_loose": y.get("thresholds", {}).get("simhash_hamming_loose", 16),
        "min_span_tokens": y.get("thresholds", {}).get("min_span_tokens", 20),
        "win_min_tokens": y.get("windowing", {}).get("min_tokens", 120),
        "win_max_tokens": y.get("windowing", {}).get("max_tokens", 500),
        "win_overlap_pct": y.get("windowing", {}).get("overlap_pct", 0.25),
    }
    return Settings(**{k: v for k, v in data.items() if v is not None})