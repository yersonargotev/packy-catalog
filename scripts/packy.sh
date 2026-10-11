#!/usr/bin/env bash
set -euo pipefail
exec python3 -B "${BASH_SOURCE[0]%/*}/packy_tool.py" \
  --pin "${BASH_SOURCE[0]%/*}/../packy-release.json" -- "$@"
