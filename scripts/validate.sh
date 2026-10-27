#!/usr/bin/env bash
set -euo pipefail
catalog_root="$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)"
args=(catalog validate --project "$catalog_root")
baseline_seen=false
json_output=false
for argument in "$@"; do
  if [[ "$argument" == --json ]]; then
    args+=(--json)
    json_output=true
  elif [[ "$argument" == -* ]] || $baseline_seen; then
    echo "usage: ./scripts/validate.sh [baseline-catalog-project] [--json]" >&2
    exit 2
  else
    baseline="$(cd "$argument" && pwd)"
    baseline_seen=true
  fi
done
"$catalog_root/scripts/validate-publication-workflows.sh" >&2
if $baseline_seen; then
  output=plain
  if $json_output; then output=json; fi
  exec python3 "$catalog_root/scripts/baseline_transition.py" "$baseline" "$output"
fi
exec "$catalog_root/scripts/packy.sh" "${args[@]}"
