#!/usr/bin/env bash
set -euo pipefail
root="$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
if [[ -z "${PACKY_TEST_ARCHIVE:-}" ]]; then
  export PACKY_CACHE_DIR="$scratch/cache"
  "$root/scripts/packy.sh" version --json >/dev/null
  for archive in "$PACKY_CACHE_DIR"/*/release.tar.gz; do
    export PACKY_TEST_ARCHIVE="$archive"
  done
fi
[[ -f "$PACKY_TEST_ARCHIVE" ]] || { echo "native archive fixture is missing" >&2; exit 1; }
python3 -B -m unittest discover -s "$root/scripts/tests" -v
python3 -B -m unittest discover -s "$root/scripts/probes" -p 'test_*.py' -v
