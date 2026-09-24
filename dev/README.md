# O2A Phase 0 development environment

This environment establishes containerized prerequisites without creating an
O2A implementation. The default service is Bitcoin Core 31.1 on an isolated,
zero-peer regtest network. Rust 1.98.1 tooling and SQLite 3.53.4 are an opt-in
container. Exact electrs 0.12.0 and patched RGB RC3 form an explicitly
disposable compatibility profile; their presence does not adopt the RGB
lineage or dependency graph.

No service publishes a host port. Bitcoin RPC and Electrum are reachable only
inside the Compose `regtest` network. Containers drop all Linux capabilities,
set `no-new-privileges`, use read-only root filesystems, and write only to
named volumes or bounded temporary filesystems. Docker remains process
isolation, not a protocol trust boundary or a substitute for wallet security.

## Current supported host

The checked setup targets Linux x86_64. The Bitcoin image downloads the
official Bitcoin Core 31.1 x86_64 archive and verifies its pinned SHA-256. The
repository's Phase 0 evidence records the checksum-signature verification.
The Rust and Debian base images are pinned by OCI index digest. The toolchain
builds SQLite 3.53.4 from the official autoconf archive and verifies the
publisher's SHA3-256 before compilation; it does not use Debian Bookworm's
older SQLite 3.40.1 package.

The base-image digests and principal tool versions are pinned. Debian package
repositories are not snapshot-pinned, so rebuilds may receive newer security
updates and must pass the same acceptance checks before use.

On the current Ubuntu 24.04 host, Docker Desktop and a native Docker Engine,
Compose, Git, curl, GnuPG, and `jq` are already available. No sudo command is
needed on this machine. Docker Desktop's `desktop-linux` context does not share
this repository's `/media` path. Use the already-running native engine for this
repository without changing the global Docker context:

```bash
export DOCKER_CONTEXT=default
```

Repeat that export in each new terminal before the commands below. Docker
access remains security-sensitive, and the writable repository bind mount
gives the toolchain container access to those host files; do not run an
unreviewed image as though it were a security sandbox.

Run the host check. It verifies that the selected engine can bind-mount this
repository, in addition to checking Docker and Compose:

```bash
./dev/check-host.sh
```

If the host UID or GID is not 1000, create the ignored local environment file:

```bash
cp dev/.env.example dev/.env
sed -i "s/^O2A_UID=.*/O2A_UID=$(id -u)/" dev/.env
sed -i "s/^O2A_GID=.*/O2A_GID=$(id -g)/" dev/.env
```

Add `--env-file dev/.env` to each Compose command below when that file is
needed.

## Build and verify the base environment

These commands do not need sudo on a correctly configured Docker host:

```bash
docker compose --file dev/compose.yaml config --quiet
docker compose --file dev/compose.yaml build bitcoin
docker compose --file dev/compose.yaml up --detach --wait bitcoin
docker compose --file dev/compose.yaml ps
docker compose --file dev/compose.yaml exec --no-TTY bitcoin \
  bitcoin-cli -regtest -datadir=/var/lib/bitcoin getblockchaininfo
```

Build and inspect the Rust toolchain without installing Rust or compilers on
the operating system:

```bash
docker compose --file dev/compose.yaml --profile tools build toolchain
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc 'rustc --version && cargo --version && rustfmt --version && cargo clippy --version && cargo audit --version && cargo deny --version && sqlite3 --version'
```

Enter an interactive container with the repository mounted at `/workspace`:

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash
```

The bind mount is writable so future source changes have the host user's UID.
The Cargo home is a named Docker volume. Do not place wallet files, seeds,
private keys, RPC cookies, or private consignments in the repository.

## Disposable RGB compatibility profile

This profile builds exact electrs tag `v0.12.0` at commit `37501cc4` and exact
RGB tag `v0.12.0-rc.3` at commit `a1e6b415`, then applies the retained CLI
compatibility patch. It intentionally uses the unadopted upstream RGB lock,
whose audit fails. Use only regtest data and never provide real keys.

```bash
docker compose --file dev/compose.yaml --profile rgb-compat build electrs rgb-compat
docker compose --file dev/compose.yaml up --detach --wait bitcoin
docker compose --file dev/compose.yaml exec --no-TTY bitcoin \
  bitcoin-cli -regtest -datadir=/var/lib/bitcoin createwallet dev
