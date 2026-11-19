# Limitations, validation scope, and roadmap

## Validation scope

The repository includes two separate evaluation layers:

1. **Extraction fixture:** a reproducible test against one public Apple Inc. FY2023 Form 10-K. This does not establish extraction accuracy for arbitrary issuers or layouts.
2. **Multi-company calculation benchmark:** hand-checked FY2022–FY2023 reference data for Apple, Microsoft, and Amazon. It validates deterministic calculations, not document extraction. See [benchmark methodology](benchmark.md).

## Known limitations

1. **Document layout:** PDF extraction matches selected statement labels and reads numeric tokens from nearby text lines. Multi-column statements, wrapped labels, footnotes, scanned documents, and issuer-specific layouts may fail or produce incomplete results.
2. **Semantic binding:** a rule-based layer binds explicitly named metrics and selected financial concepts to expected values, fiscal years, percentage units, explicit currency markers, and scale words. It is conservative and is not a general-purpose financial-language parser. It cannot reliably resolve complex comparative sentences, implied periods, accounting-policy differences, or causal claims.
3. **Evidence quality:** page and snippet provenance improve traceability but do not independently establish that the extracted value is correct.
4. **LLM output:** model output can be incomplete, misleading, or contextually wrong even when numeric and semantic checks pass.
5. **Upload validation:** uploads have a 20 MB limit, basic file-signature checks, and XLSX archive-structure/expansion checks. These controls are not malware scanning, a parser sandbox, or a guarantee against all malicious files.
6. **Deployment:** the application is a single-user research prototype. It has not undergone a formal security audit, multi-user isolation review, load test, or production deployment assessment.

## Recommended engineering roadmap

- Expand extraction fixtures across more issuers and statement layouts; add confidence scoring and human review for ambiguous results.
- Introduce fully typed financial facts and richer claim-to-evidence links, including explicit scale normalization and comparative-period handling.
- Add property-based and adversarial tests for negative values, percentages, currency symbols, scale conversions, repeated values, and complex sentence structures.
- Add parser sandboxing, malware scanning, authentication, authorization, tenant isolation, rate limiting, and audit logging before multi-user deployment.
- Conduct a formal threat model and independent security review before processing real user documents.

## Responsible use

Do not upload confidential, personal, material non-public, or restricted financial data. Outputs require qualified human review. The prototype is not investment advice, accounting advice, or a regulated financial service.
