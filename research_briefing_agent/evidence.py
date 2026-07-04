import re
from typing import Iterable, List, Set

from .config import DEFAULT_MAX_FINDINGS
from .models import BriefOptions, Evidence, Source


def normalize_evidence(source_notes: Iterable[object]) -> List[Evidence]:
    cleaned = []
    for index, item in enumerate(source_notes, start=1):
        if isinstance(item, Evidence):
            text = clean_text(item.text)
            if text:
                cleaned.append(
                    Evidence(
                        id=item.id,
                        text=text,
                        source=item.source,
                        location=item.location,
                        confidence=item.confidence,
                        relevance_score=item.relevance_score,
                    )
                )
            continue

        text = clean_text(str(item))
        if text:
            cleaned.append(
                Evidence(
                    id="note-{0}".format(index),
                    text=text,
                    source=Source(
                        id="inline-source",
                        title="inline notes",
                        path="",
                        source_type="inline",
                    ),
                    location="note {0}".format(index),
                    confidence="needs review",
                )
            )
    return cleaned


def select_findings(
    evidence: Iterable[Evidence],
    max_findings: int = DEFAULT_MAX_FINDINGS,
    options: BriefOptions = None,
) -> List[Evidence]:
    items = list(evidence)
    if not options:
        return items[:max_findings]
    keywords = _keywords_for_options(options)
    scored = []
    for index, item in enumerate(items):
        score = _score_evidence(item, keywords)
        item.relevance_score = score
        scored.append((score, index, item))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [item for score, index, item in scored[:max_findings]]


def clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def _keywords_for_options(options: BriefOptions) -> Set[str]:
    text = "{0} {1} {2} {3}".format(
        options.topic,
        options.audience,
        options.tone,
        options.mode,
    )
    keywords = {
        token.lower()
        for token in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", text)
        if len(token) > 1
    }
    mode_keywords = {
        "paper": {"method", "data", "result", "model", "experiment", "limitation", "contribution"},
        "investment": {"market", "growth", "risk", "revenue", "valuation", "industry", "margin"},
        "teaching": {"concept", "example", "question", "objective", "lesson", "case", "discussion"},
        "topic": {"evidence", "trend", "risk", "source", "decision", "question", "stakeholder"},
    }
    keywords.update(mode_keywords.get(options.mode, set()))
    return keywords


def _score_evidence(item: Evidence, keywords: Set[str]) -> int:
    text = item.text.lower()
    score = 0
    for keyword in keywords:
        if keyword in text:
            score += 3
    if item.confidence == "source-backed":
        score += 2
    if len(item.text) >= 80:
        score += 1
    if any(char.isdigit() for char in item.text):
        score += 1
    return score
