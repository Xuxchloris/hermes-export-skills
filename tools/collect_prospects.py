from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from scrapling_prospect_spider import collect_from_sources
from scrapling_spider_runner import apply_runtime_sources, collect_native_spider
from trade_utils import load_json_path, load_yaml, render_template, select_product_config, sleep_for_rate_limit, write_csv, write_json


NO_CONTACT = "没有"
PROSPECT_FIELDS = [
    "company_name",
    "website",
    "country",
    "business_type",
    "source_url",
    "evidence_summary",
    "risk_notes",
    "contact_email",
    "contact_phone",
    "email_result",
    "phone_result",
]


def with_contact_defaults(row: dict[str, Any]) -> dict[str, Any]:
    contact_email = str(row.get("contact_email") or row.get("email") or "").strip()
    contact_phone = str(row.get("contact_phone") or row.get("phone") or "").strip()
    if contact_email == NO_CONTACT:
        contact_email = ""
    if contact_phone == NO_CONTACT:
        contact_phone = ""
    return {
        **row,
        "contact_email": contact_email or NO_CONTACT,
        "contact_phone": contact_phone or NO_CONTACT,
        "email_result": "found" if contact_email else NO_CONTACT,
        "phone_result": "found" if contact_phone else NO_CONTACT,
    }


def product_keywords(product_config: dict[str, Any]) -> list[str]:
    keywords: list[str] = []
    for product in product_config.get("products", []):
        if product.get("name"):
            keywords.append(product["name"])
        keywords.extend(product.get("keywords", []))
        keywords.extend(product.get("target_applications", []))
    seen = set()
    return [item for item in keywords if item and not (item.lower() in seen or seen.add(item.lower()))]


def build_search_tasks(discovery: dict[str, Any], product_config: dict[str, Any]) -> list[dict[str, str]]:
    regions = discovery.get("default_regions", [])
    sources = discovery.get("allowed_sources", [])
    rows = []
    for keyword in product_keywords(product_config):
        for region in regions:
            for source in sources:
                rows.append(
                    {
                        "keyword": keyword,
                        "region": region,
                        "source_type": source,
                        "suggested_query": f'{keyword} {region} "{source}" importer distributor wholesaler',
                        "status": "ready_for_collection",
                    }
                )
    return rows


def api_request(api: dict[str, Any], variables: dict[str, Any]) -> dict[str, Any]:
    method = api.get("method", "GET").upper()
    endpoint = render_template(api.get("endpoint", ""), variables)
    headers = dict(api.get("headers") or {})
    key_env = api.get("api_key_env") or ""
    if key_env and os.environ.get(key_env):
        headers[api.get("auth_header", "Authorization")] = f"{api.get('auth_scheme', 'Bearer')} {os.environ[key_env]}"

    params = render_template(api.get("query_params") or {}, variables)
    body = None
    if method == "GET" and params:
        separator = "&" if "?" in endpoint else "?"
        endpoint = endpoint + separator + urlencode(params)
    elif params:
        body = json.dumps(render_template(api.get("request_body_template") or params, variables)).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    request = Request(endpoint, data=body, headers=headers, method=method)
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def collect_from_api(discovery: dict[str, Any], product_config: dict[str, Any]) -> list[dict[str, Any]]:
    api = discovery.get("collection_api", {})
    mapping = api.get("response_mapping", {})
    pagination = api.get("pagination", {})
    rate_limit = api.get("rate_limit", {}).get("requests_per_minute", 30)
    rows: list[dict[str, Any]] = []

    for keyword in product_keywords(product_config):
        for region in discovery.get("default_regions", []):
            for page in range(1, int(pagination.get("max_pages", 1)) + 1):
                variables = {"keyword": keyword, "region": region, "page": page, "page_size": pagination.get("page_size", 50)}
                response = api_request(api, variables)
                items = load_json_path(mapping.get("items_path", "items"), response) or []
                for item in items:
                    rows.append(
                        {
                            "company_name": load_json_path(mapping.get("company_name", "company_name"), item) or "",
                            "website": load_json_path(mapping.get("website", "website"), item) or "",
                            "country": load_json_path(mapping.get("country", "country"), item) or region,
                            "business_type": load_json_path(mapping.get("business_type", "business_type"), item) or "",
                            "source_url": load_json_path(mapping.get("source_url", "source_url"), item) or api.get("endpoint", ""),
                            "evidence_summary": f"Collected for keyword '{keyword}' in {region}.",
                            "risk_notes": "",
                            "contact_email": load_json_path(mapping.get("email", "email"), item) or "",
                            "contact_phone": load_json_path(mapping.get("phone", "phone"), item) or "",
                        }
                    )
                sleep_for_rate_limit(int(rate_limit))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect prospect candidates from configured discovery sources")
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
    discovery = load_yaml(args.discovery)
    discovery = apply_runtime_sources(discovery, args.source_url, args.source_name, args.source_type, args.source_country)
    product_config = load_yaml(args.product)
    product_config = select_product_config(product_config, args.product_query, args.sku)
    api = discovery.get("collection_api", {})
    spider_cfg = discovery.get("scrapling_spider", {})
    discovery_mode = str(discovery.get("discovery_mode", "")).strip().lower()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if (
        discovery_mode in {"native_scrapling_spider", "scrapling_spider"}
        or spider_cfg.get("enabled")
    ) and spider_cfg.get("runner") != "source_collector":
        rows, report = collect_native_spider(discovery, product_config)
        rows = [with_contact_defaults(row) for row in rows]
        outputs = {"report": str(args.output_dir / "crawl_report.json")}
        if rows:
            write_csv(args.output_dir / "prospects.raw.csv", rows, PROSPECT_FIELDS)
            write_json(args.output_dir / "prospects.raw.json", rows)
            outputs["csv"] = str(args.output_dir / "prospects.raw.csv")
            outputs["json"] = str(args.output_dir / "prospects.raw.json")
            print(f"Raw prospects: {args.output_dir / 'prospects.raw.csv'}")
        else:
            print(f"Source status: {report['source_status']}")
        report["outputs"] = outputs
        write_json(args.output_dir / "crawl_report.json", report)
        return 0

    if spider_cfg.get("runner") == "source_collector":
        rows, report = collect_from_sources(discovery, product_config)
        rows = [with_contact_defaults(row) for row in rows]
        write_json(args.output_dir / "crawl_report.json", report)
        if rows:
            write_csv(args.output_dir / "prospects.raw.csv", rows, PROSPECT_FIELDS)
            write_json(args.output_dir / "prospects.raw.json", rows)
            print(f"Raw prospects: {args.output_dir / 'prospects.raw.csv'}")
        else:
            print(f"Source status: {report['source_status']}")
        return 0

    if api.get("provider", "none") == "none" or not api.get("endpoint"):
        tasks = build_search_tasks(discovery, product_config)
        write_csv(args.output_dir / "prospect_search_tasks.csv", tasks, ["keyword", "region", "source_type", "suggested_query", "status"])
        write_json(args.output_dir / "prospect_search_tasks.json", tasks)
        print(f"Search tasks: {args.output_dir / 'prospect_search_tasks.csv'}")
        return 0

    rows = [with_contact_defaults(row) for row in collect_from_api(discovery, product_config)]
    write_csv(args.output_dir / "prospects.raw.csv", rows, PROSPECT_FIELDS)
    write_json(args.output_dir / "prospects.raw.json", rows)
    print(f"Raw prospects: {args.output_dir / 'prospects.raw.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
