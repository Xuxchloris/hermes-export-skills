# Quick Start

1. Install Hermes according to your own runtime environment.
2. Clone this repository.
3. Install the shared skills:

```bash
./install.sh
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

4. Create a customer profile:

```bash
./create-profile.sh demo-camping-table
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\create-profile.ps1 demo-camping-table
```

5. Edit the files under:

```text
~/.hermes/profiles/demo-camping-table/data/config/
```

Key files:

```text
PRODUCT.yaml
MARKET.yaml
TONE.yaml
PRICING.yaml
DISCOVERY.yaml
```

6. Start your Hermes profile and ask:

```text
Please research this prospect website, score it for our products, and draft a first outreach email.
```

For a workflow menu, ask:

```text
外贸
```

For prospect discovery, ask:

```text
Please create a compliant prospect discovery strategy for our camping table products in the US and EU markets.
```

Generate prospect search tasks or API collection output:

```bash
python tools/collect_prospects.py --discovery templates/DISCOVERY.example.yaml --product templates/PRODUCT.example.yaml --output-dir exports/prospect-collection
```

Run the batch customer development pipeline:

```bash
python tools/batch_prospect_pipeline.py --input exports/prospect-collection/prospects.raw.csv --product templates/PRODUCT.example.yaml --market templates/MARKET.example.yaml --tone templates/TONE.example.yaml --output-dir exports/pipeline
```

Find decision-maker clues for one company:

```bash
python tools/decision_maker_finder.py --website https://example.com --output exports/decision-makers.json
```

For quotation export, ask:

```text
Please draft a quotation for SKU CT-200A, quantity 500, and prepare HTML, PDF, and Excel export outputs for human review.
```

Run the renderer with the included example:

```bash
python -m pip install -r requirements.txt
python tools/render_quotation.py examples/quotation.example.json --output-dir exports/demo --formats html excel pdf
```
