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

from check_derivation_cross import cross_check

HERE = Path(__file__).resolve().parent
FIXTURE_PATH = HERE / "v0.1.json"
CRYPTO_MANIFEST = HERE / "crypto-checker" / "Cargo.toml"
PROTOCOL_CHECKER = HERE / "check_protocol_objects.py"
DERIVATION_FIXTURE_PATH = HERE / "derivation-v0.1.json"

ENTITY_TAG = "O2A/v0.1/entity-id"
KEY_TAG = "O2A/v0.1/key-id"
CLAIM_TAG = "O2A/v0.1/claim"
ATTESTATION_TAG = "O2A/v0.1/attestation"
PACKAGE_TAG = "O2A/v0.1/proof-package"
MAX_BYTES_LENGTH = 1_048_576
MAX_TEXT_LENGTH = 4_096
KNOWN_NETWORKS = {0, 1, 2, 3, 4}


def derivation_case_accepts(case: dict, derived: dict) -> bool:
    if case["profile_version"] != 1:
        return False
    if case["network"] != derived["network"] or case["entity"] != derived["entity"]:
        return False
    key_class = case["key_class"]
    if key_class == "payment_as_o2a":
        return False
    key = derived["keys"].get(key_class)
    if key is None:
        return False
    return case["path"] == key["path"] and case["candidate_xonly"] == key["xonly"]


