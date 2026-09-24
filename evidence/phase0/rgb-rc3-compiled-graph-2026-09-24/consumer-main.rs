use std::env;
use std::path::PathBuf;
use std::str::FromStr;

use bpstd::{Network, Wpkh, XpubDerivable};
use rgb::popls::bp::WalletProvider;
use rgbp::descriptors::RgbDescr;
use rgbp::resolvers::MultiResolver;
use rgbp::{FileHolder, Owner};

const XPUB: &str = "[643a7adc/86'/1'/0']tpubDCNiWHaiSkgnQjuhsg9kjwaUzaxQjUcmhagvYzqQ3TYJTgFGJstVaqnu4yhtFktBhCVFmBNLQ5sN53qKzZbMksm3XEyGJsEhQPfVZdWmTE2/<0;1;9;10>/*";

fn wallet(path: PathBuf) -> FileHolder {
    if path.join("descriptor.toml").exists() {
        FileHolder::load(path).expect("load wallet")
    } else {
        let xpub = XpubDerivable::from_str(XPUB).expect("xpub");
        let noise = xpub.xpub().chain_code().to_byte_array();
        let descr = RgbDescr::new_unfunded(Wpkh::from(xpub), noise);
        FileHolder::create(path, descr).expect("create wallet")
    }
}

fn main() {
    let mut args = env::args().skip(1);
    let cmd = args.next().expect("address|sync");
    let path = PathBuf::from(args.next().expect("wallet path"));
    match cmd.as_str() {
        "address" => {
            let holder = wallet(path);
            let resolver = MultiResolver::new_absent().expect("absent resolver");
            let mut owner = Owner::with_components(Network::Regtest, holder, resolver);
            println!("{}", owner.next_address());
        }
        "sync" => {
            let url = args.next().expect("electrum url");
            let holder = wallet(path);
            let resolver = MultiResolver::new_electrum(&url).expect("electrum");
            let mut owner = Owner::with_components(Network::Regtest, holder, resolver);
            owner.update_utxos().expect("sync");
            println!("utxos {}", owner.utxos().count());
        }
        other => panic!("unknown command {other}"),
    }
}
