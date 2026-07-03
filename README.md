# Research Briefing Agent

A lightweight Python command-line project for turning rough research notes into a structured briefing document.

## What It Does

- Accepts a research topic, audience, and optional source notes.
- Produces a clean Markdown briefing with summary, findings, implications, open questions, and next steps.
- Runs with the Python standard library only.

## Quick Start

```powershell
python -m research_briefing_agent --topic "AI policy in healthcare" --audience "product leaders"
```

To include local notes:

```powershell
python -m research_briefing_agent --topic "Battery supply chains" --source .\notes\example_notes.md
```

Save the output:

```powershell
python -m research_briefing_agent --topic "Semiconductor exports" --output .\brief.md
```

## Project Layout

```text
.
├── research_briefing_agent/
│   ├── __init__.py
│   ├── __main__.py
│   ├── brief.py
│   ├── cli.py
│   └── sources.py
├── tests/
│   └── test_brief.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Run Tests

```powershell
python -m unittest discover
```

## Next Ideas

- Add web search ingestion.
- Add LLM-backed summarization.
- Export briefings to PDF or Word.
- Store reusable briefing templates.
