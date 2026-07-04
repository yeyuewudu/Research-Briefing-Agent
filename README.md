# Research Briefing Agent

An AI-first briefing agent for turning PDFs, webpages, spreadsheets, documents,
slides, and notes into cited briefings, PPT outlines, speaker notes, Q&A prep,
and export files.

## Product Direction

This project exists to use large models well. Local parsing only prepares source
chunks and citations. The model does the actual understanding, synthesis, slide
planning, speaker-note writing, and Q&A preparation.

```text
source material -> source chunks -> LLM synthesis -> cited deliverable
```

## Current Capabilities

- Reads `.txt`, `.md`, `.csv`, `.pdf`, `.docx`, `.pptx`, `.xlsx`, and `http(s)` URL sources.
- Converts source content into cited `Evidence` with file, row, page, paragraph, slide, sheet, or line references.
- Calls a configured large model to generate structured findings, slide plans, speaker notes, and Q&A from evidence IDs.
- Filters unknown evidence IDs from model output.
- Produces `markdown`, `ppt-outline`, `speaker-notes`, `qa`, `docx`, `pdf`, and `pptx`.
- Reviews source coverage, source type coverage, stale date hints, and mode-specific evidence gaps.
- Keeps model, timeout, endpoint, and evidence limits in an independent config layer.

## Briefing Modes

- `paper`: paper reading, group meeting, or lab meeting notes.
- `investment`: industry, company, market, or investment memo.
- `teaching`: classroom presentation, lecture, report, or Q&A preparation.
- `topic`: multi-document topic synthesis.

## Install

```powershell
cd "E:\code\mycode\Research Briefing Agent"
pip3 install -e ".[all]"
```

Manual package install:

```powershell
pip3 install openpyxl pypdf python-docx python-pptx reportlab openai
pip3 install -e .
```

## Configuration

Default OpenAI Responses API:

```powershell
$env:LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="your-api-key"
$env:OPENAI_MODEL="gpt-5.5"
$env:OPENAI_RESPONSES_URL="https://api.openai.com/v1/responses"
$env:LLM_TIMEOUT_SECONDS="60"
$env:MAX_FINDINGS="5"
$env:MIN_SOURCE_BACKED_FINDINGS="3"
```

DeepSeek:

```powershell
$env:LLM_PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-deepseek-key"
$env:LLM_MODEL="deepseek-v4-pro"
```

通义千问 / Qwen / DashScope:

```powershell
$env:LLM_PROVIDER="qwen"
$env:DASHSCOPE_API_KEY="your-dashscope-key"
$env:LLM_MODEL="qwen-plus"
```

Kimi / Moonshot:

```powershell
$env:LLM_PROVIDER="moonshot"
$env:MOONSHOT_API_KEY="your-moonshot-key"
$env:LLM_MODEL="moonshot-v1-128k"
```

智谱 / GLM:

```powershell
$env:LLM_PROVIDER="zhipu"
$env:ZHIPU_API_KEY="your-zhipu-key"
$env:LLM_MODEL="glm-4-plus"
```

Custom OpenAI-compatible Chat Completions provider:

```powershell
$env:LLM_PROVIDER="custom-chat"
$env:LLM_API_KEY="your-provider-key"
$env:LLM_API_KEY_ENV="LLM_API_KEY"
$env:LLM_BASE_URL="https://your-provider.example.com/v1"
$env:LLM_MODEL="your-model"
```

You can also select the provider from CLI:

```powershell
python -m research_briefing_agent --provider deepseek --model deepseek-v4-pro --topic "paper briefing" --mode paper --source ".\paper.pdf"
```

## Usage

PDF to PPTX:

```powershell
python -m research_briefing_agent --topic "paper group meeting briefing" --mode paper --source ".\paper.pdf" --format pptx --output paper_brief.pptx
```

Webpage to PPT outline:

```powershell
python -m research_briefing_agent --topic "AI policy trends" --mode topic --source "https://example.com/report" --format ppt-outline
```

Multiple sources to investment brief:

```powershell
python -m research_briefing_agent `
  --topic "battery supply chain investment briefing" `
  --mode investment `
  --source ".\battery_report.pdf" `
  --source ".\data.csv" `
  --source "https://example.com/battery-news" `
  --format docx `
  --output battery_brief.docx
```

Speaker notes:

```powershell
python -m research_briefing_agent --topic "course presentation" --mode teaching --source ".\lesson.docx" --format speaker-notes --output notes.md
```

Q&A prep:

```powershell
python -m research_briefing_agent --topic "paper defense preparation" --mode paper --source ".\paper.pdf" --format qa --output qa.md
```

Choose a model:

```powershell
python -m research_briefing_agent --topic "AI governance" --mode topic --source ".\notes.md" --model gpt-5.5
```

Choose a Chinese model provider:

```powershell
python -m research_briefing_agent --provider deepseek --model deepseek-v4-pro --topic "论文组会汇报" --mode paper --source ".\paper.pdf" --format pptx --output paper_brief.pptx
python -m research_briefing_agent --provider qwen --model qwen-plus --topic "行业投资简报" --mode investment --source ".\report.pdf" --format docx --output report.docx
python -m research_briefing_agent --provider moonshot --model moonshot-v1-128k --topic "课程汇报" --mode teaching --source ".\lesson.docx" --format speaker-notes --output notes.md
python -m research_briefing_agent --provider zhipu --model glm-4-plus --topic "专题汇报" --mode topic --source ".\notes.md" --format qa --output qa.md
```

## Testing

Automated tests mock model responses and do not require an API key:

```powershell
python -m unittest discover
python -m compileall research_briefing_agent tests
```

Manual functional tests require the API key for the selected provider because
the app always uses the model for generation.

## Project Notes

Detailed design notes live in [docs/PROJECT_THINKING.md](docs/PROJECT_THINKING.md).
