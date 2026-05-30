---
name: product-loader
description: Use when a trade agent needs product catalog, SKU, specification, packaging, price-rule, MOQ, certification, lead-time, or factory profile data before research, outreach, scoring, or quotation work
---

# Product Loader

## Overview

Load product and company facts from configured files before any trade workflow uses them. The core rule is simple: no product claim, price, certification, MOQ, packaging size, or delivery promise may be invented.

## When to Use

Use this skill when the user asks about product matching, customer development, quotations, product introductions, catalogs, factory advantages, packaging details, model numbers, or delivery terms.

Do not use it to research a prospect website or write the final email body by itself.

## Inputs

- `data/config/PRODUCT.yaml`
- `data/config/PRICING.yaml`
- User-provided product notes in the current conversation

## Outputs

```json
{
  "company": {},
  "products": [],
  "pricing_rules": [],
  "missing_fields": [],
  "safe_to_quote": false
}
```

## Procedure

1. Read `PRODUCT.yaml` and extract company profile, SKUs, product names, HS codes, materials, dimensions, packaging, MOQ, lead time, certifications, applications, and keywords.
2. Read `PRICING.yaml` and extract currency, incoterm, validity, payment terms, tier prices, sample fees, and remarks.
3. Prefer current conversation facts only when the user explicitly overrides the configured file.
4. Mark missing fields instead of guessing them.
5. Set `safe_to_quote` to `true` only when SKU, quantity, unit price, incoterm, payment terms, validity, product size, and packing size are present.
6. Return a compact product context for downstream skills.

## Verification

- Product names and SKUs match the source file.
- Prices come only from `PRICING.yaml` or explicit user input.
- Missing price, size, packing, MOQ, incoterm, or lead time is listed in `missing_fields`.
- Certifications are not added unless present in source data.
- `safe_to_quote` is `false` when any required quotation field is missing.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Guessing a price from a similar SKU | Ask for confirmation or mark price missing |
| Treating marketing advantages as certifications | Keep certifications in a separate field |
| Using one product's packing size for another SKU | Match by exact SKU |
| Producing a formal quotation with missing freight terms | Produce a draft with human review required |
