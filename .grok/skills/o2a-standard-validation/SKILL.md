---
name: o2a-standard-validation
description: Run the full o2a-protocol validation suite in the Docker toolchain plus the Palimnex post-change checks, and report exact outputs.
when-to-use: After any change to specs, vectors, checkers, ADRs, docs, site or evaluation files, and before every handoff.
---

# Standard validation

Follow devinstructions.md for Docker (`export DOCKER_CONTEXT=default`, run `./dev/check-host.sh` first).

## Suite (inside the toolchain)
```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash -lc '
python3 tests/vectors/derive_route_b.py self-test
python3 tests/vectors/check_derivation_cross.py          # route b cross-check ok
python3 tests/vectors/check_vectors.py                   # ok
python3 tests/vectors/check_protocol_objects.py          # protocol objects ok
python3 tests/vectors/check_genesis_freeze.py            # genesis freeze: 63/63 outputs unchanged
python3 tests/vectors/entity-id-regression/check_entity_id_regression.py   # 27/27
cargo fmt --manifest-path tests/vectors/crypto-checker/Cargo.toml --check
cargo test --locked --manifest-path tests/vectors/crypto-checker/Cargo.toml'
```
Also run `tests/vectors/check_seal_core.py` (Bitcoin Core oracle, uses the o2a-phase0 bitcoind) and cargo audit/deny per DEPENDENCIES.md. Run `python3 scripts/build_site.py` when site/ or its sources changed (expect `Validated 2 pages; exported 11 public files`).

Historical suites (tests/vectors/option-b, tests/vectors/genesis-options) are pinned to c7b0871. They are NOT part of this suite; run them only in a worktree at that commit (see docs/26-test-catalog.md).

## Palimnex after changing indexed files
```bash
.venv/bin/python -m palimnex index --incremental
.venv/bin/python -m palimnex validate --deep
.venv/bin/python -m palimnex evaluate --limit 5     # must stay 22/22 (fixture v2)
.venv/bin/python -m palimnex ledger-status
```

## Known, non-blocking noise
- invalid `docker-sbom` plugin warning; cargo deny unmatched-allowance warnings;
- `cargo test` reports 0 Rust unit tests (the checkers are the evidence);
- ledger `stale` for historical verification records after source changes.

## Report
Paste every command's final line. A count that differs from the expected value is a failure, not noise.
