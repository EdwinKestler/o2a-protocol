// SPDX-License-Identifier: CC0-1.0

use bitcoin_hashes::{
    hmac::{Hmac, HmacEngine},
    sha512, Hash, HashEngine,
};
use secp256k1::{
    schnorr::Signature, Keypair, Message, PublicKey, Scalar, Secp256k1, SecretKey, XOnlyPublicKey,
};
use std::{env, process::ExitCode, str::FromStr};

const HARDENED: u32 = 1 << 31;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct TestXprv {
    secret: [u8; 32],
    chain_code: [u8; 32],
}

impl TestXprv {
    fn parse(value: &str) -> Result<Self, String> {
        let bytes = hex::decode(value).map_err(|error| format!("invalid xprv hex: {error}"))?;
        if bytes.len() != 64 {
            return Err("xprv must be 64 bytes encoded as k || c".to_owned());
        }
        let mut secret = [0u8; 32];
        let mut chain_code = [0u8; 32];
        secret.copy_from_slice(&bytes[..32]);
        chain_code.copy_from_slice(&bytes[32..]);
        SecretKey::from_slice(&secret)
            .map_err(|error| format!("invalid xprv private key: {error}"))?;
        Ok(Self { secret, chain_code })
    }

    fn encode(self) -> String {
        let mut bytes = [0u8; 64];
        bytes[..32].copy_from_slice(&self.secret);
        bytes[32..].copy_from_slice(&self.chain_code);
        hex::encode(bytes)
    }
}

fn hmac_sha512(key: &[u8], data: &[u8]) -> [u8; 64] {
    let mut engine = HmacEngine::<sha512::Hash>::new(key);
    engine.input(data);
    Hmac::<sha512::Hash>::from_engine(engine).to_byte_array()
}

fn bip32_master(seed: &[u8]) -> Result<TestXprv, String> {
    let digest = hmac_sha512(b"Bitcoin seed", seed);
    let mut secret = [0u8; 32];
    let mut chain_code = [0u8; 32];
    secret.copy_from_slice(&digest[..32]);
    chain_code.copy_from_slice(&digest[32..]);
    SecretKey::from_slice(&secret)
        .map_err(|error| format!("invalid BIP32 master private key: {error}"))?;
    Ok(TestXprv { secret, chain_code })
}

fn bip32_child(parent: TestXprv, index: u32) -> Result<TestXprv, String> {
    let mut data = [0u8; 37];
    if index >= HARDENED {
        data[1..33].copy_from_slice(&parent.secret);
    } else {
        let secret = SecretKey::from_slice(&parent.secret)
            .map_err(|error| format!("invalid parent private key: {error}"))?;
        data[..33]
            .copy_from_slice(&PublicKey::from_secret_key(&Secp256k1::new(), &secret).serialize());
    }
    data[33..].copy_from_slice(&index.to_be_bytes());
    let digest = hmac_sha512(&parent.chain_code, &data);
    let mut left = [0u8; 32];
    let mut chain_code = [0u8; 32];
    left.copy_from_slice(&digest[..32]);
    chain_code.copy_from_slice(&digest[32..]);
    let tweak = Scalar::from_be_bytes(left)
        .map_err(|_| "BIP32 child tweak is greater than or equal to curve order".to_owned())?;
    let parent_secret = SecretKey::from_slice(&parent.secret)
        .map_err(|error| format!("invalid parent private key: {error}"))?;
    let child = parent_secret
        .add_tweak(&tweak)
        .map_err(|error| format!("BIP32 child private key is zero: {error}"))?;
    Ok(TestXprv {
        secret: child.secret_bytes(),
        chain_code,
    })
}

fn bip32_ckd_hard(parent: TestXprv, index: u32) -> Result<TestXprv, String> {
    if index < HARDENED {
        return Err("hardened BIP32 child index must be at least 2^31".to_owned());
    }
    bip32_child(parent, index)
}

fn hardened_index(index: u32) -> Result<u32, String> {
    if index >= HARDENED {
        return Err("unhardened input index must fit in 31 bits".to_owned());
    }
    Ok(index | HARDENED)
}

fn bip85_xprv(master: TestXprv, index: u32) -> Result<TestXprv, String> {
    let mut application = master;
    for component in [83_696_968, 32, index] {
        application = bip32_ckd_hard(application, hardened_index(component)?)?;
    }
    let digest = hmac_sha512(b"bip-entropy-from-k", &application.secret);
    let mut chain_code = [0u8; 32];
    let mut secret = [0u8; 32];
    chain_code.copy_from_slice(&digest[..32]);
    secret.copy_from_slice(&digest[32..]);
    SecretKey::from_slice(&secret)
        .map_err(|error| format!("invalid BIP85 BIP32-XPRV private key: {error}"))?;
    Ok(TestXprv { secret, chain_code })
}

fn xonly_pub(xprv: TestXprv) -> Result<String, String> {
    let secret = SecretKey::from_slice(&xprv.secret)
        .map_err(|error| format!("invalid xprv private key: {error}"))?;
    let keypair = Keypair::from_secret_key(&Secp256k1::new(), &secret);
    Ok(XOnlyPublicKey::from_keypair(&keypair).0.to_string())
}

fn derive_path(root: TestXprv, path: &[u32]) -> Result<TestXprv, String> {
    let mut key = root;
    for index in path {
        key = bip32_child(key, *index)?;
    }
    Ok(key)
}

