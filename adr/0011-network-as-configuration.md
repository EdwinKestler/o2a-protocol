# ADR-0011 — Network as Configuration

**Status:** Accepted, 2026-09-29 (maintainer decision).

**Amends:** [ADR-0007](0007-signet-for-demonstration.md).

## Context

ADR-0007 selected signet for the disposable public demonstration and kept
mainnet outside that demonstration's scope. ADR-0009 subsequently froze the
mainnet genesis and `official_name` surface, including network byte `0`, Route
B coin type `0'`, and confirmation depth `6`. Treating mainnet as a separate
code path would now create configuration drift exactly where the frozen format
requires stable behavior.

O2A therefore needs one implementation path whose network-specific values are
selected from one profile. Development and testing remain on regtest and
signet. The block-0 event runs on mainnet under ADR-0009's narrower operational
scope. This decision supports that network choice; it does not declare that a
production or mainnet identity network is currently running.

## Decision

### 1. One network setting and one derived profile

An O2A implementation MUST accept exactly one network-selection setting:

```text
O2A_NETWORK = regtest | signet | mainnet
default = regtest
```

That setting selects one typed, immutable network profile. Every runtime
consumer MUST obtain all network-specific values from that profile:

| `O2A_NETWORK` | O2A network byte | Route B coin type | P2TR address HRP | RGB chain | Bitcoin backend class | Required confirmation depth |
| --- | ---: | --- | --- | --- | --- | ---: |
| `regtest` | `4` | `1'` | `bcrt` | regtest | isolated local Bitcoin Core and its configured local resolver | `1` |
| `signet` | `3` | `1'` | `tb` | default public signet | O2A-owned Bitcoin Core and configured resolver; explicit public fallbacks may be named in the profile | `1` |
| `mainnet` | `0` | `0'` | `bc` | mainnet | explicitly configured mainnet Bitcoin Core and resolver endpoints | `6` |

The profile includes the concrete Bitcoin RPC, Electrum, or Esplora endpoint
selection used by its backend class. Implementation code outside the profile
MUST NOT contain network literals, duplicate network-to-value tables, or branch
on raw network strings or bytes. It consumes the typed profile instead. Specs
and conformance fixtures may state expected literals in order to define and
test the profile.

Switching among the three supported networks MUST require configuration only,
not source edits, rebuild-time feature changes, or a different executable.
The Draft v0.1 wire encoding continues to recognize its existing testnet and
testnet4 values for verification; they are not selectable runtime profiles
under this decision.

### 2. Mainnet session authorization

`O2A_NETWORK=mainnet` is necessary but not sufficient to perform a mainnet
operation. Each process session MUST also receive both:

1. an explicit mainnet-authorization flag, equivalent to
   `--authorize-mainnet`; and
2. an interactive typed confirmation of the exact word `mainnet` after the
   active profile and intended operation are displayed.

Neither authorization may be persisted, inferred from a prior session,
supplied by the network setting, or bypassed by a stored preference. Failure
of either check MUST stop before key use, transaction construction, signing,
or broadcast. This is an operational lock around the same implementation
path, not a request for a mainnet-only code change.

### 3. Independent ADR-0009 scope limit

Network authorization does not expand protocol scope. On mainnet, a
frozen-format identity may create only the ADR-0009 genesis and its one
`official_name` claim until the concrete RGB program and remaining transition
rules are final and adopted. A configured or authorized mainnet session MUST
reject every transition, recovery, custody, additional-claim, or other
operation outside that scoped surface.

The block-0 event uses the mainnet profile and the per-session authorization
above. Its identity is permanent under ADR-0009's compatibility promise.

### 4. Development, testing, and offline mainnet proof

Development and networked automated tests MUST use regtest or signet. Mainnet
conformance is tested only by an **OFFLINE** dry run in the standard suite:
the mainnet profile is selected, its derived values and frozen genesis outputs
are checked, all network transports and broadcast paths are disabled, and the
test uses only published permanently unsafe vector material. The dry run MUST
fail if any code attempts a network connection or broadcast.

Before production implementation code exists, the 63-output ADR-0009 freeze
check is the offline evidence for the frozen mainnet profile values and
genesis bytes. The future implementation suite MUST add the full profile,
backend-selection, authorization, UI-label, and no-broadcast dry run without
altering those frozen outputs.

### 5. User-interface requirements

Every CLI, desktop, mobile, browser, and service-operator interface MUST show
the active network wherever it can construct, sign, inspect, or broadcast an
operation. Mainnet MUST use a prominent indicator that cannot be confused
with regtest or signet. Confirmation prompts MUST repeat the active network.

Signet identities, keys, balances, proofs, and application state remain
disposable test material. Mainnet identities are permanent public identities;
implementations MUST NOT describe them as disposable or offer a reset that
implies the identity can be reminted under the same identifier.

## Consequences

- Mainnet is a supported configuration, not a hard-coded exclusion or a
  separate implementation.
- Regtest remains the default and primary development network; signet remains
  the public rehearsal and interoperability network.
- Mainnet use carries an explicit session-local human authorization boundary
  in addition to configuration.
- ADR-0009, not network selection, defines what block 0 may do while the RGB
  program remains unfinished.
- No production or mainnet identity network is running merely because this
  configuration decision is accepted.
