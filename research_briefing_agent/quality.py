import re
from dataclasses import dataclass
from typing import List, Optional

from .config import DEFAULT_MIN_SOURCE_BACKED_FINDINGS
from .models import BriefDraft, BriefOptions, Evidence


@dataclass
class QualityReport:
    source_backed_findings: int
    findings_needing_validation: int
    notes: List[str]


def evaluate_quality(
    findings: List[Evidence],
    draft: Optional[BriefDraft] = None,
    min_source_backed_findings: int = DEFAULT_MIN_SOURCE_BACKED_FINDINGS,
    options: Optional[BriefOptions] = None,
    all_evidence: Optional[List[Evidence]] = None,
) -> QualityReport:
    source_backed = sum(1 for item in findings if item.confidence == "source-backed")
    needs_validation = len(findings) - source_backed
    if not findings:
        needs_validation = 3

    notes = [
        "{0} findings include source-backed citations.".format(source_backed),
        "{0} findings need validation.".format(needs_validation),
    ]
    if source_backed < min_source_backed_findings:
        notes.append(
            "Evidence coverage is thin; add at least {0} source-backed notes before relying on this brief.".format(
                min_source_backed_findings
            )
        )
    if any(item.confidence != "source-backed" for item in findings):
        notes.append(
            "Some findings came from inline notes and should be checked against primary sources."
        )
    if draft:
        notes.append(
            "LLM synthesis was constrained to provided evidence IDs; review cited claims before sharing."
        )
    notes.extend(_review_notes(findings, options, all_evidence or findings))

    return QualityReport(
        source_backed_findings=source_backed,
        findings_needing_validation=needs_validation,
        notes=notes,
    )


def _review_notes(
    findings: List[Evidence],
    options: Optional[BriefOptions],
    all_evidence: List[Evidence],
) -> List[str]:
    notes = []
    if not all_evidence:
        notes.append("No source evidence is available; treat this as a briefing outline only.")
        return notes

    sources = {
        item.source.path if item.source else "inline"
        for item in all_evidence
    }
    source_types = {
        item.source.source_type if item.source else "inline"
        for item in all_evidence
    }
    if len(sources) == 1:
        notes.append("Only one source is represented; add independent sources before making strong claims.")
    if len(source_types) == 1:
        notes.append("All evidence comes from {0} sources; consider adding another source type.".format(next(iter(source_types))))

    stale_years = sorted(_stale_years(all_evidence))
    if stale_years:
        notes.append(
            "Potentially stale dates detected ({0}); verify time-sensitive claims.".format(
                ", ".join(str(year) for year in stale_years[:5])
            )
        )

    if options:
        missing = _missing_mode_terms(options.mode, findings)
        if missing:
            notes.append(
                "Mode coverage gap: add evidence for {0}.".format(", ".join(missing))
            )
    return notes


def _stale_years(evidence: List[Evidence]) -> List[int]:
    years = set()
    for item in evidence:
        for match in re.findall(r"\b(19\d{2}|20\d{2})\b", item.text):
            year = int(match)
            if year < 2024:
                years.add(year)
    return list(years)


def _missing_mode_terms(mode: str, findings: List[Evidence]) -> List[str]:
    requirements = {
        "paper": {
            "method": ("method", "model", "experiment", "dataset", "data"),
            "result": ("result", "finding", "performance", "accuracy"),
            "limitation": ("limit", "limitation", "future", "weakness"),
        },
        "investment": {
            "growth": ("growth", "revenue", "market", "demand"),
            "risk": ("risk", "downside", "competition", "regulation"),
            "valuation": ("valuation", "margin", "price", "cost"),
        },
        "teaching": {
            "objective": ("objective", "goal", "learn", "understand"),
            "example": ("example", "case", "demo"),
            "question": ("question", "discussion", "q&a"),
        },
        "topic": {
            "consensus": ("consensus", "agree", "common", "shared"),
            "tension": ("tension", "conflict", "disagree", "risk"),
            "missing evidence": ("missing", "unknown", "gap", "question"),
        },
    }
    text = " ".join(item.text.lower() for item in findings)
    missing = []
    for label, terms in requirements[mode].items():
        if not any(term in text for term in terms):
            missing.append(label)
    return missing
