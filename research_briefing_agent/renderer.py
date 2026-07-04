from datetime import date
from typing import Iterable, List, Optional

from . import modes
from .models import BriefDraft, BriefOptions, Evidence, LabelledDraftPoint
from .quality import QualityReport


def render_markdown_brief(
    options: BriefOptions,
    evidence: List[Evidence],
    findings: List[Evidence],
    quality: QualityReport,
    draft: Optional[BriefDraft] = None,
) -> str:
    evidence_by_id = {item.id: item for item in evidence}

    sections = [
        "# Research Brief: {0}".format(options.topic),
        "",
        "**Date:** {0}".format(date.today().isoformat()),
        "**Audience:** {0}".format(options.audience),
        "**Tone:** {0}".format(options.tone),
        "**Mode:** {0}".format(options.mode),
        "",
        "## Executive Summary",
        draft.summary if draft else _summary(options, findings),
        "",
        "## Briefing Focus",
        _bullet_list(modes.focus_for(options.mode)),
        "",
        "## Key Findings",
        _draft_finding_list(draft, evidence_by_id)
        if draft
        else (
            _finding_list(findings)
            if findings
            else _bullet_list(_placeholder_findings(options.topic))
        ),
        "",
        "## {0}".format(draft.synthesis_title if draft else modes.section_title_for(options.mode)),
        _draft_synthesis_body(draft, evidence_by_id)
        if draft
        else _mode_section_body(options.mode, findings),
    ]

    if evidence:
        sections.extend(["", "## Evidence Table", _evidence_table(findings)])

    sections.extend(
        [
            "",
            "## Implications",
            _bullet_list(draft.implications if draft else modes.implications_for(options.mode)),
            "",
            "## Open Questions",
            _bullet_list(draft.open_questions if draft else modes.open_questions_for(options.mode)),
            "",
            "## Recommended Next Steps",
            _bullet_list(draft.recommended_next_steps if draft else modes.next_steps()),
            "",
            "## Quality Notes",
            _bullet_list(quality.notes),
        ]
    )

    return "\n".join(sections).strip() + "\n"


def render_ppt_outline(
    options: BriefOptions,
    findings: List[Evidence],
    quality: QualityReport,
    draft: Optional[BriefDraft] = None,
    evidence: Optional[List[Evidence]] = None,
) -> str:
    if draft and draft.slides:
        return _render_ai_ppt_outline(options, draft, quality, _evidence_map(evidence or findings))

    title = "PPT Outline: {0}".format(options.topic)
    sections = [
        "# {0}".format(title),
        "",
        "## Slide 1: Title",
        "- {0}".format(options.topic),
        "- Audience: {0}".format(options.audience),
        "",
        "## Slide 2: Executive Summary",
        "- {0}".format(draft.summary if draft else _summary(options, findings)),
        "",
        "## Slide 3: Key Findings",
        _draft_finding_list(draft, {item.id: item for item in findings})
        if draft
        else (_finding_list(findings) if findings else _bullet_list(_placeholder_findings(options.topic))),
        "",
        "## Slide 4: Evidence",
        _evidence_table(findings) if findings else "- Add source-backed evidence.",
        "",
        "## Slide 5: Implications",
        _bullet_list(draft.implications if draft else modes.implications_for(options.mode)),
        "",
        "## Slide 6: Open Questions",
        _bullet_list(draft.open_questions if draft else modes.open_questions_for(options.mode)),
        "",
        "## Slide 7: Next Steps",
        _bullet_list(draft.recommended_next_steps if draft else modes.next_steps()),
        "",
        "## Appendix: Quality Review",
        _bullet_list(quality.notes),
    ]
    return "\n".join(sections).strip() + "\n"