fn derive_route_b(seed: &[u8], network: &str, entity: u32) -> Result<(), String> {
    self_test_quiet()?;
    if entity >= HARDENED {
        return Err("entity index must fit in 31 bits".to_owned());
    }
    let coin = match network {
        "mainnet" => 0,
        "regtest" => 1,
        _ => return Err("fixture network must be mainnet or regtest".to_owned()),
    };
    let master = bip32_master(seed)?;
    let o2a = bip85_xprv(master, 998_536_622)?;

    println!("network={network}");
    println!("coin_type={coin}");
    println!("entity={entity}");
    println!("xprv_o2a={}", o2a.encode());
    println!("bip85_path=m/83696968'/32'/998536622'");
    for (name, role) in [
        ("root_identity", 0),
        ("controller_0", 1),
        ("recovery_0", 2),
        ("nostr_0", 3),
    ] {
        let path = [
            hardened_index(coin)?,
            hardened_index(entity)?,
            hardened_index(role)?,
            hardened_index(0)?,
        ];
        let key = derive_path(o2a, &path)?;
        println!("{name}_path=m/{coin}'/{entity}'/{role}'/0'");
        println!("{name}_xonly={}", xonly_pub(key)?);
    }
    let payment_path = [
        hardened_index(86)?,
        hardened_index(coin)?,
        hardened_index(0)?,
        0,
        0,
    ];
    let payment = derive_path(master, &payment_path)?;
    println!("payment_path=m/86'/{coin}'/0'/0/0");
    println!("payment_xonly={}", xonly_pub(payment)?);
    Ok(())
}

fn self_test_quiet() -> Result<(), String> {
    // BIP32 test vector 1: seed and chain m/0H.
    let seed = hex::decode("000102030405060708090a0b0c0d0e0f")
        .map_err(|error| format!("invalid embedded BIP32 vector: {error}"))?;
    let master = bip32_master(&seed)?;
    let child = bip32_ckd_hard(master, HARDENED)?;
    let expected_child = "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141";
    if child.encode() != expected_child {
        return Err("BIP32 test vector 1 m/0H mismatch".to_owned());
    }

    // BIP85 BIP32-XPRV test vector: the published master at app 32', index 0.
    let bip85_master = TestXprv::parse("3f15e5d852dc2e9ba5e9fe189a8dd2e1547badef5b563bbe6579fc6807d80ed91b67969d1ec69bdfeeae43213da8460ba34b92d0788c8f7bfcfa44906e8a589c")?;
    let derived = bip85_xprv(bip85_master, 0)?;
    let expected_derived = "ead0b33988a616cf6a497f1c169d9e92562604e38305ccd3fc96f2252c17768252405cd0dd21c5be78314a7c1a3c65ffd8d896536cc7dee3157db5824f0c92e2";
    if derived.encode() != expected_derived {
        return Err("BIP85 BIP32-XPRV test vector mismatch".to_owned());
    }

    Ok(())
}

fn self_test() -> Result<(), String> {
    self_test_quiet()?;
    println!("BIP32 vector 1 m/0H: ok");
    println!("BIP85 BIP32-XPRV app 32 index 0: ok");
    Ok(())
}

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
        [_, command] if command == "self-test" => self_test(),
        [_, command, seed] if command == "bip32-master" => {
            let seed = hex::decode(seed).map_err(|error| format!("invalid seed hex: {error}"))?;
            println!("{}", bip32_master(&seed)?.encode());
            Ok(())
        }
        [_, command, xprv, index] if command == "bip32-ckd-hard" => {
            let index = index
                .parse::<u32>()
                .map_err(|error| format!("invalid child index: {error}"))?;
            println!("{}", bip32_ckd_hard(TestXprv::parse(xprv)?, index)?.encode());
            Ok(())
        }
        [_, command, xprv, index] if command == "bip85-xprv" => {
            let index = index
                .parse::<u32>()
                .map_err(|error| format!("invalid application index: {error}"))?;
            println!("{}", bip85_xprv(TestXprv::parse(xprv)?, index)?.encode());
            Ok(())
        }
        [_, command, xprv] if command == "xonly-pub" => {
            println!("{}", xonly_pub(TestXprv::parse(xprv)?)?);
            Ok(())
        }
        [_, command, seed, network, entity] if command == "derive-route-b" => {
            let seed = hex::decode(seed).map_err(|error| format!("invalid seed hex: {error}"))?;
            let entity = entity
                .parse::<u32>()
                .map_err(|error| format!("invalid entity index: {error}"))?;
            derive_route_b(&seed, network, entity)
        }
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
            "usage: o2a-vector-crypto-checker self-test\n       o2a-vector-crypto-checker bip32-master SEED_HEX\n       o2a-vector-crypto-checker bip32-ckd-hard XPRV_HEX INDEX\n       o2a-vector-crypto-checker bip85-xprv XPRV_HEX INDEX\n       o2a-vector-crypto-checker xonly-pub XPRV_HEX\n       o2a-vector-crypto-checker derive-route-b SEED_HEX NETWORK ENTITY\n       o2a-vector-crypto-checker verify PUBKEY MESSAGE SIGNATURE\n       o2a-vector-crypto-checker validate-xonly PUBKEY\n       o2a-vector-crypto-checker sign-public-test-vector [scalar-3|bip340-vector-1|bip340-vector-2] MESSAGE"
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
