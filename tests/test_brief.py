import unittest

from research_briefing_agent.brief import BriefOptions, generate_brief


class GenerateBriefTests(unittest.TestCase):
    def test_generates_markdown_with_topic_and_notes(self):
        brief = generate_brief(
            BriefOptions(topic="AI governance", audience="policy teams"),
            ["New rules increase reporting expectations.", "Teams need audit trails."],
        )

        self.assertIn("# Research Brief: AI governance", brief)
        self.assertIn("**Audience:** policy teams", brief)
        self.assertIn("- New rules increase reporting expectations.", brief)
        self.assertIn("## Recommended Next Steps", brief)

    def test_generates_placeholder_when_no_notes_exist(self):
        brief = generate_brief(BriefOptions(topic="Battery markets"), [])

        self.assertIn("No source notes were provided yet", brief)
        self.assertIn("Add source notes", brief)


if __name__ == "__main__":
    unittest.main()
