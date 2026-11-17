"""AI Financial Analyst — Streamlit application.

A trustworthy AI financial-analysis prototype: deterministic calculation, evidence
provenance, hallucination guard, and AI-assisted interpretation (mock by default).

Run:  streamlit run app.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ai_analyst import analyse
from src.document_reader import read_figures
from src.financial_metrics import compute_all
from src.hallucination_guard import validate_all
from src.models import ClaimStatus, Concept, Figure, Metric
from src.report_generator import build_html_report, build_pdf_report, metrics_bar_html

st.set_page_config(
    page_title="AI Financial Analyst",
    page_icon="▧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ theme (Wind-style)
CUSTOM_CSS = """
<style>
  .stApp { background-color: #0e1117; }
  [data-testid="stSidebar"] { background-color: #161b24; border-right: 1px solid #232a36; }
  h1, h2, h3, h4, .stMarkdown { color: #e6edf3; }
  .brand { font-size: 22px; font-weight: 600; color: #ff8c00; letter-spacing: .3px; }
  .brand-sub { font-size: 12px; color: #8b98a9; margin-top: -6px; }
  .metric-card { background:#161b24; border:1px solid #232a36; border-left:3px solid #ff8c00;
                 border-radius:8px; padding:12px 14px; margin-bottom:10px; }
  .metric-label { font-size:12px; color:#8b98a9; }
  .metric-value { font-size:22px; font-weight:600; color:#e6edf3; }
  .up { color:#ff4d4f; } .down { color:#3fb950; }
  .tag { display:inline-block; font-size:11px; padding:2px 8px; border-radius:10px; }
  .tag-ok { background:#12331f; color:#3fb950; } .tag-block { background:#3a1414; color:#ff6b6b; }
  .evidence { font-size:12px; color:#58a6ff; }
  .stTabs [data-baseweb="tab"] { color:#8b98a9; }
  .stTabs [aria-selected="true"] { color:#ff8c00 !important; }
  div[data-testid="stDataFrame"] { background:#161b24; }
  .disclaimer { font-size:11px; color:#6e7681; border-top:1px solid #232a36; margin-top:24px; padding-top:12px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DATA = Path(__file__).parent / "data" / "sample_data"
GOLDEN = json.loads((DATA / "golden_figures.json").read_text(encoding="utf-8"))


def demo_periods() -> dict:
    return {p: dict(v) for p, v in GOLDEN["periods"].items()}


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="brand">▧ AI Financial Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">可信 AI 财务分析原型 · v1.0</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**数据源**")
    uploaded = st.file_uploader(
        "上传财报 (PDF / XLSX / CSV)",
        type=["pdf", "xlsx", "xls", "csv"],
        help="未上传时使用内置的苹果 FY2023 公开年报样本",
    )
    use_demo = uploaded is None
    if use_demo:
        st.info("当前使用内置样本：Apple Inc. FY2023 10-K（公开 SEC 文件）")
    else:
        st.success(f"已上传：{uploaded.name}")

    st.markdown("---")
    st.markdown("**AI 解释引擎**")
    provider_label = st.selectbox(
        "Provider",
        ["Mock（离线，无需 API Key）", "OpenAI-compatible（需环境变量）"],
        label_visibility="collapsed",
    )
    st.caption("计算由确定性函数完成，AI 仅解释已验证数据")
    st.markdown("---")
    st.markdown(
        "<div class='disclaimer'>实验性原型 · 非投资建议<br>所有 AI 输出需人工复核</div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ load data
@st.cache_data(show_spinner=False)
def load_uploaded(_bytes: bytes, suffix: str):
    tmp = Path(tempfile.gettempdir()) / f"uploaded_report{suffix}"
    tmp.write_bytes(_bytes)
    return read_figures(tmp)


if use_demo:
    figures: list[Figure] = []
    periods = demo_periods()
    for concept, latest_val in {
        Concept.REVENUE: 383285,
        Concept.NET_INCOME: 96995,
        Concept.TOTAL_ASSETS: 352583,
        Concept.TOTAL_LIABILITIES: 290437,
        Concept.OPERATING_CASH_FLOW: 110543,
    }.items():
        figures.append(Figure(
            concept=concept,
            value=float(latest_val),
            period="FY2023",
            evidence={
                "document": GOLDEN["meta"]["source_file"],
                "page": GOLDEN["page_references"][concept.value],
                "snippet": f"{concept.value.replace('_',' ').title()} — verified against public 10-K",
                "confidence": 1.0,
            },
        ))
else:
    try:
        figures = load_uploaded(uploaded.getvalue(), Path(uploaded.name).suffix)
        periods = {}
    except Exception as exc:  # noqa: BLE001
        st.error(f"文件解析失败：{exc}")
        st.stop()

calc = compute_all(periods) if periods else {"metrics": [], "notes": ["上传文件仅提供单期提取视图。"]}
metrics = calc["metrics"]

# AI analysis (mock by default). Force env for the selected provider.
import os

os.environ["AI_PROVIDER"] = "mock" if provider_label.startswith("Mock") else "openai"
try:
    claims = analyse(figures, [Metric(**m) for m in metrics])
except Exception as exc:  # noqa: BLE001
    st.warning(f"AI 解释不可用（{exc}）。可切换回 Mock Provider。")
    claims = []

company = GOLDEN["meta"]["company"] if use_demo else Path(uploaded.name).stem

# ------------------------------------------------------------------ header
st.title("AI 智能财务分析师")
st.markdown(
    f"**{company}** · 财报阅读 → 证据提取 → 确定性计算 → AI 解释 → 报告生成　|　"
    "计算与解释严格分离，数字可溯源"
)

top_cols = st.columns(4)
top_cols[0].metric("已提取指标", len(figures))
top_cols[1].metric("已计算比率", len(metrics))
allowed_n = sum(1 for c in claims if c.status == ClaimStatus.OK)
top_cols[2].metric("AI 有效结论", allowed_n)
top_cols[3].metric("幻觉拦截", sum(1 for c in claims if c.status == ClaimStatus.BLOCKED))

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["① 上传财报", "② 财务数据", "③ 指标计算", "④ AI 风险分析", "⑤ 报告生成"]
)

# ------------------------------------------------------------------ Tab 1
with tab1:
    st.subheader("功能一 · 上传财报")
    st.markdown(
        "在左侧上传 PDF / Excel / CSV 财报，或使用内置公开样本。系统读取文档内容并定位关键财务数据。"
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**支持格式**")
        st.markdown("- PDF：上市公司 10-K / 年报")
        st.markdown("- Excel / CSV：行为科目、列为期间的结构表")
    with c2:
        st.markdown("**当前状态**")
        st.write("样本：Apple Inc. FY2023 Form 10-K" if use_demo else f"文件：{uploaded.name}")
        st.write(f"识别期间：{', '.join(periods.keys()) if periods else '单期'}")
    st.caption("安全边界：仅处理公开资料或自建测试数据，不上传任何内部 / 保密文件。")

# ------------------------------------------------------------------ Tab 2
with tab2:
    st.subheader("功能二 · 财务数据提取（含证据溯源）")
    if figures:
        df = pd.DataFrame([{
            "科目": f.concept.value.replace("_", " ").title(),
            "数值": f"{f.value:,.0f}",
            "期间": f.period,
            "单位": "USD millions",
            "出处": f.evidence.reference(),
        } for f in figures])
        st.dataframe(df, use_container_width=True, hide_index=True)
        with st.expander("查看原文片段 (evidence snippet)"):
            for f in figures:
                st.markdown(f"**{f.concept.value}** · {f.evidence.reference()}")
                st.code(f.evidence.snippet, language="text")
    else:
        st.warning("未从文件中识别到关键财务数据。请使用内置样本或检查文件格式。")

# ------------------------------------------------------------------ Tab 3
with tab3:
    st.subheader("功能三 · 财务指标计算（确定性函数）")
    st.caption("以下数值全部由纯函数按固定公式计算，LLM 不参与任何算术。")
    if metrics:
        for m in metrics:
            is_pct = m["unit"] == "percent"
            val = m["value"]
            color = "up" if val > 0 else "down" if val < 0 else ""
            shown = f"{val:,.2f}%" if is_pct else (f"{val:,.2f}x" if m["unit"] == "ratio" else f"{val:,.2f}")
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{m["name"]} · {m["period"]}</div>'
                f'<div class="metric-value {color}">{shown}</div>'
                f'<div class="metric-label" style="margin-top:4px">公式：{m["formula"]}</div></div>',
                unsafe_allow_html=True,
            )
        chart = metrics_bar_html(metrics)
        if chart:
            st.markdown("**可视化**")
            st.components.v1.html(chart, height=420)
    else:
        st.info("暂无可计算指标（上传文件可能仅含单期数据）。")

# ------------------------------------------------------------------ Tab 4
with tab4:
    st.subheader("功能四 · AI 风险分析（含幻觉拦截）")
    st.caption("AI 仅解读已验证的数字；生成的每句话都经过数字白名单校验，未授权数字会被拦截。")
    if claims:
        for c in claims:
            if c.status == ClaimStatus.OK:
                st.markdown(f"✓ {c.text}")
            else:
                st.markdown(
                    f'<span class="tag tag-block">已拦截</span> {c.text}<br>'
                    f'<span style="color:#ff6b6b;font-size:12px">{c.reason}</span>',
                    unsafe_allow_html=True,
                )
        st.markdown("---")
        st.markdown("**校验逻辑**")
        st.markdown(
            "数字白名单由「已提取数据 + 已计算指标」构成。AI 文本中的每个数字标记都会被回查；"
            "出现白名单外的数字即判定为幻觉并拦截，不进入最终报告。"
        )
    else:
        st.info("当前无 AI 结论。")

# ------------------------------------------------------------------ Tab 5
with tab5:
    st.subheader("功能五 · 报告生成与下载")
    st.markdown("导出结构化分析报告：图表 + 指标 + AI 解读 + 证据附录 + 免责声明。")
    html_report = build_html_report(figures, metrics, claims, company=company)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "下载 HTML 报告",
            data=html_report.encode("utf-8"),
            file_name="financial_analysis_report.html",
            mime="text/html",
        )
    with col2:
        if st.button("生成 PDF 报告"):
            pdf_path = Path(tempfile.gettempdir()) / "financial_analysis_report.pdf"
            build_pdf_report(html_report, pdf_path)
            st.success(f"PDF 已生成：{pdf_path}")
            st.download_button(
                "下载 PDF 报告",
                data=pdf_path.read_bytes(),
                file_name="financial_analysis_report.pdf",
                mime="application/pdf",
            )
    with st.expander("报告预览 (HTML)"):
        st.components.v1.html(html_report, height=600, scrolling=True)

st.markdown(
    '<div class="disclaimer">AI Financial Analyst · 实验性研究原型，非受监管的财务顾问系统。'
    '财务比率由确定性函数计算，数值经人工核对；AI 解释使用 Mock Provider，需人工复核。不构成投资建议。</div>',
    unsafe_allow_html=True,
)
