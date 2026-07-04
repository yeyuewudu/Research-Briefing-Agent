# Research Briefing Agent Project Thinking

## Positioning

Research Briefing Agent is an AI-first, source-backed briefing system. It is
built for large-model use, not for rule-based summarization.

Its product shape is:

```text
materials -> chunks -> LLM evidence-aware synthesis -> citations -> quality review -> deliverable
```

The most valuable user scenarios are:

- Paper to group-meeting briefing.
- Research report to investment briefing.
- Course materials to presentation outline and Q&A.
- Multiple documents to one topic synthesis.

The differentiator is useful AI composition plus trust. The model writes the
briefing, slide plan, speaker notes, and Q&A, while the app preserves citations
back to source chunks.

## Current Architecture

- `config.py`: environment and runtime settings.
- `models.py`: domain models such as `Source`, `Evidence`, `BriefDraft`, `SlideDraft`, and `QAPair`.
- `sources.py`: local source and URL ingestion.
- `evidence.py`: evidence normalization.
- `llm.py`: LLM synthesis for findings, slide plans, speaker notes, and Q&A.
- `quality.py`: evidence coverage and review notes.
- `renderer.py`: rendering for brief, PPT outline, speaker notes, and Q&A.
- `exporters.py`: output writers for text, DOCX, PDF, and PPTX.
- `brief.py`: pipeline orchestration.
- `cli.py`: command-line interface.

## Current Pipeline

```text
CLI args
  -> AppConfig.from_env()
  -> read_source_notes()
  -> normalize_evidence()
  -> synthesize_brief() with LLM
  -> evaluate_quality()
  -> render requested deliverable
  -> optional file export
```

## Configuration Strategy

Runtime knobs live in `AppConfig` and can come from environment variables or CLI
overrides:

- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_RESPONSES_URL`
- `DEEPSEEK_API_KEY`
- `DASHSCOPE_API_KEY`
- `MOONSHOT_API_KEY`
- `ZHIPU_API_KEY`
- `LLM_BASE_URL`
- `LLM_API_KEY_ENV`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`
- `MAX_FINDINGS`
- `MIN_SOURCE_BACKED_FINDINGS`

Supported provider families:

- `openai`: OpenAI Responses API.
- `openai-chat`: OpenAI Chat Completions API.
- `deepseek`: DeepSeek OpenAI-compatible Chat Completions.
- `qwen`: Alibaba DashScope / Qwen OpenAI-compatible Chat Completions.
- `moonshot`: Moonshot / Kimi OpenAI-compatible Chat Completions.
- `zhipu`: Zhipu / GLM OpenAI-compatible Chat Completions.
- `custom-chat`: any OpenAI-compatible Chat Completions endpoint.

## LLM Strategy

- LLM output must be structured JSON.
- LLM findings must cite existing evidence IDs.
- LLM slide plans must cite existing evidence IDs.
- LLM speaker notes must cite existing evidence IDs.
- LLM Q&A answers must cite existing evidence IDs.
- Unknown evidence IDs are filtered out.
- Rendered output shows human-readable citations from local evidence.

## Completed Technical Milestones

- Text and Markdown ingestion with line/line-range citations.
- CSV with row citations.
- PDF with page and paragraph citations.
- DOCX with paragraph citations.
- PPTX with slide citations.
- XLSX with sheet and row citations.
- URL ingestion.
- LLM-generated summary, findings, synthesis, slides, speaker notes, and Q&A.
- Markdown, PPT outline, speaker notes, Q&A, DOCX, PDF, and PPTX outputs.
- Source coverage and evidence review notes.

## Next Technical Milestones

- Chunking controls for large PDFs and long webpages.
- Multi-call map-reduce synthesis for large documents.
- Better PPTX visual layout and theme support.
- Stronger contradiction detection.
- Source metadata extraction for authors, dates, publishers, and retrieval time.
