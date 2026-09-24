# Phase 0 closure agents

**Status:** executed and reviewed 2026-09-23. The first pass ran in two batches
of three workers. Coordinator review reopened five normative tracks and left
the dependency gate open; see [the Phase 0 status report](phase0closure.md).
This page preserves the original ownership and execution brief. It is not a
claim that Phase 0 closed.

No agent creates `crates/o2a-rgb`, adopts an RGB lock, or commits. The
accepted ADRs and the current normative specs stay in force until an agent
edits a file it owns and records that decision.

## Shared rules

Every agent starts from the repository root and follows `AGENTS.md`.

1. Run `.venv/bin/python -m palimnex status`. If the cache is stale, reindex
   before searching.
2. Run `.venv/bin/python -m palimnex validate --deep`.
3. Search the exact terms for its task, then open the source files. Search
   hits are not authority.
4. Start a ledger session:

```bash
.venv/bin/python -m palimnex session-start \
  --session-id phase0-<agent> \
  --task "<one sentence>"
```

5. Record each decision before editing, and each outcome after the edit:

```bash
.venv/bin/python -m palimnex remember \
  --session phase0-<agent> \
  --kind decision \
  --subject "phase0.<subject>" \
  --payload '<json>' \
  --evidence "<path>:<start>-<end>" \
  --trust observed \
  --sensitivity internal \
  --retention durable
```

6. After editing indexed files, run `index --incremental`, `validate --deep`,
   and `evaluate --limit 5`.
7. Close the session with `session-close` only after the outcome is recorded.

Ledger payloads are short JSON: `{"decision":"...","files":["..."],"status":"draft|ready"}`.
Agents do not record seeds, keys, wallet paths, or lockfile contents. They do
not run `clear`, retention activation, or pack import. They do not push.

If Redis or Palimnex is down, the agent continues from the files and reports
`cache_consulted: false`.

## How they stay out of each other's way

Each agent owns a file list. It does not edit another agent's files. Shared
facts move through the ledger, not through simultaneous edits.

| Order | What may proceed together | What waits |
| --- | --- | --- |
| First wave | Encoding, RGB contract, evidence semantics, proof-package rules, dependency gate, vector case list | Byte fixtures and signature vectors |
| Join | Coordinator reads `palimnex recall phase0 --retention durable` | Agents rewrite one another's files |
| Second wave | Vector agent fills hex only after `phase0.encoding` is `ready` | RGB program bytes and an adopted lock |

The coordinator is the session that launches these agents. It resolves a
conflict by the document-authority order: accepted ADRs, then normative
specs, then explanations. It records the resolution as a `correction`.

## 1. Encoding agent

**Session:** `phase0-encoding`  
**Subject:** `phase0.encoding`  
**Owns:** `specs/canonical-encoding.md`, the derivation section of
`specs/cryptographic-profile.md`, and the EntityID bullets of
`specs/entity-schema.md`.

**Purpose:** Freeze the v0.1 byte rules the other agents must use.

**Instructions:**

- Define little-endian integers, length-prefixed bytes, the tagged-hash
  formula already required by the cryptographic profile, and the network
  byte for mainnet, testnet, testnet4, signet, and regtest.
- Define EntityID as a tagged hash of version, network, and the 32-byte
  BIP340 root. State that recovery and controller changes do not change it.
- Define a candidate BIP32 shape that keeps the root, controller, recovery,
  and Nostr publication keys in the O2A identity hierarchy, and payment keys
  on BIP86. Do not call an unallocated purpose frozen.
- Define the object-type codes and the canonical claim layout the vector
  agent will hash.
- Do not choose an RGB library version. Do not write signature vectors.
- Remember the decision with the new file path as evidence, then mark the
  subject `ready`.

## 2. RGB contract agent

**Session:** `phase0-rgb`  
**Subject:** `phase0.rgb-contract`  
**Owns:** `specs/rgb-identity-contract.md` and the confirmation section of
`specs/verification-policy.md`.

**Purpose:** Freeze the identity state machine, seal, confirmation depth, and
reorg rule without pretending an RGB stack has been adopted.

**Instructions:**

- Specify genesis, controller rotation, recovery-policy change, authorized
  recovery, custody transfer, and revocation.
- Keep the root public key immutable. A lost recovery path creates a new
  EntityID.
- Define the seal as a Bitcoin outpoint and the anchor as the spending
  transaction that commits to the transition hash.
- Set confirmation depth to 1 on regtest, signet, testnet, and testnet4, and
  to 6 on mainnet. An anchor missing from the named best chain is not current.
- State that the concrete RGB 0.12 program bytes stay unbound until the
  dependency agent records an adopted lock.
