import argparse
import sys
from pathlib import Path

from .brief import BriefOptions, generate_brief
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
        "--source",
        action="append",
        default=[],
        help="Path to a text or Markdown file containing source notes. Can be used multiple times.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for the generated Markdown file. Prints to the console when omitted.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    options = BriefOptions(topic=args.topic, audience=args.audience, tone=args.tone)
    notes = read_source_notes([Path(path) for path in args.source])
    brief = generate_brief(options, notes)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(brief, encoding="utf-8")
        print("Brief written to {0}".format(output_path))
    else:
        sys.stdout.write(brief)

    return 0
