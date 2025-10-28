# ============================================
# File: src/plagdet_vi/report/html.py
# ============================================
from __future__ import annotations
import os, json, html
from typing import List, Dict, Any
from jinja2 import Template
from ..scoring.aggregate import ScoreReport, MatchSpan

def _token_snippet(tokens: List[str], start: int, end: int, ctx: int = 30) -> str:
    """
    Cắt snippet quanh [start, end) với ngữ cảnh ±ctx token, kèm highlight.
    Lý do: báo cáo ngắn gọn, giống các hệ thống thương mại.
    """
    n = len(tokens)
    s = max(0, start - ctx)
    e = min(n, end + ctx)
    pre_ellipsis = "…" if s > 0 else ""
    post_ellipsis = "…" if e < n else ""
    parts = []
    if s < start:
        parts.append(" ".join(tokens[s:start]))
    # vùng highlight
    parts.append(f"<mark>{html.escape(' '.join(tokens[start:end]))}</mark>")
    if end < e:
        parts.append(" ".join(tokens[end:e]))
    body = " ".join(parts).strip()
    return f"{pre_ellipsis} {body} {post_ellipsis}".strip()

def _build_match_items(paras_a: List[str], paras_b: List[str], matches: List[MatchSpan], ctx: int = 30) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for k, m in enumerate(matches):
        toks_a = paras_a[m.a_idx].split()
        toks_b = paras_b[m.b_idx].split()
        a_s, a_e = m.a_span
        b_s, b_e = m.b_span
        snip_a = _token_snippet(toks_a, a_s, a_e, ctx=ctx)
        snip_b = _token_snippet(toks_b, b_s, b_e, ctx=ctx)

        # Chi tiết (window đầy đủ) nhưng không phải toàn văn tài liệu
        def _window_html(tokens: List[str], s: int, e: int) -> str:
            out = []
            for i, tok in enumerate(tokens):
                if s <= i < e:
                    out.append(f"<span class='hl'>{html.escape(tok)}</span>")
                else:
                    out.append(html.escape(tok))
            return " ".join(out)

        detail_a = _window_html(toks_a, a_s, a_e)
        detail_b = _window_html(toks_b, b_s, b_e)

        items.append({
            "idx": k,
            "a_idx": m.a_idx,
            "b_idx": m.b_idx,
            "cos": float(m.cos),
            "j5": float(m.jac5),
            "hamm": int(m.simhash_hamm),
            "sw": int(m.sw_score),
            "rr": float(getattr(m, "rerank", 0.0) or 0.0),
            "snippet_a": snip_a,
            "snippet_b": snip_b,
            "detail_a": detail_a,
            "detail_b": detail_b,
            "a_span": m.a_span,
            "b_span": m.b_span,
        })
    return items

