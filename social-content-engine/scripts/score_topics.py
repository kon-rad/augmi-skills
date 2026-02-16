#!/usr/bin/env python3
"""
Score and rank topics from raw-trends.md for content creation.

Uses a keyword-based scoring rubric to estimate virality and AUGMI relevance.
Claude refines these scores with AI judgment after the script runs.

Usage:
    python3 score_topics.py --input OUTPUT/social-content/YYYYMMDD/raw-trends.md
                            --output OUTPUT/social-content/YYYYMMDD/scored-topics.md

Requirements:
    No dependencies beyond Python stdlib.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


# Keywords that indicate AUGMI relevance (case-insensitive)
RELEVANCE_KEYWORDS = {
    # Direct relevance (high score)
    10: ["ai agent", "autonomous agent", "crypto wallet", "openclaw", "augmi"],
    9: ["ai bot", "chatbot platform", "agent framework", "ai assistant deploy"],
    8: ["ai agents", "autonomous ai", "no-code ai", "ai deployment", "personal ai",
        "ai coding", "ai developer tool", "web3 ai", "crypto ai", "defi agent"],
    7: ["artificial intelligence", "machine learning", "large language model", "llm",
        "crypto", "bitcoin", "ethereum", "web3", "defi", "blockchain", "nft",
        "no-code", "low-code", "automation"],
    6: ["ai tool", "ai startup", "chatgpt", "claude", "gemini", "openai",
        "anthropic", "tech startup", "saas", "api"],
    5: ["developer", "coding", "programming", "software", "startup", "entrepreneur",
        "tech industry", "silicon valley", "venture capital"],
    4: ["technology", "digital", "innovation", "app", "platform", "cloud"],
}

# Keywords that indicate virality potential (case-insensitive)
VIRALITY_KEYWORDS = {
    10: ["breaking", "just announced", "shock", "unprecedented"],
    9: ["viral", "exploding", "massive", "record-breaking"],
    8: ["controversy", "debate", "banned", "leaked", "exposed"],
    7: ["trending", "surge", "boom", "crisis", "breakthrough"],
    6: ["new", "launch", "release", "update", "announce"],
    5: ["growth", "rise", "popular", "hot"],
}


def extract_topics_from_raw_trends(content):
    """Extract topics from the raw-trends.md file."""
    topics = []
    seen = set()

    # Extract from markdown tables: | # | Topic | ... |
    table_pattern = re.compile(r'^\|\s*\d+\s*\|\s*(.+?)\s*\|', re.MULTILINE)
    for match in table_pattern.finditer(content):
        topic = match.group(1).strip()
        if topic and topic.lower() not in seen and not topic.startswith("---"):
            seen.add(topic.lower())
            # Try to extract context from the same row
            row = match.group(0)
            cols = [c.strip() for c in row.split("|") if c.strip()]
            context = ""
            if len(cols) >= 3:
                context = cols[2]  # Traffic or context column
            if len(cols) >= 4:
                context += " " + cols[3]
            topics.append({
                "topic": topic,
                "context": context.strip(),
            })

    # Extract from numbered lists: 1. Topic (Source)
    list_pattern = re.compile(r'^\d+\.\s+(.+?)(?:\s*\(([^)]+)\))?\s*$', re.MULTILINE)
    for match in list_pattern.finditer(content):
        topic = match.group(1).strip()
        source = match.group(2) or ""
        if topic and topic.lower() not in seen:
            seen.add(topic.lower())
            topics.append({
                "topic": topic,
                "context": source.strip(),
            })

    return topics


def score_relevance(topic_text):
    """Score AUGMI relevance 1-10 based on keyword matching."""
    text_lower = topic_text.lower()
    best_score = 1

    for score, keywords in RELEVANCE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                best_score = max(best_score, score)

    return best_score


def score_virality(topic_text, traffic=""):
    """Score virality potential 1-10 based on signals."""
    text_lower = (topic_text + " " + traffic).lower()
    best_score = 3  # Base score for anything trending

    # Keyword-based scoring
    for score, keywords in VIRALITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                best_score = max(best_score, score)

    # Traffic volume boost
    traffic_lower = traffic.lower().replace(",", "").replace("+", "")
    if "m" in traffic_lower or "million" in traffic_lower:
        best_score = max(best_score, 9)
    elif "k" in traffic_lower:
        try:
            num = int(re.search(r'(\d+)', traffic_lower).group(1))
            if num >= 500:
                best_score = max(best_score, 8)
            elif num >= 200:
                best_score = max(best_score, 7)
            elif num >= 50:
                best_score = max(best_score, 6)
        except (ValueError, AttributeError):
            pass

    return best_score


def compute_combined_score(virality, relevance):
    """Combined = (Virality x 0.6) + (Relevance x 0.4)"""
    return round(virality * 0.6 + relevance * 0.4, 1)


def build_scored_output(scored_topics):
    """Build scored-topics.md content."""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# Scored Topics — {today}",
        "",
        "## Scoring Rubric",
        "Combined = (Virality x 0.6) + (Relevance x 0.4)",
        "",
        "> **Note:** These are preliminary keyword-based scores. Claude should refine",
        "> these scores with AI judgment, considering context, recency, and nuanced",
        "> relevance to AUGMI's mission of democratizing AI agent deployment.",
        "",
    ]

    # Top 3 selected
    top3 = scored_topics[:3]
    lines.append("## Top 3 Selected")
    lines.append("")

    for i, t in enumerate(top3, 1):
        lines.append(f"### {i}. {t['topic']} — Score: {t['combined']}")
        lines.append(f"- Virality: {t['virality']}/10 — {t['virality_reason']}")
        lines.append(f"- Relevance: {t['relevance']}/10 — {t['relevance_reason']}")
        lines.append(f"- Content angle: *To be determined by Claude during research phase*")
        lines.append("")

    # Full rankings table
    lines.append("## Full Rankings")
    lines.append("")
    lines.append("| # | Topic | Virality | Relevance | Combined | Selected |")
    lines.append("|---|-------|----------|-----------|----------|----------|")

    for i, t in enumerate(scored_topics, 1):
        selected = "YES" if i <= 3 else ""
        topic_display = t['topic'][:50] + "..." if len(t['topic']) > 50 else t['topic']
        lines.append(
            f"| {i} | {topic_display} | {t['virality']} | "
            f"{t['relevance']} | {t['combined']} | {selected} |"
        )

    lines.append("")
    return "\n".join(lines)


def get_relevance_reason(score):
    """Get a brief reason string for the relevance score."""
    if score >= 8:
        return "Directly related to AI agents, crypto, or autonomous AI"
    elif score >= 6:
        return "Related to AI/tech industry or Web3 ecosystem"
    elif score >= 4:
        return "General tech or startup adjacent"
    else:
        return "Tangentially related, needs creative angle"


def get_virality_reason(score):
    """Get a brief reason string for the virality score."""
    if score >= 8:
        return "High search volume, trending across platforms"
    elif score >= 6:
        return "Moderate interest, trending on 1-2 platforms"
    elif score >= 4:
        return "Some interest, single-source signal"
    else:
        return "Low current interest"


def main():
    parser = argparse.ArgumentParser(
        description="Score and rank trending topics for content creation"
    )
    parser.add_argument(
        "--input", "-i", type=str, required=True,
        help="Path to raw-trends.md"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output path for scored-topics.md"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    # Default output path: same directory as input
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / "scored-topics.md"

    print(f"=== Social Content Engine: Score Phase ===")
    print(f"Input: {input_path}")
    print()

    # Read and parse
    content = input_path.read_text()
    topics = extract_topics_from_raw_trends(content)

    if not topics:
        print("Error: No topics found in input file.")
        print("Expected markdown tables or numbered lists with topics.")
        return 1

    print(f"Found {len(topics)} topics to score")

    # Score each topic
    scored = []
    for t in topics:
        full_text = f"{t['topic']} {t['context']}"
        virality = score_virality(t['topic'], t['context'])
        relevance = score_relevance(full_text)
        combined = compute_combined_score(virality, relevance)

        scored.append({
            "topic": t['topic'],
            "context": t['context'],
            "virality": virality,
            "relevance": relevance,
            "combined": combined,
            "virality_reason": get_virality_reason(virality),
            "relevance_reason": get_relevance_reason(relevance),
        })

    # Sort by combined score descending
    scored.sort(key=lambda x: x['combined'], reverse=True)

    # Limit to top 10 for readability
    scored = scored[:10]

    # Build output
    output_content = build_scored_output(scored)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_content)
    print(f"\nScored topics saved to: {output_path}")

    # Print summary
    print("\nTop 3:")
    for i, t in enumerate(scored[:3], 1):
        print(f"  {i}. {t['topic']} (V:{t['virality']} R:{t['relevance']} C:{t['combined']})")

    return 0


if __name__ == "__main__":
    exit(main())
