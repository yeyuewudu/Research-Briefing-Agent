import argparse
import os
import sys
from pathlib import Path

from .brief import BriefOptions, generate_brief
from .config import AppConfig, LLM_PROVIDERS, OUTPUT_FORMATS
from .exporters import BINARY_OUTPUT_FORMATS, render_format_for_output, write_output
from .llm import LlmError, synthesize_brief
from .models import BRIEFING_MODES
from .sources import read_source_notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-briefing-agent",
        description="Generate a structured Markdown research briefing.",
    )
    parser.add_argument("--topic", required=True, help="Research topic for the briefing.")
    parser.add_argument(
        "--audience",
        default="general readers",
        help="Target audience for the briefing.",
    )
    parser.add_argument(
        "--tone",
        default="clear and concise",
        help="Writing tone to use in the briefing.",
    )
    parser.add_argument(
        "--mode",
        choices=BRIEFING_MODES,
        default="topic",
        help="Briefing mode: paper, investment, teaching, or topic.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Path or URL to source material. Can be used multiple times.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for the generated Markdown file. Prints to the console when omitted.",
    )
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="markdown",
        help="Output format to render.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use. Overrides OPENAI_MODEL/LLM_MODEL/provider default.",
    )
    parser.add_argument(
        "--provider",
        choices=LLM_PROVIDERS,
        help="LLM provider: openai, deepseek, qwen, moonshot, zhipu, openai-chat, or custom-chat.",
    )
    parser.add_argument(
        "--base-url",
        help="Chat-completions base URL for OpenAI-compatible providers.",
    )
    parser.add_argument(
        "--api-key-env",
        help="Environment variable name that stores the provider API key.",
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        help="Maximum evidence items to promote into key findings.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    options = BriefOptions(
        topic=args.topic,
        audience=args.audience,
        tone=args.tone,
        mode=args.mode,
    )
    config = AppConfig.from_env()
    if args.provider:
        config.use_provider(args.provider)
    if args.model:
        config.openai_model = args.model
        config.chat_model = args.model
    if args.base_url:
        config.chat_base_url = args.base_url
    if args.api_key_env:
        config.chat_api_key_env = args.api_key_env
        config.chat_api_key = os.environ.get(args.api_key_env, "")
    if args.max_findings:
        config.max_findings = args.max_findings

    if not args.source:
        parser.error("At least one --source is required.")
    if args.format in BINARY_OUTPUT_FORMATS and not args.output:
        parser.error("--output is required when --format is {0}.".format(args.format))

    notes = read_source_notes(args.source)
    try:
        draft = synthesize_brief(options, notes, config=config)
    except LlmError as error:
        parser.error(str(error))

    render_format = render_format_for_output(args.format)
    brief = generate_brief(
        options,
        notes,
        draft=draft,
        config=config,
        output_format=render_format,
    )

    if args.output:
        output_path = Path(args.output)
        try:
            write_output(output_path, brief, args.format)
        except ImportError as error:
            parser.error(str(error))
        print("Brief written to {0}".format(output_path))
    else:
        sys.stdout.write(brief)

    return 0
