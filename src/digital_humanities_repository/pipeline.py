from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
from pypdf import PdfReader

from .categories import assign_categories
from .config import (
    INCLUDED_DOCUMENT_TYPES,
    PDF_DIR,
    PORTUGUESE_DOMAIN_SUFFIXES,
    PROCESSED_DIR,
    RAW_DIR,
    REQUEST_TIMEOUT,
    SEARCH_FIELDS,
    SEARCH_PHRASE,
    TEXT_DIR,
    USER_AGENT,
)
from .rcaap_client import RCAAPClient, SearchHit
from .text_utils import clean_whitespace, contains_phrase, normalize_text, slugify

logging.getLogger("pypdf").setLevel(logging.ERROR)


def ensure_directories() -> None:
    for directory in (RAW_DIR, PDF_DIR, TEXT_DIR, PROCESSED_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def group_search_hits(hits: list[SearchHit]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for hit in hits:
        record = grouped.setdefault(
            hit.identifier,
            {
                "identifier": hit.identifier,
                "title_from_results": hit.title,
                "title_url": hit.title_url,
                "detail_url": hit.detail_url,
                "authors_from_results": hit.authors,
                "result_year": hit.result_year,
                "origin_name": hit.origin_name,
                "origin_url": hit.origin_url,
                "search_snippet": hit.snippet,
                "search_criteria_hits": set(),
                "search_hit_count": 0,
            },
        )
        record["search_criteria_hits"].add(hit.criterion)
        record["search_hit_count"] += 1
        if len(hit.snippet) > len(record["search_snippet"]):
            record["search_snippet"] = hit.snippet

    grouped_records = list(grouped.values())
    for record in grouped_records:
        record["search_criteria_hits"] = sorted(record["search_criteria_hits"])
    return grouped_records


def pick_first(values: list[str]) -> str:
    return values[0] if values else ""


def join_values(values: list[str], separator: str = " | ") -> str:
    return separator.join(value for value in values if value)


def parse_year(value: str) -> str:
    match = re.search(r"(19|20)\d{2}", value or "")
    return match.group(0) if match else ""


def normalize_document_type(value: str) -> str:
    return normalize_text(value)


def document_family(document_type: str) -> str:
    normalized = normalize_document_type(document_type)
    if "thesis" in normalized:
        return "thesis"
    if "report" in normalized:
        return "report"
    return "other"


def degree_level(document_type: str) -> str:
    normalized = normalize_document_type(document_type)
    if normalized == "bachelor thesis":
        return "licenciatura"
    if normalized == "master thesis":
        return "mestrado"
    if normalized == "doctoral thesis":
        return "doutoramento"
    if normalized == "thesis":
        return "thesis_unspecified"
    return ""


def normalize_institution(origin_name: str, origin_url: str) -> str:
    cleaned = clean_whitespace(origin_name)
    normalized_origin = normalize_text(cleaned)
    hostname = urlparse(origin_url).hostname or ""

    if "unl" in normalized_origin:
        return "Universidade Nova de Lisboa"
    if "ubibliorum" in normalized_origin or hostname.endswith("ubi.pt"):
        return "Universidade da Beira Interior"

    patterns = [
        r"(Universidade da Madeira)",
        r"(Universidade de Coimbra)",
        r"(Universidade do Minho)",
        r"(Universidade de Évora)",
        r"(Universidade do Porto)",
        r"(Universidade de Lisboa)",
        r"(Universidade Nova de Lisboa)",
        r"(Universidade Autónoma de Lisboa)",
        r"(Universidade Aberta)",
        r"(Universidade de Aveiro)",
        r"(Universidade da Beira Interior)",
        r"(Universidade dos Açores)",
        r"(Universidade do Algarve)",
        r"(Universidade da Maia)",
        r"(Universidade Católica Portuguesa)",
        r"(ISCTE[^|,;]*)",
        r"(Instituto Politécnico[^|,;]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned, re.I)
        if match:
            return clean_whitespace(match.group(1))
    if cleaned:
        return cleaned
    return urlparse(origin_url).netloc


def classify_country_scope(origin_url: str, origin_name: str) -> str:
    hostname = urlparse(origin_url).hostname or ""
    if hostname.endswith(PORTUGUESE_DOMAIN_SUFFIXES):
        return "pt"
    if hostname.endswith(".br") or "oasisbr" in normalize_text(origin_name):
        return "non_pt"
    return "review"


def build_internal_id(identifier: str) -> str:
    return slugify(identifier)


def extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    reader = PdfReader(str(pdf_path))
    pages = len(reader.pages)
    text_parts: list[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n\n".join(text_parts).strip(), pages


def text_quality(text: str, page_count: int) -> str:
    char_count = len(text)
    if char_count == 0:
        return "empty"
    if char_count >= 10000 or (page_count and char_count / page_count >= 1500):
        return "high"
    if char_count >= 3000:
        return "medium"
    return "low"


def download_pdf(pdf_url: str, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        content = destination.read_bytes()
        return {
            "ok": True,
            "path": str(destination),
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
        }

    response = requests.get(
        pdf_url,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
        stream=True,
        allow_redirects=True,
    )
    response.raise_for_status()

    first_chunk = next(response.iter_content(chunk_size=8192), b"")
    content_type = clean_whitespace(response.headers.get("content-type", "")).casefold()
    if not first_chunk.startswith(b"%PDF") and "pdf" not in content_type:
        raise ValueError(f"Unexpected content type for PDF download: {content_type or 'unknown'}")

    hasher = hashlib.sha256()
    total_bytes = 0
    with destination.open("wb") as handle:
        if first_chunk:
            handle.write(first_chunk)
            hasher.update(first_chunk)
            total_bytes += len(first_chunk)
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            handle.write(chunk)
            hasher.update(chunk)
            total_bytes += len(chunk)

    return {
        "ok": True,
        "path": str(destination),
        "sha256": hasher.hexdigest(),
        "bytes": total_bytes,
    }


def enrich_record(client: RCAAPClient, base_record: dict[str, Any], download_pdfs: bool) -> dict[str, Any]:
    metadata = client.fetch_oai_dc(base_record["identifier"])
    title = pick_first(metadata.get("title", [])) or base_record["title_from_results"]
    creators = metadata.get("creator", [])
    contributors = metadata.get("contributor", [])
    subjects = [subject for subject in metadata.get("subject", []) if subject and subject != "."]
    descriptions = metadata.get("description", [])
    abstract = max(descriptions, key=len) if descriptions else ""
    document_type = pick_first(metadata.get("type", []))
    persistent_id = pick_first(metadata.get("identifier", [])) or base_record["title_url"]

    landing_page_url = ""
    landing_html = ""
    content_type = ""
    pdf_candidates: list[str] = []
    if persistent_id:
        try:
            landing_page_url, landing_html, content_type = client.resolve_landing_page(persistent_id)
            pdf_candidates = client.extract_pdf_candidates(
                landing_page_url=landing_page_url,
                landing_html=landing_html,
                content_type=content_type,
                persistent_id=persistent_id,
            )
        except Exception:
            landing_page_url = ""
            pdf_candidates = []

    title_match = contains_phrase(title, SEARCH_PHRASE)
    abstract_match = any(contains_phrase(item, SEARCH_PHRASE) for item in descriptions)
    keywords_match = any(contains_phrase(item, SEARCH_PHRASE) for item in subjects)
    included_by_phrase = title_match or abstract_match or keywords_match

    normalized_type = normalize_document_type(document_type)
    included_document_type = normalized_type in INCLUDED_DOCUMENT_TYPES
    country_scope = classify_country_scope(base_record["origin_url"], base_record["origin_name"])
    included_country_scope = country_scope == "pt"

    pdf_url = pdf_candidates[0] if pdf_candidates else ""
    internal_id = build_internal_id(base_record["identifier"])
    pdf_path = PDF_DIR / f"{internal_id}.pdf"
    text_path = TEXT_DIR / f"{internal_id}.txt"
    pdf_downloaded = False
    pdf_sha256 = ""
    pdf_size_bytes = 0
    raw_text = ""
    page_count = 0
    extraction_quality = "not_attempted"
    pdf_error = ""

    should_download_pdf = (
        included_by_phrase
        and included_document_type
        and included_country_scope
        and download_pdfs
        and bool(pdf_url)
    )
    if should_download_pdf:
        for candidate in pdf_candidates:
            try:
                download_result = download_pdf(candidate, pdf_path)
                pdf_url = candidate
                pdf_sha256 = str(download_result["sha256"])
                pdf_size_bytes = int(download_result["bytes"])
                raw_text, page_count = extract_pdf_text(pdf_path)
                text_path.write_text(raw_text, encoding="utf-8")
                extraction_quality = text_quality(raw_text, page_count)
                pdf_downloaded = bool(download_result["ok"])
                pdf_error = ""
                break
            except Exception as exc:
                pdf_downloaded = False
                pdf_error = str(exc)
                extraction_quality = "failed"
                if pdf_path.exists():
                    pdf_path.unlink()
                if text_path.exists():
                    text_path.unlink()

    category_info = assign_categories(title, abstract, join_values(subjects), raw_text[:20000])

    if not included_by_phrase:
        manual_review_status = "excluded_no_exact_phrase"
    elif not included_document_type:
        manual_review_status = "excluded_document_type"
    elif not included_country_scope:
        manual_review_status = "excluded_non_portuguese_scope"
    elif pdf_url and not pdf_downloaded:
        manual_review_status = "metadata_only"
    elif not pdf_url:
        manual_review_status = "metadata_only"
    else:
        manual_review_status = "ready"

    dates = metadata.get("date", [])
    year = parse_year(base_record["result_year"]) or parse_year(pick_first(dates))

    return {
        "internal_id": internal_id,
        "identifier": base_record["identifier"],
        "record_url": base_record["detail_url"],
        "persistent_id": persistent_id,
        "landing_page_url": landing_page_url,
        "title": title,
        "authors": join_values(creators) or base_record["authors_from_results"],
        "primary_author": pick_first(creators) or base_record["authors_from_results"],
        "contributors": join_values(contributors),
        "origin_repository": base_record["origin_name"],
        "origin_repository_url": base_record["origin_url"],
        "institution_normalized": normalize_institution(base_record["origin_name"], base_record["origin_url"]),
        "country_scope": country_scope,
        "result_year": base_record["result_year"],
        "year": year,
        "document_type": document_type,
        "document_type_normalized": normalized_type,
        "document_family": document_family(document_type),
        "degree_level": degree_level(document_type),
        "language": pick_first(metadata.get("language", [])),
        "publisher": pick_first(metadata.get("publisher", [])),
        "rights": join_values(metadata.get("rights", [])),
        "abstract": abstract,
        "keywords": join_values(subjects),
        "search_snippet": base_record["search_snippet"],
        "search_criteria_hits": " | ".join(base_record["search_criteria_hits"]),
        "search_hit_count": base_record["search_hit_count"],
        "matched_title": title_match,
        "matched_abstract": abstract_match,
        "matched_keywords": keywords_match,
        "included_by_phrase_rule": included_by_phrase,
        "included_document_type": included_document_type,
        "included_country_scope": included_country_scope,
        "pdf_url": pdf_url,
        "pdf_candidate_count": len(pdf_candidates),
        "pdf_downloaded": pdf_downloaded,
        "pdf_local_path": str(pdf_path) if pdf_downloaded else "",
        "pdf_sha256": pdf_sha256,
        "pdf_size_bytes": pdf_size_bytes,
        "pdf_page_count": page_count,
        "pdf_text_path": str(text_path) if raw_text else "",
        "pdf_text_char_count": len(raw_text),
        "pdf_text_quality": extraction_quality,
        "pdf_error": pdf_error,
        "manual_review_status": manual_review_status,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        **category_info,
    }


def save_outputs(search_hits: list[dict[str, Any]], records: list[dict[str, Any]]) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    raw_hits_df = pd.DataFrame(search_hits)
    raw_hits_df.to_csv(RAW_DIR / f"rcaap_search_hits_{timestamp}.csv", index=False)
    raw_hits_df.to_csv(RAW_DIR / "rcaap_search_hits_latest.csv", index=False)

    records_df = pd.DataFrame(records).sort_values(
        by=["included_by_phrase_rule", "included_document_type", "included_country_scope", "year", "title"],
        ascending=[False, False, False, False, True],
    )
    records_df.to_csv(RAW_DIR / f"rcaap_records_enriched_{timestamp}.csv", index=False)
    records_df.to_csv(RAW_DIR / "rcaap_records_enriched_latest.csv", index=False)

    dashboard_df = records_df[
        records_df["included_by_phrase_rule"]
        & records_df["included_document_type"]
        & records_df["included_country_scope"]
    ].copy()
    dashboard_df.to_csv(PROCESSED_DIR / "dashboard_documents.csv", index=False)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "search_phrase": SEARCH_PHRASE,
        "search_fields": list(SEARCH_FIELDS.keys()),
        "raw_search_hits": int(len(raw_hits_df)),
        "unique_records": int(len(records_df)),
        "eligible_records": int(len(dashboard_df)),
        "pdf_downloaded": int(dashboard_df["pdf_downloaded"].sum()) if not dashboard_df.empty else 0,
        "institutions": sorted(
            institution
            for institution in dashboard_df["institution_normalized"].dropna().unique().tolist()
            if institution
        ),
    }
    (PROCESSED_DIR / "dashboard_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_pipeline(download_pdfs: bool = True) -> dict[str, Any]:
    ensure_directories()
    client = RCAAPClient()

    raw_hits: list[SearchHit] = []
    for criterion, field_name in SEARCH_FIELDS.items():
        raw_hits.extend(client.search_field(criterion=criterion, search_field=field_name, phrase=SEARCH_PHRASE))

    grouped_records = group_search_hits(raw_hits)
    enriched_records = [
        enrich_record(client=client, base_record=base_record, download_pdfs=download_pdfs)
        for base_record in grouped_records
    ]

    raw_hit_rows = [
        {
            "criterion": hit.criterion,
            "identifier": hit.identifier,
            "title": hit.title,
            "title_url": hit.title_url,
            "detail_url": hit.detail_url,
            "authors": hit.authors,
            "snippet": hit.snippet,
            "result_year": hit.result_year,
            "origin_name": hit.origin_name,
            "origin_url": hit.origin_url,
        }
        for hit in raw_hits
    ]
    save_outputs(raw_hit_rows, enriched_records)

    eligible_records = [
        record
        for record in enriched_records
        if record["included_by_phrase_rule"]
        and record["included_document_type"]
        and record["included_country_scope"]
    ]
    return {
        "raw_search_hits": len(raw_hits),
        "unique_records": len(grouped_records),
        "eligible_records": len(eligible_records),
        "pdf_downloaded": sum(1 for record in eligible_records if record["pdf_downloaded"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect RCAAP records about humanidades digitais and build dashboard data."
    )
    parser.add_argument(
        "--skip-pdfs",
        action="store_true",
        help="Skip PDF download and text extraction.",
    )
    args = parser.parse_args()

    summary = run_pipeline(download_pdfs=not args.skip_pdfs)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
