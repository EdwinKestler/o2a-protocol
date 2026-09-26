# SPDX-License-Identifier: CC0-1.0
"""Check fixed protocol-only O2A-CANON-1 signed-object fixtures.

These fixtures exercise canonical bytes, signature domains, and bounded local
authorization/evaluation rules. They do not execute RGB transitions, inspect
Bitcoin, derive wallet keys, or select a dependency stack.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from derive_route_b import CURVE_N, CURVE_P, _point_add, public_point

HERE = Path(__file__).resolve().parent
FIXTURE_PATH = HERE / "protocol-objects-v0.1.json"
SEAL_FIXTURE_PATH = HERE / "seal-script-v0.1.json"
CRYPTO_MANIFEST = HERE / "crypto-checker" / "Cargo.toml"

ENTITY_TAG = "O2A/v0.1/entity-id"
KEY_TAG = "O2A/v0.1/key-id"
POLICY_TAG = "O2A/v0.1/recovery-policy"
SEAL_INTERNAL_KEY = bytes.fromhex(
    "50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0"
)
SEAL_VECTOR_KEYS = [
    bytes.fromhex(value)
    for value in (
        "d25ed00ba7188d413f7c0ed100bb092460be1eaed2e69596c3dfc43dc43e5c06",
        "416e0730739014f342fc0247dc2aa2aab96463c7c49b56d1eaa499afe31f713e",
        "fd5b54671e58d4029cc5685038894ed2b2efde93ce9de62f25f00885346bb106",
        "6e5382b91922ab39a3995429c0a60fd2caa301c060cb9b2b428f20865e9d11d8",
        "fa1baf4a1b37fe1bb4a58770162d396934ce9ff5433599acaa61aa9fd83ca421",
        "f65fb6a087c9ac77b26ddff1f70df9a9f73bca85a3882f2f2bd4cb0df79b82da",
    )
]
AUTHORIZER_VECTOR_KEYS = [
    bytes.fromhex(value)
    for value in (
        "44eec350058c0f989cb2d1af8468aa2f1a12e99e98226cc36db446c54824374c",
        "1ae475832feb3331f8e760fcd7803a48078bb0b38f5e15b1fb52017fd8757917",
        "31e6b765372e8f0f5561a05012e4e1d803d3c7b6667793208da7e9abd5fc40d8",
        "f53704a3e4d3ddad5efb561617489c31522a0cf5a3098f5feb15f900b5ded236",
        "ff96950266bcbdc5f9131f722305116cd5e51fe9c1d9e2c1073e4fcb4618c3c6",
        "851bbbf4a54b784d635a5f07fea3a2548dcaee887d75fd744191eb37770da590",
    )
]
TAGS = {
    "entity_genesis": "O2A/v0.1/entity-genesis",
    "identity_transition": "O2A/v0.1/identity-transition",
    "recovery_authorization": "O2A/v0.1/recovery",
    "attestation": "O2A/v0.1/attestation",
    "challenge": "O2A/v0.1/challenge",
    "evidence_revocation": "O2A/v0.1/revocation",
    "control_challenge": "O2A/v0.1/control-challenge",
    "observation": "O2A/v0.1/observation",
    "discovery_binding": "O2A/v0.1/discovery-binding",
    "nostr_binding": "O2A/v0.1/discovery-binding",
    "event_manifest": "O2A/v0.1/music-manifest",
    "album_manifest": "O2A/v0.1/music-manifest",
}
OBJECTS = {
    "entity_genesis": (1, 1, 0),
    "identity_transition": (2, 2, 1),
    "recovery_authorization": (3, 3, 2),
    "attestation": (5, 5, 1),
    "challenge": (6, 6, 1),
    "evidence_revocation": (7, 7, 1),
    "control_challenge": (8, 8, 1),
    "observation": (9, 9, 1),
    "discovery_binding": (10, 10, 1),
    "nostr_binding": (10, 10, 1),
    "event_manifest": (11, 11, 1),
    "album_manifest": (11, 11, 1),
}
TYPE_SPECS = {
    object_type: (TAGS[name], capability, role)
    for name, (object_type, capability, role) in OBJECTS.items()
}
KNOWN_NETWORKS = {0, 1, 2, 3, 4}
NETWORK = 4
KNOWN_CAPABILITIES = set(range(1, 13))
ROOT_PUBLIC = bytes.fromhex(
    "f9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9"
)
CONTROLLER_PUBLIC = bytes.fromhex(
    "dff1d77f2a671c5f36183726db2341be58feae1da2deced843240f7b502ba659"
)
RECOVERY_PUBLIC = bytes.fromhex(
    "dd308afec5777e13121fa72b9cc1b7cc0139715309b086c960e18fd969774eb8"
)
ALBUM_ROOT = bytes.fromhex(
    "25d1dff95105f5253c4022f628a996ad3a0d95fbf21d468a1b33f8c160d8f517"
)
# Published BIP340 test-vector 4 public key. It is permanently unsafe fixture
# material and is distinct from every O2A identity/controller/recovery key here.
NOSTR_PUBLIC = bytes.fromhex(
    "d69c3509bb99e412e68b0fe8544e72837dfa30746d8be2aa65975f29d22dc7b9"
)
STATE = bytes([0x22]) * 32
NEXT_STATE = bytes([0x23]) * 32


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
    if not encoded or b"\x00" in encoded or len(encoded) > 4096:
        raise ValueError("invalid fixture text")
    return bytes_field(encoded)


def option(value: bytes | None) -> bytes:
    return b"\x00" if value is None else b"\x01" + value


def list_items(items: list[bytes]) -> bytes:
    return u32(len(items)) + b"".join(items)


def tagged_hash(tag: str, payload: bytes) -> bytes:
    tag_hash = hashlib.sha256(tag.encode("utf-8")).digest()
    return hashlib.sha256(tag_hash + tag_hash + payload).digest()


def compact_size(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative CompactSize")
    if value < 253:
        return bytes([value])
    if value <= 0xFFFF:
        return b"\xfd" + value.to_bytes(2, "little")
    raise ValueError("fixture CompactSize is too large")


def push_script_num(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative script number")
    if value == 0:
        return b"\x00"
    if value <= 16:
        return bytes([0x50 + value])
    data = bytearray()
    number = value
    while number:
        data.append(number & 0xFF)
        number >>= 8
    if data[-1] & 0x80:
        data.append(0)
    if len(data) > 75:
        raise ValueError("fixture script number requires PUSHDATA")
    return bytes([len(data)]) + bytes(data)


def binding_bytes(binding: tuple[bytes, bytes]) -> bytes:
    authorizing_key_id, seal_xonly = binding
    return authorizing_key_id + seal_xonly


def seal_policy(
    controller_bindings: list[tuple[bytes, bytes]],
    recovery_bindings: list[tuple[bytes, bytes]],
) -> bytes:
    return u16(1) + list_items(
        [binding_bytes(binding) for binding in controller_bindings]
    ) + list_items([binding_bytes(binding) for binding in recovery_bindings])


def recovery_leaf(recovery_keys: list[bytes], threshold: int, delay: int) -> bytes:
    script = bytearray()
    for index, public_key in enumerate(recovery_keys):
        script.extend(b"\x20" + public_key)
        script.append(0xAC if index == 0 else 0xBA)
    script.extend(push_script_num(threshold))
    script.append(0x9D)
    script.extend(push_script_num(delay))
    script.append(0xB2)
    return bytes(script)


def tapleaf_hash(script: bytes) -> bytes:
    return tagged_hash("TapLeaf", b"\xc0" + compact_size(len(script)) + script)


def taproot_root(nodes: list[bytes]) -> bytes:
    if not nodes:
        raise ValueError("empty TapTree")
    current = list(nodes)
    while len(current) > 1:
        next_round = []
        for index in range(0, len(current), 2):
            if index + 1 == len(current):
                next_round.append(current[index])
                continue
            left, right = sorted((current[index], current[index + 1]))
            next_round.append(tagged_hash("TapBranch", left + right))
        current = next_round
    return current[0]


def lift_x(x_bytes: bytes) -> tuple[int, int]:
    x = int.from_bytes(x_bytes, "big")
    if x >= CURVE_P:
        raise ValueError("x-only key exceeds field")
    y = pow((pow(x, 3, CURVE_P) + 7) % CURVE_P, (CURVE_P + 1) // 4, CURVE_P)
    if (y * y - (pow(x, 3, CURVE_P) + 7)) % CURVE_P:
        raise ValueError("x-only key is not on secp256k1")
    return x, y if y % 2 == 0 else CURVE_P - y


def seal_output(
    controller_bindings: list[tuple[bytes, bytes]],
    recovery_bindings: list[tuple[bytes, bytes]],
    threshold: int,
    delay: int,
) -> dict:
    controller_keys = sorted(seal_xonly for _, seal_xonly in controller_bindings)
    recovery_keys = sorted(seal_xonly for _, seal_xonly in recovery_bindings)
    controller_scripts = [b"\x20" + key + b"\xac" for key in controller_keys]
    recovery_script = recovery_leaf(recovery_keys, threshold, delay)
    scripts = controller_scripts + [recovery_script]
    leaf_hashes = [tapleaf_hash(script) for script in scripts]
    merkle_root = taproot_root(leaf_hashes)
    tweak = tagged_hash("TapTweak", SEAL_INTERNAL_KEY + merkle_root)
    tweak_value = int.from_bytes(tweak, "big")
    if tweak_value >= CURVE_N:
        raise ValueError("TapTweak exceeds group order")
    tweak_point = None if tweak_value == 0 else public_point(tweak_value)
    output_point = _point_add(lift_x(SEAL_INTERNAL_KEY), tweak_point)
    if output_point is None:
        raise ValueError("Taproot output point is infinity")
    output_key = output_point[0].to_bytes(32, "big")
    return {
        "policy_hex": seal_policy(controller_bindings, recovery_bindings).hex(),
        "scripts_hex": [script.hex() for script in scripts],
        "leaf_hashes": [leaf.hex() for leaf in leaf_hashes],
        "merkle_root": merkle_root.hex(),
        "output_key": output_key.hex(),
        "script_pubkey": (b"\x51\x20" + output_key).hex(),
    }


def entity_id(root: bytes) -> bytes:
    return tagged_hash(ENTITY_TAG, u16(1) + bytes([NETWORK]) + root)


def key_id(role: int, public_key: bytes) -> bytes:
    return tagged_hash(KEY_TAG, bytes([role]) + public_key)


def outpoint(marker: int, index: int) -> bytes:
    return bytes([marker]) * 32 + u32(index)


def common_header(
    object_type: int,
    capability: int,
    signer: bytes,
    authorizing_state: bytes | None,
    signer_key_id: bytes,
    role: int,
) -> bytes:
    return b"".join(
        (
            u16(1),
            bytes([NETWORK]),
            u16(object_type),
            signer,
            option(authorizing_state),
            signer_key_id,
            bytes([role]),
            u16(capability),
        )
    )


def controller(public_key: bytes, capabilities: list[int]) -> bytes:
    return b"".join(
        (
            key_id(1, public_key),
            public_key,
            b"\x01",
            list_items([u16(capability) for capability in capabilities]),
        )
    )


def recovery_policy(
    recovery_key_ids: list[bytes], delay_blocks: int = 6, sequence: int = 1
) -> bytes:
    ordered = sorted(recovery_key_ids)
    return b"".join(
        (
            u16(1),
            u64(sequence),
            u16(1),
            list_items(ordered),
            u32(delay_blocks),
            b"\x01",
        )
    )


def resulting_state(
    sequence: int,
    previous_state: bytes | None,
    previous_seal: bytes | None,
    next_seal: bytes,
    controller_public: bytes,
    policy: bytes,
    controller_seal_bindings: list[tuple[bytes, bytes]] | None = None,
    recovery_seal_bindings: list[tuple[bytes, bytes]] | None = None,
    status: int = 1,
) -> bytes:
    capabilities = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    if controller_seal_bindings is None:
        controller_seal_bindings = [
            (key_id(1, controller_public), SEAL_VECTOR_KEYS[0])
        ]
    if recovery_seal_bindings is None:
        recovery_seal_bindings = [(key_id(2, RECOVERY_PUBLIC), SEAL_VECTOR_KEYS[3])]
    return b"".join(
        (
            u64(sequence),
            option(previous_state),
            option(previous_seal),
            next_seal,
            list_items([controller(controller_public, capabilities)]),
            policy,
            seal_policy(controller_seal_bindings, recovery_seal_bindings),
            option(None),
            bytes([status]),
            option(None),
            option(None),
        )
    )


def content_reference(media_type: str, length: int, digest: bytes) -> bytes:
    return text_field(media_type) + u64(length) + digest


class DecodeError(ValueError):
    """A payload is not one exact bounded O2A-CANON-1 object."""


class Reader:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.offset = 0

    def take(self, length: int) -> bytes:
        end = self.offset + length
        if length < 0 or end > len(self.payload):
            raise DecodeError("truncated payload")
        value = self.payload[self.offset : end]
        self.offset = end
        return value

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return int.from_bytes(self.take(2), "little")

    def u32(self) -> int:
        return int.from_bytes(self.take(4), "little")

    def u64(self) -> int:
        return int.from_bytes(self.take(8), "little")

    def bytes(self, maximum: int = 1_048_576) -> bytes:
        length = self.u32()
        if length > maximum:
            raise DecodeError("oversized bytes")
        return self.take(length)

    def text(self, maximum: int = 4_096) -> str:
        value = self.bytes(maximum)
        if b"\x00" in value:
            raise DecodeError("NUL in text")
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError as error:
            raise DecodeError("invalid UTF-8") from error

    def option_fixed(self, length: int) -> bytes | None:
        marker = self.u8()
        if marker == 0:
            return None
        if marker == 1:
            return self.take(length)
        raise DecodeError("invalid option marker")

    def list(self, item):
        count = self.u32()
        if count > 4_096:
            raise DecodeError("oversized list")
        return [item() for _ in range(count)]

    def done(self) -> None:
        if self.offset != len(self.payload):
            raise DecodeError("trailing payload bytes")


def span(reader: Reader, read):
    start = reader.offset
    value = read()
    return value, (start, reader.offset)


def decode_content_reference(reader: Reader) -> dict:
    start = reader.offset
    media_type = reader.text(127)
    byte_length = reader.u64()
    content_hash = reader.take(32)
    return {
        "media_type": media_type,
        "byte_length": byte_length,
        "content_hash": content_hash,
        "canonical": reader.payload[start : reader.offset],
    }


def decode_recovery_policy(reader: Reader) -> dict:
    start = reader.offset
    policy_version = reader.u16()
    policy_sequence = reader.u64()
    threshold = reader.u16()
    recovery_key_ids = reader.list(lambda: reader.take(32))
    delay_blocks = reader.u32()
    cancellation_rule = reader.u8()
    return {
        "policy_version": policy_version,
        "policy_sequence": policy_sequence,
        "threshold": threshold,
        "recovery_key_ids": recovery_key_ids,
        "delay_blocks": delay_blocks,
        "cancellation_rule": cancellation_rule,
        "canonical": reader.payload[start : reader.offset],
    }


def decode_seal_policy(reader: Reader) -> dict:
    start = reader.offset
    policy_version = reader.u16()
    controller_seal_bindings = reader.list(
        lambda: (reader.take(32), reader.take(32))
    )
    recovery_seal_bindings = reader.list(
        lambda: (reader.take(32), reader.take(32))
    )
    return {
        "policy_version": policy_version,
        "controller_seal_bindings": controller_seal_bindings,
        "recovery_seal_bindings": recovery_seal_bindings,
        "canonical": reader.payload[start : reader.offset],
    }


def decode_controller(reader: Reader) -> dict:
    key = reader.take(32)
    public_key = reader.take(32)
    role = reader.u8()
    capabilities = reader.list(reader.u16)
    return {
        "key_id": key,
        "public_key": public_key,
        "role": role,
        "capabilities": capabilities,
    }


def decode_state(reader: Reader) -> dict:
    sequence = reader.u64()
    previous_state = reader.option_fixed(32)
    previous_seal = reader.option_fixed(36)
    next_seal = reader.take(36)
    controllers = reader.list(lambda: decode_controller(reader))
    recovery = decode_recovery_policy(reader)
    seal = decode_seal_policy(reader)
    custodian = reader.option_fixed(32)
    lifecycle_status = reader.u8()
    custody_acceptance = reader.option_fixed(32)
    profile_commitment = reader.option_fixed(32)
    return {
        "sequence": sequence,
        "previous_state": previous_state,
        "previous_seal": previous_seal,
        "next_seal": next_seal,
        "controllers": controllers,
        "recovery_policy": recovery,
        "seal_policy": seal,
        "custodian": custodian,
        "lifecycle_status": lifecycle_status,
        "custody_acceptance": custody_acceptance,
        "profile_commitment": profile_commitment,
    }


def decode_header(reader: Reader) -> tuple[dict, dict]:
    spans = {}
    version = reader.u16()
    network = reader.u8()
    object_type = reader.u16()
    signer_entity, spans["signer_entity"] = span(reader, lambda: reader.take(32))
    authorizing_state = reader.option_fixed(32)
    signing_key_id = reader.take(32)
    key_role, spans["key_role"] = span(reader, reader.u8)
    capability = reader.u16()
    return (
        {
            "version": version,
            "network": network,
            "object_type": object_type,
            "signer_entity": signer_entity,
            "authorizing_state": authorizing_state,
            "signing_key_id": signing_key_id,
            "key_role": key_role,
            "capability": capability,
        },
        spans,
    )


def decode_payload(payload: bytes) -> dict:
    reader = Reader(payload)
    header, spans = decode_header(reader)
    object_type = header["object_type"]
    body: dict
    if object_type == 1:
        entity_type = reader.u16()
        root, spans["root"] = span(reader, lambda: reader.take(32))
        body = {"entity_type": entity_type, "root": root, "state": decode_state(reader)}
    elif object_type == 2:
        operation, spans["operation"] = span(reader, reader.u8)
        body = {"operation": operation, "state": decode_state(reader)}
    elif object_type == 3:
        operation, spans["operation"] = span(reader, reader.u8)
        policy_hash, spans["policy_hash"] = span(reader, lambda: reader.take(32))
        not_before_height, spans["not_before_height"] = span(reader, reader.u32)
        body = {
            "operation": operation,
            "policy_hash": policy_hash,
            "not_before_height": not_before_height,
            "state": decode_state(reader),
        }
    elif object_type == 5:
        subject_kind = reader.u8()
        subject = reader.take(32)
        predicate = reader.text()
        object_value = reader.bytes()
        evidence = []
        evidence_spans = []
        count = reader.u32()
        if count > 4_096:
            raise DecodeError("oversized list")
        for _ in range(count):
            value, value_span = span(reader, lambda: reader.take(32))
            evidence.append(value)
            evidence_spans.append(value_span)
        spans["evidence"] = evidence_spans
        body = {
            "subject_kind": subject_kind,
            "subject": subject,
            "predicate": predicate,
            "object": object_value,
            "evidence": evidence,
            "context": reader.option_fixed(32),
            "nonce": reader.take(32),
        }
    elif object_type == 6:
        target = reader.take(32)
        reason = reader.text()
        evidence = []
        evidence_spans = []
        count = reader.u32()
        if count > 4_096:
            raise DecodeError("oversized list")
        for _ in range(count):
            value, value_span = span(reader, lambda: reader.take(32))
            evidence.append(value)
            evidence_spans.append(value_span)
        spans["evidence"] = evidence_spans
        body = {
            "target": target,
            "reason": reason,
            "evidence": evidence,
            "context": reader.option_fixed(32),
            "nonce": reader.take(32),
        }
    elif object_type == 7:
        body = {
            "target": reader.take(32),
            "reason": reader.text(),
            "context": reader.option_fixed(32),
            "nonce": reader.take(32),
        }
    elif object_type == 8:
        resource_type = reader.u8()
        resource = reader.text()
        control_purpose = reader.u16()
        nonce = reader.take(32)
        issued_at = reader.u64()
        expires_at, spans["expires_at"] = span(reader, reader.u64)
        body = {
            "resource_type": resource_type,
            "resource": resource,
            "control_purpose": control_purpose,
            "nonce": nonce,
            "issued_at": issued_at,
            "expires_at": expires_at,
            "policy_hash": reader.take(32),
        }
    elif object_type == 9:
        challenge_id = reader.take(32)
        method = reader.u8()
        observed_resource = reader.text()
        observed_value_hash = reader.take(32)
        observed_at = reader.u64()
        expires_at, spans["expires_at"] = span(reader, reader.u64)
        result = reader.u8()
        body = {
            "challenge_id": challenge_id,
            "method": method,
            "observed_resource": observed_resource,
            "observed_value_hash": observed_value_hash,
            "observed_at": observed_at,
            "expires_at": expires_at,
            "result": result,
        }
        marker_start = reader.offset
        marker = reader.u8()
        if marker == 0:
            body["transport_evidence"] = None
        elif marker == 1:
            body["transport_evidence"] = decode_content_reference(reader)
        else:
            raise DecodeError("invalid option marker")
        spans["transport_evidence"] = (marker_start, reader.offset)
    elif object_type == 10:
        adapter = reader.u8()
        key_scheme, spans["key_scheme"] = span(reader, reader.u8)
        adapter_public_key = reader.bytes()
        body = {
            "adapter": adapter,
            "key_scheme": key_scheme,
            "adapter_public_key": adapter_public_key,
            "binding_purpose": reader.u16(),
            "issued_at": reader.u64(),
            "expires_at": reader.option_fixed(8),
            "supersedes": reader.option_fixed(32),
            "nonce": reader.take(32),
        }
        if body["expires_at"] is not None:
            body["expires_at"] = int.from_bytes(body["expires_at"], "little")
    elif object_type == 11:
        manifest_kind = reader.u8()
        manifest_version = reader.u32()
        title_claim = reader.take(32)
        temporal_claims = reader.list(lambda: reader.take(32))
        place_claims = reader.list(lambda: reader.take(32))
        participants = reader.list(
            lambda: {"entity": reader.take(32), "role": reader.text()}
        )
        track_start = reader.offset
        track_manifest = reader.option_fixed(32)
        spans["track_manifest"] = (track_start, reader.offset)
        content_commitments = reader.list(lambda: decode_content_reference(reader))
        body = {
            "manifest_kind": manifest_kind,
            "manifest_version": manifest_version,
            "title_claim": title_claim,
            "temporal_claims": temporal_claims,
            "place_claims": place_claims,
            "participants": participants,
            "track_manifest": track_manifest,
            "content_commitments": content_commitments,
            "custodian": reader.take(32),
            "previous_manifest": reader.option_fixed(32),
        }
    else:
        raise DecodeError("unknown object type")
    reader.done()
    return {"header": header, "body": body, "spans": spans}


def signed_case(
    name: str,
    signer: bytes,
    state: bytes | None,
    public_key: bytes,
    body: bytes,
    sign_key: str,
    metadata: dict,
    evaluation: dict | None = None,
) -> dict:
    object_type, capability, role = OBJECTS[name]
    signer_key_id = key_id(role, public_key)
    payload = common_header(
        object_type,
        capability,
        signer,
        state,
        signer_key_id,
        role,
    ) + body
    return {
        "name": name,
        "tag": TAGS[name],
        "object_type": object_type,
        "capability": capability,
        "role": role,
        "signer": signer,
        "state": state,
        "public_key": public_key,
        "signing_key_id": signer_key_id,
        "sign_key": sign_key,
        "payload": payload,
        "metadata": metadata,
        "evaluation": evaluation or {},
        "authorization": (
            None
            if state is None
            else {
                "entity": signer,
                "state": state,
                "key_id": signer_key_id,
                "role": role,
                "capabilities": [capability],
            }
        ),
    }


def build_cases() -> list[dict]:
    root_entity = entity_id(ROOT_PUBLIC)
    event_entity = entity_id(RECOVERY_PUBLIC)
    album_entity = entity_id(ALBUM_ROOT)
    recovery_key = key_id(2, RECOVERY_PUBLIC)
    policy = recovery_policy([recovery_key])
    genesis_state = resulting_state(
        0,
        None,
        None,
        outpoint(0x11, 0),
        CONTROLLER_PUBLIC,
        policy,
    )
    transition_state = resulting_state(
        1,
        STATE,
        outpoint(0x11, 0),
        outpoint(0x12, 1),
        CONTROLLER_PUBLIC,
        policy,
    )
    recovery_state = resulting_state(
        2,
        STATE,
        outpoint(0x12, 1),
        outpoint(0x13, 2),
        CONTROLLER_PUBLIC,
        policy,
    )
    cases = [
        signed_case(
            "entity_genesis",
            root_entity,
            None,
            ROOT_PUBLIC,
            u16(2) + ROOT_PUBLIC + genesis_state,
            "scalar-3",
            {"entity_type": 2, "root": ROOT_PUBLIC.hex()},
        ),
        signed_case(
            "identity_transition",
            root_entity,
            STATE,
            CONTROLLER_PUBLIC,
            b"\x01" + transition_state,
            "bip340-vector-1",
            {"operation": 1, "sequence": 1, "previous_sequence": 0},
            {"prior_sequence": 0},
        ),
        signed_case(
            "recovery_authorization",
            root_entity,
            STATE,
            RECOVERY_PUBLIC,
            b"\x03"
            + tagged_hash(POLICY_TAG, policy)
            + u32(106)
            + recovery_state,
            "bip340-vector-2",
            {
                "operation": 3,
                "policy_hash": tagged_hash(POLICY_TAG, policy).hex(),
                "committed_policy_hash": tagged_hash(POLICY_TAG, policy).hex(),
                "recovery_key_ids": [recovery_key.hex()],
                "threshold": 1,
                "prior_anchor_height": 90,
                "seal_creation_height": 100,
                "delay_blocks": 6,
                "not_before_height": 106,
                "sequence": 2,
                "previous_sequence": 1,
            },
            {
                "prior_sequence": 1,
                "prior_policy_hash": tagged_hash(POLICY_TAG, policy),
                "prior_recovery_key_ids": [recovery_key],
                "prior_threshold": 1,
                "prior_anchor_height": 90,
                "seal_creation_height": 100,
                "delay_blocks": 6,
                "block_height": 106,
            },
        ),
    ]

    evidence_a = bytes([0x10]) * 32
    evidence_b = bytes([0x20]) * 32
    cases.extend(
        [
            signed_case(
                "attestation",
                root_entity,
                STATE,
                CONTROLLER_PUBLIC,
                b"\x01"
                + event_entity
                + text_field("o2a.example/recognized-artist/v1")
                + bytes_field(b"recognized")
                + list_items([evidence_a, evidence_b])
                + option(None)
                + bytes([0x31]) * 32,
                "bip340-vector-1",
                {"evidence": [evidence_a.hex(), evidence_b.hex()]},
            ),
            signed_case(
                "challenge",
                root_entity,
                STATE,
                CONTROLLER_PUBLIC,
                bytes([0x32]) * 32
                + text_field("o2a.example/dispute/v1")
                + list_items([evidence_a, evidence_b])
                + option(None)
                + bytes([0x33]) * 32,
                "bip340-vector-1",
                {"evidence": [evidence_a.hex(), evidence_b.hex()]},
            ),
            signed_case(
                "evidence_revocation",
                root_entity,
                STATE,
                CONTROLLER_PUBLIC,
                bytes([0x34]) * 32
                + text_field("o2a.example/withdrawn/v1")
                + option(None)
                + bytes([0x35]) * 32,
                "bip340-vector-1",
                {"target_kind": "object"},
            ),
        ]
    )

    issued_at = 1_700_000_000
    challenge_body = b"".join(
        (
            b"\x01",
            text_field("_o2a.example.test"),
            u16(1),
            bytes([0x36]) * 32,
            u64(issued_at),
            u64(issued_at + 3600),
            bytes([0x37]) * 32,
        )
    )
    control_case = signed_case(
        "control_challenge",
        root_entity,
        STATE,
        CONTROLLER_PUBLIC,
        challenge_body,
        "bip340-vector-1",
        {"issued_at": issued_at, "expires_at": issued_at + 3600},
    )
    challenge_id = tagged_hash(TAGS["control_challenge"], control_case["payload"])
    observation_body = b"".join(
        (
            challenge_id,
            b"\x01",
            text_field("_o2a.example.test"),
            bytes([0x38]) * 32,
            u64(issued_at + 100),
            u64(issued_at + 3700),
            b"\x01",
            option(None),
        )
    )
    cases.extend(
        [
            control_case,
            signed_case(
                "observation",
                root_entity,
                STATE,
                CONTROLLER_PUBLIC,
                observation_body,
                "bip340-vector-1",
                {
                    "observed_at": issued_at + 100,
                    "expires_at": issued_at + 3700,
                    "valid_evaluation_time": issued_at + 3600,
                    "expired_evaluation_time": issued_at + 3701,
                },
                {"evaluation_time": issued_at + 3600},
            ),
            signed_case(
                "discovery_binding",
                root_entity,
                STATE,
                CONTROLLER_PUBLIC,
                b"\x01"
                + b"\x01"
                + bytes_field(bytes([0x71]) * 32)
                + u16(1)
                + u64(issued_at)
                + option(u64(issued_at + 7200))
                + option(bytes([0x70]) * 32)
                + bytes([0x39]) * 32,
                "bip340-vector-1",
                {
                    "adapter": 1,
                    "key_scheme": 1,
                    "supersedes_present": True,
                },
                {"issuer_root": ROOT_PUBLIC},
            ),
            signed_case(
                "nostr_binding",
                root_entity,
                STATE,
                CONTROLLER_PUBLIC,
                b"\x02"
                + b"\x02"
                + bytes_field(NOSTR_PUBLIC)
                + u16(1)
                + u64(issued_at)
                + option(None)
                + option(bytes([0x72]) * 32)
                + bytes([0x73]) * 32,
                "bip340-vector-1",
                {
                    "adapter": 2,
                    "key_scheme": 2,
                    "supersedes_present": True,
                    "previous_binding_visible": True,
                },
                {"issuer_root": ROOT_PUBLIC},
            ),
        ]
    )

    participant_rows = sorted(
        [
            root_entity + text_field("artist/v1"),
            event_entity + text_field("venue/v1"),
        ]
    )
    event_body = b"".join(
        (
            b"\x01",
            u32(1),
            bytes([0x81]) * 32,
            list_items([bytes([0x82]) * 32]),
            list_items([bytes([0x83]) * 32]),
            list_items(participant_rows),
            option(None),
            list_items(
                [
                    content_reference(
                        "application/vnd.o2a.event+json", 128, bytes([0x84]) * 32
                    )
                ]
            ),
            root_entity,
            option(None),
        )
    )
    album_body = b"".join(
        (
            b"\x02",
            u32(1),
            bytes([0x91]) * 32,
            list_items([]),
            list_items([]),
            list_items([root_entity + text_field("artist/v1")]),
            option(bytes([0x92]) * 32),
            list_items(
                [content_reference("audio/flac", 4096, bytes([0x93]) * 32)]
            ),
            root_entity,
            option(None),
        )
    )
    cases.extend(
        [
            signed_case(
                "event_manifest",
                event_entity,
                NEXT_STATE,
                CONTROLLER_PUBLIC,
                event_body,
                "bip340-vector-1",
                {
                    "manifest_kind": 1,
                    "object_entity": event_entity.hex(),
                    "track_manifest_present": False,
                },
                {"expected_object_entity": event_entity},
            ),
            signed_case(
                "album_manifest",
                album_entity,
                bytes([0x24]) * 32,
                CONTROLLER_PUBLIC,
                album_body,
                "bip340-vector-1",
                {
                    "manifest_kind": 2,
                    "object_entity": album_entity.hex(),
                    "track_manifest_present": True,
                },
                {"expected_object_entity": album_entity},
            ),
        ]
    )
    return cases


def crypto(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(CRYPTO_MANIFEST),
            "--",
            *command,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def crypto_verify(public_key: bytes, message: bytes, signature: str) -> bool:
    return crypto(["verify", public_key.hex(), message.hex(), signature]).returncode == 0


def crypto_xonly_valid(public_key: bytes) -> bool:
    return crypto(["validate-xonly", public_key.hex()]).returncode == 0


def crypto_sign(key_name: str, message: bytes) -> tuple[str, str]:
    result = crypto(["sign-public-test-vector", key_name, message.hex()])
    if result.returncode != 0:
        fail(result.stderr.strip() or "test-vector signing failed")
    public_key, signature = result.stdout.strip().split()
    return public_key, signature


def build_seal_cases() -> dict[str, dict]:
    controller_key_ids = [key_id(1, key) for key in AUTHORIZER_VECTOR_KEYS[:3]]
    recovery_key_ids = [key_id(2, key) for key in AUTHORIZER_VECTOR_KEYS[3:6]]
    recovery_bindings = sorted(
        zip(recovery_key_ids, SEAL_VECTOR_KEYS[3:6]), key=binding_bytes
    )

    def controller_bindings(count: int) -> list[tuple[bytes, bytes]]:
        return sorted(
            zip(controller_key_ids[:count], SEAL_VECTOR_KEYS[:count]),
            key=binding_bytes,
        )

    return {
        "one_controller": {
            "policy_version": 1,
            "controller_seal_bindings": controller_bindings(1),
            "recovery_seal_bindings": recovery_bindings,
            "threshold": 2,
            "delay_blocks": 144,
        },
        "two_controllers_odd": {
            "policy_version": 1,
            "controller_seal_bindings": controller_bindings(2),
            "recovery_seal_bindings": recovery_bindings,
            "threshold": 2,
            "delay_blocks": 144,
        },
        "three_controllers": {
            "policy_version": 1,
            "controller_seal_bindings": controller_bindings(3),
            "recovery_seal_bindings": recovery_bindings,
            "threshold": 2,
            "delay_blocks": 144,
        },
    }


def rust_seal_output(case: dict) -> dict:
    result = crypto(
        [
            "seal-output",
            str(case["policy_version"]),
            str(case["threshold"]),
            str(case["delay_blocks"]),
            ",".join(
                f"{authorizing.hex()}:{seal.hex()}"
                for authorizing, seal in case["controller_seal_bindings"]
            ),
            ",".join(
                f"{authorizing.hex()}:{seal.hex()}"
                for authorizing, seal in case["recovery_seal_bindings"]
            ),
        ]
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "Rust seal-output checker failed")
    fields = dict(line.split("=", 1) for line in result.stdout.strip().splitlines())
    return {
        "policy_hex": fields["policy_hex"],
        "scripts_hex": fields["scripts_hex"].split(","),
        "leaf_hashes": fields["leaf_hashes"].split(","),
        "merkle_root": fields["merkle_root"],
        "output_key": fields["output_key"],
        "script_pubkey": fields["script_pubkey"],
    }


def fixture_seal_case(case: dict) -> dict:
    def display_bindings(bindings: list[tuple[bytes, bytes]], label: str) -> list[dict]:
        return [
            {label: authorizing.hex(), "seal_xonly": seal.hex()}
            for authorizing, seal in bindings
        ]

    return {
        "policy_version": case["policy_version"],
        "controller_seal_bindings": display_bindings(
            case["controller_seal_bindings"], "controller_key_id"
        ),
        "recovery_seal_bindings": display_bindings(
            case["recovery_seal_bindings"], "recovery_key_id"
        ),
        "threshold": case["threshold"],
        "delay_blocks": case["delay_blocks"],
        "expected": seal_output(
            case["controller_seal_bindings"],
            case["recovery_seal_bindings"],
            case["threshold"],
            case["delay_blocks"],
        ),
    }


def emit_seal_vectors() -> None:
    output = {
        "spdx": "CC0-1.0",
        "profile": "O2A seal output Draft v0.1",
        "unsafe_for_funds": True,
        "internal_key": SEAL_INTERNAL_KEY.hex(),
        "cases": {
            name: fixture_seal_case(case) for name, case in build_seal_cases().items()
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


def identity_history_outcome(
    *,
    bitcoin_view_source: str | None,
    best_block_hash: bytes | None,
    observed_height: int | None,
    seal_observation: str | None,
    spend_proof: bool,
    spend_confirmations: int,
    required_depth: int,
    valid_transition: bool,
) -> dict:
    result = {
        "bitcoin_view_source": bitcoin_view_source,
        "best_block_hash": best_block_hash,
        "observed_height": observed_height,
    }
    if (
        bitcoin_view_source is None
        or best_block_hash is None
        or observed_height is None
        or seal_observation is None
    ):
        return dict(result, state="INCOMPLETE")
    if seal_observation == "unspent":
        return dict(result, state="CURRENT")
    if (
        seal_observation != "spent"
        or not spend_proof
        or spend_confirmations < required_depth
    ):
        return dict(result, state="INCOMPLETE")
    if not valid_transition:
        return dict(result, state="SEAL_CLOSED_WITHOUT_VALID_TRANSITION")
    return dict(result, state="CURRENT")


def seal_output_matches(expected_script: bytes, actual_script: bytes) -> bool:
    return expected_script == actual_script


def check_seal_vectors() -> None:
    fixture = json.loads(SEAL_FIXTURE_PATH.read_text(encoding="utf-8"))
    if (
        fixture["spdx"] != "CC0-1.0"
        or not fixture["unsafe_for_funds"]
        or fixture["internal_key"] != SEAL_INTERNAL_KEY.hex()
    ):
        fail("invalid seal fixture metadata")
    cases = build_seal_cases()
    if set(fixture["cases"]) != set(cases):
        fail("seal fixture case set mismatch")
    for name, case in cases.items():
        expected_fixture = fixture_seal_case(case)
        if fixture["cases"][name] != expected_fixture:
            fail(f"{name}: seal fixture mismatch")
        if rust_seal_output(case) != expected_fixture["expected"]:
            fail(f"{name}: Python and Rust seal outputs differ")
        reader = Reader(bytes.fromhex(expected_fixture["expected"]["policy_hex"]))
        decoded = decode_seal_policy(reader)
        reader.done()
        if decoded["canonical"].hex() != expected_fixture["expected"]["policy_hex"]:
            fail(f"{name}: seal policy bytes were not canonical")

    base = cases["one_controller"]
    recovery_policy_value = {
        "policy_version": 1,
        "policy_sequence": 1,
        "threshold": 2,
        "recovery_key_ids": [bytes([1]) * 32, bytes([2]) * 32, bytes([3]) * 32],
        "delay_blocks": 144,
        "cancellation_rule": 1,
    }
    for delay in (0, 65_536):
        invalid = dict(recovery_policy_value, delay_blocks=delay)
        if valid_recovery_policy(invalid):
            fail(f"delay_blocks {delay} was accepted")
    if valid_recovery_policy(dict(recovery_policy_value, threshold=4)):
        fail("recovery threshold above key count was accepted")

    controller_bindings = base["controller_seal_bindings"]
    recovery_bindings = base["recovery_seal_bindings"]
    controller_ids = {authorizing for authorizing, _ in controller_bindings}
    recovery_ids = {authorizing for authorizing, _ in recovery_bindings}
    valid_policy = {
        "policy_version": 1,
        "controller_seal_bindings": controller_bindings,
        "recovery_seal_bindings": recovery_bindings,
    }
    if not valid_seal_policy(
        valid_policy,
        transition_controller_ids=controller_ids,
        recovery_key_ids=recovery_ids,
        forbidden_keys=set(),
    ):
        fail("valid seal policy rejected")
    two_controller_bindings = cases["two_controllers_odd"][
        "controller_seal_bindings"
    ]
    stale_controller = [
        (bytes([0xFF]) * 32, controller_bindings[0][1])
    ]
    duplicate_seal = list(recovery_bindings)
    duplicate_seal[1] = (duplicate_seal[1][0], duplicate_seal[0][1])
    duplicate_seal.sort(key=binding_bytes)
    rejection_cases = (
        (
            dict(valid_policy, policy_version=2),
            controller_ids,
            recovery_ids,
            "unknown seal-policy version",
        ),
        (
            dict(
                valid_policy,
                controller_seal_bindings=list(reversed(two_controller_bindings)),
            ),
            {binding[0] for binding in two_controller_bindings},
            recovery_ids,
            "unsorted controller seal bindings",
        ),
        (
            dict(
                valid_policy,
                recovery_seal_bindings=list(reversed(recovery_bindings)),
            ),
            controller_ids,
            recovery_ids,
            "unsorted recovery seal bindings",
        ),
        (
            dict(valid_policy, recovery_seal_bindings=duplicate_seal),
            controller_ids,
            recovery_ids,
            "duplicate recovery seal key",
        ),
        (
            dict(valid_policy, controller_seal_bindings=stale_controller),
            controller_ids,
            recovery_ids,
            "stale controller seal binding",
        ),
        (
            valid_policy,
            controller_ids | {bytes([0xEE]) * 32},
            recovery_ids,
            "unpaired controller key",
        ),
        (
            dict(valid_policy, recovery_seal_bindings=recovery_bindings[:2]),
            controller_ids,
            recovery_ids,
            "unpaired recovery key",
        ),
    )
    for invalid, expected_controllers, expected_recovery, label in rejection_cases:
        if valid_seal_policy(
            invalid,
            transition_controller_ids=expected_controllers,
            recovery_key_ids=expected_recovery,
            forbidden_keys=set(),
        ):
            fail(f"{label} was accepted")
    controller_seal = controller_bindings[0][1]
    if valid_seal_policy(
        valid_policy,
        transition_controller_ids=controller_ids,
        recovery_key_ids=recovery_ids,
        forbidden_keys={controller_seal},
    ):
        fail("seal key reused as controller key was accepted")
    expected_script = bytes.fromhex(
        fixture["cases"]["one_controller"]["expected"]["script_pubkey"]
    )
    mismatched_script = expected_script[:-1] + bytes([expected_script[-1] ^ 1])
    if seal_output_matches(expected_script, mismatched_script):
        fail("mismatched seal output script was accepted")
    if (
        identity_history_outcome(
            bitcoin_view_source="regtest-rpc",
            best_block_hash=bytes([0x44]) * 32,
            observed_height=120,
            seal_observation="unspent",
            spend_proof=False,
            spend_confirmations=0,
            required_depth=1,
            valid_transition=False,
        )["state"]
        != "CURRENT"
    ):
        fail("open seal was not reported current")
    if (
        identity_history_outcome(
            bitcoin_view_source=None,
            best_block_hash=None,
            observed_height=None,
            seal_observation=None,
            spend_proof=False,
            spend_confirmations=0,
            required_depth=1,
            valid_transition=False,
        )["state"]
        != "INCOMPLETE"
    ):
        fail("missing current-seal observation was not incomplete")
    if (
        identity_history_outcome(
            bitcoin_view_source="regtest-rpc",
            best_block_hash=bytes([0x44]) * 32,
            observed_height=120,
            seal_observation="spent",
            spend_proof=False,
            spend_confirmations=1,
            required_depth=1,
            valid_transition=False,
        )["state"]
        != "INCOMPLETE"
    ):
        fail("unproven seal spend was treated as terminal")
    if (
        identity_history_outcome(
            bitcoin_view_source="regtest-rpc",
            best_block_hash=bytes([0x44]) * 32,
            observed_height=120,
            seal_observation="spent",
            spend_proof=True,
            spend_confirmations=0,
            required_depth=1,
            valid_transition=False,
        )["state"]
        != "INCOMPLETE"
    ):
        fail("under-depth seal spend was treated as terminal")
    if (
        identity_history_outcome(
            bitcoin_view_source="regtest-rpc",
            best_block_hash=bytes([0x44]) * 32,
            observed_height=120,
            seal_observation="spent",
            spend_proof=True,
            spend_confirmations=1,
            required_depth=1,
            valid_transition=True,
        )["state"]
        != "CURRENT"
    ):
        fail("valid successor transition was not reported current")
    if (
        identity_history_outcome(
            bitcoin_view_source="regtest-rpc",
            best_block_hash=bytes([0x44]) * 32,
            observed_height=120,
            seal_observation="spent",
            spend_proof=True,
            spend_confirmations=1,
            required_depth=1,
            valid_transition=False,
        )["state"]
        != "SEAL_CLOSED_WITHOUT_VALID_TRANSITION"
    ):
        fail("terminal seal closure was not reported distinctly")
    if key_id(4, controller_seal) == key_id(1, controller_seal):
        fail("seal and controller key IDs were not role-bound")


def sorted_unique(values: list) -> bool:
    return values == sorted(values) and len(values) == len(set(values))


def strictly_sorted(values: list) -> bool:
    return bool(values) and sorted_unique(values)


def valid_recovery_policy(policy: dict) -> bool:
    keys = policy["recovery_key_ids"]
    return (
        policy["policy_version"] == 1
        and policy["policy_sequence"] >= 0
        and 0 < policy["threshold"] <= len(keys) <= 16
        and strictly_sorted(keys)
        and 1 <= policy["delay_blocks"] <= 65_535
        and policy["cancellation_rule"] == 1
    )


def valid_seal_policy(
    policy: dict,
    *,
    transition_controller_ids: set[bytes],
    recovery_key_ids: set[bytes],
    forbidden_keys: set[bytes],
) -> bool:
    controller_bindings = policy["controller_seal_bindings"]
    recovery_bindings = policy["recovery_seal_bindings"]
    all_bindings = controller_bindings + recovery_bindings
    controller_ids = [authorizing for authorizing, _ in controller_bindings]
    recovery_ids = [authorizing for authorizing, _ in recovery_bindings]
    all_authorizing_ids = controller_ids + recovery_ids
    all_keys = [seal_xonly for _, seal_xonly in all_bindings]
    return (
        policy["policy_version"] == 1
        and 0 < len(controller_bindings) <= 16
        and 0 < len(recovery_bindings) <= 16
        and strictly_sorted([binding_bytes(binding) for binding in controller_bindings])
        and strictly_sorted([binding_bytes(binding) for binding in recovery_bindings])
        and len(controller_ids) == len(set(controller_ids))
        and len(recovery_ids) == len(set(recovery_ids))
        and len(all_authorizing_ids) == len(set(all_authorizing_ids))
        and set(controller_ids) == transition_controller_ids
        and set(recovery_ids) == recovery_key_ids
        and len(all_keys) == len(set(all_keys))
        and not (set(all_keys) & forbidden_keys)
        and all(crypto_xonly_valid(key) for key in all_keys)
    )


def valid_state(state: dict, *, genesis: bool) -> bool:
    controllers = state["controllers"]
    controller_ids = [controller["key_id"] for controller in controllers]
    if not strictly_sorted(controller_ids):
        return False
    for controller_value in controllers:
        capabilities = controller_value["capabilities"]
        if (
            controller_value["role"] != 1
            or not crypto_xonly_valid(controller_value["public_key"])
            or controller_value["key_id"]
            != key_id(controller_value["role"], controller_value["public_key"])
            or not strictly_sorted(capabilities)
            or any(capability not in KNOWN_CAPABILITIES for capability in capabilities)
        ):
            return False
    recovery = state["recovery_policy"]
    transition_controller_ids = {
        controller_value["key_id"]
        for controller_value in controllers
        if 2 in controller_value["capabilities"]
    }
    if not valid_recovery_policy(recovery):
        return False
    if not valid_seal_policy(
        state["seal_policy"],
        transition_controller_ids=transition_controller_ids,
        recovery_key_ids=set(recovery["recovery_key_ids"]),
        forbidden_keys={controller_value["public_key"] for controller_value in controllers},
    ):
        return False
    if state["lifecycle_status"] not in {1, 2}:
        return False
    if genesis:
        return (
            state["sequence"] == 0
            and state["previous_state"] is None
            and state["previous_seal"] is None
        )
    return state["previous_state"] is not None and state["previous_seal"] is not None


def authorization_matches(header: dict, public_key: bytes, authorization: dict | None) -> bool:
    if authorization is None:
        return False
    return (
        authorization.get("entity") == header["signer_entity"]
        and authorization.get("state") == header["authorizing_state"]
        and authorization.get("key_id") == header["signing_key_id"]
        and authorization.get("role") == header["key_role"]
        and authorization.get("public_key", public_key) == public_key
        and header["capability"] in authorization.get("capabilities", [])
    )


def evaluate_signed_payload(
    payload: bytes,
    signature: str,
    public_key: bytes,
    tag: str,
    context: dict,
) -> str:
    try:
        decoded = decode_payload(payload)
    except DecodeError:
        return "invalid"
    header = decoded["header"]
    body = decoded["body"]
    if not crypto_verify(public_key, tagged_hash(tag, payload), signature):
        return "invalid"
    specification = TYPE_SPECS.get(header["object_type"])
    if specification is None:
        return "invalid"
    required_tag, required_capability, required_role = specification
    if (
        header["version"] != 1
        or header["network"] not in KNOWN_NETWORKS
        or context.get("expected_network", NETWORK) not in KNOWN_NETWORKS
        or header["network"] != context.get("expected_network", NETWORK)
        or tag != required_tag
        or header["capability"] != required_capability
        or header["key_role"] != required_role
        or header["signing_key_id"] != key_id(required_role, public_key)
    ):
        return "invalid"
    if header["object_type"] == 1:
        if header["authorizing_state"] is not None or context.get("authorization") is not None:
            return "invalid"
    elif header["authorizing_state"] is None or not authorization_matches(
        header, public_key, context.get("authorization")
    ):
        return "invalid"

    object_type = header["object_type"]
    if object_type == 1:
        return (
            "valid"
            if body["entity_type"] in set(range(1, 10))
            and crypto_xonly_valid(body["root"])
            and body["root"] == public_key
            and header["signer_entity"] == entity_id(body["root"])
            and valid_state(body["state"], genesis=True)
            and body["root"]
            not in set(
                binding[1]
                for binding in (
                    body["state"]["seal_policy"]["controller_seal_bindings"]
                    + body["state"]["seal_policy"]["recovery_seal_bindings"]
                )
            )
            else "invalid"
        )
    if object_type == 2:
        state = body["state"]
        valid = (
            # This bounded checker currently has the transition inputs needed
            # for controller rotation and revocation only. Policy changes and
            # custody transfers need additional prior-state/acceptance proofs.
            body["operation"] in {1, 5}
            and valid_state(state, genesis=False)
            and state["previous_state"] == header["authorizing_state"]
            and state["sequence"] == context.get("prior_sequence", -2) + 1
            and (body["operation"] != 5 or state["lifecycle_status"] == 2)
        )
        return "valid" if valid else "invalid"
    if object_type == 3:
        state = body["state"]
        valid = (
            body["operation"] == 3
            and valid_state(state, genesis=False)
            and state["previous_state"] == header["authorizing_state"]
            and state["sequence"] == context.get("prior_sequence", -2) + 1
            and body["policy_hash"] == context.get("prior_policy_hash")
            and key_id(2, public_key) in context.get("prior_recovery_key_ids", [])
            and 0 < context.get("prior_threshold", 0)
            and body["not_before_height"]
            == context.get("seal_creation_height", -1)
            + context.get("delay_blocks", -1)
        )
        if not valid:
            return "invalid"
        # One signed payload proves only its own signer. This bounded checker
        # does not verify a multi-signer recovery bundle, so it cannot promote
        # thresholds above one from caller-supplied counts.
        if context["prior_threshold"] > 1:
            return "incomplete"
        return (
            "valid"
            if context.get("block_height", -1) >= body["not_before_height"]
            else "too_early"
        )
    if object_type == 5:
        return (
            "valid"
            if body["subject_kind"] in {1, 2} and sorted_unique(body["evidence"])
            else "invalid"
        )
    if object_type == 6:
        return "valid" if sorted_unique(body["evidence"]) else "invalid"
    if object_type == 7:
        return (
            "invalid"
            if body["target"] in context.get("known_entity_ids", set())
            else "valid"
        )
    if object_type == 8:
        valid = (
            body["resource_type"] in {1, 2, 3, 4, 5}
            and body["control_purpose"] == 1
            and body["expires_at"] > body["issued_at"]
        )
        return "valid" if valid else "invalid"
    if object_type == 9:
        valid = (
            body["method"] in {1, 2, 3, 4, 5, 6}
            and body["result"] in {1, 2, 3, 4}
            and body["expires_at"] > body["observed_at"]
        )
        if not valid:
            return "invalid"
        evaluation_time = context.get("evaluation_time")
        if evaluation_time is None:
            return "incomplete"
        if evaluation_time < body["observed_at"]:
            return "not_yet_observed"
        return "valid" if evaluation_time <= body["expires_at"] else "expired"
    if object_type == 10:
        key_pair_valid = (body["adapter"], body["key_scheme"]) in {(1, 1), (2, 2)}
        expiry_valid = body["expires_at"] is None or body["expires_at"] > body["issued_at"]
        foreign_key_valid = (
            len(body["adapter_public_key"]) == 32
            and body["adapter_public_key"] != context.get("issuer_root")
            and (body["adapter"] != 2 or crypto_xonly_valid(body["adapter_public_key"]))
        )
        return (
            "valid"
            if key_pair_valid
            and body["binding_purpose"] == 1
            and expiry_valid
            and foreign_key_valid
            else "invalid"
        )
    if object_type == 11:
        participant_keys = [
            (participant["entity"], participant["role"].encode("utf-8"))
            for participant in body["participants"]
        ]
        content_keys = [
            (
                reference["content_hash"],
                reference["media_type"].encode("utf-8"),
                reference["byte_length"],
            )
            for reference in body["content_commitments"]
        ]
        valid = (
            body["manifest_kind"] in {1, 2}
            and header["signer_entity"] == context.get("expected_object_entity")
            and body["temporal_claims"] == sorted(set(body["temporal_claims"]))
            and body["place_claims"] == sorted(set(body["place_claims"]))
            and participant_keys == sorted(set(participant_keys))
            and content_keys == sorted(set(content_keys))
            and (body["manifest_kind"] != 2 or body["track_manifest"] is not None)
        )
        return "valid" if valid else "invalid"
    return "invalid"


def evaluation_context(case: dict, **changes: object) -> dict:
    context = dict(case["evaluation"])
    context.update(
        {
            "expected_network": NETWORK,
            "authorization": case["authorization"],
        }
    )
    context.update(changes)
    return context


def patch_span(payload: bytes, value_span: tuple[int, int], replacement: bytes) -> bytes:
    start, end = value_span
    return payload[:start] + replacement + payload[end:]


def resign_and_evaluate(
    case: dict,
    payload: bytes,
    expected: str,
    *,
    context: dict | None = None,
) -> None:
    public_key, signature = crypto_sign(case["sign_key"], tagged_hash(case["tag"], payload))
    if public_key != case["public_key"].hex():
        fail(f"{case['name']}: invalid-case signer changed")
    if not crypto_verify(case["public_key"], tagged_hash(case["tag"], payload), signature):
        fail(f"{case['name']}: re-signed invalid payload was not cryptographically valid")
    result = evaluate_signed_payload(
        payload,
        signature,
        case["public_key"],
        case["tag"],
        context or evaluation_context(case),
    )
    if result != expected:
        fail(f"{case['name']}: expected {expected}, got {result}")


def decode_package_inventory(manifest: bytes) -> tuple[set[bytes], set[bytes]]:
    reader = Reader(manifest)
    header, _ = decode_header(reader)
    if header["object_type"] != 12:
        raise DecodeError("not a proof-package manifest")
    reader.take(32)  # subject
    reader.take(32)  # subject state
    reader.text()
    reader.take(32)  # RGB contract id
    reader.take(32)  # RGB schema id
    identity_history = decode_content_reference(reader)
    bitcoin_proofs = reader.list(lambda: decode_content_reference(reader))
    evidence = reader.list(lambda: decode_content_reference(reader))
    omissions = reader.list(
        lambda: (reader.take(32), reader.u8(), reader.text(256))
    )
    policy = decode_content_reference(reader)
    evaluation = decode_content_reference(reader)
    reader.option_fixed(32)
    reader.done()
    omission_ids = [object_id for object_id, _, _ in omissions]
    if not sorted_unique(omission_ids) or any(
        disclosure_class not in {1, 2, 3}
        for _, disclosure_class, _ in omissions
    ):
        raise DecodeError("invalid omission list")
    included = {
        identity_history["content_hash"],
        policy["content_hash"],
        evaluation["content_hash"],
        *(reference["content_hash"] for reference in bitcoin_proofs),
        *(reference["content_hash"] for reference in evidence),
    }
    omitted = set(omission_ids)
    return included, omitted


def package_object_result(manifest: bytes, required_object_id: bytes) -> str:
    included, omitted = decode_package_inventory(manifest)
    if required_object_id in included:
        return "complete"
    if required_object_id in omitted:
        return "incomplete"
    return "incomplete"


def emit() -> None:
    output = {
        "spdx": "CC0-1.0",
        "profile": "O2A-CANON-1",
        "unsafe_for_funds": True,
        "scope": "protocol-only signed bytes and deterministic local evaluation; no Bitcoin or RGB execution",
        "cases": {},
    }
    for case in build_cases():
        digest = tagged_hash(case["tag"], case["payload"])
        public_key, signature = crypto_sign(case["sign_key"], digest)
        if public_key != case["public_key"].hex():
            fail(f"{case['name']}: signing helper returned the wrong public key")
        output["cases"][case["name"]] = {
            "tag": case["tag"],
            "payload_hex": case["payload"].hex(),
            "payload_length": len(case["payload"]),
            "digest_hex": digest.hex(),
            "public_key": public_key,
            "signature_hex": signature,
        }
    print(json.dumps(output, indent=2, sort_keys=True))


def check() -> None:
    check_seal_vectors()
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    cases = build_cases()
    for public_key in {
        ROOT_PUBLIC,
        CONTROLLER_PUBLIC,
        RECOVERY_PUBLIC,
        ALBUM_ROOT,
        NOSTR_PUBLIC,
    }:
        if not crypto_xonly_valid(public_key):
            fail("published protocol-object test key is not a valid x-only key")
    if set(fixture["cases"]) != {case["name"] for case in cases}:
        fail("protocol-object fixture case set mismatch")
    for case in cases:
        expected = fixture["cases"][case["name"]]
        payload = case["payload"]
        digest = tagged_hash(case["tag"], payload)
        if expected["tag"] != case["tag"]:
            fail(f"{case['name']}: tag mismatch")
        if expected["payload_hex"] != payload.hex() or expected["payload_length"] != len(payload):
            fail(f"{case['name']}: canonical payload mismatch")
        if expected["digest_hex"] != digest.hex():
            fail(f"{case['name']}: digest mismatch")
        if expected["public_key"] != case["public_key"].hex():
            fail(f"{case['name']}: signer mismatch")
        signature = expected["signature_hex"]
        if not crypto_verify(case["public_key"], digest, signature):
            fail(f"{case['name']}: valid signature rejected")
        changed = signature[:-2] + f"{int(signature[-2:], 16) ^ 0xFF:02x}"
        if crypto_verify(case["public_key"], digest, changed):
            fail(f"{case['name']}: mutated signature accepted")
        replay_tag = (
            "O2A/v0.1/attestation"
            if case["tag"] != "O2A/v0.1/attestation"
            else "O2A/v0.1/claim"
        )
        if crypto_verify(case["public_key"], tagged_hash(replay_tag, payload), signature):
            fail(f"{case['name']}: cross-domain signature accepted")
        if (
            evaluate_signed_payload(
                payload,
                signature,
                case["public_key"],
                case["tag"],
                evaluation_context(case),
            )
            != "valid"
        ):
            fail(f"{case['name']}: positive semantic case rejected")
        for malformed_payload, label in (
            (payload[:-1], "truncated"),
            (payload + b"\x00", "trailing-byte"),
        ):
            try:
                decode_payload(malformed_payload)
            except DecodeError:
                pass
            else:
                fail(f"{case['name']}: {label} payload decoded")
            if (
                evaluate_signed_payload(
                    malformed_payload,
                    signature,
                    case["public_key"],
                    case["tag"],
                    evaluation_context(case),
                )
                != "invalid"
            ):
                fail(f"{case['name']}: {label} payload was not rejected")
        if case["authorization"] is not None:
            denied_authorization = dict(case["authorization"])
            denied_authorization["capabilities"] = []
            denied_context = evaluation_context(case, authorization=denied_authorization)
            if (
                evaluate_signed_payload(
                    payload,
                    signature,
                    case["public_key"],
                    case["tag"],
                    denied_context,
                )
                != "invalid"
            ):
                fail(f"{case['name']}: missing state capability was accepted")

    by_name = {case["name"]: case for case in cases}
    transition = by_name["identity_transition"]
    genesis = by_name["entity_genesis"]
    genesis_decoded = decode_payload(genesis["payload"])
    wrong_root = patch_span(genesis["payload"], genesis_decoded["spans"]["root"], ALBUM_ROOT)
    resign_and_evaluate(genesis, wrong_root, "invalid")
    transition_decoded = decode_payload(transition["payload"])
    wrong_operation = patch_span(
        transition["payload"], transition_decoded["spans"]["operation"], b"\x03"
    )
    resign_and_evaluate(transition, wrong_operation, "invalid")
    for unsupported_operation in (2, 4):
        unsupported_transition = patch_span(
            transition["payload"],
            transition_decoded["spans"]["operation"],
            bytes([unsupported_operation]),
        )
        resign_and_evaluate(transition, unsupported_transition, "invalid")

    # Mutate a nested state capability, not the object header. Unknown
    # capability values in a validly signed state must fail closed.
    controller_capabilities = u32(10) + b"".join(
        u16(capability) for capability in [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    )
    if transition["payload"].count(controller_capabilities) != 1:
        fail("could not uniquely locate controller capability set in transition")
    unknown_state_capability = transition["payload"].replace(
        controller_capabilities,
        u32(10) + b"".join(
            u16(capability) for capability in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13]
        ),
        1,
    )
    resign_and_evaluate(transition, unknown_state_capability, "invalid")

    recovery = by_name["recovery_authorization"]
    recovery_signature = fixture["cases"]["recovery_authorization"]["signature_hex"]
    if (
        evaluate_signed_payload(
            recovery["payload"],
            recovery_signature,
            recovery["public_key"],
            recovery["tag"],
            evaluation_context(recovery, block_height=105),
        )
        != "too_early"
    ):
        fail("recovery authorization ignored not-before height")
    if (
        evaluate_signed_payload(
            recovery["payload"],
            recovery_signature,
            recovery["public_key"],
            recovery["tag"],
            evaluation_context(
                recovery,
                prior_threshold=2,
                signature_count=2,
            ),
        )
        != "incomplete"
    ):
        fail("recovery accepted a caller-supplied multi-signature count")
    recovery_decoded = decode_payload(recovery["payload"])
    wrong_policy = patch_span(
        recovery["payload"], recovery_decoded["spans"]["policy_hash"], bytes(32)
    )
    resign_and_evaluate(recovery, wrong_policy, "invalid")
    anchor_based_not_before = patch_span(
        recovery["payload"],
        recovery_decoded["spans"]["not_before_height"],
        u32(96),
    )
    resign_and_evaluate(recovery, anchor_based_not_before, "invalid")

    attestation = by_name["attestation"]
    attestation_decoded = decode_payload(attestation["payload"])
    attestation_evidence = attestation_decoded["body"]["evidence"]
    duplicate_evidence = patch_span(
        attestation["payload"],
        attestation_decoded["spans"]["evidence"][1],
        attestation_evidence[0],
    )
    resign_and_evaluate(attestation, duplicate_evidence, "invalid")

    challenge = by_name["challenge"]
    challenge_decoded = decode_payload(challenge["payload"])
    challenge_evidence = challenge_decoded["body"]["evidence"]
    first_span, second_span = challenge_decoded["spans"]["evidence"]
    reversed_evidence = (
        challenge["payload"][: first_span[0]]
        + challenge_evidence[1]
        + challenge_evidence[0]
        + challenge["payload"][second_span[1] :]
    )
    resign_and_evaluate(challenge, reversed_evidence, "invalid")

    revocation = by_name["evidence_revocation"]
    revocation_target = decode_payload(revocation["payload"])["body"]["target"]
    revocation_signature = fixture["cases"]["evidence_revocation"]["signature_hex"]
    if (
        evaluate_signed_payload(
            revocation["payload"],
            revocation_signature,
            revocation["public_key"],
            revocation["tag"],
            evaluation_context(revocation, known_entity_ids={revocation_target}),
        )
        != "invalid"
    ):
        fail("evidence revocation accepted an EntityID target")

    control = by_name["control_challenge"]
    control_decoded = decode_payload(control["payload"])
    non_increasing_expiry = patch_span(
        control["payload"],
        control_decoded["spans"]["expires_at"],
        u64(control_decoded["body"]["issued_at"]),
    )
    resign_and_evaluate(control, non_increasing_expiry, "invalid")

    observation = by_name["observation"]
    observation_body = decode_payload(observation["payload"])["body"]
    observation_signature = fixture["cases"]["observation"]["signature_hex"]
    if (
        evaluate_signed_payload(
            observation["payload"],
            observation_signature,
            observation["public_key"],
            observation["tag"],
            evaluation_context(
                observation,
                evaluation_time=observation_body["expires_at"] - 1,
            ),
        )
        != "valid"
    ):
        fail("observation rejected before explicit expiry")
    if (
        evaluate_signed_payload(
            observation["payload"],
            observation_signature,
            observation["public_key"],
            observation["tag"],
            evaluation_context(
                observation,
                evaluation_time=observation_body["observed_at"] - 1,
            ),
        )
        != "not_yet_observed"
    ):
        fail("future observation was accepted as current evidence")
    if (
        evaluate_signed_payload(
            observation["payload"],
            observation_signature,
            observation["public_key"],
            observation["tag"],
            evaluation_context(
                observation,
                evaluation_time=observation_body["expires_at"] + 1,
            ),
        )
        != "expired"
    ):
        fail("observation did not expire under explicit evaluation time")
    observation_decoded = decode_payload(observation["payload"])
    invalid_observation_window = patch_span(
        observation["payload"],
        observation_decoded["spans"]["expires_at"],
        u64(observation_decoded["body"]["observed_at"]),
    )
    resign_and_evaluate(observation, invalid_observation_window, "invalid")

    discovery = by_name["discovery_binding"]
    discovery_decoded = decode_payload(discovery["payload"])
    wrong_pubky_scheme = patch_span(
        discovery["payload"], discovery_decoded["spans"]["key_scheme"], b"\x02"
    )
    resign_and_evaluate(discovery, wrong_pubky_scheme, "invalid")
    if discovery_decoded["body"]["supersedes"] is None:
        fail("Pubky rebinding fixture omitted its signed supersedes reference")

    nostr = by_name["nostr_binding"]
    nostr_decoded = decode_payload(nostr["payload"])
    if nostr_decoded["body"]["adapter_public_key"] == ROOT_PUBLIC:
        fail("Nostr adapter key reused the issuer O2A root")
    wrong_nostr_scheme = patch_span(
        nostr["payload"], nostr_decoded["spans"]["key_scheme"], b"\x01"
    )
    resign_and_evaluate(nostr, wrong_nostr_scheme, "invalid")
    if nostr_decoded["body"]["supersedes"] is None:
        fail("Nostr rebinding fixture omitted its signed supersedes reference")

    # Build and sign a complete proof-package manifest whose canonical omission
    # entry names the required discovery object. Incompleteness is determined
    # from those signed bytes, not from detached fixture metadata.
    from check_vectors import build_manifest

    discovery_id = tagged_hash(discovery["tag"], discovery["payload"])
    package_manifest = build_manifest(
        entity_id(ROOT_PUBLIC),
        STATE,
        key_id(1, ROOT_PUBLIC),
        omitted_object_id=discovery_id,
        omission_class=3,
        omission_reason="missing-discovery-binding/v1",
    )
    package_manifest_id = hashlib.sha256(package_manifest).digest()
    package_message = tagged_hash(
        "O2A/v0.1/proof-package", package_manifest + package_manifest_id
    )
    package_public, package_signature = crypto_sign("scalar-3", package_message)
    if package_public != ROOT_PUBLIC.hex() or not crypto_verify(
        ROOT_PUBLIC, package_message, package_signature
    ):
        fail("missing-discovery package signature did not verify")
    included_ids, omitted_ids = decode_package_inventory(package_manifest)
    if discovery_id in included_ids or discovery_id not in omitted_ids:
        fail("signed package did not name the missing discovery object")
    if package_object_result(package_manifest, discovery_id) != "incomplete":
        fail("signed package omission did not produce an incomplete result")

    event = by_name["event_manifest"]
    event_decoded = decode_payload(event["payload"])
    wrong_event_entity = patch_span(
        event["payload"],
        event_decoded["spans"]["signer_entity"],
        entity_id(ALBUM_ROOT),
    )
    resign_and_evaluate(event, wrong_event_entity, "invalid")

    album = by_name["album_manifest"]
    album_decoded = decode_payload(album["payload"])
    missing_track = patch_span(
        album["payload"], album_decoded["spans"]["track_manifest"], b"\x00"
    )
    resign_and_evaluate(album, missing_track, "invalid")


if __name__ == "__main__":
    if sys.argv[1:] == ["--emit"]:
        emit()
    elif sys.argv[1:] == ["--emit-seal"]:
        emit_seal_vectors()
    elif sys.argv[1:]:
        fail("usage: check_protocol_objects.py [--emit|--emit-seal]")
    else:
        check()
        print("protocol objects ok")
