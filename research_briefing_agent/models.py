from dataclasses import dataclass, field
from typing import Dict, List, Optional


BRIEFING_MODES = ("paper", "investment", "teaching", "topic")


@dataclass
class BriefOptions:
    topic: str
    audience: str = "general readers"
    tone: str = "clear and concise"
    mode: str = "topic"

    def __post_init__(self) -> None:
        if self.mode not in BRIEFING_MODES:
            raise ValueError(
                "Unsupported briefing mode: {0}. Expected one of: {1}".format(
                    self.mode, ", ".join(BRIEFING_MODES)
                )
            )


@dataclass
class Source:
    id: str
    title: str
    path: str
    source_type: str = "file"


@dataclass
class Evidence:
    id: str
    text: str
    source: Optional[Source] = None
    location: str = ""
    confidence: str = "needs review"
    relevance_score: int = 0

    @property
    def citation(self) -> str:
        if self.source and self.location:
            return "{0}:{1}".format(self.source.title, self.location)
        if self.source:
            return self.source.title
        return "needs validation"


@dataclass
class DraftPoint:
    text: str
    evidence_ids: List[str]


@dataclass
class LabelledDraftPoint:
    label: str
    text: str
    evidence_ids: List[str]


@dataclass
class BriefDraft:
    summary: str
    key_findings: List[DraftPoint]
    synthesis_title: str
    synthesis_points: List[LabelledDraftPoint]
    implications: List[str]
    open_questions: List[str]
    recommended_next_steps: List[str]
    slides: List["SlideDraft"] = field(default_factory=list)
    speaker_notes: List["SpeakerNote"] = field(default_factory=list)
    qa_pairs: List["QAPair"] = field(default_factory=list)
    raw: Optional[Dict[str, object]] = None


@dataclass
class SlideDraft:
    title: str
    key_message: str
    bullets: List[str]
    evidence_ids: List[str]
    speaker_notes: str = ""


@dataclass
class SpeakerNote:
    section: str
    text: str
    evidence_ids: List[str] = field(default_factory=list)


@dataclass
class QAPair:
    question: str
    answer: str
    evidence_ids: List[str] = field(default_factory=list)
