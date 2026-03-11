from __future__ import annotations

import re
import time
import warnings
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from .config import (
    INCLUDED_DOCUMENT_TYPE_URIS,
    RCAAP_BASE_URL,
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from .text_utils import clean_whitespace, unique_preserve_order

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


@dataclass
class SearchHit:
    criterion: str
    identifier: str
    title: str
    title_url: str
    detail_url: str
    authors: str
    snippet: str
    result_year: str
    origin_name: str
    origin_url: str


class RCAAPClient:
    def __init__(self) -> None:
        self.base_url = RCAAP_BASE_URL.rstrip("/")
        self.default_headers = {
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _new_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(self.default_headers)
        return session

    def search_field(self, criterion: str, search_field: str, phrase: str) -> list[SearchHit]:
        session = self._new_session()
        payload = {
            "formname": "ADVANCED",
            "includeAll": "yes",
            "col1": search_field,
            "col_val1": f'"{phrase}"',
            "btnSearch": "Search",
        }
        payload_with_types: list[tuple[str, str]] = list(payload.items())
        payload_with_types.extend(("type.coar", uri) for uri in INCLUDED_DOCUMENT_TYPE_URIS)
        response = self._request_with_retry(
            session=session,
            method="post",
            url=f"{self.base_url}/search",
            data=payload_with_types,
            referer=f"{self.base_url}/search.jsp",
            allow_redirects=True,
        )

        first_page_hits, total_pages = self._parse_search_page(response.text, criterion)
        all_hits = list(first_page_hits)

        for page_number in range(2, total_pages + 1):
            time.sleep(0.4)
            page_response = self._request_with_retry(
                session=session,
                method="get",
                url=f"{self.base_url}/search",
                params={"formname": "SORT", "actualPage": page_number},
                referer=f"{self.base_url}/results.jsp",
            )
            page_hits, _ = self._parse_search_page(page_response.text, criterion)
            all_hits.extend(page_hits)

        return all_hits

    def _request_with_retry(
        self,
        session: requests.Session,
        method: str,
        url: str,
        referer: str,
        **kwargs: object,
    ) -> requests.Response:
        last_error: Exception | None = None
        headers = dict(self.default_headers)
        headers["Referer"] = referer
        for attempt in range(4):
            try:
                response = session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                    **kwargs,
                )
                if response.status_code == 403 and attempt < 3:
                    time.sleep(1.0 + attempt)
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt == 3:
                    raise
                time.sleep(1.0 + attempt)
        if last_error:
            raise last_error
        raise RuntimeError("Unreachable request state")

    def _parse_search_page(self, html: str, criterion: str) -> tuple[list[SearchHit], int]:
        soup = BeautifulSoup(html, "lxml")
        header = soup.find("h1")
        header_text = header.get_text(" ", strip=True) if header else ""
        total_pages_match = re.search(
            r"(?:page|página|pagina)\s+\d+\s+(?:of|de)\s+(\d+)",
            header_text,
            re.I,
        ) or re.search(r'Encontrados\s+\d+\s+documentos,\s+a\s+visualizar\s+página\s+\d+\s+de\s+(\d+)', html, re.I)
        total_pages = int(total_pages_match.group(1)) if total_pages_match else 1

        hits: list[SearchHit] = []
        for block in soup.select("div.listItem"):
            title_anchor = block.select_one("h2 a[href]")
            detail_anchor = block.find(
                "a", href=lambda href: href and href.startswith("/detail.jsp?id=")
            )
            if not title_anchor or not detail_anchor:
                continue

            detail_url = urljoin(self.base_url, detail_anchor["href"])
            identifier = parse_qs(urlparse(detail_url).query).get("id", [""])[0]
            snippet_node = next(
                (node for node in block.find_all("p", recursive=False) if node.get_text(strip=True)),
                None,
            )
            info_node = block.find("div", class_=lambda value: value and "info" in value)
            info_text = clean_whitespace(info_node.get_text(" ", strip=True) if info_node else "")
            date_match = re.search(r"Date:\s*(.*?)\s*(?:\||$)", info_text, re.I)
            origin_anchor = info_node.find("a", href=True) if info_node else None

            hits.append(
                SearchHit(
                    criterion=criterion,
                    identifier=identifier,
                    title=clean_whitespace(title_anchor.get_text(" ", strip=True)),
                    title_url=urljoin(self.base_url, title_anchor["href"]),
                    detail_url=detail_url,
                    authors=clean_whitespace(
                        block.find("em").get_text(" ", strip=True) if block.find("em") else ""
                    ),
                    snippet=clean_whitespace(snippet_node.get_text(" ", strip=True) if snippet_node else ""),
                    result_year=clean_whitespace(date_match.group(1) if date_match else ""),
                    origin_name=clean_whitespace(
                        origin_anchor.get_text(" ", strip=True) if origin_anchor else ""
                    ),
                    origin_url=urljoin(self.base_url, origin_anchor["href"]) if origin_anchor else "",
                )
            )

        return hits, total_pages

    def fetch_oai_dc(self, identifier: str) -> dict[str, list[str]]:
        response = requests.get(
            f"{self.base_url}/oai/request",
            params={
                "verb": "GetRecord",
                "metadataPrefix": "oai_dc",
                "identifier": identifier,
            },
            headers=self.default_headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        metadata = root.find(".//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc")
        if metadata is None:
            return {}

        parsed: dict[str, list[str]] = {}
        for child in metadata:
            local_name = child.tag.split("}", 1)[-1]
            parsed.setdefault(local_name, []).append(clean_whitespace("".join(child.itertext())))

        return {key: unique_preserve_order(values) for key, values in parsed.items()}

    def resolve_landing_page(self, persistent_id: str) -> tuple[str, str, str]:
        if not persistent_id:
            return "", "", ""

        response = requests.get(
            persistent_id,
            headers=self.default_headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
        content_type = clean_whitespace(response.headers.get("content-type", ""))
        if "pdf" in content_type.casefold():
            return response.url, "", content_type
        return response.url, response.text, content_type

    def extract_pdf_candidates(
        self,
        landing_page_url: str,
        landing_html: str,
        content_type: str,
        persistent_id: str,
    ) -> list[str]:
        if landing_page_url and "pdf" in content_type.casefold():
            return [landing_page_url]
        if not landing_html:
            return []

        soup = BeautifulSoup(landing_html, "lxml")
        landing_domain = urlparse(landing_page_url).netloc.casefold()
        handle_tail = persistent_id.rstrip("/").split("/")[-1].casefold() if persistent_id else ""
        scored_candidates: dict[str, int] = {}

        def add_candidate(url: str, score: int) -> None:
            absolute_url = urljoin(landing_page_url, url)
            if not absolute_url.startswith("http"):
                return
            href_lower = absolute_url.casefold()
            if any(bad_token in href_lower for bad_token in ("help", "faq", "manual", "newsletter")):
                score -= 100
            if score <= 0:
                return
            current_score = scored_candidates.get(absolute_url, 0)
            if score > current_score:
                scored_candidates[absolute_url] = score

        for meta_name in ("citation_pdf_url", "pdf_url", "eprints.document_url"):
            for meta in soup.find_all(
                "meta", attrs={"name": lambda value: value and value.casefold() == meta_name}
            ):
                content = meta.get("content", "")
                if content:
                    add_candidate(content, 100)

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            href_lower = href.casefold()
            text = clean_whitespace(anchor.get_text(" ", strip=True)).casefold()
            score = 0
            if href_lower.endswith(".pdf") or ".pdf?" in href_lower:
                score += 60
            if "/bitstream/" in href_lower:
                score += 55
            if "/download" in href_lower:
                score += 45
            if any(token in text for token in ("view/open", "download", "pdf", "texto integral")):
                score += 20
            absolute_url = urljoin(landing_page_url, href)
            if urlparse(absolute_url).netloc.casefold() == landing_domain:
                score += 10
            if handle_tail and handle_tail in absolute_url.casefold():
                score += 15
            add_candidate(href, score)

        return [
            candidate
            for candidate, _score in sorted(
                scored_candidates.items(), key=lambda item: item[1], reverse=True
            )
        ]
