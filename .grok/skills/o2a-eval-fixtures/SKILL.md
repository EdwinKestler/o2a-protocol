---
name: o2a-eval-fixtures
description: Governance for Palimnex evaluation fixtures. Fixtures are frozen and versioned; retrieval problems are reported, never tuned away.
when-to-use: When Palimnex evaluate fails or changes, or when anything under evaluation/ or .palimnex.json is touched.
paths: evaluation/**, .palimnex.json
---

# Evaluation fixtures

- `evaluation/palimnex-v1.json` and `palimnex-v2.json` are frozen. Never edit a published fixture. A change means a new version file plus an updated `.palimnex.json` checksum, justified per case in the commit body.
- `expected_paths` has all-of semantics (docs/PALIMNEX.md).
- Never reword specs, ADRs or docs to influence ranking. Never rewrite a query to quote document text verbatim.
- Known limitation: ADR-0005 ranks low for conceptual identity queries. It is documented; do not tune for it.
- When a new document displaces an expected path, report the case, the before/after ranks and the displacing document, then stop. The maintainer decides.
- Evaluation changes go in their own commit, never mixed with spec changes.
