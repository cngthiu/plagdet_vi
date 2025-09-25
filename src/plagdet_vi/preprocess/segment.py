# ============================================
# File: src/plagdet_vi/preprocess/segment.py
# ============================================
from __future__ import annotations
from .normalize import normalize_text, strip_tail_sections, lower_nodiac, split_paragraphs, split_sentences

def build_blocks(text: str) -> dict:
    """
    Trả về các biến thể văn bản (giữ dấu/không dấu), đoạn, câu.
    Why: phục vụ cả lexical lẫn semantic.
    """
    kept, _ = strip_tail_sections(normalize_text(text))
    paras = split_paragraphs(kept)
    return {
        "text_clean": kept,
        "text_nodiac": lower_nodiac(kept),
        "paras": paras,
        "paras_nodiac": [lower_nodiac(p) for p in paras],
        "sents": split_sentences(kept),
    }

def window_paragraphs(paras: list[str], min_tok: int, max_tok: int) -> list[str]:
    """
    Gộp đoạn thành cửa sổ 200–500 token.
    Why: ổn định matching, giảm nhiễu đoạn nhỏ.
    """
    def tok_count(s: str) -> int: return len(s.split())
    buf, cur, cur_tok = [], [], 0
    for p in paras:
        t = tok_count(p)
        if t == 0: 
            continue
        if cur_tok + t > max_tok and cur_tok >= min_tok:
            buf.append("\n".join(cur))
            cur, cur_tok = [], 0
        cur.append(p)
        cur_tok += t
    if cur:
        buf.append("\n".join(cur))
    return buf