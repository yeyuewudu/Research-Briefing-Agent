import json
import urllib.error
import urllib.request
from typing import Dict, Iterable, List, Optional

from .config import AppConfig, LLM_PROVIDERS
from .models import (
    BriefDraft,
    BriefOptions,
    DraftPoint,
    Evidence,
    LabelledDraftPoint,
    QAPair,
    SlideDraft,
    SpeakerNote,
)


DEFAULT_MODEL = AppConfig.from_env().openai_model
CHAT_COMPLETIONS_PATH = "/chat/completions"


class LlmError(RuntimeError):
    pass


def synthesize_brief(
    options: BriefOptions,
    evidence: Iterable[Evidence],
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    config: Optional[AppConfig] = None,
    client=None,
) -> BriefDraft:
    active_config = config or AppConfig.from_env()
    evidence_items = list(evidence)
    if not evidence_items:
        raise LlmError("LLM synthesis requires at least one source-backed evidence item.")

    if active_config.llm_provider not in LLM_PROVIDERS:
        raise LlmError("Unsupported LLM provider: {0}".format(active_config.llm_provider))

    if client:
        active_model = model or (
            active_config.openai_model
            if active_config.llm_provider == "openai"
            else active_config.chat_model
        )
        api_client = client
    elif active_config.llm_provider == "openai":
        active_model = model or active_config.openai_model
        api_client = OpenAIResponsesClient(
            api_key=api_key or active_config.openai_api_key,
            responses_url=active_config.openai_responses_url,
            timeout=active_config.llm_timeout_seconds,
        )
    else:
        active_model = model or active_config.chat_model
        api_client = ChatCompletionsClient(
            api_key=api_key or active_config.chat_api_key,
            api_key_env=active_config.chat_api_key_env,
            base_url=active_config.chat_base_url,
            timeout=active_config.llm_timeout_seconds,
            provider=active_config.llm_provider,
        )

    response = api_client.create_structured_response(
        _build_request_payload(
            options,
            evidence_items,
            active_model,
            provider=active_config.llm_provider,
        )
    )
    data = _extract_json_response(response)
    return _parse_brief_draft(data, {item.id for item in evidence_items})


class OpenAIResponsesClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        responses_url: Optional[str] = None,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or AppConfig.from_env().openai_api_key
        self.responses_url = responses_url or AppConfig.from_env().openai_responses_url
        self.timeout = timeout
        if not self.api_key:
            raise LlmError("OPENAI_API_KEY is required.")

    def create_structured_response(self, payload: Dict[str, object]) -> Dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.responses_url,
            data=body,
            headers={
                "Authorization": "Bearer {0}".format(self.api_key),
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise LlmError("OpenAI API request failed: {0} {1}".format(error.code, detail))
        except urllib.error.URLError as error:
            raise LlmError("OpenAI API request failed: {0}".format(error.reason))


class ChatCompletionsClient:
    def __init__(
        self,
        api_key: Optional[str],
        api_key_env: str,
        base_url: str,
        timeout: int = 60,
        provider: str = "chat-compatible",
    ) -> None:
        self.api_key = api_key
        self.api_key_env = api_key_env
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = timeout
        self.provider = provider
        if not self.api_key:
            raise LlmError("{0} is required for provider {1}.".format(api_key_env, provider))
        if not self.base_url:
            raise LlmError("LLM_BASE_URL is required for provider {0}.".format(provider))

    def create_structured_response(self, payload: Dict[str, object]) -> Dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            "{0}{1}".format(self.base_url, CHAT_COMPLETIONS_PATH),
            data=body,
            headers={
                "Authorization": "Bearer {0}".format(self.api_key),
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise LlmError(
                "{0} API request failed: {1} {2}".format(
                    self.provider,
                    error.code,
                    detail,
                )
            )
        except urllib.error.URLError as error:
            raise LlmError("{0} API request failed: {1}".format(self.provider, error.reason))


def _build_request_payload(
    options: BriefOptions,
    evidence: List[Evidence],
    model: str,
    provider: str = "openai",
) -> Dict[str, object]:
    evidence_payload = [
        {
            "id": item.id,
            "text": item.text,
            "citation": item.citation,
            "confidence": item.confidence,
        }
        for item in evidence
    ]
    messages = [
        {
            "role": "system",
            "content": _system_prompt(),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "topic": options.topic,
                    "audience": options.audience,
                    "tone": options.tone,
                    "mode": options.mode,
                    "task": (
                        "Create a high-quality briefing deliverable. Prioritize "
                        "insight, narrative flow, decision usefulness, and citations."
                    ),
                    "evidence": evidence_payload,
                },
                ensure_ascii=True,
            ),
        },
    ]

    if provider != "openai":
        return {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "stream": False,
        }

    return {
        "model": model,
        "input": messages,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "research_brief_draft",
                "strict": True,
                "schema": _brief_schema(),
            }
        },
    }


