# 26 — Test catalog

**Status:** supporting operations record, 2026-09-28. This catalog introduces
no protocol rule. Coverage claims are bounded by
[`tests/vectors/CASES.md`](../tests/vectors/CASES.md), and the canonical
commands remain [the isolated development instructions](../devinstructions.md).
Run from the repository root with `DOCKER_CONTEXT=default`.

`Standard` means the checker appears in the standard vector command in
`devinstructions.md`. The Core oracle is a required companion that needs the
isolated Bitcoin service, but it is not currently inside that combined command.
Palimnex intentionally runs on the host. Historical fixtures must run against
their pinned checkout and are not part of the standard suite.

| Checker path | What it covers | Classification | Exact run command | Expected output | Last verified result |
| --- | --- | --- | --- | --- | --- |
| `tests/vectors/derive_route_b.py` | Independent BIP32, BIP85 BIP32-XPRV, and BIP39 self-tests used by Route B | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/derive_route_b.py self-test'` | Three lines ending `ok` | PASS, three self-tests, 2026-09-28 |
| `tests/vectors/check_derivation_cross.py` | Route B fixture reproduction and Python/Rust derivation agreement | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/check_derivation_cross.py'` | `route b cross-check ok` | PASS, 2026-09-28 |
| `tests/vectors/check_vectors.py` | Identity, claim, semantic-claim, proof-package, EntityID, state-ID, and BIP340 vectors | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/check_vectors.py'` | `ok` | PASS, 2026-09-28 |
| `tests/vectors/check_protocol_objects.py` | Canonical signed objects, authorization, recovery, seal policy/script, lifecycle outcomes, and reject cases | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/check_protocol_objects.py'` | `protocol objects ok` | PASS, 2026-09-28 |
| `tests/vectors/check_seal_core.py` | Independent Bitcoin Core 31.1 `getdescriptorinfo` / `deriveaddresses` oracle for every seal vector | Core oracle companion | Start Core with `docker compose --file dev/compose.yaml up --detach --wait bitcoin`, then run `DOCKER_CONTEXT=default python3 tests/vectors/check_seal_core.py` | `bitcoin core seal oracle ok` | PASS, 2026-09-28 |
| `tests/vectors/check_genesis_freeze.py` | Rebuilds the proposed ADR-0009 63-output mainnet manifest; checks hashes, signatures, EntityID/state ID, and Rust agreement | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/check_genesis_freeze.py'` | `genesis freeze: 63/63 outputs unchanged` and cross-check `ok` | PASS, 63/63, 2026-09-28 |
| `tests/vectors/entity-id-regression/check_entity_id_regression.py` | ADR-0008 R1–R5 plus legacy-negative-control group N | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/entity-id-regression/check_entity_id_regression.py'` | `27/27 expectations met` | PASS, 27/27, 2026-09-28 |
| `tests/vectors/option-b/check_option_b.py` | Option B cases 1–4 and signature cross-checks under the old rule | Historical, pinned to `c7b0871` | In the prepared historical worktree below: `docker compose --file /tmp/o2a-c7b0871/dev/compose.yaml --project-directory /tmp/o2a-c7b0871/dev --project-name o2a-historical --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/option-b/check_option_b.py'` | `option-b: 46/46 expectations met` | PASS, 46/46, 2026-09-28 |
| `tests/vectors/genesis-options/check_genesis_options.py` | Options A, B, B plus activation, C, and G under the pinned adversarial harness | Historical, pinned to `c7b0871` | In the prepared historical worktree below: `docker compose --file /tmp/o2a-c7b0871/dev/compose.yaml --project-directory /tmp/o2a-c7b0871/dev --project-name o2a-historical --profile tools run --rm toolchain bash -lc 'python3 tests/vectors/genesis-options/check_genesis_options.py'` | `genesis-options: 76/76 expectations met` | PASS, 76/76, 2026-09-28 |
| `tests/vectors/crypto-checker/` | Independent Rust derivation, tagged hashes, BIP340 signatures, seal scripts, EntityIDs, and state IDs; formatting, lock audit, and dependency policy | Standard | `docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc 'cargo fmt --manifest-path tests/vectors/crypto-checker/Cargo.toml --check && cargo test --locked --manifest-path tests/vectors/crypto-checker/Cargo.toml && cargo audit --file tests/vectors/crypto-checker/Cargo.lock && bash tests/vectors/crypto-checker/check_dependency_policy.sh'` | Formatting, tests, audit, and blocking advisory/ban/source checks exit zero; the license-check output and exit are reported without failing development | PASS; current checker license report exits zero, 2026-09-28 |
| `evaluation/palimnex-v2.json` through Palimnex | Frozen source-retrieval regression for the indexed documentation corpus | Host discovery/evaluation, not Docker | `.venv/bin/python -m palimnex evaluate --limit 5` | `22/22 passed` | PASS, 22/22, 2026-09-28 |

## Historical worktree preparation

The current fixtures are copied unchanged into an isolated checkout of their
pinned code. Compose must use the checkout's `dev/` directory as its project
directory so the compose file's `..:/workspace` mount resolves to the checkout.

```bash
git worktree add --detach /tmp/o2a-c7b0871 \
  c7b08716d017d1f6125e6a728fb098673a09d433
cp -a tests/vectors/option-b tests/vectors/genesis-options \
  /tmp/o2a-c7b0871/tests/vectors/
docker compose --file /tmp/o2a-c7b0871/dev/compose.yaml \
  --project-directory /tmp/o2a-c7b0871/dev \
  --project-name o2a-historical --profile tools run --rm toolchain \
  bash -lc 'python3 tests/vectors/option-b/check_option_b.py && python3 tests/vectors/genesis-options/check_genesis_options.py'
docker compose --file /tmp/o2a-c7b0871/dev/compose.yaml \
  --project-directory /tmp/o2a-c7b0871/dev \
  --project-name o2a-historical --profile tools down
git worktree remove --force /tmp/o2a-c7b0871
```

The `--force` cleanup is limited to this disposable worktree and is necessary
because the two copied historical fixture directories are untracked at
`c7b0871`. Do not add them to a standard-suite command against current code.
