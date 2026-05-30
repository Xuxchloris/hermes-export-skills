---
name: prospect-list-enrichment
description: Use when a trade agent needs to clean, deduplicate, normalize, enrich, or prepare CSV and Excel prospect lists before company research, scoring, or campaign planning
---

# Prospect List Enrichment

## Overview

Prepare CSV and Excel prospect lists for research and scoring. The core rule is to preserve source evidence while turning inconsistent rows into a reviewable company-level queue.

Do not create generated company rows. Every enriched row must come from the user's file or a configured collection output.

## When to Use

Use this skill when the user provides a CSV or Excel customer list, asks to remove duplicates, wants missing fields flagged, or needs a batch queue for company research.

Use `prospect-discovery` first when the user needs a sourcing strategy instead of list processing.

## Inputs

- CSV or Excel prospect list
- Product context from `product-loader`
- Market rules from `MARKET.yaml`
- Optional discovery output from `prospect-discovery`

## Outputs

```json
{
  "input_rows": 0,
  "unique_companies": 0,
  "duplicate_rows": [],
  "ready_for_research": [],
  "needs_review": [],
  "excluded_rows": [],
  "output_columns": [],
  "next_steps": ["company-research", "prospect-scoring"]
}
```

## Procedure

1. Run `python tools/batch_prospect_pipeline.py --input <prospects.csv|xlsx> --product <PRODUCT.yaml> --market <MARKET.yaml> --tone <TONE.yaml> --discovery <DISCOVERY.yaml> --output-dir <folder>` when one-step batch output is needed.
2. If the product file is a catalog and the user names one product, add `--product-query <name>` or `--sku <sku>` instead of editing the catalog.
3. Read CSV or Excel rows without changing the original file.
4. Normalize column names and map available values to company name, website, country, business type, source URL, source note, and contact clue.
5. Normalize websites by domain and deduplicate rows by domain first, then by normalized company name and country.
6. Preserve all source URLs and merge useful source notes when duplicates are combined.
7. Mark rows without company name or website as `needs_review`.
8. Mark rows outside the target market or unrelated to the product category as `excluded_rows` with a reason.
9. Write `prospects.enriched.xlsx`, `research_reports.json`, `scores.xlsx`, and `email_drafts.xlsx` when using the batch pipeline.
10. Treat `research_reports.json` as the source of fetched evidence for scoring and emails.
11. Do not fill missing company facts from assumptions; use `needs_review`, `fetch_failed`, or `no_evidence`.
12. Send research-ready rows to `company-research`; send researched rows to `prospect-scoring`.

## Verification

- Original input file remains unchanged.
- Batch output includes `prospects.enriched.xlsx`, `research_reports.json`, `scores.xlsx`, and `email_drafts.xlsx`.
- Duplicate handling preserves source evidence.
- Every ready row includes company name, website, and source URL.
- Missing fields are listed instead of guessed.
- No generated rows appear in output workbooks.
- Scoring and email drafts are based on fetched evidence.
- Research happens before scoring.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Deduplicating only by display name | Prefer normalized website domain |
| Dropping source URLs during merge | Preserve every useful source record |
| Treating missing fields as empty facts | Mark them for review |
| Scoring raw rows immediately | Run company research first |