def _system_prompt() -> str:
    return (
        "You are an AI research briefing agent. Transform source chunks into a "
        "useful, presentation-ready briefing. Do not summarize mechanically. Infer "
        "the briefing structure, extract important claims, build a slide plan, "
        "write speaker notes, and prepare Q&A. Use only the provided evidence. "
        "Every factual claim, finding, slide, speaker note, and answer must include "
        "evidence_ids from the provided list. If evidence is insufficient, say so. "
        "Return only valid JSON matching this schema: {0}".format(
            json.dumps(_brief_schema(), ensure_ascii=True)
        )
    )


def _brief_schema() -> Dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "key_findings": {
                "type": "array",
                "items": _draft_point_schema(["finding", "evidence_ids"]),
            },
            "synthesis_title": {"type": "string"},
            "synthesis_points": {
                "type": "array",
                "items": _labelled_draft_point_schema(),
            },
            "implications": {"type": "array", "items": {"type": "string"}},
            "open_questions": {"type": "array", "items": {"type": "string"}},
            "recommended_next_steps": {"type": "array", "items": {"type": "string"}},
            "slides": {
                "type": "array",
                "items": _slide_schema(),
            },
            "speaker_notes": {
                "type": "array",
                "items": _speaker_note_schema(),
            },
            "qa_pairs": {
                "type": "array",
                "items": _qa_pair_schema(),
            },
        },
        "required": [
            "summary",
            "key_findings",
            "synthesis_title",
            "synthesis_points",
            "implications",
            "open_questions",
            "recommended_next_steps",
            "slides",
            "speaker_notes",
            "qa_pairs",
        ],
    }


def _draft_point_schema(required: List[str]) -> Dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "finding": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
        },
        "required": required,
    }


def _labelled_draft_point_schema() -> Dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "label": {"type": "string"},
            "text": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["label", "text", "evidence_ids"],
    }


def _slide_schema() -> Dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "key_message": {"type": "string"},
            "bullets": {"type": "array", "items": {"type": "string"}},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
            "speaker_notes": {"type": "string"},
        },
        "required": ["title", "key_message", "bullets", "evidence_ids", "speaker_notes"],
    }


def _speaker_note_schema() -> Dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "section": {"type": "string"},
            "text": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["section", "text", "evidence_ids"],
    }


def _qa_pair_schema() -> Dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "question": {"type": "string"},
            "answer": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["question", "answer", "evidence_ids"],
    }


def _extract_json_response(response: Dict[str, object]) -> Dict[str, object]:
    if "output_text" in response:
        return json.loads(response["output_text"])

    if "choices" in response:
        content = response["choices"][0]["message"].get("content", "{}")
        return _loads_json_content(content)

    for output_item in response.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                return _loads_json_content(content_item.get("text", "{}"))

    raise LlmError("LLM response did not contain structured output text.")


def _loads_json_content(content: str) -> Dict[str, object]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1])
        raise


def _parse_brief_draft(data: Dict[str, object], allowed_evidence_ids: set) -> BriefDraft:
    return BriefDraft(
        summary=str(data.get("summary", "")),
        key_findings=[
            DraftPoint(
                text=str(item.get("finding", "")),
                evidence_ids=_allowed_ids(item.get("evidence_ids", []), allowed_evidence_ids),
            )
            for item in data.get("key_findings", [])
            if item.get("finding")
        ],
        synthesis_title=str(data.get("synthesis_title", "LLM Synthesis")),
        synthesis_points=[
            LabelledDraftPoint(
                label=str(item.get("label", "Point")),
                text=str(item.get("text", "")),
                evidence_ids=_allowed_ids(item.get("evidence_ids", []), allowed_evidence_ids),
            )
            for item in data.get("synthesis_points", [])
            if item.get("text")
        ],
        implications=[str(item) for item in data.get("implications", []) if item],
        open_questions=[str(item) for item in data.get("open_questions", []) if item],
        recommended_next_steps=[
            str(item) for item in data.get("recommended_next_steps", []) if item
        ],
        slides=[
            SlideDraft(
                title=str(item.get("title", "Slide")),
                key_message=str(item.get("key_message", "")),
                bullets=[str(bullet) for bullet in item.get("bullets", []) if bullet],
                evidence_ids=_allowed_ids(item.get("evidence_ids", []), allowed_evidence_ids),
                speaker_notes=str(item.get("speaker_notes", "")),
            )
            for item in data.get("slides", [])
            if item.get("title")
        ],
        speaker_notes=[
            SpeakerNote(
                section=str(item.get("section", "Notes")),
                text=str(item.get("text", "")),
                evidence_ids=_allowed_ids(item.get("evidence_ids", []), allowed_evidence_ids),
            )
            for item in data.get("speaker_notes", [])
            if item.get("text")
        ],
        qa_pairs=[
            QAPair(
                question=str(item.get("question", "")),
                answer=str(item.get("answer", "")),
                evidence_ids=_allowed_ids(item.get("evidence_ids", []), allowed_evidence_ids),
            )
            for item in data.get("qa_pairs", [])
            if item.get("question") and item.get("answer")
        ],
        raw=data,
    )


def _allowed_ids(values: Iterable[object], allowed_evidence_ids: set) -> List[str]:
    return [str(value) for value in values if str(value) in allowed_evidence_ids]
