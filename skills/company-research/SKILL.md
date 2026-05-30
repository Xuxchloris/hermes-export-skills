---
name: company-research
description: Use when a trade agent needs to analyze a prospect company, website, business type, product line, purchasing possibility, red flags, decision-maker clues, or personalization evidence
---

# Company Research

## Overview

Turn prospect website content into evidence-backed sales intelligence. The core rule is to separate observed facts from inferred opportunities.

## When to Use

Use this skill when the user provides a company name, website URL, prospect list row, LinkedIn snippet, trade-show exhibitor page, or distributor page and asks whether the company is worth developing.

Do not use it to fabricate contact names or emails.

## Inputs

- Company name
- Website URL or pasted website content
- Tool output from `tools/batch_prospect_pipeline.py` or `tools/decision_maker_finder.py` when a URL/list is provided
- Product context from `product-loader`
- Market context from `MARKET.yaml`

## Outputs

```json
{
  "company_summary": "",
  "business_type": "",
  "main_products": [],
  "target_customers": "",
  "countries_served": [],
  "evidence": [],
  "evidence_status": "verified|no_evidence|fetch_failed",
  "possible_needs": [],
  "personalization_points": [],
  "decision_maker_clues": [],
  "contact_email": "",
  "contact_phone": "",
  "email_result": "found|没有",
  "phone_result": "found|没有",
  "red_flags": [],
  "confidence": "low|medium|high"
}
```

## Procedure

1. If the user provides a URL or list file and no fetched content, run `tools/batch_prospect_pipeline.py` or the relevant crawler-backed tool first. Required command reference: run tools/batch_prospect_pipeline.py before scoring or email drafting.
2. Read the provided website content, browsing result, or `research_reports.json` output.
3. Do not output company facts without fetched evidence. If fetching fails, return `evidence_status: "fetch_failed"` and stop at review notes.
4. Extract observed facts: products, business type, brands, market focus, contact page, about page, and catalog clues.
5. If the input is a company name or company link, resolve the official website when possible and run official website contact search across homepage, contact, about, team, catalog, and product pages.
6. Record visible email and phone values as `contact_email` and `contact_phone`; if either value is not found, write `email_result: "没有"` or `phone_result: "没有"` instead of guessing.
7. Record every fact with an evidence URL and short evidence text.
8. Identify business type using evidence: importer, distributor, wholesaler, retailer, brand owner, manufacturer, contractor, marketplace seller, or unrelated site.
9. Compare observed facts against the product context.
10. Create `possible_needs` only when there is visible product, category, application, or channel overlap.
11. If fetched pages contain no relevant product or channel clue, return `evidence_status: "no_evidence"` and keep confidence low.
12. Create personalization points from concrete website facts, not generic praise.
13. Flag red flags: no business relevance, consumer-only content, inactive website, unverifiable contact, unrelated industry, or low-quality scraped directory.
14. Return confidence based on evidence quantity and recency.

## Verification

- Every personalization point has website evidence.
- Every observed fact includes an evidence URL.
- Official website contact search is run when a company name, website, or company link is available.
- Contact outputs include `contact_email`, `contact_phone`, `email_result`, and `phone_result`.
- Inferences are labeled as possible needs, not facts.
- No contact name is invented.
- Red flags are present when the website is weak or unrelated.
- Confidence is `low` when evidence is thin.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Calling every distributor a strong lead | Require product or channel overlap |
| Saying the company imports a product with no proof | Use "may need" and cite the clue |
| Writing generic personalization | Quote a concrete category, market, or service |
| Ignoring weak websites | Mark confidence and red flags clearly |
