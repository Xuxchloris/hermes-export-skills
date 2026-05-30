#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILL_DIR="$HERMES_HOME/skills"
TOOL_DIR="$HERMES_HOME/tools"

mkdir -p "$SKILL_DIR"
mkdir -p "$TOOL_DIR"
cp -R "$ROOT_DIR/skills/"* "$SKILL_DIR/"
cp "$ROOT_DIR/tools/collect_prospects.py" "$TOOL_DIR/collect_prospects.py"
cp "$ROOT_DIR/tools/batch_prospect_pipeline.py" "$TOOL_DIR/batch_prospect_pipeline.py"
cp "$ROOT_DIR/tools/decision_maker_finder.py" "$TOOL_DIR/decision_maker_finder.py"
cp "$ROOT_DIR/tools/render_quotation.py" "$TOOL_DIR/render_quotation.py"
cp "$ROOT_DIR/tools/trade_utils.py" "$TOOL_DIR/trade_utils.py"

echo "Installed trade skills to $SKILL_DIR"
echo "Installed trade tools to $TOOL_DIR"
echo "Run: ./create-profile.sh demo-trade-agent"
