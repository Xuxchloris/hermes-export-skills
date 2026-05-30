---
name: prospect-scoring
description: Use when a trade agent needs to rank, qualify, prioritize, segment, score, or reject overseas prospects based on product fit, channel value, decision-maker access, market relevance, and risk
---

# Prospect Scoring

## Overview

Score prospects with transparent evidence so the user knows who to contact first. The score is a decision aid, not a claim that the prospect is ready to buy.

## When to Use

Use this skill after `company-research` has produced facts and evidence for a prospect, or when the user uploads a prospect list and asks which companies deserve outreach.

Do not use it when there is no product context.

## Inputs

- Product context from `product-loader`
- Company research output
- Target market rules from `MARKET.yaml`
- Optional contact availability data

## Outputs

```json
{
  "score": 0,
  "priority": "A|B|C|D",
  "score_breakdown": {},
  "recommended_action": "",
  "evidence_status": "verified|no_evidence|fetch_failed",
  "reason": "",
  "evidence": [],
  "risk_notes": []
}
```

## Procedure

1. Score product and category fit from 0 to 40.
2. Score channel value from 0 to 20.
3. Score decision-maker access from 0 to 15.
4. Score target-market value from 0 to 10.
5. Score website quality and business activity from 0 to 10.
6. Apply risk adjustment from 0 to -10 for weak evidence, unrelated business, suspicious contact data, or compliance concerns.
7. If evidence status is `fetch_failed` or `no_evidence`, cap priority at D and set `recommended_action` to `manual_review`.
8. If no product or channel evidence was fetched, do not assign A or B even when the market is relevant.
9. Assign priority:
   - A: 80-100, contact first
   - B: 60-79, contact after manual review
   - C: 40-59, keep for monitoring or enrichment
   - D: 0-39, do not contact
10. Provide a recommended next action.

## Verification

- Score breakdown totals equal final score.
- Priority matches the score range.
- A or B priority requires fetched evidence for product or channel fit.
- A-level prospects include at least two evidence points.
- D-level prospects are not recommended for outreach.
- Risk notes explain every deduction.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Giving high score because the company is large | Product fit must carry the most weight |
| Ignoring missing decision-maker data | Reflect it in the access score |
| Hiding risk deductions | List each risk note |
| Treating score as purchase intent | Explain that score means development priority |
