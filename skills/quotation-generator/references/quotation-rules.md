# Quotation Rules

Required for quotation draft:

- Buyer name
- SKU
- Quantity
- Unit price
- Currency
- Incoterm
- Payment terms
- Product size
- Packing size
- Lead time
- Validity

Blocking conditions:

- Missing unit price
- Missing SKU
- Quantity below MOQ without approval
- CIF/DDP request without freight data
- Certification claim not present in product data

Export requirements:

- HTML export uses `skills/quotation-generator/templates/quotation.html`.
- PDF export is generated from the HTML quotation after the draft data is inserted.
- Excel export includes `Quotation`, `Items`, `Terms`, and `Review Notes` sheets.
- Export filename format is `quotation-<quotation_number>-<buyer>-draft.<ext>`.
- Export is blocked when quotation status is `blocked`.
- Every exported file keeps the draft label until human approval.
- Every exported file records `human_review_required`.