- Do not edit the encoding spec or the evidence schemas.

## 3. Evidence agent

**Session:** `phase0-evidence`  
**Subject:** `phase0.evidence`  
**Owns:** `specs/claim-schema.md`, `specs/attestation-schema.md`,
`specs/challenge-schema.md`, `specs/control-proof-schema.md`,
`specs/discovery-binding-schema.md`, and `specs/music-object-schema.md`.

**Purpose:** Freeze what each evidence object means, which key role and
authorization capability sign it, and which cases the vectors must cover.

**Instructions:**

- Keep human names as competing claims. Do not add a first-claim registry.
- Keep DNS, HTTPS, and social proofs as channel-control evidence with an
  expiry input.
- Keep Pubky and Nostr bindings in the discovery-binding domain, signed by an
  authorized BIP340 controller, with the foreign key inside the payload.
- Keep event and album manifests as claims by those entities' own keys.
- Recall `phase0.encoding` before writing byte layouts. Until it is `ready`,
  edit only the semantic requirements and the required vector cases.
- Do not invent a new signature tag. Use the tags already listed in the
  cryptographic profile.

## 4. Proof-package agent

**Session:** `phase0-package`  
**Subject:** `phase0.package`  
**Owns:** `specs/proof-package-schema.md` only.

**Purpose:** Freeze publication, privacy, and offline verification for the
public identity package.

**Instructions:**

- Define three locators: a local file, a direct wallet transfer, and an
  HTTPS URL whose body must match the content hash.
- State that locators are not signed and are not evidence of validity.
- Exclude Bitcoin spending descriptors from public packages.
- Require the manifest to name omitted objects. A missing named object makes
  evaluation incomplete.
- Recall `phase0.encoding` before changing the package hash or signature
  bytes. The publication rules themselves can be written immediately.
- Do not add a discovery host or a registry as the history store.

## 5. Dependency-gate agent

**Session:** `phase0-dependency`  
**Subject:** `phase0.dependency`  
**Owns:** a new `docs/phase0-dependency-gate.md` and the dependency paragraph
of `docs/21-proposed-tech-stack-and-development-environment.md`.

**Purpose:** Decide what is still blocking adoption of the RGB stack. This
agent reads the retained evidence and writes the decision. It does not build
containers or crates.

**Instructions:**

- Read `evidence/phase0/rgb-rc3-remediation-2026-09-23/lock-review/SUMMARY.md`
  and `RUN.md`.
- Record three separate decisions: whether the three-line CLI overlay is the
  pinned dev patch, whether any current lock is adoptable, and whether
  `rust-bitcoin` 0.32.102 remains excluded from consensus-sensitive signing.
- Treat 15 advisories on the full lock, and unmaintained `paste` 1.0.15 on
  the Electrum-only lock, as adoption blockers unless a newer retained audit
  says otherwise.
- Do not vendor RGB, do not run a new regtest, and do not mark Phase 0
  closed.

## 6. Vector agent

**Session:** `phase0-vectors`  
**Subject:** `phase0.vectors`  
**Owns:** `tests/vectors/` only, including a CC0-1.0 notice for that
directory.

**Purpose:** Build the case list the roadmap gate requires, then fill bytes
after the encoding decision is ready.

**Instructions:**

- In the first wave, write the case list in words. Cover distinct root and
  payment keys, duplicate names, an invalid BIP340 signature, cross-domain
  replay, the wrong network, the wrong RGB contract, a forked or missing
  consignment, a mismatched seal, compromise, recovery, revocation, an
  expired control proof, Pubky and Nostr rebinding, album and event custody,
  and unavailable discovery.
- Do not generate signature hex until `palimnex recall phase0.encoding`
  returns `ready`.
- The second wave adds the byte fixtures and a checker that recomputes the
  tagged hashes and BIP340 checks. The checker is a vector tool, not a
  wallet.
- License only this directory under CC0-1.0. Leave the rest of the repository
  under `MIT OR Apache-2.0`.

## Coordinator checklist

After the first wave, the coordinator runs:

```bash
.venv/bin/python -m palimnex recall phase0 --retention durable --limit 30
.venv/bin/python -m palimnex search "canonical encoding RGB identity proof package dependency gate" --limit 5
.venv/bin/python -m palimnex evaluate --limit 5
```

It then writes `docs/phase0closure.md` with the decisions, the files each
agent changed, and any gate that is still open. Phase 0 is closed only when
the encoding, contract, evidence, package, vector, and dependency subjects are
all ready, including an adopted compatible dependency lock. An open dependency
gate does not get recorded as a closed phase.
