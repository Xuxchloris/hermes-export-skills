from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from decision_maker_finder import find_decision_makers
from trade_utils import crawl_company_pages, load_yaml, read_table, select_product_config, website_key, write_json, write_workbook


def first_value(row: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def product_terms(product_config: dict[str, Any]) -> tuple[str, list[str]]:
    products = product_config.get("products", [])
    primary_name = products[0].get("name", "our product") if products else "our product"
    terms: list[str] = []
    for product in products:
        terms.append(product.get("name", ""))
        terms.append(product.get("category", ""))
        terms.extend(product.get("keywords", []))
        terms.extend(product.get("target_applications", []))
    seen = set()
    clean = [term for term in terms if term and not (term.lower() in seen or seen.add(term.lower()))]
    return primary_name, clean


def normalize_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_key: dict[str, dict[str, Any]] = {}
    review: list[dict[str, Any]] = []

    for row in rows:
        normalized = {
            "company_name": first_value(row, ["company_name", "company", "name"]),
            "website": first_value(row, ["website", "url", "domain"]),
            "country": first_value(row, ["country", "market", "region"]),
            "business_type": first_value(row, ["business_type", "type"]),
            "source_url": first_value(row, ["source_url", "source", "source_note"]),
        }
        if not normalized["company_name"] or not normalized["website"]:
            normalized["status"] = "needs_review"
            normalized["review_reason"] = "missing company_name or website"
            review.append(normalized)
            continue

        key = website_key(normalized["website"]) or normalized["company_name"].lower()
        if key not in by_key:
            normalized["status"] = "ready_for_research"
            normalized["merged_source_urls"] = normalized["source_url"]
            by_key[key] = normalized
        else:
            existing = by_key[key]
            sources = [source for source in [existing.get("merged_source_urls"), normalized["source_url"]] if source]
            existing["merged_source_urls"] = "; ".join(dict.fromkeys("; ".join(sources).split("; ")))
            if not existing.get("business_type") and normalized.get("business_type"):
                existing["business_type"] = normalized["business_type"]
    return list(by_key.values()), review


def analyze_fit(text: str, terms: list[str], country: str, market_config: dict[str, Any]) -> dict[str, Any]:
    lowered = text.lower()
    matched_terms = [term for term in terms if term.lower() in lowered]
    channel_terms = ["importer", "distributor", "wholesaler", "retail", "category", "sourcing", "purchasing"]
    matched_channels = [term for term in channel_terms if term in lowered]
    target_countries = [item.get("country") for item in market_config.get("target_markets", [])]

    product_fit = min(40, len(matched_terms) * 12)
    channel_value = min(20, len(matched_channels) * 7)
    market_value = 10 if country in target_countries else 5
    activity = 10 if text.strip() else 0
    decision_access = 15 if any(role in lowered for role in ["purchasing manager", "sourcing manager", "category manager", "founder", "owner"]) else 5
    score = min(100, product_fit + channel_value + market_value + activity + decision_access)
    if not matched_terms:
        score = min(score, 39)
    priority = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
    return {
        "score": score,
        "priority": priority,
        "matched_terms": ", ".join(matched_terms),
        "matched_channels": ", ".join(matched_channels),
    }


def evidence_status(pages: list[dict[str, str]], product_evidence: str) -> str:
    if product_evidence:
        return "verified"
    if any(page.get("text", "").strip() for page in pages):
        return "no_product_evidence"
    if any(page.get("error") for page in pages):
        return "fetch_failed"
    return "no_evidence"


def make_email(company: str, evidence: str, product_name: str) -> tuple[str, str, str]:
    subject = f"{product_name} for {company}"
    if not evidence:
        body = (
            "No product overlap was verified from the fetched pages. "
            "Review this prospect manually before writing a personalized outreach email."
        )
        return subject, body, "blocked_no_evidence"

    opening = evidence
    body = (
        f"Hi,\n\n"
        f"{opening} We manufacture {product_name} with export-ready product and packing details.\n\n"
        "If this category is relevant for your team, I can send a short catalog and price range for review.\n\n"
        "Best regards"
    )
    return subject, body, "draft_ready"


def run_pipeline(
    input_path: Path,
    product_path: Path,
    market_path: Path,
    tone_path: Path,
    output_dir: Path,
    discovery_path: Path | None = None,
    product_query: str = "",
    sku: str = "",
) -> None:
    product_config = load_yaml(product_path)
    product_config = select_product_config(product_config, product_query, sku)
    market_config = load_yaml(market_path)
    load_yaml(tone_path)
    discovery = load_yaml(discovery_path) if discovery_path else {}
    scraping = discovery.get("scraping")
    product_name, terms = product_terms(product_config)
    unique_rows, review_rows = normalize_rows(read_table(input_path))

    enriched_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    email_rows: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []

    for row in unique_rows:
        pages = crawl_company_pages(row["website"], max_pages=5, scraping=scraping)
        combined_text = "\n".join(page.get("text", "") for page in pages)
        first_evidence = ""
        first_evidence_url = ""
        for line in combined_text.splitlines():
            if any(term.lower() in line.lower() for term in terms):
                first_evidence = line.strip()
                for page in pages:
                    if first_evidence in page.get("text", ""):
                        first_evidence_url = page["url"]
                        break
                break
        fit = analyze_fit(combined_text, terms, row.get("country", ""), market_config)
        status = evidence_status(pages, first_evidence)
        decision_makers = find_decision_makers(row["website"], scraping=scraping)
        subject, body, draft_status = make_email(row["company_name"], first_evidence, product_name)
        recommended_action = "draft_outreach" if status == "verified" and fit["priority"] in {"A", "B"} else "manual_review"

        contact_search = decision_makers.get("contact_search", {})
        enriched_rows.append(
            {
                **row,
                "matched_terms": fit["matched_terms"],
                "decision_maker_count": len(decision_makers["candidates"]),
                "email_result": contact_search.get("email_result", "没有"),
                "phone_result": contact_search.get("phone_result", "没有"),
            }
        )
        score_rows.append(
            {
                "company_name": row["company_name"],
                "priority": fit["priority"],
                "score": fit["score"],
                "matched_terms": fit["matched_terms"],
                "matched_channels": fit["matched_channels"],
                "evidence_status": status,
                "recommended_action": recommended_action,
            }
        )
        email_rows.append(
            {
                "company_name": row["company_name"],
                "priority": fit["priority"],
                "subject": subject,
                "body": body,
                "draft_status": draft_status,
                "human_review_required": True,
            }
        )
        reports.append(
            {
                "company_name": row["company_name"],
                "website": row["website"],
                "pages_checked": [page["url"] for page in pages],
                "summary_evidence": first_evidence,
                "summary_evidence_url": first_evidence_url,
                "evidence_status": status,
                "fetch_errors": [page["error"] for page in pages if page.get("error")],
                "score": fit,
                "decision_makers": decision_makers["candidates"],
                "contact_search": contact_search,
            }
        )

    for row in review_rows:
        enriched_rows.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_workbook(output_dir / "prospects.enriched.xlsx", {"Prospects": enriched_rows or [{"status": "empty"}]})
    write_workbook(output_dir / "scores.xlsx", {"Scores": score_rows or [{"status": "empty"}]})
    write_workbook(output_dir / "email_drafts.xlsx", {"Email Drafts": email_rows or [{"status": "empty"}]})
    write_json(output_dir / "research_reports.json", reports)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run batch prospect cleanup, research, scoring, and email drafting")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--market", type=Path, required=True)
    parser.add_argument("--tone", type=Path, required=True)
    parser.add_argument("--discovery", type=Path)
    parser.add_argument("--product-query", default="")
    parser.add_argument("--sku", default="")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_pipeline(args.input, args.product, args.market, args.tone, args.output_dir, args.discovery, args.product_query, args.sku)
    print(f"Pipeline outputs: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
