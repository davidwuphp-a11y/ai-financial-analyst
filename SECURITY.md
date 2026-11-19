# Security Policy

## Scope

AI Financial Analyst is an experimental portfolio and research project. It is not designed for confidential or production financial data.

## Safe use

- Use public filings or synthetic test data only.
- Never commit API keys, credentials, personal information, confidential client material, or material non-public information.
- Keep provider credentials in environment variables or a deployment secret manager.
- Review generated reports before sharing them.

## Reporting a vulnerability

Please do not publish sensitive exploit details in a public issue. Contact the maintainer through the email listed on the GitHub profile with a concise description and reproduction steps. Do not include confidential financial documents or secrets in the report.

## Current security limitations

The project has not undergone a formal security audit. Current controls include a 20 MB upload limit, basic content-signature checks, XLSX archive structure and expansion checks, per-upload temporary files with cleanup, HTML output escaping, CI tests, CodeQL, and Dependabot. These controls are not malware scanning or parser sandboxing. Before multi-user deployment, add authentication, authorization, tenant isolation, rate limiting, audit logging, parser isolation, and an independent security review.
