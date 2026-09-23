# 12 — SplitNight

## Status

Downstream economic module. It is intentionally separated from identity and trust.

## Inputs

SplitNight may consume verified identifiers for:

- event;
- artist;
- venue;
- promoter;
- eligible economic participants.

## Economic model

A possible event net revenue model is:

[
R_{net}=R_{tickets}+R_{sponsors}+R_{merch}+R_{F\&B}-C_{event}
]

Participant allocation:

[
P_i=\alpha_i R_{net}
]

with:

[
\sum_i \alpha_i=1
]

## Boundary

Split logic and settlement transport are separate concerns.

Cross-chain HTLC or atomic-swap functionality should be an optional settlement adapter, not part of the identity protocol.

## Dependency rule

Economic modules reference Bitcoin-rooted O2A identities; economic outcomes do
not define who an entity is. Identity keys MUST NOT be reused as payment keys.

## Related remuneration application

[Artist-authorized uses and payments](16-artist-authorized-use-payments.md)
proposes signed permission for selected promotional mentions and catalog or
tour-date links, coupled with payment. A later SplitNight integration could
allocate that revenue among explicitly authorized participants. A single
artist payment does not require a split engine, and payment allocation must
not be inferred from identity or social relationships alone.
