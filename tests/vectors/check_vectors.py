# SPDX-License-Identifier: CC0-1.0
"""Check the executable O2A-CANON-1 remediation fixtures.

This tool implements bounded byte assembly and hashing only. BIP340 checks are
delegated to the pinned rust-secp256k1-backed helper in crypto-checker/.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE_PATH = HERE / "v0.1.json"
CRYPTO_MANIFEST = HERE / "crypto-checker" / "Cargo.toml"

ENTITY_TAG = "O2A/v0.1/entity-id"
KEY_TAG = "O2A/v0.1/key-id"
CLAIM_TAG = "O2A/v0.1/claim"
ATTESTATION_TAG = "O2A/v0.1/attestation"
PACKAGE_TAG = "O2A/v0.1/proof-package"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def u16(value: int) -> bytes:
    return value.to_bytes(2, "little")


def u32(value: int) -> bytes:
    return value.to_bytes(4, "little")


def u64(value: int) -> bytes:
    return value.to_bytes(8, "little")


def bytes_field(value: bytes) -> bytes:
    return u32(len(value)) + value


def text_field(value: str) -> bytes:
    encoded = value.encode("utf-8")
    if b"\x00" in encoded or len(encoded) > 4096:
        fail("invalid canonical text")
    return bytes_field(encoded)


def option(value: bytes | None) -> bytes:
    return b"\x00" if value is None else b"\x01" + value


def tagged_hash(tag: str, payload: bytes) -> bytes:
    tag_hash = hashlib.sha256(tag.encode("utf-8")).digest()
    return hashlib.sha256(tag_hash + tag_hash + payload).digest()


def content_reference(media_type: str, length: int, digest: bytes) -> bytes:
    if len(digest) != 32 or len(media_type.encode("utf-8")) > 127:
        fail("invalid content reference")
    return text_field(media_type) + u64(length) + digest


def common_header(
    object_type: int,
    capability: int,
    entity: bytes,
    state: bytes,
    key_id: bytes,
) -> bytes:
    return b"".join(
        (
            u16(1),
            bytes([4]),
            u16(object_type),
            entity,
            option(state),
            key_id,
            bytes([1]),  # controller role
            u16(capability),
        )
    )


def crypto_verify(public_key: str, message: str, signature: str) -> bool:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(CRYPTO_MANIFEST),
            "--",
            "verify",
            public_key,
            message,
            signature,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def build_claim(fixture: dict, entity: bytes, state: bytes, key_id: bytes) -> bytes:
    claim = fixture["claim"]
    return b"".join(
        (
            common_header(claim["object_type"], claim["capability"], entity, state, key_id),
            entity,
            text_field(claim["predicate_utf8"]),
            bytes_field(claim["object_utf8"].encode("utf-8")),
            option(None),
            bytes.fromhex(claim["nonce_hex"]),
            option(None),
            option(None),
        )
    )


def build_manifest(entity: bytes, state: bytes, key_id: bytes) -> bytes:
    identity_history = content_reference(
        "application/vnd.o2a.rgb-history", 3, bytes([0x66]) * 32
    )
    bitcoin_proof = content_reference(
        "application/vnd.o2a.bitcoin-proof", 4, bytes([0x77]) * 32
    )
    evidence = content_reference(
        "application/vnd.o2a.claim", 5, bytes([0x88]) * 32
    )
    omission = bytes([0x99]) * 32 + bytes([1]) + text_field("private-attestation/v1")
    policy = content_reference("application/vnd.o2a.policy", 6, bytes([0xAA]) * 32)
    context = content_reference("application/vnd.o2a.context", 7, bytes([0xBB]) * 32)
    return b"".join(
        (
            common_header(12, 12, entity, state, key_id),
            entity,
            state,
            text_field("o2a-bitcoin-rgb-v0.1"),
            bytes([0x44]) * 32,
            bytes([0x55]) * 32,
            identity_history,
            u32(1),
            bitcoin_proof,
            u32(1),
            evidence,
            u32(1),
            omission,
            policy,
            context,
            option(None),
        )
    )


def check() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    identity = fixture["identity"]
    public_key = fixture["public_test_key"]["xonly_hex"]
    root = bytes.fromhex(identity["root_xonly_hex"])
    entity = tagged_hash(ENTITY_TAG, u16(1) + bytes([identity["network"]]) + root)
    if entity.hex() != identity["entity_id_hex"]:
        fail("EntityID mismatch")

    key_id = tagged_hash(KEY_TAG, bytes([identity["controller_role"]]) + bytes.fromhex(public_key))
    if key_id.hex() != identity["controller_key_id_hex"]:
        fail("controller key ID mismatch")
    state = bytes.fromhex(identity["authorizing_state_hex"])

    claim_fixture = fixture["claim"]
    claim = build_claim(fixture, entity, state, key_id)
    if claim.hex() != claim_fixture["payload_hex"] or len(claim) != claim_fixture["payload_length"]:
        fail("claim payload mismatch")
    claim_digest = tagged_hash(CLAIM_TAG, claim)
    cross_digest = tagged_hash(ATTESTATION_TAG, claim)
    if claim_digest.hex() != claim_fixture["digest_hex"]:
        fail("claim digest mismatch")
    if cross_digest.hex() != claim_fixture["cross_domain_digest_hex"]:
        fail("cross-domain digest mismatch")
    signature = claim_fixture["signature_hex"]
    if not crypto_verify(public_key, claim_digest.hex(), signature):
        fail("rust-secp256k1 rejected the claim signature")
    if crypto_verify(public_key, cross_digest.hex(), signature):
        fail("claim signature verified in the attestation domain")
    changed = signature[:-2] + f"{int(signature[-2:], 16) ^ 0xFF:02x}"
    if crypto_verify(public_key, claim_digest.hex(), changed):
        fail("mutated claim signature verified")

    package_fixture = fixture["proof_package"]
    manifest = build_manifest(entity, state, key_id)
    if manifest.hex() != package_fixture["manifest_payload_hex"]:
        fail("proof-package manifest payload mismatch")
    if len(manifest) != package_fixture["manifest_payload_length"]:
        fail("proof-package manifest length mismatch")
    manifest_id = hashlib.sha256(manifest).digest()
    if manifest_id.hex() != package_fixture["manifest_id_hex"]:
        fail("manifest ID mismatch")
    package_message = tagged_hash(PACKAGE_TAG, manifest + manifest_id)
    if package_message.hex() != package_fixture["message_hex"]:
        fail("proof-package message mismatch")
    package_signature = bytes.fromhex(package_fixture["signature_hex"])
    if not crypto_verify(public_key, package_message.hex(), package_signature.hex()):
        fail("rust-secp256k1 rejected the package signature")
    envelope = manifest + manifest_id + package_signature
    if len(envelope) != package_fixture["signed_envelope_length"]:
        fail("signed envelope length mismatch")
    package_id = hashlib.sha256(envelope).hexdigest()
    if package_id != package_fixture["package_id_hex"]:
        fail("package ID mismatch")
    if hashlib.sha256(envelope[:-1]).hexdigest() == package_id:
        fail("truncated package retained the package ID")
    mutated = envelope[:-1] + bytes([envelope[-1] ^ 0xFF])
    if hashlib.sha256(mutated).hexdigest() == package_id:
        fail("mutated package retained the package ID")

    wrong_capability = bytearray(claim)
    capability_at = 2 + 1 + 2 + 32 + 1 + 32 + 32 + 1
    wrong_capability[capability_at : capability_at + 2] = u16(5)
    if bytes(wrong_capability) == claim:
        fail("wrong capability did not change the claim")
    if tagged_hash(CLAIM_TAG, bytes(wrong_capability)) == claim_digest:
        fail("wrong capability preserved the claim digest")

    wrong_network = bytearray(claim)
    wrong_network[2] = 0
    if tagged_hash(CLAIM_TAG, bytes(wrong_network)) == claim_digest:
        fail("wrong network preserved the claim digest")

    other_root = bytes.fromhex(public_key)
    other_entity = tagged_hash(ENTITY_TAG, u16(1) + bytes([4]) + other_root)
    if other_entity == entity:
        fail("distinct roots produced one EntityID")
    other_claim = build_claim(fixture, other_entity, state, key_id)
    if other_claim == claim:
        fail("duplicate name claims were byte-identical")
    if claim_fixture["object_utf8"].encode("utf-8") not in other_claim:
        fail("duplicate name text missing from the second claim")

    key_a = bytes([0x11]) * 32
    key_b = bytes([0x22]) * 32
    policy = b"".join(
        (
            u16(1),
            u64(1),
            u16(2),
            u32(2),
            key_a,
            key_b,
            u32(6),
            bytes([1]),
        )
    )
    policy_hash = tagged_hash("O2A/v0.1/recovery-policy", policy)
    if len(policy_hash) != 32 or policy_hash == hashlib.sha256(policy).digest():
        fail("recovery-policy hash was not domain separated")
    if policy[:2] != b"\x01\x00" or policy[-1:] != b"\x01":
        fail("recovery policy version or cancellation rule mismatch")


if __name__ == "__main__":
    check()
    print("ok")
