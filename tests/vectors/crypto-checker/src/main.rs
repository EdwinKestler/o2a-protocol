// SPDX-License-Identifier: CC0-1.0

use secp256k1::{schnorr::Signature, Keypair, Message, Secp256k1, SecretKey, XOnlyPublicKey};
use std::{env, process::ExitCode, str::FromStr};

fn decode_32(value: &str, label: &str) -> Result<[u8; 32], String> {
    let bytes = hex::decode(value).map_err(|error| format!("invalid {label} hex: {error}"))?;
    bytes
        .try_into()
        .map_err(|_| format!("{label} must be 32 bytes"))
}

fn verify(public_key: &str, message: &str, signature: &str) -> Result<(), String> {
    let public_key = XOnlyPublicKey::from_str(public_key)
        .map_err(|error| format!("invalid x-only public key: {error}"))?;
    let message = Message::from_digest(decode_32(message, "message")?);
    let signature = Signature::from_str(signature)
        .map_err(|error| format!("invalid Schnorr signature: {error}"))?;
    Secp256k1::verification_only()
        .verify_schnorr(&signature, &message, &public_key)
        .map_err(|error| format!("BIP340 verification failed: {error}"))
}

fn validate_xonly(public_key: &str) -> Result<(), String> {
    XOnlyPublicKey::from_str(public_key)
        .map(|_| ())
        .map_err(|error| format!("invalid x-only public key: {error}"))
}

fn sign_test_vector(key_name: &str, message: &str) -> Result<(), String> {
    // Published BIP340 test-vector keys only. They are permanently unsafe for
    // funds. This command exists only to regenerate CC0 fixtures; the verifier
    // path never loads a secret.
    let scalar = match key_name {
        "scalar-3" => {
            let mut scalar = [0u8; 32];
            scalar[31] = 3;
            scalar
        }
        "bip340-vector-1" => decode_32(
            "b7e151628aed2a6abf7158809cf4f3c762e7160f38b4da56a784d9045190cfef",
            "published test secret",
        )?,
        "bip340-vector-2" => decode_32(
            "c90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b14e5c9",
            "published test secret",
        )?,
        _ => return Err("unknown public test-vector key".to_owned()),
    };
    let secret = SecretKey::from_slice(&scalar)
        .map_err(|error| format!("invalid public test secret: {error}"))?;
    let secp = Secp256k1::new();
    let keypair = Keypair::from_secret_key(&secp, &secret);
    let message = Message::from_digest(decode_32(message, "message")?);
    let signature = secp.sign_schnorr_no_aux_rand(&message, &keypair);
    let (public_key, _) = XOnlyPublicKey::from_keypair(&keypair);
    println!("{} {}", public_key, signature);
    Ok(())
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().collect();
    match args.as_slice() {
        [_, command, public_key, message, signature] if command == "verify" => {
            verify(public_key, message, signature)
        }
        [_, command, public_key] if command == "validate-xonly" => validate_xonly(public_key),
        [_, command, message] if command == "sign-public-test-vector" => {
            sign_test_vector("scalar-3", message)
        }
        [_, command, key_name, message] if command == "sign-public-test-vector" => {
            sign_test_vector(key_name, message)
        }
        _ => Err(
            "usage: o2a-vector-crypto-checker verify PUBKEY MESSAGE SIGNATURE\n       o2a-vector-crypto-checker validate-xonly PUBKEY\n       o2a-vector-crypto-checker sign-public-test-vector [scalar-3|bip340-vector-1|bip340-vector-2] MESSAGE"
                .to_owned(),
        ),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}
