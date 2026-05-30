from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, AsyncGenerator
from urllib.parse import urlparse

from scrapling.spiders import Request, Response, Spider

try:  # Support both `python tools/x.py` and `from tools.x import ...`.
    from .scrapling_prospect_spider import SourceSeed, _product_terms, _seed_entries, _source_matches_product
    from .trade_utils import load_yaml, select_product_config, website_key, write_csv, write_json
except ImportError:  # pragma: no cover - script execution path.
    from scrapling_prospect_spider import SourceSeed, _product_terms, _seed_entries, _source_matches_product
    from trade_utils import load_yaml, select_product_config, website_key, write_csv, write_json


def apply_runtime_sources(
    discovery: dict[str, Any],
    source_urls: list[str | dict[str, Any]] | None = None,
    source_name: str = "",
    source_type: str = "",
    source_country: str = "",
) -> dict[str, Any]:
    if not source_urls:
        return discovery

    updated = dict(discovery)
    spider_cfg = dict(updated.get("scrapling_spider", {}) or {})
    existing_sources = list(spider_cfg.get("source_urls", []) or [])
    runtime_sources: list[dict[str, str]] = []

    for item in source_urls:
        if isinstance(item, str):
            url = item.strip()
            if not url:
                continue
            runtime_sources.append(
                {
                    "url": url,
                    "name": source_name,
                    "source_type": source_type,
                    "country": source_country,
                }
            )
            continue
        if isinstance(item, dict):
            url = str(item.get("url", "")).strip()
            if not url:
                continue
            runtime_sources.append(
                {
                    "url": url,
                    "name": str(item.get("name", source_name) or source_name),
                    "source_type": str(item.get("source_type", source_type) or source_type),
                    "country": str(item.get("country", source_country) or source_country),
                    "business_type": str(item.get("business_type", "")),
                }
            )

    if not runtime_sources:
        return discovery

    spider_cfg["enabled"] = True
    spider_cfg.setdefault("runner", "native")
    spider_cfg["source_urls"] = existing_sources + runtime_sources
    spider_cfg["_runtime_sources_count"] = len(runtime_sources)
    updated["scrapling_spider"] = spider_cfg
    updated["discovery_mode"] = "native_scrapling_spider"
    return updated


