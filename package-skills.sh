#!/usr/bin/env bash
# package-skills.sh — 将每个 skill 目录打包为 Cowork 兼容的 .skill 文件
# 用法: ./package-skills.sh [version]
# 示例: ./package-skills.sh v0.1.0

set -euo pipefail

VERSION="${1:-v0.1.0}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$ROOT_DIR/skills"
RELEASES_DIR="$ROOT_DIR/releases"

rm -rf "$RELEASES_DIR"
mkdir -p "$RELEASES_DIR"

echo "=== Packaging skills from $SKILLS_DIR ==="
echo ""

packed=0
for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")

    # 检查 SKILL.md 是否存在
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        echo "SKIP: $skill_name (no SKILL.md)"
        continue
    fi

    # 读取 skill 描述
    description=$(head -5 "$skill_dir/SKILL.md" | grep "description:" | sed 's/description: //' || echo "")

    output_file="$RELEASES_DIR/${skill_name}-${VERSION}.skill"

    # 打包为 zip（.skill 本质是 zip）
    cd "$skill_dir"
    zip -r "$output_file" . -x "*.DS_Store" > /dev/null 2>&1
    cd "$ROOT_DIR"

    size=$(du -h "$output_file" | cut -f1)
    echo "OK: $skill_name → ${skill_name}-${VERSION}.skill ($size)"
    echo "    $description"
    echo ""
    packed=$((packed + 1))
done

echo "=== Done: $packed skills packaged to $RELEASES_DIR ==="
echo ""
echo "Next steps:"
echo "  1. Upload files in releases/ to GitHub Releases"
echo "  2. Or distribute directly via link/email"
echo "  3. Users download .skill file → Cowork shows 'Save skill' button → one-click install"
