# O2A Key-Derivation Profile — Proposed v0.1

## Status

**Proposed, not frozen.** This profile is a Phase 0 candidate. It does not
authorize production identities, change an EntityID, adopt an RGB dependency,
or reserve a BIP43 purpose.

Every mnemonic, seed, extended private key, and private key published with the
conformance vectors for this profile is permanently unsafe for funds.

## O2A wallet root

O2A uses BIP85's BIP32-XPRV application to derive an independent extended
private root from the wallet's master BIP32 tree:

```text
wallet_root_tagged_hash = TaggedHash("O2A/v0.1/wallet-root", empty)
O2A_INDEX = be32(wallet_root_tagged_hash[0..4]) >> 1 = 998536622
bip85_path = m/83696968'/32'/998536622'
xprv_o2a = BIP85-BIP32-XPRV(master_xprv, O2A_INDEX)
```

`O2A_INDEX` is exact: compute
`TaggedHash("O2A/v0.1/wallet-root", empty)`, take bytes `0..4` as a
big-endian `u32`, and shift that value right by one bit. The full tagged hash is
`7708eb5c35e272440dd51e4b1d4bff3304e9aa8ce2eae38b7e8ad59e4d11c38d`.
The result is `998536622`. Reading the low 31 bits instead would produce
`1997073244`; that value is **not** this profile. The selected index is
deterministic, documented, nonzero, and does not claim a shared registry
entry. Its residual collision surface is explicit: another BIP85 BIP32-XPRV
consumer would have to choose the same application index.

BIP85 purpose `83696968'` and application `32'` are registered by BIP85.
BIP85 derives entropy from the hardened application path, using
`HMAC-SHA512(key="bip-entropy-from-k", msg=k)`. For application `32'`, the
first 32 output bytes become the new chain code and the second 32 bytes become
the new private key; depth, parent fingerprint, and child number are zero.
Thus `xprv_o2a` is an independent BIP32 root, not a key reused from the master
tree.

## Permanently unsafe test seed

The conformance vectors use the published BIP39 English test mnemonic
`abandon` repeated eleven times followed by `about`, with passphrase `TREZOR`.
It produces this 64-byte seed:

```text
c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e5349553
1f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04
```

The Python conformance implementation derives this seed from the mnemonic and
asserts equality with the published bytes. The independent Rust implementation
takes the seed bytes as input and does not implement BIP39. The mnemonic,
passphrase, seed, extended keys, and every derived key are permanently unsafe
for funds.

## Identity tree below `xprv_o2a`

In the paths below, `m` means `xprv_o2a`, never the wallet's master seed or
master extended key. Every component is hardened:

```text
m/coin'/entity'/0'/0'        root identity
m/coin'/entity'/1'/index'    controller
m/coin'/entity'/2'/index'    recovery
m/coin'/entity'/3'/index'    Nostr publication
```

The network-to-coin mapping is the O2A-CANON-1 mapping: mainnet uses `0'`;
testnet, testnet4, signet, and regtest use `1'`. A declared network and its
coin value MUST agree.

`entity'` is a wallet-local unsigned 31-bit identity index. The first EntityID
created by a wallet uses `0'`; each later EntityID uses the smallest index
greater than every index previously allocated by that wallet. An allocated
index MUST be durably recorded and MUST NOT be reused after transfer,
revocation, deletion, or failed publication. Concurrent wallet instances MUST
coordinate this allocation before deriving a persistent identity. An invalid
BIP32 child is a hard failure for that exact path; an implementation MUST NOT
silently increment a component and create a path alias.

Each artist, venue, promoter, label, EVENT, and ALBUM root receives its own
`entity'` value. EVENT and ALBUM identities are never role children of an
artist identity. Unique entity, role, and operational indexes yield distinct
fully hardened BIP32 paths. Assuming BIP32's pseudorandom child derivation and
secp256k1 key uniqueness, distinct allocated paths collide only with
cryptographically negligible probability; the no-reuse rule prevents a
wallet-level path collision.

Identity role values are fixed: `0'` root, `1'` controller, `2'` recovery,
and `3'` Nostr publication. Root identity uses fixed terminal index `0'`.
Controller, recovery, and Nostr indexes are monotonically allocated within
their role and MUST NOT be reused. Unhardened identity components, unknown
roles, and components outside the unsigned 31-bit range are invalid.

## Payment and external keys

Bitcoin payment keys remain on BIP86 under the wallet master seed:

```text
m/86'/coin'/account'/0/index
```

This `m` is the master BIP32 tree, not `xprv_o2a`. A payment key has no O2A
key role or O2A key identifier and MUST NOT sign an O2A object. Payment paths
retain BIP86's unhardened change and address-index components.

Pubky uses Ed25519 and remains outside this profile. This document does not
define Pubky key derivation.

## Retirement and compatibility

BIP43 purpose `827'` is retired. It is not parameterized, is not a valid O2A
path, and appears nowhere else in normative text. Route A—requesting a BIP or
SLIP allocation—may be adopted later without changing existing EntityIDs,
because no persistent O2A identity has yet been derived from a seed under a
frozen profile.

A generic hardware wallet will not derive these keys unaided. A signing
device must explicitly implement this profile, including BIP85 application
`32'`, the fixed O2A index, the network mapping, and the hardened identity
subtree.

## Source basis

- [BIP85: Deterministic Entropy From BIP32 Keychains](https://github.com/bitcoin/bips/blob/master/bip-0085.mediawiki)
- [BIP32: Hierarchical Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
- [BIP86: Key Derivation for Single Key P2TR Outputs](https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki)
