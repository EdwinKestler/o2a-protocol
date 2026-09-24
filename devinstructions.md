# O2A isolated development environment instructions

This is the operating guide for AI agents using the O2A Phase 0 development
environment. Read [AGENTS.md](AGENTS.md) first. Repository files and Git state
are authoritative; containers provide reproducible tools but do not authorize
protocol, dependency, release, or deployment decisions.

O2A is still a specification project. The environment may be used to check
specifications, CC0 conformance vectors, Bitcoin Core regtest behavior, and
disposable RGB compatibility. It MUST NOT be used to introduce a production
wallet, freeze the proposed key-derivation profile, adopt the RGB RC3 lock, use
real funds, or claim that Phase 0 is closed without a separate authorized task.

## Where everything is

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Mandatory repository workflow and Palimnex rules |
| `docs/21-proposed-tech-stack-and-development-environment.md` | Proposed stack and architecture boundaries |
| `docs/23-stack-compatibility-and-security-readiness.md` | Compatibility, security, and known RGB limitations |
| `dev/README.md` | Detailed environment build, RGB exercise, cleanup, and Docker-install fallback |
| `dev/compose.yaml` | Canonical Compose project, services, profiles, network, and volumes |
| `dev/Dockerfile.toolchain` | Rust, Python, SQLite, compiler, audit, and license tools |
| `dev/Dockerfile.bitcoin` | Verified Bitcoin Core 31.1 regtest image |
| `dev/Dockerfile.electrs` | Pinned electrs compatibility image |
| `dev/Dockerfile.rgb-compat` | Pinned and patched disposable RGB RC3 image |
| `dev/bitcoin.conf` | Container-only zero-peer regtest configuration |
| `dev/check-host.sh` | Host, Compose, active-engine, and bind-mount check |
| `dev/.env.example` | Optional UID/GID overrides for Compose |
| `.env.example` | Repository-wide safe placeholder documentation; no Phase 0 secrets are required |
| `tests/vectors/` | CC0 fixtures and Python checkers |
| `tests/vectors/crypto-checker/` | Scoped Rust cryptographic checker, lockfile, and `cargo-deny` policy |

Do not replace these files with machine-local instructions. If a pinned version
changes, update the authoritative file and its supporting evidence together.

## Host prerequisites

The checked environment supports Linux x86_64. The host needs only:

- Git;
- a running Docker Engine that can bind-mount this repository;
- Docker Compose v2 through `docker compose`; and
- the repository-local Python virtual environment for Palimnex.

Normal repository work must not require host installations of Rust, Bitcoin
Core, electrs, RGB, SQLite development headers, or compiler toolchains. Those
belong in the checked-in images.

On the current host, use the native engine because Docker Desktop's
`desktop-linux` context cannot mount this repository under `/media`:

```bash
cd /media/kestl/andor/ffwd/o2a-protocol
export DOCKER_CONTEXT=default
./dev/check-host.sh
```

Set `DOCKER_CONTEXT=default` in every new shell used for this repository. Do
not change the global Docker context. If the host check fails because Docker is
missing, report the failure and give the maintainer the reviewed Ubuntu setup
commands in `dev/README.md`; an agent must not run `sudo`, change daemon
security, or add the user to the `docker` group without explicit authority.

If the host UID or GID differs from 1000, create the ignored local override:

```bash
cp dev/.env.example dev/.env
sed -i "s/^O2A_UID=.*/O2A_UID=$(id -u)/" dev/.env
sed -i "s/^O2A_GID=.*/O2A_GID=$(id -g)/" dev/.env
```

Then include `--env-file dev/.env` immediately after `docker compose` in each
command. Never commit `dev/.env`.

## Mandatory agent startup

Run Palimnex on the host, from the repository root, before searching or
editing. It is not a Compose service and its repository-private Redis socket
is not intended to be shared with the containers.

```bash
.venv/bin/python -m palimnex status
.venv/bin/python -m palimnex validate --deep
.venv/bin/python -m palimnex search "<exact task terms>" --limit 5
```

Follow the stale-cache recovery and post-edit workflow in `AGENTS.md`. If
Palimnex is unavailable, continue from repository files and report
`cache_consulted: false`. Never flush Redis or use another project's cache.

Before editing, also run:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Preserve unrelated changes. A container command does not grant permission to
commit, push, deploy, delete volumes, or change external services.

## Compose services and isolation

The Compose project is named `o2a-phase0` and contains:

| Service | Profile | Use |
| --- | --- | --- |
| `bitcoin` | default | Bitcoin Core 31.1, zero-peer regtest |
| `toolchain` | `tools` | Rust 1.98.1 and repository validation tools |
| `electrs` | `rgb-compat` | Local Electrum resolver backed by the same regtest node |
| `rgb-compat` | `rgb-compat` | Disposable patched RGB `v0.12.0-rc.3` CLI |

No service publishes a host port. Bitcoin RPC and Electrum remain inside the
internal `regtest` network. Services drop all Linux capabilities, set
`no-new-privileges`, use read-only root filesystems, and write only to named
volumes or bounded temporary filesystems.

The toolchain is the exception that bind-mounts this repository at
`/workspace`. That mount is writable so its commands can update source files
with the host UID/GID. Review commands before running them: Docker isolation is
not protection from destructive writes through that mount.

## Build and start the base environment

Use `dev/compose.yaml` explicitly so agents do not accidentally select an
unrelated Compose project:

