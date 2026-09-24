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

fn sign_test_vector(message: &str) -> Result<(), String> {
    // Public vector key only: scalar 3 is the published BIP340 test key and is
    // permanently unsafe for funds. This command exists only to regenerate
    // CC0 fixtures; the verifier path never loads a secret.
    let mut scalar = [0u8; 32];
    scalar[31] = 3;
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
        [_, command, message] if command == "sign-public-test-vector" => {
            sign_test_vector(message)
        }
        _ => Err(
            "usage: o2a-vector-crypto-checker verify PUBKEY MESSAGE SIGNATURE\n       o2a-vector-crypto-checker sign-public-test-vector MESSAGE"
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
