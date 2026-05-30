# Product Schema Reference

Recommended fields:

| Field | Required For | Notes |
| --- | --- | --- |
| `sku` | matching, quotation | Stable product identifier |
| `name` | all workflows | English product name preferred |
| `hs_code` | prospecting | Optional but useful for trade data |
| `product_size` | quotation | Required for specification sheet |
| `packing_size` | quotation | Required for CBM and logistics checks |
| `moq` | quotation | Required before commercial offer |
| `lead_time_days` | quotation | Use range when exact date is unknown |
| `certifications` | outreach | Only list verified certifications |
