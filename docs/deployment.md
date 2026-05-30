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
    scrapling_prospect_spider.py
    scrapling_spider_runner.py
    scrapling_mcp_server.py
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

When `DISCOVERY.yaml` uses `discovery_mode: "native_scrapling_spider"` and provides `scrapling_spider.source_urls`, the same `collect_prospects.py` command runs the native Scrapling Spider runner and writes:

- `data/prospects/prospects.raw.csv`
- `data/prospects/prospects.raw.json`
- `data/prospects/crawl_report.json`

When no API or source URL is configured, it writes auditable search tasks instead of inventing customer records.

Run the native Spider runner directly when you want to test crawling separately from the main discovery command:

```bash
python tools/scrapling_spider_runner.py --discovery data/config/DISCOVERY.yaml --product data/config/PRODUCT.yaml --output-dir data/prospects
```

Agents can also pass task-selected source pages at runtime without modifying `DISCOVERY.yaml`:

```bash
python tools/collect_prospects.py --discovery data/config/DISCOVERY.yaml --product data/config/PRODUCT.yaml --source-url https://example.com/exhibitors --source-type trade_show --source-country "United States" --output-dir data/prospects
```

## Scrapling Backend

The default scraper uses `scrapling-fetcher`. Install dependencies before running batch crawling tools:

```bash
python -m pip install -r requirements.txt
```

Run `scrapling install` only for `scrapling-dynamic` or `scrapling-stealthy`. Set `scraping.engine` in `DISCOVERY.yaml` to `scrapling-fetcher`, `scrapling-dynamic`, `scrapling-stealthy`, or `http`.

For a fixed network egress, set `SCRAPING_PROXY_URL` in the profile environment. The scraping tools also accept `scraping.proxy` or `scraping.proxies` in `DISCOVERY.yaml`; keep private proxy credentials out of Git.

## MCP Server

The MCP entrypoint wraps the same native Spider runner:

```bash
python tools/scrapling_mcp_server.py
```

Configure your MCP-capable agent with command `python` and args `["tools/scrapling_mcp_server.py"]` from the repository or profile directory. The exposed tool is `collect_prospects`.
