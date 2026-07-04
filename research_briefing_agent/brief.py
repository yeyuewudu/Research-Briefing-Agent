from typing import Iterable, Optional

from .config import AppConfig
from .evidence import normalize_evidence, select_findings
from .models import BriefDraft, BriefOptions
from .quality import evaluate_quality
from .renderer import (
    render_markdown_brief,
    render_ppt_outline,
    render_qa_prep,
    render_speaker_notes,
)


def generate_brief(
    options: BriefOptions,
    source_notes: Iterable[object],
    draft: Optional[BriefDraft] = None,
    config: Optional[AppConfig] = None,
    output_format: str = "markdown",
) -> str:
    active_config = config or AppConfig.from_env()
    evidence = normalize_evidence(source_notes)
    findings = select_findings(evidence, active_config.max_findings, options=options)
    quality = evaluate_quality(
        findings,
        draft=draft,
        min_source_backed_findings=active_config.min_source_backed_findings,
        options=options,
        all_evidence=evidence,
    )
    if output_format in ("markdown", "docx", "pdf"):
        return render_markdown_brief(
            options=options,
            evidence=evidence,
            findings=findings,
            quality=quality,
            draft=draft,
        )
    if output_format in ("ppt-outline", "pptx"):
        return render_ppt_outline(options, findings, quality, draft=draft, evidence=evidence)
    if output_format == "speaker-notes":
        return render_speaker_notes(options, findings, quality, draft=draft, evidence=evidence)
    if output_format == "qa":
        return render_qa_prep(options, findings, quality, draft=draft, evidence=evidence)
    raise ValueError("Unsupported output format: {0}".format(output_format))
