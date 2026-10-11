#!/usr/bin/env bash
set -euo pipefail
exec python3 -B "${BASH_SOURCE[0]%/*}/validate_publication_workflows.py"
