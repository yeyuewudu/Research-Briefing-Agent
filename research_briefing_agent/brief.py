from dataclasses import dataclass
from datetime import date
from typing import Iterable, List


@dataclass
class BriefOptions:
    topic: str
    audience: str = "general readers"
    tone: str = "clear and concise"


def generate_brief(options: BriefOptions, source_notes: Iterable[str]) -> str:
    notes = _clean_notes(source_notes)
    findings = _extract_findings(notes)

    sections = [
        "# Research Brief: {0}".format(options.topic),
        "",
        "**Date:** {0}".format(date.today().isoformat()),
        "**Audience:** {0}".format(options.audience),
        "**Tone:** {0}".format(options.tone),
        "",
        "## Executive Summary",
        _summary(options, findings),
        "",
        "## Key Findings",
        _bullet_list(findings or _fallback_findings(options.topic)),
        "",
        "## Implications",
        _bullet_list(
            [
                "Clarify which stakeholders are most affected by this topic.",
                "Separate confirmed evidence from assumptions before making decisions.",
                "Track the most important unknowns as follow-up research items.",
            ]
        ),
        "",
        "## Open Questions",
        _bullet_list(
            [
                "What evidence would change the current interpretation?",
                "Which data sources are missing or underrepresented?",
                "What decision needs this briefing to support?",
            ]
        ),
        "",
        "## Recommended Next Steps",
        _bullet_list(
            [
                "Validate the strongest claims against primary sources.",
                "Add fresh source notes for any time-sensitive facts.",
                "Turn this brief into an action memo for the target audience.",
            ]
        ),
    ]

    if notes:
        sections.extend(["", "## Source Notes", _bullet_list(notes)])

    return "\n".join(sections).strip() + "\n"


def _clean_notes(source_notes: Iterable[str]) -> List[str]:
    cleaned = []
    for note in source_notes:
        line = " ".join(note.strip().split())
        if line:
            cleaned.append(line)
    return cleaned


def _extract_findings(notes: List[str]) -> List[str]:
    if not notes:
        return []
    return notes[:5]


def _summary(options: BriefOptions, findings: List[str]) -> str:
    if findings:
        return (
            "This brief summarizes the available notes on {topic} for {audience}. "
            "The current evidence points to {finding}"
        ).format(
            topic=options.topic,
            audience=options.audience,
            finding=findings[0].rstrip(".") + ".",
        )

    return (
        "This starter brief frames {topic} for {audience}. Add source notes to "
        "replace this placeholder with evidence-based findings."
    ).format(topic=options.topic, audience=options.audience)


def _fallback_findings(topic: str) -> List[str]:
    return [
        "No source notes were provided yet for {0}.".format(topic),
        "The topic needs evidence collection before conclusions are finalized.",
        "A useful next pass should add sources, dates, and decision context.",
    ]


def _bullet_list(items: Iterable[str]) -> str:
    return "\n".join("- {0}".format(item) for item in items)
