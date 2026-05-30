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
    "bootstrap.sh",
    "bootstrap.ps1",
    "create-profile.sh",
    "create-profile.ps1",
    "requirements.txt",
    "tools/render_quotation.py",
    "tools/collect_prospects.py",
    "tools/scrapling_prospect_spider.py",
    "tools/scrapling_spider_runner.py",
    "tools/scrapling_mcp_server.py",
    "tools/batch_prospect_pipeline.py",
    "tools/decision_maker_finder.py",
    "examples/quotation.example.json",
]

REQUIRED_TEMPLATES = [
    "PRODUCT.example.yaml",
    "PRODUCTS.catalog.example.yaml",
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
            "do not use browser navigation as the default customer-discovery path",
            "prospect_search_tasks.csv",
            "Do not manually browse arbitrary B2B platforms",
            "Search tasks are not treated as customer results",
            "source_status",
            "source_unavailable",
            "Do not return a numbered customer list",
            "prospects.raw.csv",
            "contact_email",
            "contact_phone",
            "email_result",
            "phone_result",
            "scrapling_spider",
            "native_scrapling_spider",
            "tools/scrapling_spider_runner.py",
            "tools/scrapling_mcp_server.py",
            "source_urls",
            "crawl_report.json",
            "company name or company link",
            "official website contact search",
            "--product-query",
            "--sku",
        ],
    )
    assert_text_contains(
        "templates/DISCOVERY.example.yaml",
        [
            'engine: "scrapling-fetcher"',
            "method",
            "auth_header",
            "query_params",
            "request_body_template",
            "response_mapping",
            "pagination",
            "rate_limit",
            "retry_policy",
            "contact_enrichment_api",
            "discovery_mode",
            "scrapling_spider",
            "contact_email",
            "contact_phone",
            "email_result",
            "phone_result",
            "runner",
            "native",
            "concurrent_requests_per_domain",
            "checkpoint_interval_seconds",
            "max_blocked_retries",
            "source_urls",
            "scraping",
            "scrapling",
            "proxy",
            "proxies",
            "SCRAPING_PROXY_URL",
        ],
    )
    assert_text_contains(
        "skills/product-loader/SKILL.md",
        ["Optional product catalog file with multiple SKUs", "select the matching product from the catalog"],
    )
    assert_text_contains(
        "skills/company-research/SKILL.md",
        ["official website contact search", "contact_email", "contact_phone", "email_result", "phone_result"],
    )


def validate_pipeline_tools_contract() -> None:
    assert_text_contains(
        "skills/prospect-discovery/SKILL.md",
        ["tools/collect_prospects.py", "tools/scrapling_spider_runner.py", "tools/scrapling_mcp_server.py", "search tasks", "prospects.raw.csv", "--product-query", "--sku"],
    )
    assert_text_contains(
        "skills/trade-workflow-router/SKILL.md",
        ["output format", "--formats", "recommended default"],
    )
    assert_text_contains(
        "skills/prospect-list-enrichment/SKILL.md",
        ["tools/batch_prospect_pipeline.py", "prospects.enriched.xlsx", "email_drafts.xlsx", "contact_email", "contact_phone", "email_result", "phone_result", "--product-query", "--sku"],
    )
    assert_text_contains(
        "skills/decision-maker-finder/SKILL.md",
        ["tools/decision_maker_finder.py", "role", "email_status", "source_url", "contact_search", "phone_result", "official website contact search", "没有"],
    )
    assert_text_contains(
        "docs/deployment.md",
        [
            "scrapling",
            "scrapling-fetcher",
            "scrapling install",
            "scrapling-dynamic",
            "scrapling-stealthy",
        ],
    )


def validate_evidence_contract() -> None:
    assert_text_contains(
        "skills/trade-workflow-router/SKILL.md",
        [
            "run the tool",
            "do not output company facts",
            "fetched evidence",
        ],
    )
    assert_text_contains(
        "skills/company-research/SKILL.md",
        [
            "run tools/batch_prospect_pipeline.py",
            "evidence url",
            "do not output company facts without fetched evidence",
            "fetch_failed",
            "no_evidence",
        ],
    )
    assert_text_contains(
        "skills/prospect-list-enrichment/SKILL.md",
        [
            "research_reports.json",
            "fetched evidence",
            "no generated rows",
        ],
    )
    assert_text_contains(
        "skills/email-crafting/SKILL.md",
        [
            "blocked_no_evidence",
            "personalization_evidence",
            "do not invent",
        ],
    )
    assert_text_contains(
        "skills/prospect-scoring/SKILL.md",
        [
            "no_evidence",
            "fetch_failed",
            "manual_review",
        ],
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
            "tools/scrapling_spider_runner.py",
            "tools/scrapling_mcp_server.py",
            "tools/batch_prospect_pipeline.py",
            "tools/decision_maker_finder.py",
            "tools/render_quotation.py",
            "ask the user to choose",
        ],
    )


def validate_quick_start_example() -> None:
    assert_text_contains("docs/quick-start.md", ["SKU CT-200A"])


def validate_bootstrap_contract() -> None:
    assert_text_contains(
        "README.md",
        [
            "https://github.com/Xuxchloris/hermes-export-skills.git",
            "bootstrap.sh",
            "bootstrap.ps1",
            "raw.githubusercontent.com/Xuxchloris/hermes-export-skills/main/bootstrap.sh",
            "raw.githubusercontent.com/Xuxchloris/hermes-export-skills/main/bootstrap.ps1",
        ],
    )
    assert_text_contains(
        "bootstrap.sh",
        ["Xuxchloris/hermes-export-skills.git", "requirements.txt", "install.sh", "create-profile.sh", "HERMES_HOME"],
    )
    assert_text_contains(
        "bootstrap.ps1",
        ["Xuxchloris/hermes-export-skills.git", "requirements.txt", "install.ps1", "create-profile.ps1", "HERMES_HOME"],
    )
    assert_text_contains(
        "install.sh",
        ["tools", "collect_prospects.py", "scrapling_prospect_spider.py", "scrapling_spider_runner.py", "scrapling_mcp_server.py", "batch_prospect_pipeline.py", "decision_maker_finder.py", "render_quotation.py"],
    )
    assert_text_contains(
        "install.ps1",
        ["tools", "collect_prospects.py", "scrapling_prospect_spider.py", "scrapling_spider_runner.py", "scrapling_mcp_server.py", "batch_prospect_pipeline.py", "decision_maker_finder.py", "render_quotation.py"],
    )
    assert_text_contains(
        "create-profile.sh",
        ["tools", "PRODUCTS.catalog.example.yaml", "collect_prospects.py"],
    )
    assert_text_contains(
        "create-profile.ps1",
        ["tools", "PRODUCTS.catalog.example.yaml", "collect_prospects.py"],
    )


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
    validate_evidence_contract()
    validate_router_contract()
    validate_quick_start_example()
    validate_bootstrap_contract()
    print("PASS: skill package structure and required content are valid")


if __name__ == "__main__":
    main()
