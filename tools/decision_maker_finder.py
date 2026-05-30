from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from trade_utils import crawl_company_pages, load_json_path, load_yaml, render_template, sleep_for_rate_limit, write_json


ROLE_PATTERNS = [
    "Owner",
    "Founder",
    "CEO",
    "Managing Director",
    "Purchasing Manager",
    "Sourcing Manager",
    "Category Manager",
    "Procurement Manager",
    "Buyer",
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,5}\d{2,4}")
PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}


def email_status(email: str) -> str:
    if not EMAIL_RE.fullmatch(email):
        return "invalid_format"
    domain = email.split("@", 1)[1].lower()
    if domain in PERSONAL_DOMAINS:
        return "format_valid"
    return "domain_match"


def find_name_for_role(line: str, role: str) -> str:
    before = line.split(role, 1)[0].strip(" :-,\t")
    after = line.split(role, 1)[-1].strip(" :-,\t")
    if before and 1 <= len(before.split()) <= 4:
        return before
    if after and 1 <= len(after.split()) <= 4 and "@" not in after:
        return after
    return ""


def phone_values(text: str) -> list[str]:
    phones: list[str] = []
    for match in PHONE_RE.findall(text):
        value = match.strip(" .,:;")
        digits = re.sub(r"\D", "", value)
        if 7 <= len(digits) <= 15 and value not in phones:
            phones.append(value)
    return phones


def evidence_line(text: str, value: str) -> str:
    for line in text.splitlines():
        if value in line:
            return line.strip()
    return value


def extract_contact_search_from_pages(pages: list[dict[str, str]]) -> dict[str, Any]:
    emails: list[dict[str, str]] = []
    phones: list[dict[str, str]] = []
    seen_emails: set[str] = set()
    seen_phones: set[str] = set()

    for page in pages:
        text = page.get("text", "")
        source_url = page.get("url", "")
        for email in EMAIL_RE.findall(text):
            key = email.lower()
            if key in seen_emails:
                continue
            seen_emails.add(key)
            emails.append(
                {
                    "value": email,
                    "status": email_status(email),
                    "source_url": source_url,
                    "evidence": evidence_line(text, email),
                }
            )
        for phone in phone_values(text):
            key = re.sub(r"\D", "", phone)
            if key in seen_phones:
                continue
            seen_phones.add(key)
            phones.append(
                {
                    "value": phone,
                    "source_url": source_url,
                    "evidence": evidence_line(text, phone),
                }
            )

    return {
        "email_result": "found" if emails else "没有",
        "phone_result": "found" if phones else "没有",
        "emails": emails,
        "phones": phones,
    }


def extract_candidates_from_pages(pages: list[dict[str, str]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for page in pages:
        text = page.get("text", "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        all_emails = EMAIL_RE.findall(text)
        all_phones = phone_values(text)
        for index, line in enumerate(lines):
            nearby = "\n".join(lines[max(0, index - 2) : index + 3])
            for role in ROLE_PATTERNS:
                if role.lower() not in line.lower() and role.lower() not in nearby.lower():
                    continue
                email = (EMAIL_RE.findall(nearby) or all_emails or [""])[0]
                phone = (phone_values(nearby) or all_phones or [""])[0]
                name = find_name_for_role(line, role)
                key = (role, email, phone, page["url"])
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(
                    {
                        "name": name,
                        "role": role,
                        "email": email,
                        "email_status": email_status(email) if email else "missing",
                        "phone": phone,
                        "phone_status": "found" if phone else "missing",
                        "confidence": "high" if email else "medium",
                        "source_url": page["url"],
                        "evidence": line,
                    }
                )
    return candidates


def find_decision_makers(website: str, scraping: dict[str, Any] | None = None) -> dict[str, Any]:
    pages = crawl_company_pages(website, max_pages=5, scraping=scraping)
    candidates = extract_candidates_from_pages(pages)
    contact_search = extract_contact_search_from_pages(pages)
    return {
        "website": website,
        "pages_checked": [page["url"] for page in pages],
        "contact_search": contact_search,
        "candidates": candidates,
        "review_notes": [] if candidates else ["No decision-maker clue found in checked pages."],
    }


def contact_api_candidates(discovery_path: Path | None, website: str, company_name: str) -> list[dict[str, Any]]:
    if not discovery_path:
        return []
    discovery = load_yaml(discovery_path)
    api = discovery.get("contact_enrichment_api", {})
    if api.get("provider", "none") == "none" or not api.get("endpoint"):
        return []

    parsed = urlparse(website)
    domain = parsed.netloc or Path(parsed.path).stem
    variables = {"domain": domain, "company_name": company_name}
    method = api.get("method", "GET").upper()
    endpoint = render_template(api.get("endpoint", ""), variables)
    headers = dict(api.get("headers") or {})
    key_env = api.get("api_key_env") or ""
    if key_env and os.environ.get(key_env):
        headers[api.get("auth_header", "Authorization")] = f"{api.get('auth_scheme', 'Bearer')} {os.environ[key_env]}"

    params = render_template(api.get("query_params") or {}, variables)
    body = None
    if method == "GET" and params:
        endpoint = endpoint + ("&" if "?" in endpoint else "?") + urlencode(params)
    elif params:
        body = json.dumps(render_template(api.get("request_body_template") or params, variables)).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    request = Request(endpoint, data=body, headers=headers, method=method)
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    mapping = api.get("response_mapping", {})
    items = load_json_path(mapping.get("items_path", "items"), payload) or []
    sleep_for_rate_limit(int(api.get("rate_limit", {}).get("requests_per_minute", 20)))
    return [
        {
            "name": load_json_path(mapping.get("name", "name"), item) or "",
            "role": load_json_path(mapping.get("role", "role"), item) or "",
            "email": load_json_path(mapping.get("email", "email"), item) or "",
            "email_status": "api_verified",
            "phone": load_json_path(mapping.get("phone", "phone"), item) or "",
            "phone_status": "found" if load_json_path(mapping.get("phone", "phone"), item) else "missing",
            "confidence": "high",
            "source_url": load_json_path(mapping.get("source_url", "source_url"), item) or api.get("endpoint", ""),
            "evidence": "Contact enrichment API result",
        }
        for item in items
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find decision-maker clues from company pages")
    parser.add_argument("--website", required=True)
    parser.add_argument("--company-name", default="")
    parser.add_argument("--discovery", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    discovery = load_yaml(args.discovery) if args.discovery else {}
    result = find_decision_makers(args.website, discovery.get("scraping"))
    result["candidates"].extend(contact_api_candidates(args.discovery, args.website, args.company_name))
    write_json(args.output, result)
    print(f"Decision-maker clues: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
