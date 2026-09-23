# 17 — Control proofs, independent recognition, and verification bonds

**Status:** proposed design and local experiment plan, reviewed 2026-09-23.
This refines the artist-name verification idea. It does not finalize wire
formats, add production code, or authorize real-fund experiments.

## Polished proposal

An artist first validates the Bitcoin-anchored RGB history of a dedicated
BIP340-rooted EntityID, then originates a signed name claim, proves control of
established public channels, and obtains attestations from identifiable
counterparties. Independent clients evaluate that portable evidence under a
named policy.
An optional, time-limited satoshi bond can support accountability where its
release conditions and failure handling are explicit.

The intended incentive is: **make legitimate claims practical to verify and
fraud costly to sustain.** Locking money alone does not establish identity.
A refundable deposit and a forfeitable fraud bond are different mechanisms.
Their deterrence must be measured, not assumed.

Recommended scope: adopt channel-control challenges and scoped attestations
into the specification plan; test a refundable bond on regtest after the core
passes conformance; defer forfeiture until adjudication and Bitcoin spending
conditions have a concrete, tested design. Identity creation remains free of
any bond requirement. Names remain non-exclusive claims attached to EntityIDs.

## What Internet Identity and id.ai contribute

[Internet Identity](https://github.com/dfinity/internet-identity) and
[id.ai](https://id.ai/) are the source project and user-facing service for the
same authentication system, not two independent identity witnesses. The
repository uses a Rust backend on ICP and a TypeScript/SvelteKit frontend.
Its passkey and delegated-session patterns are useful references for reducing
onboarding friction. These are references, not a reason to replace O2A's
Rust/Axum and conventional web application plan.

The [id.ai product explanation](https://id.ai/about) emphasizes convenient
sign-in, passkeys, and separate pseudonyms per application. O2A can learn from
the separation of a simple user journey and detailed identity management.
Authentication establishes access to an account; it does not establish that
the account represents a particular recognized music artist.

The [II specification](https://docs.internetcomputer.org/references/internet-identity-spec/)
derives identities by application origin and delegates to session keys.
Therefore an II principal should not replace O2A's stable EntityID. An
optional integration must bind the authenticated application identity to an
O2A controller through explicit authorization. Login, controller changes,
public claim signing, and spending permissions remain separate actions.

[ICP verifiable credentials](https://docs.internetcomputer.org/guides/authentication/verifiable-credentials/)
separate issuer, user, identity provider, and relying party. Their alias flow
and explicit consent are useful models. Importing such credentials would
require verification of both canister-signed credentials, issuer identity,
subject linkage, origin, expiry, and the requested claim semantics. Decoding
a JWT is insufficient. An O2A adapter must either retain verifiable original
evidence and its trust roots, or clearly identify an adapter's own attestation
as an additional trust dependency. A global public artist profile must not
silently expose otherwise private application identities.

Source revision reviewed:
`2cc9efbb9e2b19af2064e365fa71ef5cb28c0b0c`. Its
[root license](https://github.com/dfinity/internet-identity/blob/2cc9efbb9e2b19af2064e365fa71ef5cb28c0b0c/LICENSE)
is the Internet Computer Community Source License v1.0, with a platform
limitation in section 3(A). Do not assume the repository can be copied into
the off-ICP Rust service. Check licenses separately for any SDK or library
selected for integration. This assessment adopts concepts and copies no code.

## What the TXT challenge actually proves

The relevant precedent is **domain-control validation**, particularly ACME
DNS-01, rather than a domain transfer. ACME binds an unpredictable challenge
to an account key and checks a corresponding DNS TXT value.
[RFC 8555, section 8.4](https://datatracker.ietf.org/doc/html/rfc8555#section-8.4).

O2A should distinguish these assertions:

| Evidence | Supported assertion | Additional evidence still needed |
| --- | --- | --- |
| Controller signature | This authorized EntityID controller signed these exact bytes. | Real-world representation and channel control. |
| DNS TXT response | Someone authorized to publish at this DNS location placed the expected token during the observation window. | The domain's connection to the artist; delegation and compromise checks. |
| HTTPS file or platform post | The token was published at the identified endpoint/account. | Authority to represent the artist; account provenance and freshness. |
| Label or ticket-service statement | That identified issuer endorses a specified artist/controller or relationship. | Issuer authentication, authority, independence, and conflict policy. |
| Confirmed bond output | Specified funds were locked under specified spending conditions. | Every identity claim above, plus the bond's actual risk and settlement rules. |

A third party publishing a token on its own site is an **endorsement**, not
proof that the artist controls that site. A user-generated ticket listing,
paid platform badge, or matching display name is not automatically a verified
issuer. Independent observers reading one domain improve observation coverage;
they do not turn one domain into several independent identity endorsements.

DNS records can be delegated and propagation can differ by location.
[Let's Encrypt's challenge guidance](https://letsencrypt.org/docs/challenge-types/)
documents both. DNSSEC, where validated, authenticates DNS data within its
trust chain; it does not certify the artist's name. HTTPS responses ordinarily
remain observations vouched for by the observer, not portable signatures by
the web publisher. Preserve this distinction in proof packages.

## Proposed flow

1. **Claim.** A music artist creates a BIP340-rooted EntityID through an RGB
   genesis anchored to Bitcoin, then signs a non-exclusive name claim.
   Representatives declare their role and authorization. Neither the first
   claimant nor the largest bond gets exclusive ownership of a name.
2. **Challenge.** Create a short-lived, single-use challenge with at least
   128 bits of cryptographic randomness. Bind it to the claim ID, EntityID,
   controller state/key, exact resource, purpose, protocol environment,
   policy hash, expiry, and verification-request ID. Each resource has its
   own challenge. The claimant signs the binding.
3. **Publication.** Put the derived public token in a DNS TXT record such as
   `_o2a-challenge.artist.example`, an HTTPS resource such as
   `https://artist.example/.well-known/o2a-proof/<challenge-id>`, or a supported
   social account's post/profile field. These are proposed O2A conventions,
   not existing standards. Prefer stable platform account IDs over handles.
4. **Observation.** Fetch through the appropriate adapter. Observers sign
   exact result records: challenge/request ID, token digest, endpoint and
   canonical account ID, observation time, expiry, response/evidence hash,
   observer identity/key, method, and failure category. Retain the referenced
   evidence bytes with an explicit disclosure and retention policy.
5. **Recognition.** Obtain separate statements linking the controller or
   channel to the artist from suitable labels, venues, promoters, or ticket
   services. Preserve issuer role, representative authority, and conflicts.
6. **Evaluation.** The Rust core verifies the EntityIDs' RGB histories,
   controller authorization, fixed evidence package, and named policy. It
   reports supported claims, missing evidence, freshness, challenges, and
   trust assumptions. It does not fetch the live Internet.
7. **Optional bond resolution.** A downstream adapter applies the agreed
   outcome to the correct funded contract. Financial settlement and identity
   evaluation remain separate records. Later compromise or revocation creates
   new evidence; it never silently rewrites the historical result.

Conceptually, the public value is
`base64url(H("o2a-control-proof-v1" || Canonical(challenge-binding)))`.
The encoding, field lengths, hash profile, and signature envelope must be
specified before implementation. Display the EntityID, purpose, and expiry
alongside posting instructions so a user can detect a phishing request.
The token is public and **must never be a spending secret or payment preimage**.

Fetching must resist SSRF, DNS rebinding, cross-origin redirects, private and
metadata IP destinations, oversized responses, and parser ambiguity. Require
valid HTTPS for the O2A HTTPS method; do not copy ACME's certificate-bootstrap
exceptions. Treat propagation delays, API throttling, removed posts, and
unavailable providers as missing evidence, not dishonesty.

## Recognition policy and the initial trust problem

A candidate high-assurance pilot policy could require a fresh channel-control
proof plus two representation/relationship endorsements from different
administrative organizations, with no unresolved applicable conflict. The
number is a hypothesis to test, not a finalized v0.1 rule. A channel's prior
association with the artist must be supported by provenance; a newly created
lookalike domain is insufficient. The same agency operating a domain, social
account, and label cannot satisfy three independent-witness slots.

The pilot needs a disclosed, versioned issuer list, manually authenticated
issuer keys, representation scope, and explicit independence/conflict records.
This is a trust bootstrap, not decentralized truth. Later communities can
choose different policies and issuer sets. No central O2A catalog becomes the
only authority, but external platforms and attestors remain dependencies for
the particular claims that rely on them.

Keep less demanding routes for emerging artists: local venue/promoter
endorsements, evidence of shared work, and an honest incomplete status while
evidence accumulates. Sponsoring someone's deposit confers no extra identity
authority. Avoid follower-count thresholds and wealth-weighted recognition.

## Bond economics and settlement

There are three separate prices: verification service fees, the opportunity
cost of temporarily locked funds, and collateral actually subject to loss.
State them independently before funding. A successful claimant receives its
deposit back subject to disclosed transaction fees; no reward is created by
the act of verification. Any reward requires a separately funded sponsor.

| Mechanism | Value | Limitation / recommendation |
| --- | --- | --- |
| Refundable verification deposit | Demonstrates funding and limits rapid reuse of the same capital while a request is pending. | Returning it on success or timeout exposes no principal to fraud loss. Start with this transparent regtest experiment. |
| Bond held through a challenge window | Can retain collateral while a claim is being relied upon. | Requires bounded deadlines, observers/adjudicators, appeal and payout rules. Release removes the economic backing; show that explicitly. |
| Forfeitable fraud bond | Could penalize proven misconduct under agreed terms. | Do not implement until misconduct, admissible evidence, authority, payout recipient, and enforceable transaction paths are specified. |

The heuristic `p × L + C > G` describes a deterrence target: `p` is the
probability of enforceable detection before release, `L` the loss actually
collectible, `C` the attack's other costs, and `G` its expected benefit.
It is not a security proof. With immediate principal refunds, `L = 0` after
release. Compromised accounts, colluding issuers, and high-value impersonation
can defeat a small bond. Fees also burden honest claimants.

For the first local experiment, model these outcomes separately:

| Evidence outcome | Identity result | Deposit outcome |
| --- | --- | --- |
| Required evidence succeeds | Supported under the named policy. | Early cooperative refund after the agreed confirmation rules. |
| Evidence missing, expired, or service unavailable | Incomplete; no positive recognition. | Claimant can refund after the fixed timeout. |
| Applicable challenge appears | Challenged/disputed under policy. | No early success path; ordinary timeout still exists. This prototype cannot confiscate funds. |
| Funding absent, insufficient, spent, or reorganized | Evaluate identity evidence independently; bond status is unsatisfied or pending. | Do not report funded or refunded until the required chain evidence exists. |

One regtest candidate is claimant-plus-verifier cooperative spending with a
claimant-only timelocked refund path. The claimant must inspect the complete
spend template and verify recovery before funding. This is a candidate
construction, not an audited script. It cannot enforce a fraud penalty without
additional transaction/signing machinery. A threshold verifier set is a later
experiment, not an assumption of this initial design.

**An application dispute cannot freeze an already valid Bitcoin refund.**
Timelocks make paths available after a boundary; they do not automatically
expire competing spend paths. A future forfeiture design must analyze refund
races, signer collusion, reorgs, transaction fees, and censorship, with a
bounded recovery path. Do not advertise automatic slashing based on a status
field in PostgreSQL.
[Bitcoin BIP 65](https://github.com/bitcoin/bips/blob/master/bip-0065.mediawiki)
provides the underlying timelock reference.

For later research, DLCs connect prespecified payouts to oracle signatures
and include refund arrangements. They still depend on oracle observations;
they do not make DNS or artist identity objective. See the
[DLC specifications](https://github.com/discreetlogcontracts/dlcspecs/blob/master/Introduction.md).
Failure to publish a token, duplicate stage names, and inaccessible APIs are
not evidence sufficient for forfeiture. Cryptographically proven misconduct
and contested real-world representation require different adjudication rules.
Bound dispute extensions and prevent an attacker from locking honest funds
indefinitely by submitting repeated challenges.

## Fit with the O2A stack

| Component | Responsibility |
| --- | --- |
| Self-custodial wallet/node | Store the seed, dedicated identity keys, controller history, RGB consignments, attestations, and proof packages; use a full Bitcoin node or an explicit light mode. |
| Rust core | BIP340 root and controller signatures, RGB identity-history validation, Bitcoin anchors, canonical challenge/evidence validation, policy, and explicit evaluation context; no hidden live DNS/HTTP calls. |
| Rust/Axum application and workers | Challenge issuance, rate limits, DNS/HTTPS/platform adapters, signed observation collection, retry and expiry handling. |
| Next.js/TypeScript or CLI | Clear publication instructions, passkey-friendly sessions, separate controller authorization, understandable evidence and refund status. |
| PostgreSQL and object storage | Rebuildable request/result projections and retained immutable evidence packages; Redis remains optional cache. |
| Optional Internet Identity adapter | Login or imported credentials after origin, authorization, privacy, signature, trust-root, and license checks. No ICP requirement in the kernel. |
| Bitcoin and RGB identity profile | Required EntityID genesis, controller rotation, recovery-policy changes, revocation, single-use seals, and client-side validation. It has no authority to interpret DNS or social facts. |
| Optional native-BTC bond adapter | Exact network/outpoint/value/script/confirmation checks, bond funding and spending, persistent intents, and restart-safe refunds. It remains separate from identity ownership. |
| Lightning / USDt swaps | Separate future service-payment or settlement routes. Neither is needed for basic channel proofs or the first BTC bond experiment. |

Bitcoin validates order, anchors, and transaction spending conditions, not
social accounts. An RGB transition validates supplied client-side identity
state against its contract and anchor; off-chain observations must still come
from explicit evidence issuers.
[RGB overview](https://rgb.info/). An RGB proof or commitment alone cannot
release a separate native-BTC output: a compatible spending construction and
authorized signatures are required. The DNS token cannot bridge that gap.

The collection layer is online and time-dependent. Portable verification is
deterministic over preserved observations, policy, issuer-state proofs, and
an explicit evaluation time/evidence boundary. It verifies who attested what;
it does not recreate an old webpage or prove no undiscovered dispute exists.
Revalidation adds a new observation rather than changing an old package.

## Implementation gates and evaluation

1. **Specification:** first freeze the Bitcoin/RGB identity profile, then
   define challenge bindings, observer and endorsement
   predicates, resource normalization, issuer bootstrap, provenance, freshness,
   disclosure, and reason codes. Keep challenge requests distinct from O2A
   dispute objects. Do not edit frozen cryptographic/wire rules by implication.
2. **Local control proof:** mock DNS/HTTPS and platform fixtures; exercise a
   recognized artist, authorized representative, and competing claimant. Two
   independent verifiers must reproduce the same result offline.
3. **Regtest deposit:** after core acceptance, test confirmed funding,
   cooperative success, unilateral timeout, crash/restart, duplicated
   callbacks, spent/wrong outpoint, substituted recipient, fees, and reorgs.
   Persist intent before transactions; never equate a broadcast with settlement.
4. **Optional authentication adapter:** separately assess II login/credential
   import and recovery. Test wrong origin, expired delegation, mismatched
   subject/alias, untrusted issuer, and outage without changing EntityID.
5. **Economic pilot:** before any forfeiture or real funds, measure legitimate
   completion time, false acceptance/rejection, recovery success, operator
   effort, fees, opportunity cost, collateral reuse, and adversarial outcomes.
   Define appeal deadlines, loss allocation, and limits before promotion.

Mandatory adversarial vectors include copied/public tokens, nonce replay,
cross-claim and cross-environment reuse, rotated/revoked keys, domain resale,
shared management, lookalike names/domains, hijacked social accounts, unsigned
screenshots, fake issuer lists, stale observations, conflicting attestations,
unavailable endpoints, and observer collusion. Malicious control of every
accepted source is a stated policy failure case, not a cryptographic guarantee.

**Decision:** this is a valuable proposed onboarding/evidence profile above
the required Bitcoin/RGB identity foundation. Prioritize proof of control and
independent recognition. Treat economic deterrence as a separate experiment;
native-BTC bonds, additional RGB rights profiles, and USDt conversion remain
distinct from the mandatory RGB identity lifecycle.