address=$(docker compose --file dev/compose.yaml exec --no-TTY bitcoin \
  bitcoin-cli -regtest -datadir=/var/lib/bitcoin -rpcwallet=dev getnewaddress)
docker compose --file dev/compose.yaml exec --no-TTY bitcoin \
  bitcoin-cli -regtest -datadir=/var/lib/bitcoin -rpcwallet=dev \
  generatetoaddress 101 "${address}"
docker compose --file dev/compose.yaml --profile rgb-compat up --detach electrs rgb-compat
docker compose --file dev/compose.yaml --profile rgb-compat exec --no-TTY rgb-compat \
  rgb sync --help
```

If `createwallet dev` reports that the wallet already exists, continue with
`getnewaddress`. Wait until electrs has indexed the 101 blocks, then run the
bounded resolver check below. It passes only a public descriptor to RGB and
does not expose Bitcoin Core's private descriptors:

```bash
docker compose --file dev/compose.yaml --profile rgb-compat exec --no-TTY \
  rgb-compat rgb --network regtest --data-dir /var/lib/rgb/test-run \
  --no-network-prefix init
full_descriptor=$(docker compose --file dev/compose.yaml exec --no-TTY bitcoin \
  bitcoin-cli -regtest -datadir=/var/lib/bitcoin -rpcwallet=dev \
  listdescriptors false | jq -r \
  '.descriptors[] | select(.active == true and .internal == false and (.desc | startswith("wpkh("))) | .desc' | head -n 1)
descriptor="${full_descriptor#wpkh(}"
descriptor="${descriptor%%)#*}"
docker compose --file dev/compose.yaml --profile rgb-compat exec --no-TTY \
  --env O2A_TEST_DESCRIPTOR="${descriptor}" rgb-compat sh -c \
  'exec rgb --network regtest --data-dir /var/lib/rgb/test-run --no-network-prefix create --wpkh test "$O2A_TEST_DESCRIPTOR"'
docker compose --file dev/compose.yaml --profile rgb-compat exec --no-TTY \
  rgb-compat rgb --network regtest --data-dir /var/lib/rgb/test-run \
  --no-network-prefix sync --electrum=tcp://electrs:50001 test
unset descriptor full_descriptor
```

This profile confirms environment and resolver wiring only; it does not create
an O2A identity, exercise an RGB contract, or prove RGB transition validity.
The exact RC3 lock remains unadopted and contains known audit findings.

## Status and recoverable cleanup

Inspect state:

```bash
docker compose --file dev/compose.yaml --profile tools --profile rgb-compat ps
docker compose --file dev/compose.yaml logs --no-color --tail 200 bitcoin
docker compose --file dev/compose.yaml --profile rgb-compat logs --no-color --tail 200 electrs
```

Stop containers while retaining regtest data and Cargo caches:

```bash
docker compose --file dev/compose.yaml --profile tools --profile rgb-compat down
```

Do not add `--volumes` unless you intentionally want to delete the disposable
Bitcoin, electrs, RGB, and Cargo volumes. Before doing that, list the exact
project resources:

```bash
docker compose --file dev/compose.yaml --profile tools --profile rgb-compat ps --all
docker volume ls --filter label=com.docker.compose.project=o2a-phase0
```

## Docker installation fallback for Ubuntu 24.04

Use this block only on an Ubuntu host where `./dev/check-host.sh` reports that
Docker or Compose is missing and Docker Desktop is not already providing the
active context. These are the Docker-maintained apt repository steps; they
require sudo:

```bash
sudo apt update
sudo apt install --yes ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install --yes docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod --append --groups docker "$USER"
```

Log out and back in after `usermod`, then run:

```bash
docker version
docker compose version
docker run --rm hello-world
./dev/check-host.sh
```

Do not run the convenience `get.docker.com` script for this setup. Review the
official Docker installation and rootless-mode documentation before changing
daemon security, firewall, or user-namespace settings.
