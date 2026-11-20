# AI Financial Analyst

> A research prototype for evidence-backed financial-report analysis: document extraction, deterministic calculations, and AI-assisted interpretation with numeric and semantic validation.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)
[![Tests](https://github.com/davidwuphp-a11y/ai-financial-analyst/actions/workflows/tests.yml/badge.svg)](https://github.com/davidwuphp-a11y/ai-financial-analyst/actions/workflows/tests.yml)
[![CodeQL](https://github.com/davidwuphp-a11y/ai-financial-analyst/actions/workflows/codeql.yml/badge.svg)](https://github.com/davidwuphp-a11y/ai-financial-analyst/actions/workflows/codeql.yml)
[![License](https://img.shields.io/badge/license-MIT-gray)](LICENSE)

## Overview

This project explores a safer division of responsibility for AI-assisted financial analysis:

- **Extraction:** locate financial figures in supported documents and retain source evidence.
- **Calculation:** compute financial metrics with deterministic Python functions, not an LLM.
- **Interpretation:** let an LLM explain extracted figures and pre-computed metrics.
- **Validation:** check numeric allow-list membership and explicit metric/value, period, unit, currency, and scale associations.
- **Reporting:** export a reviewable report with an evidence appendix.

**Design principle:** the model may explain verified data; it must not be treated as the source of financial facts or arithmetic.

## Current capabilities

| Area | Current implementation |
|---|---|
| Input | PDF, XLSX, XLS, and CSV |
| Upload safety | 20 MB limit, basic file signatures, XLSX archive structure/CRC/expansion checks, unique temporary files and cleanup |
| Evidence | Document name, page (PDF) or sheet, and source snippet where available |
| Financial calculations | Deterministic, unit-tested Python functions |
| AI provider | Offline mock by default; optional OpenAI-compatible endpoint |
| Narrative validation | Numeric allow-list plus explicit metric/value, fiscal period, percentage, currency, and scale checks |
| Reporting | HTML and PDF exports; untrusted text is escaped in HTML |
| Engineering controls | GitHub Actions tests, CodeQL, Dependabot, security policy, contribution and PR templates |

## Trust boundary

```text
Document
   ↓
Upload validation
   ↓
Extraction + source evidence
   ↓
Verified figures
   ↓
Deterministic metric calculations
   ↓
LLM interpretation (optional)
   ↓
Numeric + semantic validation
   ↓
Human-reviewed report
```

The numeric and semantic guard is a **defense-in-depth check**, not proof of complete semantic correctness. It checks numeric allow-list membership and binds explicitly named metrics and selected financial concepts to their own verified values. It also checks explicit fiscal-year labels, percentage wording, currency markers, and scale wording where available. It is intentionally conservative and does not provide general natural-language understanding or prove causal claims.

## Evaluation

Two evaluation layers are kept separate:

1. **Extraction fixture:** the included Apple FY2023 Form 10-K test checks five selected figures and their page evidence. The included sample evaluation also tests injected numeric fakes. These are sample-specific results, not a claim of accuracy on arbitrary filings.
2. **Multi-company calculation benchmark:** hand-checked FY2022–FY2023 reference data for Apple, Microsoft, and Amazon are used to validate deterministic revenue growth, net margin, debt-to-asset ratio, and operating-cash-flow growth. This is a calculation benchmark, **not** a multi-company PDF extraction benchmark.

Amazon FY2023 total liabilities are derived from reported total assets less reported total stockholders' equity; this derivation is disclosed in the benchmark metadata. The three issuers have different fiscal year-end dates, so cross-company comparisons require period awareness.

See [benchmark methodology](docs/benchmark.md), [limitations](docs/limitations.md), and [methodology](docs/methodology.md).

## Quick start

```bash
git clone https://github.com/davidwuphp-a11y/ai-financial-analyst.git
cd ai-financial-analyst

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Run tests and both reproducible evaluations:

```bash
pytest tests/ -q
python evaluate.py
python evaluate_benchmark.py
```

The app uses the built-in public sample and Mock provider by default. No API key is needed.

## Optional: OpenAI-compatible provider

The real provider is optional and is imported only when selected. Install its SDK separately:

```bash
pip install "openai>=1.40,<3"
```

Then set environment variables (PowerShell example):

```powershell
$env:AI_PROVIDER="openai"
$env:AI_API_KEY="your_api_key"
$env:AI_BASE_URL="https://api.openai.com/v1"
$env:AI_MODEL="gpt-4o-mini"
```

Never commit API keys or secrets. Use environment variables or your deployment platform's secret manager. A safe variable template is provided in `.env.example`.

## Free public demo

**Live demo:** https://ai-financial-analyst-85femw8iudtthcvghkcfzu.streamlit.app/

The app is deployed on Streamlit Community Cloud using Python 3.11. The public demo uses the built-in Apple FY2023 sample and the offline Mock provider; no API key or secrets are configured. Use public or synthetic documents only.

## Project structure

```text
├── app.py
├── evaluate.py
├── evaluate_benchmark.py
├── requirements.txt
├── src/
│   ├── models.py
│   ├── document_reader.py
│   ├── financial_metrics.py
│   ├── hallucination_guard.py
│   ├── upload_security.py
│   ├── ai_analyst.py
│   └── report_generator.py
├── tests/
├── docs/
└── data/
    ├── sample_data/
    └── benchmarks/
```

## Known limitations

- PDF extraction uses layout-sensitive text-line matching; scanned PDFs, complex multi-column tables, footnotes, and issuer-specific layouts are not reliably supported.
- Multi-company reference data currently test deterministic calculations, not multi-company document extraction.
- Semantic validation is rule-based and cannot reliably interpret complex natural-language comparisons, implied periods, accounting-policy differences, or causal claims.
- Upload checks are not malware scanning or parser sandboxing.
- Authentication, tenant isolation, rate limiting, and audit logging are not implemented; do not use this prototype for confidential or restricted documents.
- The project does not replace accountant, analyst, compliance, or investment-professional review.

See [docs/architecture.md](docs/architecture.md), [docs/limitations.md](docs/limitations.md), [docs/benchmark.md](docs/benchmark.md), [docs/deployment.md](docs/deployment.md), and [SECURITY.md](SECURITY.md).

## Security and responsible use

Use public or synthetic documents only. Do not upload confidential, personal, material non-public, or otherwise restricted financial information. This is an experimental portfolio project, not a regulated financial advisory system and not investment advice. Review all outputs before relying on them.

## Author

**David Wu** · [LinkedIn](https://www.linkedin.com/in/david-wu-a60a0144b) · [GitHub](https://github.com/davidwuphp-a11y)
