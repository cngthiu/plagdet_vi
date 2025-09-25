# ============================================
# File: src/plagdet_vi/report/html.py
# ============================================
from __future__ import annotations
import os, json
from typing import List
from jinja2 import Template
from ..scoring.aggregate import ScoreReport, MatchSpan

_FALLBACK_TMPL = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"/>
<title>PlagDet-Vi Report</title>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; }
.highlight { background: rgba(255, 215, 0, 0.35); border-radius: 6px; }
.small { color: #666; font-size: 12px; }
.badge { display:inline-block; padding: 4px 8px; border-radius: 999px; background: #222; color: #fff; font-size: 12px; }
pre { white-space: pre-wrap; }
</style></head>
<body>
<h2>PlagDet-Vi — Report</h2>
<p><span class="badge">{{ verdict }}</span> &nbsp; Score: <b>{{ score|round(1) }}</b> / 100 &nbsp; Coverage: {{ (coverage*100)|round(1) }}% &nbsp; Mean Cos: {{ mean_cos|round(3) }}</p>
<div class="grid">
  <div class="card"><h3>Tài liệu A</h3>
    {% for i, p in enumerate(paras_a) %}<h4>Đoạn {{ i }}</h4><pre>{{ p }}</pre>{% endfor %}
  </div>
  <div class="card"><h3>Tài liệu B</h3>
    {% for i, p in enumerate(paras_b) %}<h4>Đoạn {{ i }}</h4><pre>{{ p }}</pre>{% endfor %}
  </div>
</div>
<hr/><h3>Khớp đoạn</h3><ol>
{% for m in matches %}
<li><b>A[{{ m.a_idx }}] ↔ B[{{ m.b_idx }}]</b> &nbsp; cos={{ m.cos|round(3) }}, jacc5={{ m.jac5|round(3) }}, simhash={{ m.simhash_hamm }}, sw={{ m.sw_score }}, rerank={{ m.rerank|round(3) }}
<div class="grid">
  <div class="card"><div class="small">A[{{ m.a_idx }}] span {{ m.a_span }}</div><pre>
{% set a_toks = paras_a[m.a_idx].split() %}
{% for t in range(a_toks|length) %}{% if t >= m.a_span[0] and t < m.a_span[1] %}<span class="highlight">{{ a_toks[t] }}</span>{% else %}{{ a_toks[t] }}{% endif %} {% endfor %}
  </pre></div>
  <div class="card"><div class="small">B[{{ m.b_idx }}] span {{ m.b_span }}</div><pre>
{% set b_toks = paras_b[m.b_idx].split() %}
{% for t in range(b_toks|length) %}{% if t >= m.b_span[0] and t < m.b_span[1] %}<span class="highlight">{{ b_toks[t] }}</span>{% else %}{{ b_toks[t] }}{% endif %} {% endfor %}
  </pre></div>
</div></li>
{% endfor %}
</ol></body></html>
"""

def save_report(out_dir: str, report: ScoreReport, paras_a: List[str], paras_b: List[str]) -> str:
    os.makedirs(out_dir, exist_ok=True)
    tmpl_path = os.path.join(os.path.dirname(__file__), "templates", "report.html.j2")
    if os.path.exists(tmpl_path):
        with open(tmpl_path, "r", encoding="utf-8") as f:
            tmpl = Template(f.read())
    else:
        tmpl = Template(_FALLBACK_TMPL)
    html = tmpl.render(
        verdict=report.verdict,
        score=report.score_0_100,
        coverage=report.coverage_ratio,
        mean_cos=report.mean_cos,
        matches=[m.__dict__ for m in report.matches],
        paras_a=paras_a,
        paras_b=paras_b,
        enumerate=enumerate
    )
    html_path = os.path.join(out_dir, "report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    json_path = os.path.join(out_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(report, default=lambda o: o.__dict__, ensure_ascii=False, indent=2))
    return html_path