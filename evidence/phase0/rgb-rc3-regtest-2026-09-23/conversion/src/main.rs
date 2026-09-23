fn main() {
    // Public, well-known secp256k1 generator key; no secret material.
    let bytes = [
        0x02, 0x79, 0xbe, 0x66, 0x7e, 0xf9, 0xdc, 0xbb, 0xac, 0x55, 0xa0,
        0x62, 0x95, 0xce, 0x87, 0x0b, 0x07, 0x02, 0x9b, 0xfc, 0xdb, 0x2d,
        0xce, 0x28, 0xd9, 0x59, 0xf2, 0x81, 0x5b, 0x16, 0xf8, 0x17, 0x98,
    ];

    let bitcoin_key = bitcoin::secp256k1::PublicKey::from_slice(&bytes).unwrap();
    let serialized = bitcoin_key.serialize();
    let bp_key = bp::CompressedPk::from_byte_array(serialized).unwrap();
    assert_eq!(bp_key.to_byte_array(), serialized);
    let bitcoin_roundtrip =
        bitcoin::secp256k1::PublicKey::from_slice(&bp_key.to_byte_array()).unwrap();
    assert_eq!(bitcoin_roundtrip, bitcoin_key);

    let bitcoin_xonly =
        bitcoin::secp256k1::XOnlyPublicKey::from_slice(&serialized[1..]).unwrap();
    let xonly_bytes = bitcoin_xonly.serialize();
    let bp_xonly = bp::XOnlyPk::from_byte_array(xonly_bytes).unwrap();
    assert_eq!(bp_xonly.to_byte_array(), xonly_bytes);
    let bitcoin_xonly_roundtrip =
        bitcoin::secp256k1::XOnlyPublicKey::from_slice(&bp_xonly.to_byte_array()).unwrap();
    assert_eq!(bitcoin_xonly_roundtrip, bitcoin_xonly);

    let mut bad_compressed = serialized;
    bad_compressed[0] = 0x05;
    assert!(bitcoin::secp256k1::PublicKey::from_slice(&bad_compressed).is_err());
    assert!(bp::CompressedPk::from_byte_array(bad_compressed).is_err());
    assert!(bitcoin::secp256k1::XOnlyPublicKey::from_slice(&[0xff; 32]).is_err());
    assert!(bp::XOnlyPk::from_byte_array([0xff; 32]).is_err());

    println!("bitcoin secp -> serialized bytes -> BP CompressedPk/XOnlyPk -> bitcoin secp: pass");
    println!("malformed compressed/x-only public key rejection: pass");
}
