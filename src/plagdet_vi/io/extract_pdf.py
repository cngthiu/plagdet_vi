# ============================================
# File: src/plagdet_vi/io/extract_pdf.py
# ============================================
from __future__ import annotations
import fitz
from typing import List
from ..preprocess.normalize import normalize_text

def read_pdf_text(path: str, ocr: bool = False) -> str:
    """
    Ưu tiên text layer; fallback OCR theo trang khi cần.
    Why: nhiều luận văn PDF scan.
    """
    doc = fitz.open(path)
    pages: List[str] = []
    for i, p in enumerate(doc):
        t = p.get_text("text")
        if not t and ocr:
            try:
                import pytesseract
                from pdf2image import convert_from_path
                imgs = convert_from_path(path, first_page=i+1, last_page=i+1, fmt="png")
                if imgs:
                    t = pytesseract.image_to_string(imgs[0], lang="vie+eng")
            except Exception:
                t = ""
        pages.append(t or "")
    return normalize_text("\n".join(pages))