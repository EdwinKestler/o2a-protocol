# Phase 0 identity derivation allocation

**Status:** Route B is demo-stable v0.1 under ADR-0006. The allocation question
is closed for the demo track and reopens only for the mainnet freeze.

## Decision record

2026-09-23 — purpose `827'` is PROVISIONAL test data. Freeze is blocked on:
(a) an official BIP or SLIP allocation, or a written and tested
collision-safe alternative scheme that does not occupy the BIP43 purpose
slot; (b) two independent implementations deriving identical keys from the
published unsafe test seed; (c) a collision-free indexing rule for multiple
EntityIDs in one wallet. Route (request an allocation vs. specify an
alternative) is not yet chosen.

2026-09-24 — Route B is the selected candidate. It uses BIP85's registered
BIP32-XPRV application `m/83696968'/32'/998536622'` to derive `xprv_o2a`, then
uses a fully hardened network/entity/role/index subtree below that independent
root. This avoids occupying a BIP43 purpose slot and requires no BIP or SLIP
allocation. The former provisional purpose is retired except in historical
records and explicit rejection vectors. Selection and completed conformance
evidence do not freeze the profile; freezing remains a separate maintainer
decision.

2026-09-24 — [ADR-0006](../adr/0006-route-b-key-derivation-via-bip85.md)
designates Route B **demo-stable v0.1**. All seven evidence gates remain
satisfied. Freezing is deferred because demonstration identities are
disposable; a mainnet-capable release requires a separate maintainer ADR.
The allocation question is therefore closed for the demo track and reopens
only when the mainnet derivation profile is frozen.

O2A needs deterministic wallet separation between root identity, controller,
recovery, Nostr-publication, and Bitcoin payment keys. Route B derives an
independent `xprv_o2a` with BIP85 and records those roles below it. The retired
literal purpose has no accepted interoperability allocation and is not a valid
O2A path.

## Candidate shape

```text
wallet master: m/83696968'/32'/998536622' -> xprv_o2a
xprv_o2a:     m/coin'/entity'/0'/0'       root identity
xprv_o2a:     m/coin'/entity'/1'/index'   controller
xprv_o2a:     m/coin'/entity'/2'/index'   recovery
xprv_o2a:     m/coin'/entity'/3'/index'   Nostr publication
wallet master: m/86'/coin'/account'/0/index Bitcoin payment
```

Pubky remains outside this hierarchy because its key is Ed25519. A payment key
has no O2A key role or O2A key identifier and must never sign an O2A object.

## Acceptance gate

The Route B profile becomes eligible for a separate freeze decision only after
all of these are recorded:

1. a collision review against existing BIP43 application purposes;
2. a selected collision-safe mechanism and its exact semantics, without
   claiming an unassigned BIP43 or SLIP purpose;
3. two independent implementations deriving the same keys from one published,
   explicitly unsafe test seed, with seed format, passphrase, wordlist,
   network-to-coin-type mapping, and implementation/library versions recorded;
4. exact expected public keys and paths for root identity, controller,
   recovery, Nostr publication, and BIP86 payment keys on mainnet and test
   networks;
5. a collision-free account/entity indexing rule for multiple independent
   identities in one wallet, including artist, venue, promoter, label, EVENT,
   and ALBUM roots. EVENT and ALBUM are separate EntityIDs, not child roles of
   the artist's EntityID;
6. invalid-case vectors for unhardened identity roles, cross-role or
   cross-entity key reuse, path aliases, wrong coin type/network, unsupported
   derivation versions, and payment-key use in an O2A signature; and
7. regeneration of every fixture that used the retired provisional path, or an
   explicit inventory marking it obsolete.

Route B is that documented alternative mechanism. Passing these evidence gates
does not itself freeze the wallet profile.

## Gate status — 2026-09-24

| Gate | Status | Evidence |
| ---: | --- | --- |
| 1 | satisfied | Route B uses registered BIP85 application `32'` and a deterministic application index outside the BIP43 purpose slot. |
| 2 | satisfied | `specs/key-derivation-profile.md` specifies the BIP85 path, HMAC operation, raw `xprv_o2a`, and hardened subtree. |
| 3 | satisfied | Independent Rust and Python implementations agree from the published unsafe BIP39 test seed; Rust consumes seed bytes and Python also checks BIP39. |
| 4 | satisfied | `tests/vectors/derivation-v0.1.json` records exact paths, raw extended private roots, and x-only keys for mainnet and regtest, entities 0 and 1. |
| 5 | satisfied | The profile monotonically allocates and never reuses wallet-local `entity'` indexes; each artist, venue, promoter, label, EVENT, and ALBUM gets its own index. |
| 6 | satisfied | The derivation fixture executes the required invalid cases against both implementations. |
| 7 | satisfied | Normative references use Route B; the retired path remains only in history, an explicit rejection, or unrelated hexadecimal evidence. |

All seven evidence gates remain satisfied. The profile is **demo-stable v0.1**
under ADR-0006 and is not frozen for mainnet or production identities.

## Collision review — 2026-09-23

BIP43 says a new scheme should use its BIP number as the hardened purpose so
wallet trees do not overlap. Purposes `10001'` through `19999'` are reserved
for SLIPs. Deployed Bitcoin purposes that this profile must not reuse include
`44'`, `45'`, `48'`, `49'`, `84'`, and `86'`. Payment keys already use `86'`.

The retired provisional purpose is not an assigned BIP. No BIP or SLIP number
was requested or granted. Route B avoids that allocation requirement by using
BIP85's registered BIP32-XPRV application and a deterministic application
index.

## Effect on current work

Seed-to-root derivation is now specified and independently tested with public,
permanently unsafe fixtures. Implementations may use those fixtures while
working on canonical bytes, but MUST NOT create persistent production
identities until the proposed profile is explicitly frozen.
