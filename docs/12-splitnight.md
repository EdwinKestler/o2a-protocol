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

Economic modules reference O2A identities; economic outcomes do not define who an entity is.
