#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${HERMES_EXPORT_SKILLS_REPO_URL:-https://github.com/Xuxchloris/hermes-export-skills.git}"
PROFILE_NAME="${1:-${HERMES_PROFILE_NAME:-demo-trade-agent}}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
WORK_DIR="$(mktemp -d -t hermes-export-skills-XXXXXX)"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

if command -v git >/dev/null 2>&1; then
  git clone --depth 1 "$REPO_URL" "$WORK_DIR/repo"
else
  echo "git is required for bootstrap.sh"
  exit 1
fi

cd "$WORK_DIR/repo"
export HERMES_HOME
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install -r requirements.txt
elif command -v python >/dev/null 2>&1; then
  python -m pip install -r requirements.txt
else
  echo "Python is required to install tool dependencies."
  exit 1
fi
chmod +x install.sh create-profile.sh
./install.sh
./create-profile.sh "$PROFILE_NAME"

echo "Bootstrapped hermes-export-skills into profile: $PROFILE_NAME"
