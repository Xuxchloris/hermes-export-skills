from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse

try:  # Support both `python tools/x.py` and `from tools.x import ...`.
    from .trade_utils import fetch_url, parse_html, website_key
except ImportError:  # pragma: no cover - script execution path.
    from trade_utils import fetch_url, parse_html, website_key


@dataclass
class SourceSeed:
    url: str
    name: str = ""
    source_type: str = ""
    country: str = ""
    business_type: str = ""


class AnchorTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._current_href: str = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._current_href = ""
            self._current_text = []
            for name, value in attrs:
                if name.lower() == "href" and value:
                    self._current_href = value

    def handle_data(self, data: str) -> None:
        if self._current_href and data.strip():
            self._current_text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href:
            text = " ".join(self._current_text).strip()
            self.links.append({"href": self._current_href, "text": text})
            self._current_href = ""
            self._current_text = []


def _first_region(discovery: dict[str, Any]) -> str:
    regions = discovery.get("default_regions", [])
    return str(regions[0]) if regions else ""


def _seed_entries(discovery: dict[str, Any]) -> list[SourceSeed]:
    spider_cfg = discovery.get("scrapling_spider", {})
    raw_sources = spider_cfg.get("source_urls", [])
    seeds: list[SourceSeed] = []
    for item in raw_sources:
        if isinstance(item, str):
            seeds.append(SourceSeed(url=item, country=_first_region(discovery)))
            continue
        if isinstance(item, dict):
            url = str(item.get("url", "")).strip()
            if not url:
                continue
            seeds.append(
                SourceSeed(
                    url=url,
                    name=str(item.get("name", "")).strip(),
                    source_type=str(item.get("source_type", "")).strip(),
                    country=str(item.get("country", "")).strip() or _first_region(discovery),
                    business_type=str(item.get("business_type", "")).strip(),
                )
            )
    return seeds


def _product_terms(product_config: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for product in product_config.get("products", []):
        for key in ["name", "category", "sku", "hs_code"]:
            value = product.get(key)
            if value:
                terms.append(str(value))
        terms.extend(str(item) for item in product.get("keywords", []))
        terms.extend(str(item) for item in product.get("target_applications", []))
    seen = set()
    return [term for term in terms if term and not (term.lower() in seen or seen.add(term.lower()))]


def _source_matches_product(text: str, links: list[dict[str, str]], terms: list[str]) -> bool:
    lowered = text.lower()
    if any(term.lower() in lowered for term in terms):
        return True
    for link in links:
        link_text = link.get("text", "").lower()
        href = link.get("href", "").lower()
        if any(term.lower() in link_text or term.lower() in href for term in terms):
            return True
    return False


def _extract_rows(seed: SourceSeed, html: str, terms: list[str]) -> list[dict[str, Any]]:
    parser = AnchorTextParser()
    parser.feed(html)
    text, _ = parse_html(html)
    rows: list[dict[str, Any]] = []
    source_host = urlparse(seed.url).netloc.lower()

    for link in parser.links:
        href = link.get("href", "").strip()
        if not href:
            continue
        absolute = urljoin(seed.url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        if not link.get("text", "").strip():
            continue
        if source_host and parsed.netloc.lower() == source_host and parsed.path in {"", "/"}:
            continue
        rows.append(
            {
                "company_name": link["text"].strip(),
                "website": absolute,
                "country": seed.country,
                "business_type": seed.business_type,
                "source_url": seed.url,
                "evidence_summary": f"{seed.name or seed.source_type or 'source page'}: {link['text'].strip()}",
                "risk_notes": seed.source_type,
                "_matched": _source_matches_product(text, parser.links, terms),
            }
        )
    return rows


def collect_from_sources(discovery: dict[str, Any], product_config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    spider_cfg = discovery.get("scrapling_spider", {})
    seeds = _seed_entries(discovery)
    scraping = discovery.get("scraping")
    terms = _product_terms(product_config)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen_sites: set[str] = set()

    for seed in seeds:
        try:
            html = fetch_url(seed.url, scraping)
        except Exception as error:  # noqa: BLE001 - report source failure for review.
            errors.append({"source_url": seed.url, "error": str(error)})
            continue

        extracted = _extract_rows(seed, html, terms)
        for row in extracted:
            if terms and not row.pop("_matched", False):
                row["risk_notes"] = (row["risk_notes"] + "; " if row["risk_notes"] else "") + "no product keyword on source page"
            website_host = urlparse(row["website"]).netloc.lower()
            source_host = urlparse(row["source_url"]).netloc.lower()
            key = row["website"].lower() if website_host == source_host else website_key(row["website"]) or row["website"].lower()
            if key in seen_sites:
                continue
            seen_sites.add(key)
            rows.append(row)

    report = {
        "source_status": "verified" if rows else "source_unavailable",
        "sources_checked": len(seeds),
        "candidates_found": len(rows),
        "errors": errors,
        "discovery_mode": "scrapling_spider",
    }
    return rows, report


def main() -> int:
    raise SystemExit("Use this module through tools/collect_prospects.py")


if __name__ == "__main__":
    main()
