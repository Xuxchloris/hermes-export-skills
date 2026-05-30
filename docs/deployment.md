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
```

Keep private API keys and real customer data out of Git.

## Updating Skills

Pull the repository, run the installer again, then restart the Hermes session so the latest skill text is loaded.

## Batch Tools

The batch tools write output under `exports/` by default:

```bash
python tools/collect_prospects.py --discovery templates/DISCOVERY.example.yaml --product templates/PRODUCT.example.yaml --output-dir exports/prospect-collection
python tools/batch_prospect_pipeline.py --input exports/prospect-collection/prospects.raw.csv --product templates/PRODUCT.example.yaml --market templates/MARKET.example.yaml --tone templates/TONE.example.yaml --discovery templates/DISCOVERY.example.yaml --output-dir exports/pipeline
python tools/decision_maker_finder.py --website https://example.com --output exports/decision-makers.json
```

## Scrapling Backend

The default scraper uses `scrapling-fetcher`. Install dependencies before running batch crawling tools:

```bash
python -m pip install -r requirements.txt
```

Run `scrapling install` only for `scrapling-dynamic` or `scrapling-stealthy`. Set `scraping.engine` in `DISCOVERY.yaml` to `scrapling-fetcher`, `scrapling-dynamic`, `scrapling-stealthy`, or `http`.
