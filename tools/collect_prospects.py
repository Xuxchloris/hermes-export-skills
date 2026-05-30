from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from trade_utils import load_json_path, load_yaml, render_template, sleep_for_rate_limit, write_csv, write_json


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
                        }
                    )
                sleep_for_rate_limit(int(rate_limit))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect prospect candidates from configured discovery sources")
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    discovery = load_yaml(args.discovery)
    product_config = load_yaml(args.product)
    api = discovery.get("collection_api", {})
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if api.get("provider", "none") == "none" or not api.get("endpoint"):
        tasks = build_search_tasks(discovery, product_config)
        write_csv(args.output_dir / "prospect_search_tasks.csv", tasks, ["keyword", "region", "source_type", "suggested_query", "status"])
        write_json(args.output_dir / "prospect_search_tasks.json", tasks)
        print(f"Search tasks: {args.output_dir / 'prospect_search_tasks.csv'}")
        return 0

    rows = collect_from_api(discovery, product_config)
    fields = ["company_name", "website", "country", "business_type", "source_url", "evidence_summary", "risk_notes"]
    write_csv(args.output_dir / "prospects.raw.csv", rows, fields)
    write_json(args.output_dir / "prospects.raw.json", rows)
    print(f"Raw prospects: {args.output_dir / 'prospects.raw.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
