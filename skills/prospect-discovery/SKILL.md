---
name: prospect-discovery
description: Use when a trade agent needs compliant prospect discovery, customer sourcing strategy, lead source planning, search keywords, public directory review, or collection API setup before company research
---

# Prospect Discovery

## Overview

Create a customer discovery strategy before research and scoring. The core rule is to use approved business sources, record where each lead came from, and pass candidates to `company-research` and `prospect-scoring` for evidence review.

## When to Use

Use this skill when the user asks how to find overseas customers, build a prospect list, plan search keywords, use a collection API, review public directories, or prepare leads for outreach.

Use it for company-level discovery planning and evidence collection before outreach drafting.

## Inputs

- Product context from `product-loader`
- Market rules from `MARKET.yaml`
- Discovery settings from `DISCOVERY.yaml`
- Target countries or regions
- Approved collection API details, if provided by the user

## Outputs

```json
{
  "collection_api_status": "configured|none|needs_user_input",
  "keyword_strategy": [],
  "target_regions": [],
  "exclude_terms": [],
  "allowed_sources": [],
  "candidate_fields": [],
  "source_status": "verified|search_tasks_only|source_unavailable",
  "source_evidence_rules": [],
  "risk_notes": [],
  "next_steps": ["company-research", "prospect-scoring"]
}
```

## Procedure

1. Read `DISCOVERY.yaml` before asking about collection tooling.
2. If `collection_api.provider` is missing, ask the user once for the collection API. If there is no API, write `none` into `DISCOVERY.yaml` when file editing is available.
3. If the user provides an approved API after setup, write its provider, endpoint, method, API key environment variable, auth header, query parameters, response mapping, pagination, rate limit, and retry policy into `DISCOVERY.yaml`; keep raw secrets in environment variables.
4. Read `scraping.engine`. Use `scrapling-fetcher` only for crawling company pages after a candidate is already known. Do not use browser navigation as the default customer-discovery path.
5. Run `python tools/collect_prospects.py --discovery <DISCOVERY.yaml> --product <PRODUCT.yaml> --output-dir <folder>` when file output is needed.
6. If the user only names a product or SKU, pass `--product-query` or `--sku` instead of rewriting `PRODUCT.yaml`.
7. If the agent has already identified source pages during the task, pass them at runtime with `--source-url` instead of editing `DISCOVERY.yaml`.
8. If `discovery_mode` is `native_scrapling_spider`, `scrapling_spider.enabled` is true, or runtime `--source-url` values are provided, `tools/collect_prospects.py` routes to `tools/scrapling_spider_runner.py`, uses Scrapling's native `Spider`, and writes `crawl_report.json`.
9. If the agent has MCP access configured, call `tools/scrapling_mcp_server.py` through the `collect_prospects` MCP tool and pass runtime `source_urls` for the same native Spider workflow.
10. When neither a configured API, configured `scrapling_spider.source_urls`, nor runtime source URLs are available, create search tasks for Google search results, trade show websites, industry directories, prospect company websites, LinkedIn public summaries, and B2B platform public pages.
11. If the tool outputs only `prospect_search_tasks.csv`, stop and report `source_status: "search_tasks_only"`; ask for a collection API, a user-provided list, or permission to process a specific approved source.
12. Do not manually browse arbitrary B2B platforms after search tasks are generated.
13. Do not return a numbered customer list unless it comes from `prospects.raw.csv`, a user-provided prospect file, or fetched company pages with source URLs.
14. If sources cannot be accessed or provide no usable company records, return `source_status: "source_unavailable"` and do not fill the gap with industry knowledge.
15. With a configured API, produce `prospects.raw.csv` and `prospects.raw.json`.
16. Build keyword groups from product names, HS codes, applications, buyer types, target regions, and channel terms.
17. Add exclude terms for jobs, consumer reviews, unrelated retail-only pages, marketplaces without seller websites, and irrelevant industries.
18. Keep each candidate tied to a source URL, company-level signal, and reviewable evidence summary.
19. For each candidate, record company name, website, country, business type, source URL, evidence summary, and risk notes.
20. Send candidates with evidence to `company-research`; send researched prospects to `prospect-scoring`.

## Verification

- `DISCOVERY.yaml` is checked before asking for collection API details.
- Missing API is recorded as `none` instead of repeatedly asking.
- Search tasks are written when no collection API is configured.
- Search tasks are not treated as customer results.
- Browser navigation is not used to continue discovery after search-task output.
- Native Scrapling spider mode accepts configured `scrapling_spider.source_urls` or runtime `--source-url` values, uses `tools/scrapling_spider_runner.py`, and writes `crawl_report.json`.
- MCP mode uses `tools/scrapling_mcp_server.py`, accepts runtime `source_urls`, and returns the same output paths as the CLI runner.
- A numbered customer list requires `prospects.raw.csv`, a user-provided prospect file, or source URLs from fetched company pages.
- `source_unavailable` is used when sources do not return usable company records.
- API collection writes `prospects.raw.csv` and `prospects.raw.json`.
- Configured APIs include response mapping, pagination, rate limit, and retry policy.
- Scrapling is the default scraping backend, and browser modes are enabled only when their dependencies are installed.
- Product or SKU selection can be passed through `--product-query` or `--sku`.
- Every candidate includes a public source URL and evidence summary.
- Every candidate depends on reviewable company-level evidence.
- Next steps include `company-research` before `prospect-scoring`.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Treating search results as verified buyers | Pass candidates to research before scoring |
| Filling a requested customer count from industry knowledge | Return `source_unavailable` or `search_tasks_only` |
| Saving raw API keys in project files | Save only the environment variable name |
| Keeping weak source records | Store source URL, date, and evidence summary |
| Mixing company and contact evidence | Keep discovery focused on company-level signals |
