#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Monte Carlo evaluation of restore skip-ahead for ADR-0015 (one-shot).

Models one index sequence (an `entity'` counter or one role counter; both
follow the same allocation rule). A wallet allocates T indexes, some are
published, backups reach off-site storage with lag, then the device is lost
and the wallet restores from the off-site manifest (if any) plus a gap-limit
scan of off-site histories. The restored wallet's next index is

    next = max(manifest_next, scan_high + 1) + S

and **reuse** happens when next <= T - 1 (an index allocated before the loss
would be derived again). The simulation compares skip values S and two
allocation policies:

* `free`: allocations never wait for off-site backup;
* `cap`:  the ADR-0015 candidate invariant — never allocate an index more
  than S beyond the restorable high-water mark (the highest index covered by
  an off-site manifest or by an off-site published history). If the next
  allocation would break it, the wallet syncs off-site first.

    python3 scripts/simulate_restore_skip.py <output-dir> [scan-gap]
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

SCAN_GAP = 20
SKIPS = (0, 5, 10, 20, 50, 100, "adaptive")
ADAPTIVE = (20, 100)  # (skip after a manifest restore, skip after a scan-only restore)
TRIALS = 20_000
SEED = 20261022

SCENARIOS = {
    # p_pub: allocation is published; sync: per-allocation chance the
    # manifest and histories reach off-site storage; lost: off-site manifest
    # missing at restore; hist: a synced published history is retained.
    "typical": {"p_pub": 0.7, "sync": 0.3, "lost": 0.1, "hist": 0.95},
    "poor_backups": {"p_pub": 0.7, "sync": 0.05, "lost": 0.3, "hist": 0.7},
    "draft_bursts": {"p_pub": 0.3, "sync": 0.2, "lost": 0.2, "hist": 0.9},
    "no_manifest_ever": {"p_pub": 0.7, "sync": 0.3, "lost": 1.0, "hist": 0.95},
    # Same as above, but the manifest is kept in two independent off-site
    # copies, so it is missing only if both are lost (lost**2).
    "poor_backups_2copies": {"p_pub": 0.7, "sync": 0.05, "lost": 0.3 ** 2, "hist": 0.7},
    "draft_bursts_2copies": {"p_pub": 0.3, "sync": 0.2, "lost": 0.2 ** 2, "hist": 0.9},
}


def trial(rng: random.Random, sc: dict, skip, policy: str) -> tuple[bool, bool, int, int]:
    cap_skip, scan_skip = ADAPTIVE if skip == "adaptive" else (skip, skip)
    total = rng.randint(1, 200)
    published = []
    offsite_manifest_next = 0      # manifest entries covering [0, next)
    offsite_hist: set[int] = set()  # published histories stored off-site
    pending_hist: list[int] = []
    syncs = 0

    def sync(upto: int) -> None:
        nonlocal offsite_manifest_next, syncs
        offsite_manifest_next = upto
        for i in pending_hist:
            if rng.random() < sc["hist"]:
                offsite_hist.add(i)
        pending_hist.clear()
        syncs += 1

    for index in range(total):
        if policy == "cap":
            restorable = max(offsite_manifest_next - 1, max(offsite_hist, default=-1))
            if index > restorable + cap_skip:
                sync(index + 1)  # write-ahead manifest covering this index
        is_pub = rng.random() < sc["p_pub"]
        published.append(is_pub)
        if is_pub:
            pending_hist.append(index)
        if rng.random() < sc["sync"]:
            sync(index + 1)

    lost = rng.random() < sc["lost"]
    manifest_next = 0 if lost else offsite_manifest_next
    # Gap-limit scan over off-site histories, continuing past manifest_next.
    high, misses, i = -1, 0, 0
    while misses < SCAN_GAP or i < manifest_next:
        if i in offsite_hist:
            high, misses = i, 0
        elif i >= manifest_next:
            misses += 1
        i += 1
    nxt = max(manifest_next, high + 1) + (scan_skip if lost else cap_skip)
    last_published = max((i for i, p in enumerate(published) if p), default=-1)
    return nxt <= total - 1, nxt <= last_published, nxt - total, syncs


def run() -> dict:
    results = {}
    for name, sc in SCENARIOS.items():
        for policy in ("free", "cap"):
            for skip in SKIPS:
                rng = random.Random(f"{SEED}/{name}/{policy}/{skip}")  # deterministic per cell
                reuse = exposed = 0
                waste, syncs = [], []
                for _ in range(TRIALS):
                    r, x, w, s = trial(rng, sc, skip, policy)
                    reuse += r
                    exposed += x
                    if not r:
                        waste.append(w)
                    syncs.append(s)
                results[f"{name}/{policy}/S={skip}"] = {
                    "scenario": name, "policy": policy, "skip": skip,
                    "reuse_rate": reuse / TRIALS, "reuse_trials": reuse,
                    "published_reuse_rate": exposed / TRIALS, "published_reuse_trials": exposed,
                    "mean_waste_indexes": round(statistics.fmean(waste), 2) if waste else None,
                    "mean_offsite_syncs": round(statistics.fmean(syncs), 2),
                }
    return results


def main() -> None:
    global SCAN_GAP
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/restore-skip-simulation")
    if len(sys.argv) > 2:
        SCAN_GAP = int(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    results = run()
    (out / "results.json").write_text(json.dumps(
        {"seed": SEED, "trials": TRIALS, "scan_gap": SCAN_GAP, "scenarios": SCENARIOS,
         "results": results}, indent=2, sort_keys=True) + "\n")
    lines = ["| Escenario | Política | S | Reutilización (cualquier índice) | Reutilización (índice publicado) | Desperdicio medio | Sincronizaciones |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in results.values():
        lines.append(f"| {row['scenario']} | {row['policy']} | {row['skip']} | "
                     f"{row['reuse_rate']:.4%} ({row['reuse_trials']}) | "
                     f"{row['published_reuse_rate']:.4%} ({row['published_reuse_trials']}) | "
                     f"{row['mean_waste_indexes']} | {row['mean_offsite_syncs']} |")
    (out / "table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
