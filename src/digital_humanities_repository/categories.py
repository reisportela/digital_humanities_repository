from __future__ import annotations

from .config import CATEGORY_RULES
from .text_utils import normalize_text


def assign_categories(*parts: str) -> dict[str, str]:
    haystack = normalize_text(" ".join(part for part in parts if part))
    matched_categories: list[str] = []
    matched_labels: list[str] = []
    matched_terms: list[str] = []

    for rule in CATEGORY_RULES:
        rule_matches = [
            keyword for keyword in rule["keywords"] if normalize_text(keyword) in haystack
        ]
        if not rule_matches:
            continue
        matched_categories.append(rule["category"])
        matched_labels.append(rule["label"])
        matched_terms.extend(rule_matches)

    if not matched_categories:
        matched_categories = ["revisao_manual"]
        matched_labels = ["Revisão manual"]

    return {
        "primary_category": matched_categories[0],
        "primary_category_label": matched_labels[0],
        "categories": " | ".join(matched_categories),
        "category_labels": " | ".join(matched_labels),
        "category_rule_matches": " | ".join(sorted(set(matched_terms))),
    }
