from pathlib import Path
import re
import sys


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

REQUIRED_SKILLS = [
    "trade-workflow-router",
    "product-loader",
    "company-research",
    "prospect-discovery",
    "prospect-list-enrichment",
    "prospect-scoring",
    "email-crafting",
    "reply-classification",
    "follow-up-planner",
    "decision-maker-finder",
    "quotation-generator",
]

REQUIRED_ROOT_FILES = [
    "README.md",
    "LICENSE",
    "install.sh",
    "install.ps1",
    "create-profile.sh",
    "create-profile.ps1",
    "requirements.txt",
    "tools/render_quotation.py",
    "tools/collect_prospects.py",
    "tools/batch_prospect_pipeline.py",
    "tools/decision_maker_finder.py",
    "examples/quotation.example.json",
]

REQUIRED_TEMPLATES = [
    "PRODUCT.example.yaml",
    "MARKET.example.yaml",
    "TONE.example.yaml",
    "PRICING.example.yaml",
    "DISCOVERY.example.yaml",
    ".env.example",
]

REQUIRED_DOCS = [
    "docs/quick-start.md",
    "docs/deployment.md",
    "docs/compliance.md",
    "docs/roadmap.md",
    "tests/pressure-scenarios.md",
]

REQUIRED_SECTIONS = [
    "# ",
    "## Overview",
    "## When to Use",
    "## Inputs",
    "## Outputs",
    "## Procedure",
    "## Verification",
    "## Common Mistakes",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def assert_exists(relative_path: str) -> None:
    path = ROOT / relative_path
    if not path.exists():
        fail(f"missing {relative_path}")


def parse_frontmatter(text: str, file: Path) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail(f"{file} missing YAML frontmatter")
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def validate_skill(skill: str) -> None:
    skill_file = ROOT / "skills" / skill / "SKILL.md"
    if not skill_file.exists():
        fail(f"missing skills/{skill}/SKILL.md")

    text = skill_file.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text, skill_file)

    if frontmatter.get("name") != skill:
        fail(f"{skill_file} name must be {skill}")

    description = frontmatter.get("description", "")
    if not description.startswith("Use when"):
        fail(f"{skill_file} description must start with 'Use when'")

    if len(description) > 500:
        fail(f"{skill_file} description should stay under 500 characters")

    if len(text.split("---", 2)[1]) > 1024:
        fail(f"{skill_file} frontmatter must stay under 1024 characters")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"{skill_file} missing section {section}")

    banned = ["TODO", "TBD", "fill in", "later"]
    for term in banned:
        if term.lower() in text.lower():
            fail(f"{skill_file} contains placeholder term {term}")


def assert_text_contains(relative_path: str, required_terms: list[str]) -> None:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8").lower()
    for term in required_terms:
        if term.lower() not in text:
            fail(f"{relative_path} missing required term {term}")


def validate_quotation_exports() -> None:
    assert_text_contains(
        "skills/quotation-generator/SKILL.md",
        ["export_outputs", "html", "pdf", "excel", "human_review_required"],
    )
    assert_text_contains(
        "skills/quotation-generator/references/quotation-rules.md",
        ["HTML", "PDF", "Excel", "export filename", "blocked"],
    )
    assert_text_contains(
        "skills/quotation-generator/templates/quotation.html",
        ["{{quotation_number}}", "{{buyer_name}}", "{{items}}", "{{total_amount}}"],
    )


def validate_discovery_contract() -> None:
    assert_text_contains(
        "skills/prospect-discovery/SKILL.md",
        [
            "DISCOVERY.yaml",
            "collection_api",
            "Google search results",
            "trade show websites",
            "industry directories",
            "approved business sources",
            "company-level signals",
            "company-research",
            "prospect-scoring",
        ],
    )
    assert_text_contains(
        "templates/DISCOVERY.example.yaml",
        [
            "method",
            "auth_header",
            "query_params",
            "request_body_template",
            "response_mapping",
            "pagination",
            "rate_limit",
            "retry_policy",
            "contact_enrichment_api",
        ],
    )


def validate_pipeline_tools_contract() -> None:
    assert_text_contains(
        "skills/prospect-discovery/SKILL.md",
        ["tools/collect_prospects.py", "search tasks", "prospects.raw.csv"],
    )
    assert_text_contains(
        "skills/prospect-list-enrichment/SKILL.md",
        ["tools/batch_prospect_pipeline.py", "prospects.enriched.xlsx", "email_drafts.xlsx"],
    )
    assert_text_contains(
        "skills/decision-maker-finder/SKILL.md",
        ["tools/decision_maker_finder.py", "role", "email_status", "source_url"],
    )


def validate_router_contract() -> None:
    assert_text_contains(
        "skills/trade-workflow-router/SKILL.md",
        [
            "外贸工作菜单",
            "prospect-discovery",
            "prospect-list-enrichment",
            "company-research",
            "prospect-scoring",
            "decision-maker-finder",
            "email-crafting",
            "reply-classification",
            "follow-up-planner",
            "quotation-generator",
            "tools/collect_prospects.py",
            "tools/batch_prospect_pipeline.py",
            "tools/decision_maker_finder.py",
            "tools/render_quotation.py",
            "ask the user to choose",
        ],
    )


def validate_quick_start_example() -> None:
    assert_text_contains("docs/quick-start.md", ["SKU CT-200A"])


def main() -> None:
    for file in REQUIRED_ROOT_FILES:
        assert_exists(file)
    for template in REQUIRED_TEMPLATES:
        assert_exists(f"templates/{template}")
    for doc in REQUIRED_DOCS:
        assert_exists(doc)
    for skill in REQUIRED_SKILLS:
        validate_skill(skill)
    validate_quotation_exports()
    validate_discovery_contract()
    validate_pipeline_tools_contract()
    validate_router_contract()
    validate_quick_start_example()
    print("PASS: skill package structure and required content are valid")


if __name__ == "__main__":
    main()
