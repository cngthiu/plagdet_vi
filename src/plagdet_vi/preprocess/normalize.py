# ============================================
# File: src/plagdet_vi/preprocess/normalize.py
# ============================================
from __future__ import annotations
import re, unicodedata
from unidecode import unidecode

_STOP_SECTIONS = [
    r"^tài liệu tham khảo\b",
    r"^tham khảo\b",
    r"^references\b",
    r"^bibliography\b",
    r"^phụ lục\b",
    r"^phu luc\b",
]
_BOILERPLATE = [
    r"^lời cảm ơn$",
    r"^lời cam đoan$",
    r"^mục lục$",
    r"^danh mục hình\b",
    r"^danh mục bảng\b",
    r"^abstract$",
    r"^tóm tắt$",
]

_WS = re.compile(r"\s+")
_SENT_END = re.compile(r"([\.!?…]+)(\s+|$)")

def normalize_text(s: str) -> str:
    s = s or ""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00ad", "")
    s = _WS.sub(" ", s)
    return s.strip()

def lower_nodiac(s: str) -> str:
    return unidecode((s or "").lower())

def strip_tail_sections(text: str) -> tuple[str, str]:
    """
    Cắt phần 'Tài liệu tham khảo/Phụ lục' khỏi scoring.
    Why: giảm false positive.
    """
    lines = [l.strip() for l in text.splitlines()]
    tail_idx = None
    rx = [re.compile(p, re.I) for p in _STOP_SECTIONS]
    for i, l in enumerate(lines):
        if any(r.search(lower_nodiac(l)) for r in rx):
            tail_idx = i
            break
    if tail_idx is None:
        return text, ""
    kept = "\n".join(lines[:tail_idx]).strip()
    removed = "\n".join(lines[tail_idx:]).strip()
    return kept, removed

def split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n{2,}|\r\n{2,}", text)
    parts = [normalize_text(p) for p in parts]
    return [p for p in parts if p]

def split_sentences(text: str) -> list[str]:
    s = text.strip()
    out, pos = [], 0
    for m in _SENT_END.finditer(s):
        end = m.end()
        out.append(s[pos:end].strip())
        pos = end
    if pos < len(s):
        out.append(s[pos:].strip())
    return [x for x in out if x]