class ProspectDiscoverySpider(Spider):
    name = "hermes-prospect-discovery"

    def __init__(
        self,
        seeds: list[SourceSeed],
        product_terms: list[str],
        scraping: dict[str, Any] | None = None,
        spider_config: dict[str, Any] | None = None,
    ) -> None:
        self.seeds = seeds
        self.product_terms = product_terms
        self.scraping = scraping or {}
        self.spider_config = spider_config or {}
        self.fetch_errors: list[dict[str, str]] = []
        self.source_statuses: dict[str, str] = {}

        self.robots_txt_obey = bool(self.spider_config.get("robots_txt_obey", False))
        self.concurrent_requests = int(self.spider_config.get("concurrent_requests", 4))
        self.concurrent_requests_per_domain = int(self.spider_config.get("concurrent_requests_per_domain", 0))
        self.download_delay = float(self.spider_config.get("crawl_delay_seconds", 0))
        self.max_blocked_retries = int(self.spider_config.get("max_blocked_retries", 3))
        super().__init__(
            crawldir=self.spider_config.get("checkpoint_dir") or None,
            interval=float(self.spider_config.get("checkpoint_interval_seconds", 300)),
        )

    def configure_sessions(self, manager: Any) -> None:
        engine = self.scraping.get("engine", "scrapling-fetcher")
        if engine in {"http", "scrapling-fetcher"}:
            from scrapling.fetchers import FetcherSession

            manager.add(
                "default",
                FetcherSession(
                    stealthy_headers=bool(self.scraping.get("stealthy_headers", True)),
                    timeout=self.scraping.get("timeout", 30),
                ),
                default=True,
            )
            return
        if engine == "scrapling-dynamic":
            from scrapling.fetchers import DynamicSession

            manager.add(
                "default",
                DynamicSession(
                    headless=bool(self.scraping.get("headless", True)),
                    network_idle=bool(self.scraping.get("network_idle", True)),
                ),
                default=True,
            )
            return
        if engine == "scrapling-stealthy":
            from scrapling.fetchers import StealthySession

            manager.add(
                "default",
                StealthySession(
                    headless=bool(self.scraping.get("headless", True)),
                    network_idle=bool(self.scraping.get("network_idle", True)),
                ),
                default=True,
            )
            return
        raise ValueError(f"Unknown scraping engine for native Spider: {engine}")

    async def start_requests(self) -> AsyncGenerator[Request, None]:
        for seed in self.seeds:
            yield Request(seed.url, meta={"seed": seed})

    async def parse(self, response: Response) -> AsyncGenerator[dict[str, Any] | Request | None, None]:
        seed = response.meta.get("seed")
        if not isinstance(seed, SourceSeed):
            seed = SourceSeed(url=response.url)

        self.source_statuses[seed.url] = f"status_{getattr(response, 'status', '')}"
        links = response.css("a")
        source_text = response.get_all_text() or ""
        link_snapshots = [
            {
                "href": str(link.attrib.get("href", "")),
                "text": (link.get_all_text() or link.text or "").strip(),
            }
            for link in links
        ]
        source_matched = _source_matches_product(source_text, link_snapshots, self.product_terms)

        for link in links:
            href = str(link.attrib.get("href", "")).strip()
            text = (link.get_all_text() or link.text or "").strip()
            if not href or not text:
                continue
            absolute = response.urljoin(href)
            parsed = urlparse(absolute)
            if parsed.scheme not in {"http", "https"}:
                continue

            risk_notes = seed.source_type
            if self.product_terms and not source_matched:
                risk_notes = (risk_notes + "; " if risk_notes else "") + "no product keyword on source page"

            yield {
                "company_name": text,
                "website": absolute,
                "country": seed.country,
                "business_type": seed.business_type,
                "source_url": seed.url,
                "evidence_summary": f"{seed.name or seed.source_type or 'source page'}: {text}",
                "risk_notes": risk_notes,
            }

    async def on_error(self, request: Request, error: Exception) -> None:
        self.fetch_errors.append({"source_url": request.url, "error": str(error)})


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        website_host = urlparse(str(row.get("website", ""))).netloc.lower()
        source_host = urlparse(str(row.get("source_url", ""))).netloc.lower()
        key = str(row.get("website", "")).lower() if website_host == source_host else website_key(str(row.get("website", "")))
        key = key or str(row.get("website", "")).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def collect_native_spider(discovery: dict[str, Any], product_config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    spider_cfg = discovery.get("scrapling_spider", {}) or {}
    seeds = _seed_entries(discovery)
    product_terms = _product_terms(product_config)
    spider = ProspectDiscoverySpider(
        seeds=seeds,
        product_terms=product_terms,
        scraping=discovery.get("scraping") or {},
        spider_config=spider_cfg,
    )
    result = spider.start()
    rows = _dedupe_rows([dict(item) for item in result.items])
    stats = result.stats.to_dict()
    report = {
        "source_status": "verified" if rows else "source_unavailable",
        "sources_checked": len(seeds),
        "candidates_found": len(rows),
        "runtime_sources_count": int(spider_cfg.get("_runtime_sources_count", 0) or 0),
        "errors": spider.fetch_errors,
        "source_http_statuses": spider.source_statuses,
        "discovery_mode": "native_scrapling_spider",
        "runner": "scrapling_native_spider",
        "spider_stats": stats,
        "paused": result.paused,
        "completed": result.completed,
    }
    return rows, report


def run_spider(
    discovery_path: Path,
    product_path: Path,
    output_dir: Path,
    product_query: str = "",
    sku: str = "",
    source_urls: list[str | dict[str, Any]] | None = None,
    source_name: str = "",
    source_type: str = "",
    source_country: str = "",
) -> dict[str, Any]:
    discovery = load_yaml(discovery_path)
    discovery = apply_runtime_sources(discovery, source_urls, source_name, source_type, source_country)
    product_config = select_product_config(load_yaml(product_path), product_query, sku)
    rows, report = collect_native_spider(discovery, product_config)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "crawl_report.json", report)
    outputs: dict[str, str] = {"report": str(output_dir / "crawl_report.json")}
    if rows:
        fields = ["company_name", "website", "country", "business_type", "source_url", "evidence_summary", "risk_notes"]
        write_csv(output_dir / "prospects.raw.csv", rows, fields)
        write_json(output_dir / "prospects.raw.json", rows)
        outputs["csv"] = str(output_dir / "prospects.raw.csv")
        outputs["json"] = str(output_dir / "prospects.raw.json")
    report["outputs"] = outputs
    write_json(output_dir / "crawl_report.json", report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run native Scrapling Spider prospect discovery")
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--product-query", default="")
    parser.add_argument("--sku", default="")
    parser.add_argument("--source-url", action="append", default=[])
    parser.add_argument("--source-name", default="")
    parser.add_argument("--source-type", default="")
    parser.add_argument("--source-country", default="")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_spider(
        args.discovery,
        args.product,
        args.output_dir,
        args.product_query,
        args.sku,
        args.source_url,
        args.source_name,
        args.source_type,
        args.source_country,
    )
    print(f"Source status: {report['source_status']}")
    if "csv" in report["outputs"]:
        print(f"Raw prospects: {report['outputs']['csv']}")
    print(f"Crawl report: {report['outputs']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
