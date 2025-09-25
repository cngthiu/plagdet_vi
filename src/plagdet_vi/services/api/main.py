# ============================================
# File: src/plagdet_vi/services/api/main.py
# (không đổi, để chạy REST nhanh)
# ============================================
from __future__ import annotations
from fastapi import FastAPI, Query
from pydantic import BaseModel
from ...config.settings import load_settings
from ...pipeline.compare import compare_paths

app = FastAPI(title="PlagDet-Vi API")

class CompareResp(BaseModel):
    verdict: str
    score: float
    coverage: float
    mean_cos: float
    report_path: str

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/compare", response_model=CompareResp)
def compare(a: str = Query(..., description="Path to document A (PDF/DOCX)"),
            b: str = Query(..., description="Path to document B (PDF/DOCX)"),
            out: str = Query("reports", description="Output directory")):
    cfg = load_settings()
    rep = compare_paths(a, b, out, cfg)
    return CompareResp(
        verdict=rep["verdict"],
        score=rep["score"],
        coverage=rep["coverage"],
        mean_cos=rep["mean_cos"],
        report_path=rep["report_path"],
    )