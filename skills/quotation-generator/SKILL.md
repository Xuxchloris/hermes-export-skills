---
name: quotation-generator
description: Use when a trade agent needs quotation drafts, price table, SKU quote, proforma offer, MOQ, payment terms, incoterm, packing information, validity, or buyer inquiry response pricing
---

# Quotation Generator

## Overview

Generate quotation drafts from approved product and pricing data. The core rule is that missing commercial data blocks a formal quote and creates a review note.

## When to Use

Use this skill when the user asks for a quotation, price offer, PI draft, inquiry reply with pricing, SKU comparison table, quote-ready product summary, HTML quotation, PDF quotation, or Excel quotation sheet.

Do not use it to invent freight, insurance, certifications, unit price, or delivery terms.

## Inputs

- Product context from `product-loader`
- Pricing rules from `PRICING.yaml`
- Buyer name and country
- Requested SKU and quantity
- Requested incoterm and destination, if provided
- `tools/render_quotation.py` when file exports are requested

## Outputs

```json
{
  "quotation_status": "draft|blocked",
  "quotation_number": "",
  "buyer": "",
  "items": [],
  "terms": {},
  "total_amount": 0,
  "export_outputs": {
    "html": {
      "enabled": false,
      "filename": "",
      "template": "skills/quotation-generator/templates/quotation.html"
    },
    "pdf": {
      "enabled": false,
      "filename": "",
      "source": "html"
    },
    "excel": {
      "enabled": false,
      "filename": "",
      "sheets": []
    }
  },
  "human_review_required": true,
  "missing_fields": [],
  "review_notes": []
}
```

## Procedure

1. Match each requested item by exact SKU.
2. Select the correct tier price based on requested quantity.
3. Verify product size, packing size, MOQ, unit price, currency, incoterm, payment terms, lead time, and validity.
4. If the requested quantity is below MOQ, mark the quote as `blocked` unless the user approves sample pricing.
5. If CIF, DDP, or freight-included terms are requested without confirmed freight and insurance, mark freight fields as missing.
6. Calculate line totals only from approved unit prices.
7. Produce a draft quotation table and a buyer reply email draft.
8. Save the approved draft data as JSON before file export.
9. Run `python tools/render_quotation.py <quotation.json> --output-dir <folder> --formats html excel` for HTML and Excel output.
10. Add `pdf` to `--formats` when PDF output is requested. Generate PDF from the reviewed HTML layout so the printable file matches the HTML source.
11. For Excel output, create workbook sheets for `Quotation`, `Items`, `Terms`, and `Review Notes`.
12. Use export filenames in the pattern `quotation-<quotation_number>-<buyer>-draft.<ext>`.
13. Set `human_review_required` to `true` for every HTML, PDF, and Excel export until the user explicitly approves sending.
14. Add a clear human-review note before any commercial document is sent.

## Verification

- Every quoted SKU exists in product data.
- Unit prices come from pricing rules or explicit user approval.
- Quantity below MOQ is flagged.
- CIF/DDP terms are blocked without freight data.
- Draft status is used until a human approves the offer.
- `export_outputs` lists HTML, PDF, and Excel status when any export is requested.
- HTML, PDF, and Excel exports keep the draft status and human review requirement.
- PDF exports are generated from the HTML layout, not from a separate unverified structure.
- Excel exports include item rows, terms, totals, missing fields, and review notes.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Estimating freight to complete CIF | Block or ask for freight confirmation |
| Quoting a similar SKU | Require exact SKU match |
| Ignoring MOQ | Flag quantity and request approval |
| Treating draft as official PI | Label it as draft until reviewed |