def render_speaker_notes(
    options: BriefOptions,
    findings: List[Evidence],
    quality: QualityReport,
    draft: Optional[BriefDraft] = None,
    evidence: Optional[List[Evidence]] = None,
) -> str:
    if draft and (draft.speaker_notes or draft.slides):
        return _render_ai_speaker_notes(options, draft, findings, quality, _evidence_map(evidence or findings))

    sections = [
        "# Speaker Notes: {0}".format(options.topic),
        "",
        "## Opening",
        "Today I will brief {audience} on {topic}. The goal is to separate source-backed evidence from assumptions.".format(
            audience=options.audience,
            topic=options.topic,
        ),
        "",
        "## Talk Track",
    ]
    for index, item in enumerate(findings, start=1):
        sections.extend(
            [
                "### Point {0}".format(index),
                "{0}. Citation: {1}.".format(item.text.rstrip("."), item.citation),
                "",
            ]
        )
    if draft:
        sections.extend(["## LLM Synthesis Summary", draft.summary, ""])
    sections.extend(
        [
            "## Close",
            "The strongest claims should be validated against primary sources before decisions are made.",
            "",
            "## Review Reminders",
            _bullet_list(quality.notes),
        ]
    )
    return "\n".join(sections).strip() + "\n"


def render_qa_prep(
    options: BriefOptions,
    findings: List[Evidence],
    quality: QualityReport,
    draft: Optional[BriefDraft] = None,
    evidence: Optional[List[Evidence]] = None,
) -> str:
    if draft and draft.qa_pairs:
        return _render_ai_qa_prep(options, draft, findings, quality, _evidence_map(evidence or findings))

    questions = draft.open_questions if draft else modes.open_questions_for(options.mode)
    sections = [
        "# Q&A Prep: {0}".format(options.topic),
        "",
        "## Likely Questions",
        _bullet_list(questions),
        "",
        "## Evidence To Cite",
        _finding_list(findings) if findings else "- Add source-backed evidence before Q&A.",
        "",
        "## Defensive Notes",
        _bullet_list(
            [
                "Name which claims are supported by evidence and which are assumptions.",
                "Use citations when answering factual questions.",
                "When evidence is thin, state what source would resolve the uncertainty.",
            ]
        ),
        "",
        "## Quality Review",
        _bullet_list(quality.notes),
    ]
    return "\n".join(sections).strip() + "\n"


def _render_ai_ppt_outline(
    options: BriefOptions,
    draft: BriefDraft,
    quality: QualityReport,
    evidence_by_id: dict,
) -> str:
    sections = [
        "# PPT Outline: {0}".format(options.topic),
        "",
        "## Slide 1: Title",
        "- {0}".format(options.topic),
        "- Audience: {0}".format(options.audience),
        "",
    ]
    start_index = 2
    for offset, slide in enumerate(draft.slides, start=start_index):
        sections.extend(
            [
                "## Slide {0}: {1}".format(offset, slide.title),
                "- Key message: {0}".format(slide.key_message),
            ]
        )
        for bullet in slide.bullets:
            sections.append("- {0}".format(bullet))
        sections.append("- Citations: {0}".format(_citation_list(slide.evidence_ids, evidence_by_id)))
        if slide.speaker_notes:
            sections.append("- Speaker notes: {0}".format(slide.speaker_notes))
        sections.append("")
    sections.extend(["## Appendix: Quality Review", _bullet_list(quality.notes)])
    return "\n".join(sections).strip() + "\n"


def _render_ai_speaker_notes(
    options: BriefOptions,
    draft: BriefDraft,
    findings: List[Evidence],
    quality: QualityReport,
    evidence_by_id: dict,
) -> str:
    sections = [
        "# Speaker Notes: {0}".format(options.topic),
        "",
        "## Opening",
        draft.summary,
        "",
    ]
    if draft.speaker_notes:
        for note in draft.speaker_notes:
            sections.extend(
                [
                    "## {0}".format(note.section),
                    "{0} [{1}]".format(note.text, _citation_list(note.evidence_ids, evidence_by_id)),
                    "",
                ]
            )
    else:
        for slide in draft.slides:
            sections.extend(
                [
                    "## {0}".format(slide.title),
                    slide.speaker_notes or slide.key_message,
                    "",
                ]
            )
    sections.extend(
        [
            "## Evidence To Keep Handy",
            _finding_list(findings) if findings else "- Add source-backed evidence.",
            "",
            "## Review Reminders",
            _bullet_list(quality.notes),
        ]
    )
    return "\n".join(sections).strip() + "\n"


