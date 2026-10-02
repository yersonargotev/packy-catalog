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
  baseline_root="$(cd "$1" && pwd)"
  if python3 - "$baseline_root" <<'PY'
import json, pathlib, sys
manifests = list(pathlib.Path(sys.argv[1]).glob('packs/*/pack.json'))
sys.exit(0 if manifests and all(json.loads(p.read_text()).get('schema_version') == 2 for p in manifests) else 1)
PY
  then
    python3 "$catalog_root/scripts/validate-schema-v3-cut.py" "$catalog_root" "$baseline_root"
  else
    args+=(--baseline "$baseline_root")
  fi
fi

"$catalog_root/scripts/validate-publication-workflows.sh"

cd "$validator_root"
go run ./internal/tools/catalogvalidate "${args[@]}"
