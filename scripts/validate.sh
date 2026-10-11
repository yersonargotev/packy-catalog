#!/usr/bin/env bash
set -euo pipefail
catalog_root="$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)"
args=(catalog validate --project "$catalog_root")
baseline_seen=false
for argument in "$@"; do
  if [[ "$argument" == --json ]]; then
    args+=(--json)
  elif [[ "$argument" == -* ]] || $baseline_seen; then
    echo "usage: ./scripts/validate.sh [baseline-catalog-project] [--json]" >&2
    exit 2
  else
    baseline="$(cd "$argument" && pwd)"
    args+=(--baseline "$baseline")
    baseline_seen=true
  fi
done
"$catalog_root/scripts/validate-publication-workflows.sh" >&2
exec "$catalog_root/scripts/packy.sh" "${args[@]}"
