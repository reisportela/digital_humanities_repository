from __future__ import annotations

import re
import unicodedata


def clean_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def strip_accents(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )


def normalize_text(value: str | None) -> str:
    return clean_whitespace(strip_accents((value or "").casefold()))


def contains_phrase(value: str | None, phrase: str) -> bool:
    return normalize_text(phrase) in normalize_text(value)


def slugify(value: str) -> str:
    normalized = normalize_text(value)
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-") or "record"


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = clean_whitespace(value)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result
