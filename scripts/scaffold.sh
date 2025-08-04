#!/usr/bin/env bash
# Wrapper script around Copier to scaffold a new project from this template.

set -euo pipefail

if ! command -v copier &>/dev/null; then
  echo "Error: copier is not installed.  Install with 'pip install copier' before running this script." >&2
  exit 1
fi

DEST_DIR="${1:-../new-project}"

echo "Scaffolding project into $DEST_DIR..."
copier copy --trust . "$DEST_DIR"
echo "Running post‑copy verification..."
(cd "$DEST_DIR" && ./scripts/verify.sh)