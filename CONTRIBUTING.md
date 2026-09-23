# Contributing to O2A

O2A is currently in the specification phase. Discuss protocol-rule changes
before implementation, follow [document authority](docs/DOCUMENT-AUTHORITY.md),
and keep Bitcoin spending authorization, RGB transition validity, and O2A
identity/controller authorization distinct.

## Contribution license

Except where you explicitly identify a different compatible license for
third-party material, every contribution you intentionally submit to this
repository is offered under both the MIT License and the Apache License 2.0,
at the recipient's option:

```text
MIT OR Apache-2.0
```

This is an inbound-equals-outbound policy. It does not transfer your copyright
and does not relicense third-party work. Conformance-vector contributions under
`tests/vectors/`, when that directory exists, are offered under CC0-1.0 instead
of the repository-wide dual license, as stated in that directory.

## Developer Certificate of Origin

Every new contribution commit must carry a `Signed-off-by` trailer certifying the
[Developer Certificate of Origin 1.1](https://developercertificate.org/):

```text
Signed-off-by: Your Name <you@example.com>
```

Add it with `git commit --signoff`. The sign-off states that you have the right
to submit the contribution under the repository's licenses. It is not a
copyright assignment or a contributor license agreement.

## Repository checks

Before submitting a change:

1. read `AGENTS.md` and the relevant accepted ADRs and normative specs;
2. run the repository's Palimnex status, deep validation, focused search,
   incremental reindex after edits, and evaluation workflow;
3. run `git diff --check` and the relevant site or conformance checks;
4. exclude keys, credentials, wallets, databases, build outputs, local caches,
   and private proof material; and
5. describe what was validated and what remains unproven.
