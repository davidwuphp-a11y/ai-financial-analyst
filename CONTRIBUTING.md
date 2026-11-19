# Contributing

Thank you for considering a contribution to AI Financial Analyst.

## Project boundaries

This is an experimental research prototype. Contributions must preserve the separation between document extraction, deterministic financial calculation, AI interpretation, and human review. Do not describe the project as production-ready or as a substitute for regulated financial, accounting, or investment advice.

## Development setup

```bash
python -m venv .venv
# Activate the environment for your platform
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest tests/ -q
python evaluate.py
python evaluate_benchmark.py
```

Python 3.11 or newer is required.

## Contribution expectations

- Add or update tests for behavior changes and bug fixes.
- Keep financial arithmetic deterministic and outside the LLM.
- Cite primary filings for new benchmark data and disclose derived values.
- Do not add confidential, personal, material non-public, or licensed data without permission.
- Escape untrusted content before inserting it into generated HTML.
- Never commit API keys, tokens, credentials, or real client documents.
- Update documentation when changing validation scope or known limitations.

## Pull requests

Describe the problem, implementation, tests run, and any remaining limitations. Keep changes focused and avoid overstating benchmark results.