def check_derivation_vectors() -> None:
    fixture = json.loads(DERIVATION_FIXTURE_PATH.read_text(encoding="utf-8"))
    if fixture["license"] != "CC0-1.0" or fixture["profile_version"] != 1:
        fail("invalid derivation fixture license or profile version")
    rows = cross_check()
    by_case = {(row["network"], row["entity"]): row for row in rows}
    if len(fixture["positives"]) != len(by_case):
        fail("derivation positive-case count mismatch")
    for expected in fixture["positives"]:
        row = by_case.get((expected["network"], expected["entity"]))
        if row is None:
            fail("missing derivation implementation result")
        normalized = dict(expected)
        normalized["bip85_path"] = fixture["bip85_path"]
        for implementation in ("python", "rust"):
            if row[implementation] != normalized:
                fail(
                    f"{implementation} derivation does not match fixture for "
                    f"{expected['network']} entity {expected['entity']}"
                )
    for case in fixture["rejections"]:
        row = by_case.get((case["network"], case["entity"]))
        if row is None:
            fail(f"rejection {case['id']} lacks a derived comparison case")
        for implementation in ("python", "rust"):
            if derivation_case_accepts(case, row[implementation]):
                fail(f"{implementation} accepted derivation rejection {case['id']}")


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
    network: int = 4,
    key_role: int = 1,
) -> bytes:
    return b"".join(
        (
            u16(1),
            bytes([network]),
            u16(object_type),
            entity,
            option(state),
            key_id,
            bytes([key_role]),
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


def crypto_xonly_valid(public_key: str) -> bool:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(CRYPTO_MANIFEST),
            "--",
            "validate-xonly",
            public_key,
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def crypto_sign_test_vector(key_name: str, message: bytes) -> tuple[str, str]:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(CRYPTO_MANIFEST),
            "--",
            "sign-public-test-vector",
            key_name,
            message.hex(),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "public test-vector signing failed")
    return tuple(result.stdout.strip().split())


def entity_id(network: int, root: bytes) -> bytes:
    if network not in KNOWN_NETWORKS:
        raise ValueError("unknown Bitcoin network")
    if not crypto_xonly_valid(root.hex()):
        raise ValueError("root is not a BIP340 x-only public key")
    return tagged_hash(ENTITY_TAG, u16(1) + bytes([network]) + root)


def build_claim(
    claim: dict,
    entity: bytes,
    state: bytes,
    key_id: bytes,
    network: int = 4,
    key_role: int = 1,
) -> bytes:
    return b"".join(
        (
            common_header(
                claim["object_type"],
                claim["capability"],
                entity,
                state,
                key_id,
                network,
                key_role,
            ),
            entity,
            text_field(claim["predicate_utf8"]),
            bytes_field(claim["object_utf8"].encode("utf-8")),
            option(None),
            bytes.fromhex(claim["nonce_hex"]),
            option(None),
            option(None),
        )
    )


class ClaimDecodeError(ValueError):
    """The bounded claim fixture is not an O2A-CANON-1 claim payload."""


def parse_claim(payload: bytes) -> dict:
    offset = 0

    def take(length: int) -> bytes:
        nonlocal offset
        end = offset + length
        if length < 0 or end > len(payload):
            raise ClaimDecodeError("truncated claim")
        value = payload[offset:end]
        offset = end
        return value

    def take_u16() -> int:
        return int.from_bytes(take(2), "little")

    def take_u32() -> int:
        return int.from_bytes(take(4), "little")

    def take_bytes(max_length: int = MAX_BYTES_LENGTH, label: str = "bytes") -> bytes:
        length = take_u32()
        if length > max_length:
            raise ClaimDecodeError(f"oversized {label} field")
        return take(length)

    def take_text() -> str:
        value = take_bytes(MAX_TEXT_LENGTH, "text")
        if b"\x00" in value:
            raise ClaimDecodeError("NUL in canonical text")
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ClaimDecodeError("invalid UTF-8") from error

    def take_optional_digest() -> bytes | None:
        present = take(1)
        if present == b"\x00":
            return None
        if present == b"\x01":
            return take(32)
        raise ClaimDecodeError("invalid option marker")

    version = take_u16()
    network = take(1)[0]
    object_type = take_u16()
    signing_entity = take(32)
    authorizing_state = take_optional_digest()
    signing_key_id = take(32)
    key_role = take(1)[0]
    capability = take_u16()
    subject = take(32)
    predicate = take_text()
    object_value = take_bytes()
    context_marker = take(1)
    if context_marker != b"\x00":
        raise ClaimDecodeError("fixture requires absent claim context")
    nonce = take(32)
    supersedes = take_optional_digest()
    checkpoint = take_optional_digest()
    if offset != len(payload):
        raise ClaimDecodeError("trailing claim bytes")
    return {
        "version": version,
        "network": network,
        "object_type": object_type,
        "signing_entity": signing_entity,
        "authorizing_state": authorizing_state,
        "signing_key_id": signing_key_id,
        "key_role": key_role,
        "capability": capability,
        "subject": subject,
        "predicate": predicate,
        "object": object_value,
        "nonce": nonce,
        "supersedes": supersedes,
        "checkpoint": checkpoint,
    }


def evaluate_name_claim(
    payload: bytes,
    signature: str,
    public_key: str,
    expected_network: int,
    authorization: dict,
) -> tuple[bool, str]:
    try:
        claim = parse_claim(payload)
    except ClaimDecodeError as error:
        return False, str(error)
    digest = tagged_hash(CLAIM_TAG, payload)
    if not crypto_verify(public_key, digest.hex(), signature):
        return False, "invalid signature"
    if claim["network"] not in KNOWN_NETWORKS or expected_network not in KNOWN_NETWORKS:
        return False, "unknown Bitcoin network"
    if claim["network"] != expected_network:
        return False, "wrong verifier network"
    if claim["version"] != 1 or claim["object_type"] != 4 or claim["capability"] != 4:
        return False, "object/domain/capability mismatch"
    if claim["key_role"] != 1:
        return False, "wrong signing-key role"
    if claim["authorizing_state"] is None:
        return False, "missing authorizing state"
    try:
        public_key_bytes = bytes.fromhex(public_key)
    except ValueError:
        return False, "invalid public key encoding"
    expected_key_id = tagged_hash(
        KEY_TAG, bytes([claim["key_role"]]) + public_key_bytes
    )
    if claim["signing_key_id"] != expected_key_id:
        return False, "signing key ID does not match role and public key"
    if claim["signing_entity"] != claim["subject"]:
        return False, "name claim is not self-issued"
    if (
        authorization.get("entity") != claim["signing_entity"].hex()
        or authorization.get("state")
        != (claim["authorizing_state"].hex() if claim["authorizing_state"] else None)
        or authorization.get("key_id") != claim["signing_key_id"].hex()
        or authorization.get("public_key") != public_key
        or authorization.get("key_role") != claim["key_role"]
        or claim["capability"] not in authorization.get("capabilities", [])
    ):
        return False, "signer is not authorized by the stated fixture state"
    return True, "accepted"


def build_manifest(
    entity: bytes,
    state: bytes,
    key_id: bytes,
    omitted_object_id: bytes | None = None,
    omission_class: int = 1,
    omission_reason: str = "private-attestation/v1",
) -> bytes:
    identity_history = content_reference(
        "application/vnd.o2a.rgb-history", 3, bytes([0x66]) * 32
    )
    bitcoin_proof = content_reference(
        "application/vnd.o2a.bitcoin-proof", 4, bytes([0x77]) * 32
    )
    evidence = content_reference(
        "application/vnd.o2a.claim", 5, bytes([0x88]) * 32
    )
    omission_id = omitted_object_id or bytes([0x99]) * 32
    if len(omission_id) != 32:
        fail("omitted object ID must be 32 bytes")
    if omission_class not in {1, 2, 3}:
        fail("invalid omission disclosure class")
    omission = omission_id + bytes([omission_class]) + text_field(omission_reason)
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
    entity = entity_id(identity["network"], root)
    if entity.hex() != identity["entity_id_hex"]:
        fail("EntityID mismatch")

    key_id = tagged_hash(KEY_TAG, bytes([identity["controller_role"]]) + bytes.fromhex(public_key))
    if key_id.hex() != identity["controller_key_id_hex"]:
        fail("controller key ID mismatch")
    state = bytes.fromhex(identity["authorizing_state_hex"])

    claim_fixture = fixture["claim"]
    claim = build_claim(claim_fixture, entity, state, key_id)
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

    semantic = fixture["semantic_claims"]
    bounds = semantic["decoder_bounds"]
    if bounds["bytes_max"] != MAX_BYTES_LENGTH or bounds["text_max"] != MAX_TEXT_LENGTH:
        fail("fixture decoder bounds do not match O2A-CANON-1")
    large_object_fixture = dict(claim_fixture)
    large_object_fixture["object_utf8"] = "A" * bounds["accepted_object_length"]
    large_object = parse_claim(build_claim(large_object_fixture, entity, state, key_id))
    if len(large_object["object"]) != bounds["accepted_object_length"]:
        fail("valid bytes field above the text limit was rejected")
    oversized_object_fixture = dict(claim_fixture)
    oversized_object_fixture["object_utf8"] = "A" * bounds["rejected_object_length"]
    try:
        parse_claim(build_claim(oversized_object_fixture, entity, state, key_id))
        fail("bytes field above the canonical maximum was accepted")
    except ClaimDecodeError as error:
        if str(error) != "oversized bytes field":
            fail(f"unexpected oversized-bytes rejection: {error}")
    predicate_bytes = text_field(claim_fixture["predicate_utf8"])
    predicate_at = claim.index(predicate_bytes)
    oversized_text = b"".join(
        (
            claim[:predicate_at],
            u32(bounds["rejected_text_length"]),
            b"A" * bounds["rejected_text_length"],
            claim[predicate_at + len(predicate_bytes) :],
        )
    )
    try:
        parse_claim(oversized_text)
        fail("text field above the canonical maximum was accepted")
    except ClaimDecodeError as error:
        if str(error) != "oversized text field":
            fail(f"unexpected oversized-text rejection: {error}")

    invalid_root = bytes.fromhex(semantic["root_validation"]["invalid_xonly_hex"])
    if crypto_xonly_valid(invalid_root.hex()):
        fail("invalid root bytes parsed as a BIP340 x-only public key")
    try:
        entity_id(semantic["expected_network"], invalid_root)
        fail("invalid root bytes were hashed into an EntityID")
    except ValueError as error:
        if str(error) != "root is not a BIP340 x-only public key":
            fail(f"unexpected invalid-root rejection: {error}")

    primary_authorization = semantic["primary_authorization"]
    accepted, reason = evaluate_name_claim(
        claim, signature, public_key, semantic["expected_network"], primary_authorization
    )
    if not accepted:
        fail(f"valid primary name claim was rejected: {reason}")

    # A caller-supplied authorization context cannot make an absent state or
    # arbitrary key ID valid; both are bound by the canonical header/profile.
    state_marker_offset = 2 + 1 + 2 + 32
    if claim[state_marker_offset] != 1:
        fail("primary claim fixture unexpectedly omits authorizing state")
    missing_state_payload = (
        claim[:state_marker_offset]
        + b"\x00"
        + claim[state_marker_offset + 33 :]
    )
    missing_state_public, missing_state_signature = crypto_sign_test_vector(
        "scalar-3", tagged_hash(CLAIM_TAG, missing_state_payload)
    )
    if missing_state_public != public_key:
        fail("missing-state signer mismatch")
    accepted, reason = evaluate_name_claim(
        missing_state_payload,
        missing_state_signature,
        public_key,
        semantic["expected_network"],
        dict(primary_authorization, state=None),
    )
    if accepted or reason != "missing authorizing state":
        fail("claim with absent authorizing state was accepted")

    key_id_start = state_marker_offset + 1 + 32
    forged_key_id = bytes([0xA5]) * 32
    arbitrary_key_id_payload = (
        claim[:key_id_start] + forged_key_id + claim[key_id_start + 32 :]
    )
    arbitrary_key_id_public, arbitrary_key_id_signature = crypto_sign_test_vector(
        "scalar-3", tagged_hash(CLAIM_TAG, arbitrary_key_id_payload)
    )
    if arbitrary_key_id_public != public_key:
        fail("arbitrary-key-ID signer mismatch")
    arbitrary_authorization = dict(
        primary_authorization, key_id=forged_key_id.hex()
    )
    accepted, reason = evaluate_name_claim(
        arbitrary_key_id_payload,
        arbitrary_key_id_signature,
        public_key,
        semantic["expected_network"],
        arbitrary_authorization,
    )
    if accepted or reason != "signing key ID does not match role and public key":
        fail("claim with arbitrary signing key ID was accepted")

    wrong_capability = semantic["wrong_capability"]
    wrong_capability_payload = bytes.fromhex(wrong_capability["payload_hex"])
    wrong_capability_digest = tagged_hash(CLAIM_TAG, wrong_capability_payload)
    if wrong_capability_digest.hex() != wrong_capability["digest_hex"]:
        fail("wrong-capability digest mismatch")
    if crypto_verify(public_key, wrong_capability_digest.hex(), signature):
        fail("original signature verified after capability mutation")
    if not crypto_verify(
        public_key, wrong_capability_digest.hex(), wrong_capability["signature_hex"]
    ):
        fail("re-signed wrong-capability claim was not cryptographically valid")
    accepted, reason = evaluate_name_claim(
        wrong_capability_payload,
        wrong_capability["signature_hex"],
        public_key,
        semantic["expected_network"],
        primary_authorization,
    )
    if accepted or reason != "object/domain/capability mismatch":
        fail("wrong capability was not rejected by semantic evaluation")

    wrong_role = semantic["wrong_role"]
    wrong_role_payload = bytes.fromhex(wrong_role["payload_hex"])
    if wrong_role_payload != build_claim(
        claim_fixture, entity, state, key_id, key_role=wrong_role["key_role"]
    ):
        fail("wrong-role payload mismatch")
    wrong_role_digest = tagged_hash(CLAIM_TAG, wrong_role_payload)
    if wrong_role_digest.hex() != wrong_role["digest_hex"]:
        fail("wrong-role digest mismatch")
    if crypto_verify(public_key, wrong_role_digest.hex(), signature):
        fail("original signature verified after key-role mutation")
    if not crypto_verify(public_key, wrong_role_digest.hex(), wrong_role["signature_hex"]):
        fail("re-signed wrong-role claim was not cryptographically valid")
    accepted, reason = evaluate_name_claim(
        wrong_role_payload,
        wrong_role["signature_hex"],
        public_key,
        semantic["expected_network"],
        primary_authorization,
    )
    if accepted or reason != "wrong signing-key role":
        fail("wrong key role was not rejected by semantic evaluation")

    wrong_network = semantic["wrong_network"]
    wrong_network_payload = bytes.fromhex(wrong_network["payload_hex"])
    wrong_network_entity = entity_id(0, root)
    if wrong_network_entity.hex() != wrong_network["entity"]:
        fail("wrong-network EntityID mismatch")
    wrong_network_digest = tagged_hash(CLAIM_TAG, wrong_network_payload)
    if wrong_network_digest.hex() != wrong_network["digest_hex"]:
        fail("wrong-network digest mismatch")
    if not crypto_verify(public_key, wrong_network_digest.hex(), wrong_network["signature_hex"]):
        fail("wrong-network claim was not independently valid")
    accepted, reason = evaluate_name_claim(
        wrong_network_payload,
        wrong_network["signature_hex"],
        public_key,
        semantic["expected_network"],
        wrong_network["authorization"],
    )
    if accepted or reason != "wrong verifier network":
        fail("wrong network was not rejected by verifier context")
    accepted, reason = evaluate_name_claim(
        wrong_network_payload,
        wrong_network["signature_hex"],
        public_key,
        wrong_network["network"],
        wrong_network["authorization"],
    )
    if not accepted:
        fail(f"well-formed alternate-network claim was rejected: {reason}")

    unknown_network = semantic["unknown_network"]
    unknown_network_payload = bytes.fromhex(unknown_network["payload_hex"])
    unknown_network_digest = tagged_hash(CLAIM_TAG, unknown_network_payload)
    if unknown_network_digest.hex() != unknown_network["digest_hex"]:
        fail("unknown-network digest mismatch")
    if not crypto_verify(
        public_key, unknown_network_digest.hex(), unknown_network["signature_hex"]
    ):
        fail("signed unknown-network claim was not cryptographically valid")
    accepted, reason = evaluate_name_claim(
        unknown_network_payload,
        unknown_network["signature_hex"],
        public_key,
        unknown_network["network"],
        primary_authorization,
    )
    if accepted or reason != "unknown Bitcoin network":
        fail("unknown network enum was accepted by matching verifier context")
    try:
        entity_id(unknown_network["network"], root)
        fail("unknown network enum was accepted for EntityID construction")
    except ValueError as error:
        if str(error) != "unknown Bitcoin network":
            fail(f"unexpected unknown-network rejection: {error}")

    competing = semantic["competing_name_claim"]
    competing_payload = bytes.fromhex(competing["payload_hex"])
    competing_entity = entity_id(
        semantic["expected_network"], bytes.fromhex(competing["root_public_test_key"])
    )
    competing_key_id = tagged_hash(
        KEY_TAG, bytes([1]) + bytes.fromhex(competing["public_key"])
    )
    if competing_entity.hex() != competing["entity"]:
        fail("competing-name EntityID mismatch")
    if competing_key_id.hex() != competing["authorization"]["key_id"]:
        fail("competing-name controller key ID mismatch")
    competing_digest = tagged_hash(CLAIM_TAG, competing_payload)
    if competing_digest.hex() != competing["digest_hex"]:
        fail("competing-name digest mismatch")
    accepted, reason = evaluate_name_claim(
        competing_payload,
        competing["signature_hex"],
        competing["public_key"],
        semantic["expected_network"],
        competing["authorization"],
    )
    if not accepted:
        fail(f"valid competing name claim was rejected: {reason}")
    parsed_primary = parse_claim(claim)
    parsed_competing = parse_claim(competing_payload)
    if parsed_primary["signing_entity"] == parsed_competing["signing_entity"]:
        fail("competing name claims resolved to one EntityID")
    if (
        parsed_primary["predicate"] != parsed_competing["predicate"]
        or parsed_primary["object"] != parsed_competing["object"]
    ):
        fail("competing claims do not contain the same name assertion")
    visible_claims = {
        parsed_primary["signing_entity"].hex(): claim_digest.hex(),
        parsed_competing["signing_entity"].hex(): competing_digest.hex(),
    }
    if visible_claims != semantic["expected_visible_claims"]:
        fail("competing name claims were merged or hidden")

    accepted, reason = evaluate_name_claim(
        claim[:-1], signature, public_key, semantic["expected_network"], primary_authorization
    )
    if accepted or reason != "truncated claim":
        fail("truncated claim was not rejected during decoding")

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

    check_derivation_vectors()

    protocol_result = subprocess.run(
        [sys.executable, str(PROTOCOL_CHECKER)],
        check=False,
        capture_output=True,
        text=True,
    )
    if protocol_result.returncode != 0:
        fail(protocol_result.stderr.strip() or "protocol-object vector checker failed")


if __name__ == "__main__":
    check()
    print("ok")
