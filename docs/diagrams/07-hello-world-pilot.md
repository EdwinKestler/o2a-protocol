# 07 — Hello-World Pilot

This is the smallest scenario that demonstrates O2A as a protocol rather than a centralized database.

```mermaid
flowchart LR
    A["Alice creates Artist EntityID A<br/>BIP340 root + RGB genesis<br/>anchored to Bitcoin"]
    SC["Alice signs self-claim<br/>'I am Artist X'"]
    V["Venue V creates<br/>Venue EntityID"]
    VA["Venue V attests<br/>'Artist A performed at Event E'"]
    P["Promoter P creates<br/>Promoter EntityID"]
    E["Promoter or venue creates<br/>Event EntityID E<br/>own key + manifest hash"]
    PA["Promoter P attests<br/>'I booked Artist A for Event E'"]
    PKG["Signed evidence package"]
    C1["Verifier Client 1"]
    C2["Verifier Client 2"]
    POL["Same Trust Policy"]
    R1["Result R"]
    R2["Result R"]

    A --> SC --> VA
    E --> VA
    E --> PA
    V --> VA
    P --> PA
    SC --> PKG
    VA --> PKG
    PA --> PKG

    PKG --> C1
    PKG --> C2
    POL --> C1
    POL --> C2
    C1 --> R1
    C2 --> R2
```

## Success condition

```text
same evidence
+ same policy
+ same protocol version
= same verification result
```

This is the primary deterministic compatibility invariant for independent implementations.
