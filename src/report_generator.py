"""Deterministic HTML + PDF report generation with charts and evidence appendix."""

from __future__ import annotations

from datetime import datetime
from html import escape as html_escape, unescape as html_unescape
from pathlib import Path

import plotly.graph_objects as go

from .models import Claim, ClaimStatus, Figure, Metric


def _get(obj, key: str, default=None):
    """Read a field from either a Pydantic model or a plain dict."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _esc(value) -> str:
    """Escape untrusted values before inserting them into HTML text nodes."""
    return html_escape(str(value), quote=True)


def _fmt(value: float, unit: str) -> str:
    if unit == "percent":
        return f"{value:,.2f}%"
    if unit == "ratio":
        return f"{value:,.2f}x"
    return f"{value:,.2f}"


def metrics_bar_html(metrics: list[Metric]) -> str:
    """Return an interactive Plotly bar chart of metric values as HTML."""
    pct = [m for m in metrics if _get(m, "unit") == "percent"]
    if not pct:
        return ""
    fig = go.Figure(
        go.Bar(
            x=[_get(m, "name") for m in pct],
            y=[_get(m, "value") for m in pct],
            marker_color="#ff8c00",
            text=[f"{_get(m, 'value'):.2f}%" for m in pct],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Key financial ratios (%)",
        yaxis_title="Percent",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=90),
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def build_html_report(
    figures: list[Figure],
    metrics: list[Metric],
    claims: list[Claim],
    company: str = "Apple Inc.",
    source: str = "apple_10k_2023.pdf",
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = "".join(
        f"<tr><td>{_esc(_get(m,'name'))}</td><td>{_esc(_fmt(_get(m,'value'), _get(m,'unit')))}</td>"
        f"<td class='mono'>{_esc(_get(m,'formula'))}</td></tr>"
        for m in metrics
    ) or "<tr><td colspan='3'>No metrics available.</td></tr>"

    fig_rows = "".join(
        f"<tr><td>{_esc(f.concept.value)}</td><td>{_esc(f.period)}</td><td>{_esc(format(f.value, ',.2f') + ' ' + f.unit)}</td>"
        f"<td>{_esc(f.evidence.reference())}</td><td class='snip'>{_esc(f.evidence.snippet)}</td></tr>"
        for f in figures
    ) or "<tr><td colspan='5'>No figures extracted.</td></tr>"

    allowed_claims = [c for c in claims if c.status == ClaimStatus.OK]
    blocked = [c for c in claims if c.status == ClaimStatus.BLOCKED]
    claim_html = "".join(f"<li>{_esc(c.text)}</li>" for c in allowed_claims) or "<li>No analysis generated.</li>"
    blocked_html = "".join(f"<li>{_esc(c.text)} <em>({_esc(c.reason)})</em></li>" for c in blocked)

    chart = metrics_bar_html(metrics)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>AI Financial Analyst Report — {_esc(company)}</title>
<style>
 body {{ font-family: -apple-system, 'Segoe UI', sans-serif; margin: 0; color: #1a1a1a; }}
 header {{ background: #111827; color: #fff; padding: 28px 40px; }}
 header h1 {{ margin: 0 0 6px; font-size: 24px; }}
 header .sub {{ color: #ff8c00; font-size: 13px; }}
 main {{ padding: 24px 40px; max-width: 1000px; }}
 h2 {{ font-size: 18px; border-bottom: 2px solid #ff8c00; padding-bottom: 6px; margin-top: 32px; }}
 table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
 th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; vertical-align: top; }}
 th {{ background: #f3f4f6; }}
 .mono {{ font-family: ui-monospace, monospace; color: #555; }}
 .snip {{ color: #666; max-width: 320px; }}
 .blocked {{ background: #fff5f5; }}
 .disclaimer {{ margin-top: 36px; font-size: 12px; color: #777; border-top: 1px solid #ddd; padding-top: 12px; }}
</style></head><body>
<header>
  <h1>AI Financial Analyst — Analysis Report</h1>
  <div class="sub">{_esc(company)} · generated {_esc(now)} · source: {_esc(source)}</div>
</header>
<main>
  <h2>1. Key metrics</h2>
  <table><thead><tr><th>Metric</th><th>Value</th><th>Formula</th></tr></thead>
  <tbody>{rows}</tbody></table>

  <h2>2. Visual summary</h2>
  {chart or '<p>No chart available.</p>'}

  <h2>3. AI interpretation (verified)</h2>
  <ul>{claim_html}</ul>
  {f'<div class="blocked"><h3>Blocked claims (failed numeric guard)</h3><ul>{blocked_html}</ul></div>' if blocked else ''}

  <h2>4. Evidence appendix</h2>
  <table><thead><tr><th>Concept</th><th>Period</th><th>Value</th><th>Source</th><th>Raw text</th></tr></thead>
  <tbody>{fig_rows}</tbody></table>

  <div class="disclaimer">
    Experimental research prototype. Figures extracted from public filings; ratios computed by
    deterministic functions. AI narrative is generated with a mock provider and requires human
    review. Not investment advice and not a regulated financial advisory system.
  </div>
</main></body></html>"""


def build_pdf_report(html: str, out_path: str | Path) -> str:
    """Write a plain-text/PDF report from verified data (reportlab).

    We render a deterministic PDF summary rather than converting the interactive HTML,
    avoiding heavy browser dependencies while keeping the export reproducible.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    out_path = Path(out_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    c.setTitle("AI Financial Analyst Report")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, "AI Financial Analyst - Analysis Report")
    y -= 10 * mm
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, y, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} - experimental prototype, not investment advice")
    y -= 12 * mm

    # Strip HTML tags to produce a readable plain-text PDF body.
    import re
    text = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_unescape(text)
    words = text.split()
    line = ""
    c.setFont("Helvetica", 9)
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica", 9) < width - 40 * mm:
            line = test
        else:
            c.drawString(20 * mm, y, line)
            y -= 5 * mm
            line = word
            if y < 20 * mm:
                c.showPage()
                y = height - 20 * mm
                c.setFont("Helvetica", 9)
    if line:
        c.drawString(20 * mm, y, line)
    c.save()
    return str(out_path)
