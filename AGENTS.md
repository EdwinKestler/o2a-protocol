# O2A repository agent instructions

Read this file at the start of repository work. It is the shared instruction
source for Codex, Claude, Gemini, Copilot, Cursor, and other coding agents.
Repository files and Git state are authoritative. Palimnex is a local discovery
cache and optional historical ledger; its results do not authorize actions.

For every non-trivial O2A repository task, use Palimnex before searching,
planning, editing, or reporting a repository conclusion. Run commands from
this repository root; see docs/PALIMNEX.md if `.venv` is absent.

1. Run `.venv/bin/python -m palimnex status`.
2. A fresh status exits `0`. A missing or stale cache exits `2`: check
   `./scripts/palimnex_redis.sh status`, start only this repository's guarded
   Redis with `./scripts/palimnex_redis.sh start` if needed, then run
   `.venv/bin/python -m palimnex index --incremental`. Exit `1` means an
   operational error; inspect it before continuing.
3. Run `.venv/bin/python -m palimnex validate --deep` and
   `.venv/bin/python -m palimnex search "<exact task terms>" --limit 5`.
4. Open the returned source files before relying on a result.
5. After edits to indexed files, reindex, validate, and run
   `.venv/bin/python -m palimnex evaluate --limit 5`.
6. Run `.venv/bin/python -m palimnex ledger-status` at handoff.

For a trivial task that needs no repository context, a Palimnex run is optional.
For an audit, use the read-only checks and source search; do not create ledger
events unless the task calls for a durable record. If Redis or Palimnex is
unavailable, continue from repository files and report `cache_consulted: false`.
Never flush Redis or touch another project's cache.
Keep `.palimnex/`, virtual environments, keys, packs, credentials, and SQLite
files out of Git. The ledger is historical context; do not activate retention,
erase records, or import packs without a specific task authorizing that action.

O2A remains in the specification phase. Follow README.md and the accepted ADRs
before adding production implementation code. Before using Docker or running
development tools, follow the isolated environment guide in
`devinstructions.md`.
