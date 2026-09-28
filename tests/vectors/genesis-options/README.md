# Genesis-uniqueness options: adversarial comparison (disposable)

**Test-only. Not normative. Not frozen. Nothing here adopts an option.**
Pinned spec: `c7b08716d017d1f6125e6a728fb098673a09d433`. CC0-1.0.

`check_genesis_options.py` runs the same attacker against five candidate rules,
using the repository's own genesis, transition, claim, seal-script and history
evaluators, with signatures verified by the Rust crypto checker. It reuses
primitives from `../option-b/check_option_b.py`.

| Option | Rule under test |
|---|---|
| A | EntityID from root only (spec as written). A verifier holding two valid, different geneses for one EntityID reports `GENESIS_EQUIVOCATION` and accepts no claims for it. |
| B | EntityID = `TaggedHash(entity-id, u16(1) \|\| network \|\| root \|\| genesis_seal)`. |
| B+act | B, plus: a history whose genesis seal is unspent is `PENDING_ACTIVATION`, never `CURRENT`. |
| G | EntityID = `TaggedHash(entity-id, genesis payload)`; the genesis header's `signer_entity` is 32 zero bytes. Every distinct genesis, including one on the same seal, gets its own EntityID. Drafted as ADR-0008. |
| C | EntityID from root only. A genesis counts only when committed by a confirmed transaction that pays `G(root) = P2TR(NUMS, leaf OP_RETURN<root>)` and carries its digest; the first confirmed commitment wins. `strict` treats an earlier unknown digest as INCOMPLETE; `lax` skips it. |

In every case the attacker holds the root key. Scenarios:
- **own seal:** the attacker funds its own seal with its own seal keys;
- **same seal:** a second genesis on the legitimate seal;
- **takeover:** the attacker also holds the legitimate seal key.

A relying party accepts a `settlement_endpoint` claim only if:
- the claim is valid against the presented package;
- the history is CURRENT;
- plus the option's own check.

"Expected" records what each rule does, including its failures.

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc 'python3 tests/vectors/genesis-options/check_genesis_options.py'
```

Limitations match `../option-b/README.md`:
- transactions are synthetic, so full-chain results are unproven;
- the RGB state ID is a stand-in;
- the genesis and commitment carriers are placeholders;
- verifier knowledge is modelled explicitly as the packages each verifier holds.
