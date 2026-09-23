# 13 — Roadmap

## Phase 0 — Specification

- freeze terminology;
- define canonical schemas;
- define canonical serialization;
- define authorization transitions;
- define portable proof package;
- create deterministic test vectors.

## Phase 1 — Local / regtest

Release sequence:

```text
0.0.1 Entity
0.0.2 Claim
0.0.3 Attestation
0.0.4 Challenge + Revocation
0.0.5 Policy Engine
0.1.0 Complete Hello World
```

Exit condition: multiple independent verifier implementations produce identical outputs from fixed vectors.

## Phase 2 — Test network

- Artist Catalog;
- Venue Registry;
- Event Registry;
- shared test environment;
- adversarial identity collisions;
- registry destruction/rebuild tests;
- key rotation and revocation tests.

## Phase 3 — Public test release

- public API;
- CLI verifier;
- SDK;
- portable proof package exchange;
- external integrator testing;
- schema/policy compatibility matrix.

## Phase 4 — Mainnet v1

Initial public release should prioritize:

```text
Identity + Evidence + Verification
```

Do not require GatePass, SplitNight, or financial settlement for v1.

## Phase 5 — Applications

After protocol stability:

- GatePass;
- sponsorship/merchandise integrations;
- SplitNight;
- additional registry applications.

## Phase 6 — Federation and reputation

Only after sufficient real evidence:

- federated registries;
- policy diversity;
- graph reputation research;
- optional cross-chain settlement adapters.
