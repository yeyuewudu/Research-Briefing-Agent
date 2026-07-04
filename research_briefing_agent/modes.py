from typing import Iterable, List, Tuple

from .models import Evidence


MODE_FOCUS = {
    "paper": [
        "Frame the research problem, method, data, results, contribution, and limits.",
        "Prepare evidence that can support a lab meeting or reading group discussion.",
    ],
    "investment": [
        "Extract the core thesis, data support, industry logic, catalysts, and risks.",
        "Separate investment conclusions from assumptions that require validation.",
    ],
    "teaching": [
        "Turn learning materials into a teachable outline, examples, and discussion prompts.",
        "Highlight concepts that need explanation before presenting conclusions.",
    ],
    "topic": [
        "Combine multiple materials into one coherent theme rather than separate summaries.",
        "Track consensus, disagreement, missing evidence, and follow-up research needs.",
    ],
}


MODE_SECTION_TITLES = {
    "paper": "Research Reading Notes",
    "investment": "Investment Thesis Scaffold",
    "teaching": "Teaching Plan Scaffold",
    "topic": "Synthesis Scaffold",
}


MODE_EMPTY_GUIDANCE = {
    "paper": [
        "Add notes about the research problem, method, dataset, results, and limitations.",
        "Include claims that can be traced to exact sections, tables, or figures.",
    ],
    "investment": [
        "Add notes about market size, growth drivers, competitive position, valuation, and risks.",
        "Include dated data points and source names for each financial or industry claim.",
    ],
    "teaching": [
        "Add notes about learning objectives, core concepts, examples, and expected questions.",
        "Include the teacher's requirements or grading focus when available.",
    ],
    "topic": [
        "Add notes from multiple materials so the brief can compare consensus and disagreement.",
        "Include source dates and author context for time-sensitive claims.",
    ],
}


MODE_IMPLICATIONS = {
    "paper": [
        "Identify how the findings change the understanding of the research problem.",
        "Separate demonstrated contributions from possible future extensions.",
        "Flag methods, datasets, or assumptions that need closer inspection.",
    ],
    "investment": [
        "Clarify which value drivers matter most to the investment view.",
        "Separate reported data from forward-looking assumptions.",
        "Track downside risks and evidence that could weaken the thesis.",
    ],
    "teaching": [
        "Turn dense material into a sequence that the audience can follow.",
        "Use examples or cases to make abstract claims easier to explain.",
        "Prepare likely questions before the classroom or presentation setting.",
    ],
    "topic": [
        "Clarify which stakeholders are most affected by this topic.",
        "Separate confirmed evidence from assumptions before making decisions.",
        "Track the most important unknowns as follow-up research items.",
    ],
}


MODE_OPEN_QUESTIONS = {
    "paper": [
        "Which claims are directly supported by experiments or data?",
        "What are the strongest limitations or threats to validity?",
        "Which follow-up study would most improve the work?",
    ],
    "investment": [
        "Which data would most change the current investment interpretation?",
        "What assumptions drive the upside and downside cases?",
        "Which industry or company sources are missing?",
    ],
    "teaching": [
        "Which concepts will the audience likely find hardest?",
        "What examples or cases would make the material more concrete?",
        "What questions should be prepared for discussion or Q&A?",
    ],
    "topic": [
        "What evidence would change the current interpretation?",
        "Which data sources are missing or underrepresented?",
        "What decision needs this briefing to support?",
    ],
}


DEFAULT_NEXT_STEPS = [
    "Validate the strongest claims against primary sources.",
    "Add fresh source notes for any time-sensitive facts.",
    "Turn this brief into an action memo for the target audience.",
]


def focus_for(mode: str) -> List[str]:
    return MODE_FOCUS[mode]


def section_title_for(mode: str) -> str:
    return MODE_SECTION_TITLES[mode]


def empty_guidance_for(mode: str) -> List[str]:
    return MODE_EMPTY_GUIDANCE[mode]


def implications_for(mode: str) -> List[str]:
    return MODE_IMPLICATIONS[mode]


def open_questions_for(mode: str) -> List[str]:
    return MODE_OPEN_QUESTIONS[mode]


def next_steps() -> List[str]:
    return list(DEFAULT_NEXT_STEPS)


def scaffold_points(mode: str, findings: List[Evidence]) -> List[Tuple[str, Evidence]]:
    labels = {
        "paper": [
            "Problem / Background",
            "Method / Evidence",
            "Result / Contribution",
            "Limit / Follow-up",
        ],
        "investment": [
            "Core Thesis",
            "Data Support",
            "Industry Logic",
            "Risk / Watch Item",
        ],
        "teaching": [
            "Learning Objective",
            "Core Concept",
            "Example / Case",
            "Q&A Preparation",
        ],
        "topic": [
            "Main Theme",
            "Supporting Evidence",
            "Consensus / Tension",
            "Missing Evidence",
        ],
    }
    return [
        (label, _item_at(findings, index))
        for index, label in enumerate(labels[mode])
    ]


def _item_at(items: List[Evidence], index: int) -> Evidence:
    if index < len(items):
        return items[index]
    return Evidence(
        id="missing-{0}".format(index),
        text="Needs more evidence for this part of the briefing.",
        location="",
        confidence="needs review",
    )
