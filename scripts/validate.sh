#!/usr/bin/env bash

set -euo pipefail

catalog_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
validator_root="${PACKY_VALIDATOR_ROOT:-$(cd "$catalog_root/../packy" && pwd)}"

if [[ $# -gt 1 ]]; then
  echo "usage: ./scripts/validate.sh [baseline-catalog-project]" >&2
  exit 2
fi

args=(--project "$catalog_root")
if [[ $# -eq 1 ]]; then
  args+=(--baseline "$(cd "$1" && pwd)")
fi

"$catalog_root/scripts/validate-publication-workflows.sh"

cd "$validator_root"
go run ./internal/tools/catalogvalidate "${args[@]}"