```bash
docker compose --file dev/compose.yaml config --quiet
docker compose --file dev/compose.yaml build bitcoin
docker compose --file dev/compose.yaml up --detach --wait bitcoin
docker compose --file dev/compose.yaml ps
docker compose --file dev/compose.yaml exec --no-TTY bitcoin \
  bitcoin-cli -regtest -datadir=/var/lib/bitcoin getblockchaininfo
```

Build and inspect the isolated toolchain:

```bash
docker compose --file dev/compose.yaml --profile tools build toolchain
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc 'rustc --version && cargo --version && rustfmt --version && cargo clippy --version && cargo audit --version && cargo deny --version && python3 --version && sqlite3 --version'
```

Use `bash -lc` for scripted toolchain commands so its reviewed Cargo path and
profile are loaded consistently.

## Tools inside the toolchain image

The pinned toolchain image contains:

- Rust and Cargo 1.98.1, with the `rustfmt` and `clippy` components;
- `cargo-audit` 0.22.2 and `cargo-deny` 0.20.2;
- Python 3 and `venv` support;
- SQLite 3.53.4 built from its verified publisher archive;
- Git, curl, GnuPG, and `jq`;
- GCC/build-essential, Clang, CMake, `pkg-config`, `libclang`, OpenSSL headers,
  and standard native build support.

Before assuming an unlisted tool exists, check it inside the container with
`command -v TOOL`. Do not install ad hoc packages on the host. If a tool must
be reproducible, add it to the appropriate Dockerfile in a separately reviewed
change and rebuild the image.

The current host may print a warning about a missing user-level
`docker-sbom` CLI plugin while otherwise passing Docker and Compose checks.
Report that warning, but do not delete or repair files under `~/.docker`
without an explicit host-maintenance task.

Open an interactive shell when investigation is needed:

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain bash
```

The working directory is `/workspace`. The Cargo cache is the named
`cargo-cache` volume; `target/` remains ignored in the repository.

## Standard vector validation

Run the current Phase 0 vector suite inside the toolchain:

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc '
    set -euo pipefail
    python3 tests/vectors/derive_route_b.py self-test
    python3 tests/vectors/check_derivation_cross.py
    python3 tests/vectors/check_vectors.py
    python3 tests/vectors/check_protocol_objects.py
    cargo fmt --manifest-path tests/vectors/crypto-checker/Cargo.toml --check
    cargo test --locked --manifest-path tests/vectors/crypto-checker/Cargo.toml
    cargo audit --file tests/vectors/crypto-checker/Cargo.lock
    cargo deny --manifest-path tests/vectors/crypto-checker/Cargo.toml check
  '
```

The checker lock and license policy apply only to
`tests/vectors/crypto-checker/`. They are not an adopted production workspace
lock or an RGB dependency decision. Test mnemonics, seeds, extended private
keys, and derived keys in the CC0 vectors are public and permanently unsafe for
funds.

## Disposable RGB compatibility profile

Use the `rgb-compat` profile only when a task explicitly calls for the retained
compatibility experiment. Build it with:

```bash
docker compose --file dev/compose.yaml --profile rgb-compat build electrs rgb-compat
```

The exact regtest funding, descriptor, Electrum sync, and verification commands
are in `dev/README.md`. Follow them rather than improvising another wallet or
publishing ports.

This profile is deliberately unadopted. Its upstream RGB lock has known audit
findings and its CLI carries a retained compatibility patch. A successful
build or resolver sync does not create an O2A identity, validate an O2A RGB
contract, authorize `crates/o2a-rgb`, or close Phase 0.

Only use the disposable regtest wallet created by the documented procedure.
Never mount a real wallet, hardware signer, seed, private descriptor, RPC
cookie, private consignment, or production data into any service.

## Credentials and local state

Phase 0 requires no external credentials or secrets:

- Bitcoin Core and electrs use container-internal cookie authentication;
- no service exposes a host port;
- Palimnex uses its repository-local owner-only socket; and
- specification/vector checks do not need DNS, social, Pubky, Nostr, GitHub,
  deployment, or production account credentials.

`dev/.env` contains UID/GID values only. Do not store secrets in `.env`,
`dev/.env`, command history, source files, logs, or Compose configuration. The
repository ignores common key, seed, wallet, cookie, database, and local-state
formats, but ignore rules are not a security boundary.

## Inspect, stop, and clean up

Inspect bounded service state:

```bash
docker compose --file dev/compose.yaml --profile tools --profile rgb-compat ps
docker compose --file dev/compose.yaml logs --no-color --tail 200 bitcoin
docker compose --file dev/compose.yaml --profile rgb-compat logs --no-color --tail 200 electrs
```

Stop containers and retain caches and regtest data:

```bash
docker compose --file dev/compose.yaml --profile tools --profile rgb-compat down
```

Do not add `--volumes`, run `docker system prune`, delete data directories, or
remove shared images unless the maintainer explicitly requests destructive
cleanup. Before any authorized volume deletion, list the exact project-owned
targets:

```bash
docker compose --file dev/compose.yaml --profile tools --profile rgb-compat ps --all
docker volume ls --filter label=com.docker.compose.project=o2a-phase0
```

## Required handoff

After indexed-file edits, run on the host:

```bash
.venv/bin/python -m palimnex index --incremental
.venv/bin/python -m palimnex validate --deep
.venv/bin/python -m palimnex evaluate --limit 5
.venv/bin/python -m palimnex ledger-status
git diff --check
git status --short --branch
```

Report which Compose profiles ran, exact validation results, whether
Palimnex was consulted, current Git state, and any untested boundary. Keep
“built,” “tested,” “committed,” “pushed,” “deployed,” and “live verified” as
separate states.
