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
7. Without a configured API, create search tasks for Google search results, trade show websites, industry directories, prospect company websites, LinkedIn public summaries, and B2B platform public pages.
8. With a configured API, produce `prospects.raw.csv` and `prospects.raw.json`.
9. Build keyword groups from product names, HS codes, applications, buyer types, target regions, and channel terms.
10. Add exclude terms for jobs, consumer reviews, unrelated retail-only pages, marketplaces without seller websites, and irrelevant industries.
11. Keep each candidate tied to a source URL, company-level signal, and reviewable evidence summary.
12. For each candidate, record company name, website, country, business type, source URL, evidence summary, and risk notes.
13. Send candidates with evidence to `company-research`; send researched prospects to `prospect-scoring`.

## Verification

- `DISCOVERY.yaml` is checked before asking for collection API details.
- Missing API is recorded as `none` instead of repeatedly asking.
- Search tasks are written when no collection API is configured.
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
| Saving raw API keys in project files | Save only the environment variable name |
| Keeping weak source records | Store source URL, date, and evidence summary |
| Mixing company and contact evidence | Keep discovery focused on company-level signals |
