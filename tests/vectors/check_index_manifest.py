#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Proposed restore/discovery vectors for entity and role indexes (ADR-0015).

Covers the authenticated index manifest (primary) and the bounded gap-limit
scan (fallback, gap 100), including the restore skip-ahead that prevents
index reuse (20 after a manifest restore, 100 after a scan-only restore).
Uses the permanently unsafe Route B test seed.

    python3 tests/vectors/check_index_manifest.py          # check
    python3 tests/vectors/check_index_manifest.py --emit   # regenerate
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from derive_route_b import (  # noqa: E402
    O2A_INDEX,
    UNSAFE_SEED_HEX,
    bip32_master,
    bip85_xprv,
    compressed_pub,
    derive_path,
    hardened,
    xonly_pub,
)
from check_protocol_objects import list_items, option, tagged_hash, u16, u32, u64  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "index-manifest-v0.1.json"
SCAN_GAP = 100        # consecutive misses before a scan stops
SKIP_MANIFEST = 20    # skip-ahead after a restore with a verified manifest
SKIP_SCAN_ONLY = 100  # skip-ahead after a scan-only restore
ROLES = (1, 2, 3, 4)
RESERVED, PUBLISHED, ABANDONED = 1, 2, 3
NETWORK_COIN = {0: 0, 1: 1, 2: 1, 3: 1, 4: 1}


class Reject(Exception):
    pass


def o2a_root():
    return bip85_xprv(bip32_master(bytes.fromhex(UNSAFE_SEED_HEX)), O2A_INDEX)


def wallet_tag(root) -> bytes:
    return tagged_hash("O2A/v0.1/index-manifest-wallet", compressed_pub(root.secret))


def mac_key(root) -> bytes:
    return tagged_hash("O2A/v0.1/index-manifest-key",
                       root.secret.to_bytes(32, "big") + root.chain_code)


def entry(index: int, state: int, entity: bytes | None, next_indexes: tuple) -> bytes:
    return u32(index) + bytes([state]) + option(entity) + b"".join(u32(n) for n in next_indexes)


def manifest(network: int, tag: bytes, sequence: int, entries: list[bytes]) -> bytes:
    return u16(1) + bytes([network]) + tag + u64(sequence) + list_items(entries)


def seal(root, body: bytes) -> bytes:
    digest = tagged_hash("O2A/v0.1/index-manifest", body)
    return body + hmac.new(mac_key(root), digest, hashlib.sha256).digest()


