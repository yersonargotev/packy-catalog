#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
validation="$root/.github/workflows/validate.yml"
publication="$root/.github/workflows/publish.yml"

fail() {
  echo "publication workflow validation: $1" >&2
  exit 1
}

grep -Fq 'permissions:' "$validation" || fail "candidate validation must declare permissions"
grep -Fq 'contents: read' "$validation" || fail "candidate validation must remain read-only"
if grep -Eq '(contents|id-token|attestations): write|secrets\.' "$validation"; then
  fail "candidate validation must not receive publication authority"
fi

for required in \
  'workflow_run:' \
  "github.event.workflow_run.event == 'push'" \
  "github.event.workflow_run.head_branch == 'main'" \
  'github.event.workflow_run.head_repository.full_name == github.repository' \
  "github.event.workflow_run.conclusion == 'success'" \
  'permissions: {}' \
  'contents: read' \
  'attestations: write' \
  'contents: write' \
  'id-token: write' \
  'internal/tools/catalogsnapshot' \
  'publish-catalog-snapshot.sh'; do
  grep -Fq "$required" "$publication" || fail "publication workflow is missing $required"
done

builder_commit="$(sed -n 's/^[[:space:]]*PACKY_BUILDER_COMMIT:[[:space:]]*\([0-9a-f]\{40\}\)$/\1/p' "$publication" | sort -u)"
validator_commit="$(sed -n 's/^[[:space:]]*ref:[[:space:]]*\([0-9a-f]\{40\}\)$/\1/p' "$validation" | tail -1)"
if [[ ! "$builder_commit" =~ ^[0-9a-f]{40}$ ]] || [[ "$validator_commit" != "$builder_commit" ]]; then
  fail "validation and publication must use the same immutable Packy commit"
fi

publish_job="$(sed -n '/^  publish:/,$p' "$publication")"
if grep -Eq 'path: catalog-project|working-directory: catalog-project|catalog-project/' <<< "$publish_job"; then
  fail "write-authorized job must not check out or execute Catalog Project content"
fi

echo "validated read-only candidate checks and isolated publication authority"