def _render_ai_qa_prep(
    options: BriefOptions,
    draft: BriefDraft,
    findings: List[Evidence],
    quality: QualityReport,
    evidence_by_id: dict,
) -> str:
    sections = [
        "# Q&A Prep: {0}".format(options.topic),
        "",
        "## Prepared Questions",
    ]
    for pair in draft.qa_pairs:
        sections.extend(
            [
                "### {0}".format(pair.question),
                "{0} [{1}]".format(pair.answer, _citation_list(pair.evidence_ids, evidence_by_id)),
                "",
            ]
        )
    sections.extend(
        [
            "## Evidence To Cite",
            _finding_list(findings) if findings else "- Add source-backed evidence before Q&A.",
            "",
            "## Quality Review",
            _bullet_list(quality.notes),
        ]
    )
    return "\n".join(sections).strip() + "\n"


def _summary(options: BriefOptions, findings: List[Evidence]) -> str:
    if findings:
        return (
            "This brief summarizes source-backed evidence on {topic} for {audience}. "
            "The current evidence points to {finding}"
        ).format(
            topic=options.topic,
            audience=options.audience,
            finding=findings[0].text.rstrip(".") + ".",
        )

    return (
        "This starter brief frames {topic} for {audience}. Add source notes to "
        "replace this placeholder with evidence-based findings."
    ).format(topic=options.topic, audience=options.audience)


def _placeholder_findings(topic: str) -> List[str]:
    return [
        "No source notes were provided yet for {0}.".format(topic),
        "The topic needs evidence collection before conclusions are finalized.",
        "A useful next pass should add sources, dates, and decision context.",
    ]


def _mode_section_body(mode: str, findings: List[Evidence]) -> str:
    if not findings:
        return _bullet_list(modes.empty_guidance_for(mode))
    return _labelled_points(modes.scaffold_points(mode, findings))


def _labelled_points(points: Iterable[object]) -> str:
    rows = []
    for label, item in points:
        rows.append(
            "- **{0}:** {1}. [{2}]".format(
                label,
                item.text.rstrip("."),
                item.citation,
            )
        )
    return "\n".join(rows)


def _finding_list(findings: Iterable[Evidence]) -> str:
    return "\n".join(
        "- {0}. [{1}]".format(item.text.rstrip("."), item.citation)
        for item in findings
    )


def _draft_finding_list(draft: BriefDraft, evidence_by_id: dict) -> str:
    rows = []
    for point in draft.key_findings:
        rows.append(
            "- {0}. [{1}]".format(
                point.text.rstrip("."),
                _citation_list(point.evidence_ids, evidence_by_id),
            )
        )
    return "\n".join(rows)


def _draft_synthesis_body(draft: BriefDraft, evidence_by_id: dict) -> str:
    return "\n".join(
        _format_labelled_draft_point(point, evidence_by_id)
        for point in draft.synthesis_points
    )


def _format_labelled_draft_point(point: LabelledDraftPoint, evidence_by_id: dict) -> str:
    return "- **{0}:** {1}. [{2}]".format(
        point.label,
        point.text.rstrip("."),
        _citation_list(point.evidence_ids, evidence_by_id),
    )


def _citation_list(evidence_ids: Iterable[str], evidence_by_id: dict) -> str:
    citations = []
    for evidence_id in evidence_ids:
        item = evidence_by_id.get(evidence_id)
        if item:
            citations.append(item.citation)
    if not citations:
        return "needs validation"
    return "; ".join(citations)


def _evidence_map(evidence: List[Evidence]) -> dict:
    return {item.id: item for item in evidence}


def _evidence_table(findings: Iterable[Evidence]) -> str:
    rows = ["| Claim | Source | Location | Confidence |", "|---|---|---|---|"]
    for item in findings:
        source = item.source.title if item.source else "needs validation"
        location = item.location or "unknown"
        rows.append(
            "| {0} | {1} | {2} | {3} |".format(
                _escape_table(item.text), source, location, item.confidence
            )
        )
    return "\n".join(rows)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def _bullet_list(items: Iterable[str]) -> str:
    return "\n".join("- {0}".format(item) for item in items)
