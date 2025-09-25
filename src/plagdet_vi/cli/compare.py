# ============================================
# File: src/plagdet_vi/cli/compare.py
# ============================================
from __future__ import annotations
import argparse, os, json
from ..config.settings import load_settings
from ..pipeline.compare import compare_paths

def main():
    ap = argparse.ArgumentParser(description="PlagDet-Vi: so khớp A vs B (PDF/DOCX) — có reranker CE.")
    ap.add_argument("--a", required=True, help="Đường dẫn tài liệu A (.pdf/.docx)")
    ap.add_argument("--b", required=True, help="Đường dẫn tài liệu B (.pdf/.docx)")
    ap.add_argument("--out", default="reports", help="Thư mục xuất report")
    ap.add_argument("--config", default=None, help="Đường dẫn YAML cấu hình (tùy chọn)")
    args = ap.parse_args()

    cfg = load_settings(args.config)
    os.makedirs(args.out, exist_ok=True)
    result = compare_paths(args.a, args.b, args.out, cfg)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()