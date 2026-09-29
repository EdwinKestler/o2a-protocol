# ADR-0010 — RGB 0.11.1 Opret Carrier Line

**Status:** Proposed, 2026-09-28.

## Context

O2A needs a production RGB line for its first identity transitions, but the
O2A genesis is intentionally independent of an RGB contract identifier,
schema, dependency graph, and commitment carrier. Proposed
[ADR-0009](0009-scoped-genesis-freeze.md) keeps those RGB details outside its
frozen genesis format and forbids a transition until the RGB stack, program,
and commitment carrier are final and adopted.

The earlier Phase 0 work tested the RGB-WG 0.12 release-candidate stack. That
evidence remains useful and must stay archived. A later isolated compatibility
spike tested the published `rgb-protocol` v0.11.1 line against the O2A seal
model and found a working Opret transition path without giving RGB wallet code
custody of the seal.

**O2A's genesis is RGB-line-agnostic; its first transitions use the production
RGB line.**

## Decision

If this ADR is accepted:

1. O2A's first identity transitions MUST use `rgb-protocol` v0.11.1 and the
   Opret commitment method.
2. O2A genesis remains RGB-line-agnostic. An RGB contract identifier, schema
   identifier, assignment identifier, dependency version, or commitment
   carrier MUST NOT change the O2A genesis bytes, EntityID, or state 0 ID.
3. The RGB 0.12 RC3 evidence and patched compatibility fork remain archived;
   they MUST NOT be deleted or rewritten to support this choice.
4. O2A MUST enforce the C6 and C7 lifecycle semantics through the evaluation
   context's current-seal observation. RGB validation alone does not establish
   that the current seal is unspent, and a contract remaining internally valid
   after a plain or competing spend does not make the O2A history `CURRENT`.
5. `rgb-lib` MUST NOT control O2A seal custody. The O2A implementation owns
   seal records, construction, script-path signing, and finalization; RGB APIs
   receive the external seal input and transition commitment.
6. The v0.11.1 adapter MUST live in a separate Cargo workspace from every
   v0.12 experiment. The two incompatible RGB lines MUST NOT appear in one
   dependency graph.
7. Where the selected crates compile two `secp256k1` versions, the adapter MUST
   cross that boundary only with validated byte encodings, never by assuming
   Rust type compatibility.

## Evidence

The evidence is demo commit `2ddfe8c`, bundle
`evidence/regtest-rgb011-compat-2026-09-28/` in the sibling
`o2a-testnet-demo` repository, and
`docs/rgb-0.11.1-compat-memo.md` in that commit. The bundle contains a 22-file
`MANIFEST.sha256`; the manifest file's SHA-256 is
`2b376eed8bb5e5640fe542fbf4b5b4cb7d63315502a4de9f7115b18e16bd2cad`.
It is disposable regtest evidence, not production or mainnet evidence.

- C1–C7 pass: the custom identity schema, external O2A seal, Opret PSBT
  commitment, controller spend, delayed recovery, plain spend observation, and
  competing-contract case behaved as recorded.
- C8 passes under the 2026-09-28 license-assessment decision recorded as D14.
  The blocking advisory, ban, and source checks passed. The report-only license
  check identified `hex_lit 0.1.1` under MITNFA, now recorded as accepted in
  the license register. The original evidence and its verdict under the
  superseded 2026-09-24 policy remain unchanged.
- C9 selects Opret only. Tapret on the O2A script-tree host was unsupported in
  this run; the passing transition path used Opret.

## Consequences

- O2A preserves its independent current-seal check on v0.11.1, as it did for
  the 0.12 evidence, because C6 and C7 show that RGB validity alone does not
  prove an outpoint remains unspent or uniquely current for O2A.
- Seal custody and script-path finalization remain O2A responsibilities;
  `rgb-lib` is not used for them.
- The maintained adapter requires a separate Cargo workspace, and duplicate
  `secp256k1` versions are bridged by bytes.
- Porting the demonstrated adapter and seal flow into the maintained module is
  estimated at three to five focused days. This estimate is not acceptance
  evidence.
- The 0.12-specific Phase 0 dependency-gate document, upstream-needs record,
  and patched fork become historical evidence if this ADR is accepted. They
  remain preserved and do not govern the selected transition workspace.
- Opret is the only carrier selected by this proposal. A later Tapret choice
  requires new evidence and a new decision; it is not inferred from the
  key-only report in C9.

## Required evidence before acceptance

The maintainer MUST NOT accept this ADR until all of the following are true:

1. the v0.11.1 adapter port is merged in its separate Cargo workspace;
2. a complete disposable regtest lineage exercises O2A transitions on
   v0.11.1 with Opret;
3. a signet rehearsal exercises the same v0.11.1/Opret path; and
4. the maintainer reviews the dependency license register, including the
   `hex_lit 0.1.1` assessment.

Until then, this ADR is a proposal. It does not adopt a dependency lock, permit
a frozen-format identity to transition, or make a mainnet-readiness claim.
