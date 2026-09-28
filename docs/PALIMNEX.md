# Palimnex in O2A

This repository uses Palimnex 2.7.0 for local source discovery and an optional
durable history ledger. It is installed as a Python package in an ignored
virtual environment; no Palimnex engine source is vendored into O2A.

To reproduce the local installation, obtain a reviewed Palimnex 2.7.0 wheel
and run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-deps /path/to/palimnex-2.7.0-py3-none-any.whl
./scripts/palimnex_redis.sh start
.venv/bin/python -m palimnex status
.venv/bin/python -m palimnex index --incremental
.venv/bin/python -m palimnex validate --deep
.venv/bin/python -m palimnex evaluate --limit 5
.venv/bin/python -m palimnex ledger-init
.venv/bin/python -m palimnex ledger-status
```

The current local wheel came from `/home/kestl/github/palimnex/dist/` and has
SHA-256 `be01f323b0bfc3ab4755ea53780384f21b839f66da443d2ba45d25efb3d94044`.
The O2A project UUID and cache namespace are distinct from Palimnex's own.
The private Redis socket and SQLite ledger live under ignored `.palimnex/`.
Frozen retrieval fixtures are under `evaluation/` and excluded from indexing.
Within a case, `expected_paths` has all-of semantics: every listed path must
appear within that case's result limit. Use a dedicated case when alternatives
or a more exact query need separate coverage.

Known limitation: ADR-0005 ranks below summaries and narrower documents for
broad conceptual identity queries. That retrieval ranking does not change the
document-authority order. The evaluation fixture is not tuned to force
ADR-0005 into those result sets; use an exact ADR or authority query when its
decision text is required.

Agent instructions live in the repository-root `AGENTS.md`. Claude and Gemini
have root instruction files, Copilot has `.github/copilot-instructions.md`, and
Cursor has an always-applied rule under `.cursor/rules/`; each points to that
shared workflow. Agents should use it for non-trivial repository work and can
skip the cache for tasks that need no repository context. If the local package
or Redis is unavailable, they continue from source and disclose
`cache_consulted: false`.

After changing indexed files, run `index --incremental`, `validate --deep`,
and `evaluate --limit 5`. Search results locate current source; the source
remains authoritative. Do not record private material in the ledger.