_TEMPLATE = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"/>
<title>PlagDet-Vi Report</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
:root{--bg:#fff;--fg:#111;--muted:#666;--card:#fafafa;--b:#e6e6e6;--brand:#0b6bcb;--hl:rgba(255,215,0,.45)}
html,body{background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0}
.container{max-width:1080px;margin:24px auto;padding:0 16px}
.card{background:var(--card);border:1px solid var(--b);border-radius:14px;padding:16px}
h1{font-size:22px;margin:0 0 8px 0}
h2{font-size:18px;margin:0 0 8px 0}
.kpi{display:flex;flex-wrap:wrap;gap:12px;margin:8px 0}
.kpi .box{border:1px solid var(--b);border-radius:10px;padding:10px 12px;background:#fff}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;background:#111;color:#fff;font-size:12px}
.mut{color:var(--muted);font-size:12px}
.list{display:flex;flex-direction:column;gap:12px;margin-top:12px}
.item{border:1px solid var(--b);border-radius:12px;background:#fff;overflow:hidden}
.item-header{display:grid;grid-template-columns:1fr auto;gap:8px;padding:12px;border-bottom:1px solid var(--b)}
.scores{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.score-pill{font-size:12px;border:1px solid var(--b);border-radius:999px;padding:4px 8px;background:#f7f7f7}
.progress{height:6px;border-radius:999px;background:#eee;overflow:hidden;width:140px}
.progress > i{display:block;height:100%;background:var(--brand)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}
.snip{border:1px dashed var(--b);border-radius:10px;padding:10px;min-height:48px;background:#fcfcfc}
mark{background:var(--hl);padding:0 .2em;border-radius:.25em}
.hl{background:var(--hl);padding:0 .15em;border-radius:.2em}
.meta{display:flex;gap:16px;flex-wrap:wrap}
.btn{appearance:none;border:1px solid var(--b);background:#fff;border-radius:10px;padding:6px 10px;cursor:pointer}
.btn:active{transform:translateY(1px)}
.details{display:none;border-top:1px solid var(--b);padding:12px;background:#fff}
.small{font-size:12px;color:var(--muted)}
.footer{margin:24px 0 40px 0;color:var(--muted);font-size:12px;text-align:center}
@media (max-width: 840px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
  <div class="card">
    <h1>PlagDet-Vi — Báo cáo so khớp</h1>
    <div class="kpi">
      <div class="box"><div class="mut">Verdict</div><div class="badge">{{ verdict }}</div></div>
      <div class="box"><div class="mut">Score</div><div><b>{{ score|round(1) }}</b> / 100</div></div>
      <div class="box"><div class="mut">Coverage</div><div>{{ (coverage*100)|round(1) }}%</div></div>
      <div class="box"><div class="mut">Mean Cosine</div><div>{{ mean_cos|round(3) }}</div></div>
      <div class="box"><div class="mut">Số đoạn trùng</div><div>{{ items|length }}</div></div>
    </div>
    <div class="mut">Báo cáo tóm lược; chỉ hiển thị đoạn nghi vấn với ngữ cảnh ngắn gọn, không in toàn bộ văn bản.</div>
  </div>

  <h2 style="margin:16px 0 8px 8px;">Các đoạn nghi vấn</h2>
  <div class="list">
    {% for it in items %}
    <div class="item" id="m{{ it.idx }}">
      <div class="item-header">
        <div class="meta">
          <div><b>A[{{ it.a_idx }}]</b> ↔ <b>B[{{ it.b_idx }}]</b></div>
          <div class="scores">
            <span class="score-pill">cos {{ it.cos|round(3) }}</span>
            <span class="score-pill">j5 {{ it.j5|round(3) }}</span>
            <span class="score-pill">CE {{ it.rr|round(3) }}</span>
            <span class="score-pill">SW {{ it.sw }}</span>
          </div>
        </div>
        <div class="progress" title="CE-weighted rank">
          {% set pct = (it.rr if it.rr>0 else it.cos) * 100 %}
          <i style="width: {{ [pct,100]|min }}%"></i>
        </div>
      </div>
      <div class="grid">
        <div>
          <div class="small mut">Trích A[{{ it.a_idx }}] (ngắn gọn)</div>
          <div class="snip">{{ it.snippet_a | safe }}</div>
        </div>
        <div>
          <div class="small mut">Trích B[{{ it.b_idx }}] (ngắn gọn)</div>
          <div class="snip">{{ it.snippet_b | safe }}</div>
        </div>
      </div>
      <div style="display:flex; gap:8px; padding:0 12px 12px 12px;">
        <button class="btn" onclick="toggleDetails('{{ it.idx }}')">Xem chi tiết</button>
        <a class="btn" href="#m{{ it.idx }}">Liên kết</a>
      </div>
      <div class="details" id="d{{ it.idx }}">
        <div class="grid">
          <div>
            <div class="small mut">A[{{ it.a_idx }}] — span {{ it.a_span }}</div>
            <div class="snip">{{ it.detail_a | safe }}</div>
          </div>
          <div>
            <div class="small mut">B[{{ it.b_idx }}] — span {{ it.b_span }}</div>
            <div class="snip">{{ it.detail_b | safe }}</div>
          </div>
        </div>
      </div>
    </div>
    {% endfor %}
    {% if items|length == 0 %}
    <div class="card">Không phát hiện đoạn trùng đáng kể theo ngưỡng hiện tại.</div>
    {% endif %}
  </div>

  <div class="footer">PlagDet-Vi · Báo cáo rút gọn • Không hiển thị toàn văn để đảm bảo tính gọn nhẹ.</div>
</div>

<script>
function toggleDetails(id){
  const el = document.getElementById('d'+id);
  if(!el) return;
  el.style.display = (el.style.display === 'block') ? 'none' : 'block';
}
</script>
</body></html>
"""

def save_report(out_dir: str, report: ScoreReport, paras_a: List[str], paras_b: List[str], context_tokens: int = 30) -> str:
    """
    Sinh báo cáo rút gọn:
      - Header KPI
      - Danh sách match với preview ngắn (±context_tokens)
      - Chi tiết per-match theo window (không in toàn văn)
    """
    os.makedirs(out_dir, exist_ok=True)
    items = _build_match_items(paras_a, paras_b, report.matches, ctx=context_tokens)
    tmpl = Template(_TEMPLATE)
    html_out = tmpl.render(
        verdict=report.verdict,
        score=report.score_0_100,
        coverage=report.coverage_ratio,
        mean_cos=report.mean_cos,
        items=items
    )
    html_path = os.path.join(out_dir, "report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    # JSON chi tiết (đủ để debug/hoặc tái render)
    json_path = os.path.join(out_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(report, default=lambda o: o.__dict__, ensure_ascii=False, indent=2))
    return html_path
