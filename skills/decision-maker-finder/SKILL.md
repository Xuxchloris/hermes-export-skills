---
name: decision-maker-finder
description: Use when a trade agent needs decision-maker clues, buyer roles, purchasing manager signals, sourcing contacts, category manager hints, contact-page evidence, or email validation status
---

# Decision Maker Finder

## Overview

Find role-level contact clues from company pages and optional enrichment API results. The core rule is to output decision-maker evidence with `source_url`, `role`, and `email_status` while also forcing a separate email and phone search across checked pages.

## When to Use

Use this skill when the user asks who to contact, whether a company has purchasing clues, or how to enrich a prospect with decision-maker signals.

Use `company-research` first when the company fit is still unknown.

## Inputs

- Company website
- Company name and country, if available
- Decision-maker roles from `MARKET.yaml`
- Contact enrichment settings from `DISCOVERY.yaml`
- Optional output from `prospect-list-enrichment`

## Outputs

```json
{
  "website": "",
  "pages_checked": [],
  "contact_search": {
    "email_result": "found|没有",
    "phone_result": "found|没有",
    "emails": [],
    "phones": []
  },
  "candidates": [
    {
      "name": "",
      "role": "",
      "email": "",
      "email_status": "missing|invalid_format|format_valid|domain_match|api_verified",
      "phone": "",
      "phone_status": "missing|found",
      "confidence": "low|medium|high",
      "source_url": "",
      "evidence": ""
    }
  ],
  "review_notes": []
}
```

## Procedure

1. Run `python tools/decision_maker_finder.py --website <url> --output <decision_makers.json>` when file output is needed.
2. Check company pages such as homepage, about, contact, team, catalog, and product pages.
3. Always run forced contact search across every checked page for email and phone values, even when no role clue is found.
4. If email or phone is not found, output `email_result: "没有"` or `phone_result: "没有"` in `contact_search`.
5. Look for role clues such as Owner, Founder, Purchasing Manager, Sourcing Manager, Category Manager, Procurement Manager, and Buyer.
6. Validate email syntax and mark whether the email domain appears company-level.
7. If a phone appears near a role clue, include it with `phone_status`.
8. If `DISCOVERY.yaml` has a configured contact enrichment API, use its schema and record API results as additional evidence.
9. Return role, name if visible, email if visible, phone if visible, confidence, source URL, and evidence text.
10. Pass useful candidates into `prospect-scoring` as decision-maker access evidence.

## Verification

- Every candidate includes a role and source URL.
- `contact_search` is present even when there are no candidates.
- `email_status` is present for every candidate.
- Missing email or phone search results are written as `没有`.
- A role clue is not described as confirmed purchase intent.
- API keys are read from environment variables, not written into output files.
- Low-confidence clues remain review items.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Treating a role mention as a named contact | Separate role, name, and evidence |
| Calling a generic email verified | Use `format_valid` unless stronger evidence exists |
| Leaving phone or email blank after search | Put `没有` in `contact_search` result fields |
| Dropping source pages | Keep `source_url` for every candidate |
| Sending outreach automatically | Return candidates for human review |
