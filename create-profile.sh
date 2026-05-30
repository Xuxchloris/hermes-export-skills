#!/usr/bin/env bash
set -euo pipefail

PROFILE_NAME="${1:-}"
if [ -z "$PROFILE_NAME" ]; then
  echo "Usage: ./create-profile.sh <profile-name>"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PROFILE_DIR="$HERMES_HOME/profiles/$PROFILE_NAME"

mkdir -p "$PROFILE_DIR/data/config"
mkdir -p "$PROFILE_DIR/data/prospects" "$PROFILE_DIR/data/reports" "$PROFILE_DIR/data/emails" "$PROFILE_DIR/data/quotations"
mkdir -p "$PROFILE_DIR/data/replies" "$PROFILE_DIR/data/follow-ups"
mkdir -p "$PROFILE_DIR/sessions" "$PROFILE_DIR/memory" "$PROFILE_DIR/skills/custom"

cp "$ROOT_DIR/templates/PRODUCT.example.yaml" "$PROFILE_DIR/data/config/PRODUCT.yaml"
cp "$ROOT_DIR/templates/MARKET.example.yaml" "$PROFILE_DIR/data/config/MARKET.yaml"
cp "$ROOT_DIR/templates/TONE.example.yaml" "$PROFILE_DIR/data/config/TONE.yaml"
cp "$ROOT_DIR/templates/PRICING.example.yaml" "$PROFILE_DIR/data/config/PRICING.yaml"
cp "$ROOT_DIR/templates/DISCOVERY.example.yaml" "$PROFILE_DIR/data/config/DISCOVERY.yaml"
cp "$ROOT_DIR/templates/.env.example" "$PROFILE_DIR/.env.example"

cat > "$PROFILE_DIR/AGENTS.md" <<'EOF'
# Trade Agent Instructions

- Use `trade-workflow-router` as the entry point when the user mentions foreign trade broadly.
- Read product data from `data/config/PRODUCT.yaml`.
- Read market strategy from `data/config/MARKET.yaml`.
- Read tone rules from `data/config/TONE.yaml`.
- Read quotation rules from `data/config/PRICING.yaml`.
- Read prospect discovery rules and collection API status from `data/config/DISCOVERY.yaml`.
- Save prospects in `data/prospects/`.
- Save research reports in `data/reports/`.
- Save email drafts in `data/emails/`.
- Save quotation drafts in `data/quotations/`.
- Save classified replies in `data/replies/`.
- Save follow-up plans in `data/follow-ups/`.
- Never invent company facts, contact names, prices, certifications, or delivery dates.
- Use approved business sources and record source evidence for each prospect.
- Emails and quotations require human review before sending.
EOF

echo "Created profile at $PROFILE_DIR"
