# Deployment

## Local Development

Use this repository as the source of truth. Install skills into Hermes with:

```bash
./install.sh
```

Set `HERMES_HOME` if your Hermes data directory is not `~/.hermes`.

```bash
HERMES_HOME=/path/to/hermes ./install.sh
```

## Customer Profile Model

Each customer should have an isolated profile:

```text
profiles/<customer>/
  AGENTS.md
  .env.example
  data/config/PRODUCT.yaml
  data/config/PRODUCTS.catalog.yaml
  data/config/MARKET.yaml
  data/config/TONE.yaml
  data/config/PRICING.yaml
  data/config/DISCOVERY.yaml
  data/prospects/
  data/reports/
  data/emails/
  data/quotations/
  data/replies/
  data/follow-ups/
  tools/
    collect_prospects.py
    batch_prospect_pipeline.py
    decision_maker_finder.py
    render_quotation.py
```

Keep private API keys and real customer data out of Git.

## Updating Skills

Pull the repository, run the installer again, then restart the Hermes session so the latest skill text is loaded.

## Batch Tools

The quick installer also copies automation scripts into each profile's `tools/` directory. Run them from the profile directory when Hermes is using an installed profile:

```bash
python tools/collect_prospects.py --discovery data/config/DISCOVERY.yaml --product data/config/PRODUCT.yaml --output-dir data/prospects
python tools/batch_prospect_pipeline.py --input data/prospects/prospects.raw.csv --product data/config/PRODUCT.yaml --market data/config/MARKET.yaml --tone data/config/TONE.yaml --discovery data/config/DISCOVERY.yaml --output-dir data/reports
python tools/decision_maker_finder.py --website https://example.com --output data/reports/decision-makers.json
```

## Scrapling Backend

The default scraper uses `scrapling-fetcher`. Install dependencies before running batch crawling tools:

```bash
python -m pip install -r requirements.txt
```

Run `scrapling install` only for `scrapling-dynamic` or `scrapling-stealthy`. Set `scraping.engine` in `DISCOVERY.yaml` to `scrapling-fetcher`, `scrapling-dynamic`, `scrapling-stealthy`, or `http`.
