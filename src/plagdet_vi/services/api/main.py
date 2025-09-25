# ============================================
# File: src/plagdet_vi/services/api/main.py
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
def compare(a: str = Query(...), b: str = Query(...), out: str = Query("reports"), config: str | None = Query(None)):
    cfg = load_settings(config)
    rep = compare_paths(a, b, out, cfg)
    return CompareResp(**rep)