def parse(blob: bytes, root, network: int) -> dict:
    if len(blob) < 32:
        raise Reject("TRUNCATED")
    body, mac = blob[:-32], blob[-32:]
    expected = hmac.new(mac_key(root), tagged_hash("O2A/v0.1/index-manifest", body),
                        hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise Reject("MAC")
    pos = 0

    def take(n: int) -> bytes:
        nonlocal pos
        if pos + n > len(body):
            raise Reject("TRUNCATED")
        pos += n
        return body[pos - n:pos]

    if int.from_bytes(take(2), "little") != 1:
        raise Reject("VERSION")
    if take(1)[0] != network:
        raise Reject("WRONG_NETWORK")
    if take(32) != wallet_tag(root):
        raise Reject("WRONG_WALLET")
    sequence = int.from_bytes(take(8), "little")
    count = int.from_bytes(take(4), "little")
    entries, last = [], -1
    for _ in range(count):
        index = int.from_bytes(take(4), "little")
        if index >= 2**31 or index <= last:
            raise Reject("ENTRIES_NOT_STRICTLY_INCREASING")
        last = index
        state = take(1)[0]
        marker = take(1)[0]
        if marker not in (0, 1):
            raise Reject("OPTION_MARKER")
        entity = take(32) if marker else None
        if state not in (RESERVED, PUBLISHED, ABANDONED):
            raise Reject("UNKNOWN_STATE")
        if (state == PUBLISHED) != (entity is not None):
            raise Reject("ENTITY_ID_PRESENCE")
        nexts = tuple(int.from_bytes(take(4), "little") for _ in ROLES)
        if any(n >= 2**31 for n in nexts):
            raise Reject("INDEX_RANGE")
        entries.append({"index": index, "state": state, "entity": entity, "next": nexts})
    if pos != len(body):
        raise Reject("TRAILING_BYTES")
    return {"sequence": sequence, "entries": entries}


_KEY_CACHE: dict = {}


def role_key(root, coin: int, entity: int, role: int, index: int) -> str:
    cache_key = (root.encode(), coin, entity, role, index)
    if cache_key not in _KEY_CACHE:
        path = [hardened(coin), hardened(entity), hardened(role), hardened(index)]
        _KEY_CACHE[cache_key] = xonly_pub(derive_path(root, path).secret)
    return _KEY_CACHE[cache_key]


def scan(root, coin: int, sources: list[dict], start_high: int = -1) -> dict:
    """Gap-limit scan: sources are verified genesis/history records.

    Each source record gives the root x-only key and every x-only key that
    appears in any valid state of that history, by role.
    """
    found, misses, index, high = {}, 0, 0, start_high
    roots = {s["root_xonly"]: s for s in sources}
    while misses < SCAN_GAP or index <= high:
        key = role_key(root, coin, index, 0, 0)
        if key in roots:
            found[index] = roots[key]
            high = max(high, index)
            misses = 0
        elif index > high:
            misses += 1
        index += 1
    roles = {}
    for e, record in found.items():
        nexts = []
        for role in ROLES:
            seen, top, i = set(record["keys"].get(str(role), [])), -1, 0
            while i <= top + SCAN_GAP:
                if role_key(root, coin, e, role, i) in seen:
                    top = i
                i += 1
            nexts.append(top + 1)
        roles[e] = tuple(nexts)
    return {"high": high, "found": sorted(found), "role_next": roles}


def restore(root, network: int, blobs: list[bytes], sources: list[dict]) -> dict:
    coin = NETWORK_COIN[network]
    good, rejected = [], []
    for blob in blobs:
        try:
            good.append(parse(blob, root, network))
        except Reject as error:
            rejected.append(str(error))
    status = "MANIFEST" if good else "SCAN_ONLY"
    manifest_next_entity, manifest_roles, conflict = 0, {}, False
    if good:
        top = max(m["sequence"] for m in good)
        tops = [m for m in good if m["sequence"] == top]
        conflict = len({json.dumps(m, default=lambda b: b.hex(), sort_keys=True) for m in tops}) > 1
        for m in tops:  # equal-sequence conflict: merge by maximum
            for e in m["entries"]:
                manifest_next_entity = max(manifest_next_entity, e["index"] + 1)
                prev = manifest_roles.get(e["index"], (0, 0, 0, 0))
                manifest_roles[e["index"]] = tuple(max(a, b) for a, b in zip(prev, e["next"]))
    scanned = scan(root, coin, sources, manifest_next_entity - 1)
    # Restore skip-ahead: a restored wallet cannot know whether its newest
    # manifest is the last one written, so every next index moves past it
    # (20 after a manifest restore, 100 after a scan-only restore; see the
    # 2026-10-22 restore-skip simulation).
    skip = SKIP_MANIFEST if good else SKIP_SCAN_ONLY
    next_entity = max(manifest_next_entity, scanned["high"] + 1) + skip
    role_next = {}
    for e in sorted(set(manifest_roles) | set(scanned["role_next"])):
        m = manifest_roles.get(e, (0, 0, 0, 0))
        s = scanned["role_next"].get(e, (0, 0, 0, 0))
        role_next[e] = [max(a, b) + skip for a, b in zip(m, s)]
    published = {e["index"] for m in good for e in m["entries"] if e["state"] == PUBLISHED}
    missing = sorted(published - set(scanned["found"]))
    return {"status": "CONFLICT_MERGED" if conflict else status, "rejected": rejected,
            "next_entity": next_entity, "role_next": {str(k): v for k, v in role_next.items()},
            "history_missing": missing, "found": scanned["found"]}


def build() -> dict:
    root = o2a_root()
    tag = wallet_tag(root)
    coin = 1
    network = 4

    def source(e: int, max_index: dict) -> dict:
        return {"root_xonly": role_key(root, coin, e, 0, 0),
                "keys": {str(r): [role_key(root, coin, e, r, i) for i in range(n + 1)]
                         for r, n in max_index.items()}}

    eid0, eid3 = tagged_hash("fixture/entity", b"\x00"), tagged_hash("fixture/entity", b"\x03")
    entries = [entry(0, PUBLISHED, eid0, (3, 1, 1, 4)), entry(1, ABANDONED, None, (1, 1, 0, 1)),
               entry(2, RESERVED, None, (1, 1, 0, 1)), entry(3, PUBLISHED, eid3, (1, 1, 0, 1))]
    v2 = seal(root, manifest(network, tag, 2, entries))
    v1 = seal(root, manifest(network, tag, 1, entries[:2]))
    sources = [source(0, {1: 2, 2: 0, 4: 3}), source(3, {1: 0, 2: 0, 4: 0})]
    flip = bytearray(v2)
    flip[60] ^= 1
    dropped = manifest(network, tag, 2, entries[:3]) + v2[-32:]  # entry removed, old MAC
    cases = {
        "manifest_latest_wins": (restore(root, network, [v1, v2], sources), None),
        "rollback_only_old_manifest": (restore(root, network, [v1], sources), None),
        "scan_only_skip_ahead": (restore(root, network, [], sources), None),
        "scan_only_history_gap": (restore(root, network, [], [sources[0]]), None),
        "manifest_without_history": (restore(root, network, [v2], [sources[0]]), None),
        "tampered_byte": (None, reject_code(bytes(flip), root, network)),
        "entry_dropped": (None, reject_code(dropped, root, network)),
        "wrong_network": (None, reject_code(seal(root, manifest(3, tag, 2, entries)), root, network)),
        "unsorted_entries": (None, reject_code(seal(root, manifest(network, tag, 2,
                                                                    [entries[1], entries[0]])), root, network)),
        "published_without_entity": (None, reject_code(seal(root, manifest(network, tag, 2,
                                     [entry(0, PUBLISHED, None, (1, 1, 1, 1))])), root, network)),
        "foreign_wallet": (None, reject_code(seal(root, manifest(network, bytes(32), 2, entries)),
                                             root, network)),
    }
    return {
        "spdx": "CC0-1.0",
        "status": "proposed (ADR-0015); not frozen until accepted",
        "unsafe_for_funds": True,
        "scan_gap": SCAN_GAP,
        "skip_after_manifest": SKIP_MANIFEST,
        "skip_after_scan_only": SKIP_SCAN_ONLY,
        "wallet_tag": tag.hex(),
        "mac_key": mac_key(root).hex(),
        "manifest_v2_hex": v2.hex(),
        "manifest_v1_hex": v1.hex(),
        "cases": {k: ({"restore": r} if r is not None else {"reject": c}) for k, (r, c) in cases.items()},
    }


def reject_code(blob: bytes, root, network: int) -> str:
    try:
        parse(blob, root, network)
    except Reject as error:
        return str(error)
    return "ACCEPT"


EXPECTED = {
    "manifest_latest_wins": {"status": "MANIFEST", "next_entity": 24, "history_missing": [],
                             "role_next": {"0": [23, 21, 21, 24], "1": [21, 21, 20, 21],
                                           "2": [21, 21, 20, 21], "3": [21, 21, 20, 21]}},
    "rollback_only_old_manifest": {"status": "MANIFEST", "next_entity": 24, "history_missing": []},
    "scan_only_skip_ahead": {"status": "SCAN_ONLY", "next_entity": 104, "history_missing": [],
                             "role_next": {"0": [103, 101, 100, 104], "3": [101, 101, 100, 101]}},
    "scan_only_history_gap": {"status": "SCAN_ONLY", "next_entity": 101, "history_missing": []},
    "manifest_without_history": {"status": "MANIFEST", "next_entity": 24, "history_missing": [3]},
    "tampered_byte": "MAC", "entry_dropped": "MAC", "wrong_network": "WRONG_NETWORK",
    "unsorted_entries": "ENTRIES_NOT_STRICTLY_INCREASING",
    "published_without_entity": "ENTITY_ID_PRESENCE", "foreign_wallet": "WRONG_WALLET",
}


def main() -> None:
    data = build()
    if "--emit" in sys.argv:
        FIXTURE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(f"wrote {FIXTURE.name}")
        return
    if json.loads(FIXTURE.read_text()) != json.loads(json.dumps(data, sort_keys=True)):
        print("index manifest: regenerated vectors differ from fixture", file=sys.stderr)
        sys.exit(1)
    for name, want in EXPECTED.items():
        got = data["cases"][name]
        if isinstance(want, str):
            ok = got.get("reject") == want
        else:
            ok = all(got["restore"][k] == v for k, v in want.items())
        if not ok:
            print(f"index manifest case {name}: want {want} got {got}", file=sys.stderr)
            sys.exit(1)
    print(f"index manifest: {len(EXPECTED)}/{len(EXPECTED)} restore and reject cases as expected")


if __name__ == "__main__":
    main()
