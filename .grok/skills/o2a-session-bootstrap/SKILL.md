---
name: o2a-session-bootstrap
description: Start any non-trivial o2a-protocol task with the Palimnex discovery workflow, including recovery of this repository's private Redis after a reboot.
when-to-use: At the start of every non-trivial task in o2a-protocol, and whenever a Palimnex command fails with a connection error.
---

# O2A session bootstrap

AGENTS.md is authoritative. This skill adds the recovery steps learned in practice.

## Sequence
1. From the repository root:
   ```bash
   .venv/bin/python -m palimnex status
   .venv/bin/python -m palimnex validate --deep
   .venv/bin/python -m palimnex search "<exact task terms>" --limit 5
   ```
2. If a command fails with `Connection refused` (typically after a machine reboot):
   - run `./scripts/palimnex_redis.sh status`, then `./scripts/palimnex_redis.sh start`;
   - this repository's Redis listens on a private Unix socket (`.palimnex/redis/redis.sock`, managed by `scripts/palimnex_redis.sh`). A Redis on TCP port 6379 belongs to something else: never touch, flush, or restart it;
   - re-run `status`. If the cache is stale, run `index --incremental`, then `validate --deep`.
3. Open every returned source file before concluding anything. Palimnex is a discovery cache, not an authority.
4. If Palimnex stays unavailable, continue from repository sources and report `cache_consulted: false`.

## Report
Always state `cache_consulted: true|false` and any recovery you performed.
