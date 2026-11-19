# AI Financial Analyst

> A research prototype for evidence-backed financial-report analysis: document extraction, deterministic calculations, and AI-assisted interpretation with a numeric validation layer.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)
[![Tests](https://github.com/davidwuphp-a11y/ai-financial-analyst/actions/workflows/tests.yml/badge.svg)](https://github.com/davidwuphp-a11y/ai-financial-analyst/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-gray)](LICENSE)

## Overview

This project explores a safer division of responsibility for AI-assisted financial analysis:

- **Extraction:** locate financial figures in supported documents and retain source evidence.
- **Calculation:** compute financial metrics with deterministic Python functions, not an LLM.
- **Interpretation:** let an LLM explain only the extracted figures and pre-computed metrics.
- **Validation:** inspect generated narrative for numeric tokens that are not in the trusted-value allow-list.
- **Reporting:** export a reviewable report with an evidence appendix.

**Design principle:** the model may explain verified data; it must not be treated as the source of financial facts or arithmetic.

## Current capabilities

| Area | Current implementation |
|---|---|
| Input | PDF, XLSX, and CSV; 20 MB limit and file/container validation |
| Evidence | Document name, page (PDF), and source snippet |
| Financial calculations | Deterministic, unit-tested functions |
| AI provider | Offline mock by default; optional OpenAI-compatible endpoint |
| Numeric validation | Numeric allow-list plus explicit metric/value, period, currency, and scale association checks |\n| Upload safety | Signature checks, XLSX ZIP integrity/expansion limits, unique temporary files and cleanup |
| Interface | Streamlit |
| Export | HTML and PDF reports |

## Trust boundary

```text
Document
   ↓
Extraction + source evidence
   ↓
Verified figures
   ↓
Deterministic metric calculations
   ↓
LLM interpretation (optional)
   ↓
Numeric validation
   ↓
Human-reviewed report
```

The numeric guard is a **defense-in-depth check**, not a proof of semantic correctness. In addition to numeric allow-list membership, the current rule-based layer checks explicitly named metrics against their own verified values, flags mismatched fiscal years, and checks explicit percentage, currency, and scale wording. It is intentionally conservative and does not provide general natural-language understanding or prove causal claims.

## Evaluation

The included benchmark uses one hand-verified sample from Apple's public FY2023 Form 10-K. The repository's evaluation script reports:

| Measure | Demo result |
|---|---:|
| Key figure extraction | 5/5 on the included filing |
| Page evidence | 5/5 on the included filing |
| Injected numeric fakes blocked | 3/3 in the included test cases |
| Unit tests | Run locally or through GitHub Actions |

These are **sample-specific results**, not a claim of 100% accuracy on arbitrary filings. A separate calculation benchmark now covers Apple, Microsoft, and Amazon FY2022–FY2023 reference data. It checks deterministic ratio calculations against hand-calculated expected values; it does **not** claim multi-company PDF extraction accuracy. Amazon FY2023 total liabilities are derived from reported total assets less reported stockholders’ equity and are disclosed as such in the benchmark metadata. CI runs the automated test suite on pushes and pull requests; the workflow badge reports the latest CI status.

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

Run tests and the reproducible sample evaluation:

```bash
pytest tests/ -q
python evaluate.py
```

The app uses the built-in public sample and mock provider by default. No API key is needed. For a free public demo, see [the Streamlit Community Cloud deployment guide](docs/deployment.md).

### Optional: OpenAI-compatible provider

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

Do not commit API keys or secrets. Use environment variables or your deployment platform's secret manager.

## Project structure

```text
├── app.py
├── evaluate.py
├── requirements.txt
├── src/
│   ├── models.py
│   ├── document_reader.py
│   ├── financial_metrics.py
│   ├── hallucination_guard.py
│   ├── ai_analyst.py
│   └── report_generator.py
├── tests/
├── docs/
└── data/sample_data/
```

## Known limitations and next steps

- PDF extraction currently uses layout-sensitive text-line matching; it is not a general-purpose financial-statement parser.
- Scanned PDFs, complex multi-column tables, and issuer-specific statement layouts are not reliably supported.
- The current benchmark covers one public filing and a small set of test cases.
- The numeric allow-list does not yet bind a value to its metric, unit, currency, scale, or period.
- The prototype does not replace accountant, analyst, compliance, or investment-professional review.
- Upload handling and report generation should be further hardened before any multi-user or public deployment.

See [docs/limitations.md](docs/limitations.md), [docs/methodology.md](docs/methodology.md), [docs/architecture.md](docs/architecture.md), [docs/benchmark.md](docs/benchmark.md), [docs/deployment.md](docs/deployment.md), and [SECURITY.md](SECURITY.md).

## Security and responsible use

Use public or synthetic documents only. Do not upload confidential, personal, material non-public, or otherwise restricted financial information. This is an experimental portfolio project, not a regulated financial advisory system and not investment advice. Review all outputs before relying on them.

## Author

**David Wu** · [LinkedIn](https://www.linkedin.com/in/david-wu-a60a0144b) · [GitHub](https://github.com/davidwuphp-a11y)
