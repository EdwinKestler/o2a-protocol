#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Offline checks for the proposed O2A RGB program v0.1 vector (ADR-0012).

Python cannot recompute an RGB schema id; the Rust `program-dump` in the
demo repository does. This checker pins the strict bytes by SHA-256 and
length, checks the declared type numbers and names inside those bytes, and
checks the O2A operation/transition-type/domain mapping.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_SCHEMA_SHA256 = "ee097382b2de46bfd406d63fd7114cffe368ecea0ab747412540fb0596d9536e"
EXPECTED_SCHEMA_ID = "rgb:sch:0c4GOQpl9wgzWtkBQqf4ULj~1Xp~TkJj0Ger~0CLB6A#subway-october-region"
DOMAINS = {8101: "O2A/v0.1/identity-transition", 8102: "O2A/v0.1/recovery"}


def fail(message: str) -> None:
    print(f"rgb program check failed: {message}", file=sys.stderr)
    sys.exit(1)


def pairing_valid(operation: int, transition_type: int) -> bool:
    if operation == 3:
        return transition_type == 8102
    if operation in (1, 2, 4, 5):
        return transition_type == 8101
    return False


def main() -> None:
    data = json.loads((HERE / "rgb-program-v0.1.json").read_text())
    program = data["program"]
    raw = bytes.fromhex(program["schema_strict_hex"])
    if len(raw) != program["schema_strict_len"]:
        fail("schema length")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != program["schema_strict_sha256"] or digest != EXPECTED_SCHEMA_SHA256:
        fail("schema bytes digest")
    if program["schema_id"] != EXPECTED_SCHEMA_ID:
        fail("schema id")
    if program["schema_id"] == data["superseded_demo_schema_id"]:
        fail("program must differ from the demo schema")
    for name in (b"O2aIdentityV01", b"genesisDigest", b"transitionDigest", b"identity",
                 b"transition", b"recover"):
        if name not in raw:
            fail(f"name {name!r} missing from schema bytes")
    for name in (b"rotate", b"revoke"):
        if name in raw:
            fail(f"demo transition {name!r} present")
    for number in (3101, 3102, 4101, 8101, 8102):
        if number.to_bytes(2, "little") not in raw:
            fail(f"type {number} missing from schema bytes")
    if program["validators"] != "none" or program["close_method"] != "opret1st":
        fail("validators or close method")
    seen = set()
    for row in data["operation_mapping"]:
        op, ty = row["operation"], row["transition_type"]
        if not pairing_valid(op, ty) or DOMAINS[ty] != row["domain"]:
            fail(f"mapping row {row}")
        seen.add(op)
    if seen != {1, 2, 3, 4, 5}:
        fail("mapping must cover operations 1..5 exactly")
    for row in data["rejected_pairings"]:
        if pairing_valid(row["operation"], row["transition_type"]):
            fail(f"rejected pairing accepted {row}")
    print("rgb program ok")


if __name__ == "__main__":
    main()
