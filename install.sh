#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILL_DIR="$HERMES_HOME/skills"

mkdir -p "$SKILL_DIR"
cp -R "$ROOT_DIR/skills/"* "$SKILL_DIR/"

echo "Installed trade skills to $SKILL_DIR"
echo "Run: ./create-profile.sh demo-trade-agent"
