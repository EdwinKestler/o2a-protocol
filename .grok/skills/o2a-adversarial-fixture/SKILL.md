---
name: o2a-adversarial-fixture
description: Build deterministic adversarial fixtures that test a candidate protocol rule against the repository's own evaluators, with negative controls and honest labelling.
when-to-use: When asked to test a proposed rule or attack (equivalents of tests/vectors/option-b, genesis-options, entity-id-regression).
paths: tests/vectors/**
---

# Adversarial fixture pattern

Reference implementations: tests/vectors/option-b/, tests/vectors/genesis-options/, tests/vectors/entity-id-regression/.

## Rules
1. Reuse the repository's evaluators (decode_payload, valid_state, evaluate_signed_payload, seal_output, identity_history_outcome, evaluate_name_claim). Substitute ONE thing at a single, named seam (for example the entity_id function) and restore it in `finally`.
2. Deterministic: `--emit` writes the fixture JSON; check mode fails if the generator no longer reproduces it byte for byte.
3. Keys: only the published BIP340 test keys the Rust signer exposes (`scalar-3`, `bip340-vector-1`, `bip340-vector-2`). Verify every signature with the Rust crypto checker.
4. Bitcoin data: synthetic but well-formed transactions (real txids from their serialization). No headers or merkle proofs, so every full-chain result is labelled UNPROVEN.
5. "Expected" records what the rule under test ACTUALLY does, including when the attack succeeds. Say so in the README.
6. Model verifier knowledge explicitly: a verifier holds only the packages it was shown.
7. Include negative controls: the old rule must still admit the attack, or the suite proves nothing.
8. Regression suites keep a RULE SEAM (entity_id_of, genesis_valid, identity_state) that later points at the normative implementation, with every expectation unchanged.

## Report
A matrix: case, input difference, expected, observed, the spec rule (or missing rule) responsible. End with pass / fail / unproven.
