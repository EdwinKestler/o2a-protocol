#!/usr/bin/env bash
set -euo pipefail

checker_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
manifest="$checker_dir/Cargo.toml"

# Blocking supply-chain gates.
cargo deny --manifest-path "$manifest" check advisories bans sources

# License findings are recorded for assessment and never fail development.
license_status=0
cargo deny --manifest-path "$manifest" check licenses || license_status=$?
printf 'cargo deny licenses report-only: exit %s\n' "$license_status"
