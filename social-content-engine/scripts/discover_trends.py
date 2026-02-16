#!/usr/bin/env python3
"""
Discover trending topics by running the trend-finder script and merging results
with additional social media trend signals.

This script wraps the existing trend-finder (find_trends.py) and produces
a merged raw-trends.md file for the social-content-engine pipeline.

Usage:
    # General trends
    python3 discover_trends.py

    # Niche-focused trends
    python3 discover_trends.py --topic "AI agents"

Requirements:
    pip3 install requests --break-system-packages
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_trend_finder(topic=None, geo="united_states", limit=20, related=True):
    """Run the trend-finder script and capture its output file."""
    script_path = Path(__file__).resolve().parent.parent.parent / "trend-finder" / "scripts" / "find_trends.py"

    if not script_path.exists():
        print(f"Warning: trend-finder script not found at {script_path}")
        return None

    today = datetime.now().strftime("%Y%m%d")
    suffix = f"-{topic.lower().replace(' ', '-')}" if topic else ""
    output_path = Path(f"OUTPUT/trends/{today}-trends{suffix}.md")

    cmd = [
        sys.executable, str(script_path),
        "--geo", geo,
        "--limit", str(limit),
        "--output", str(output_path),
    ]
    if topic:
        cmd.extend(["--topic", topic])
    if related and topic:
        cmd.append("--related")

    print(f"Running trend-finder: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"Warning: trend-finder exited with code {result.returncode}")
            if result.stderr:
                print(f"  stderr: {result.stderr[:500]}")
        else:
            print(f"  trend-finder output saved to {output_path}")
    except subprocess.TimeoutExpired:
        print("Warning: trend-finder timed out after 120s")
        return None
    except Exception as e:
        print(f"Warning: failed to run trend-finder: {e}")
        return None

    if output_path.exists():
        return output_path.read_text()
    return None


def parse_google_trends_table(content):
    """Extract topics from Google Trends markdown table."""
    topics = []
    if not content:
        return topics

    lines = content.split("\n")
    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith("| #") or line.startswith("|---"):
            in_table = True
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2:
                topics.append({
                    "topic": cols[1] if len(cols) > 1 else "",
                    "traffic": cols[2] if len(cols) > 2 else "",
                    "context": cols[3] if len(cols) > 3 else "",
                    "source": "google_trends",
                })
        elif in_table and not line.startswith("|"):
            in_table = False

    return topics


def build_raw_trends_md(google_trends_content, topic=None):
    """Build the raw-trends.md file from Google Trends data.

    Note: Twitter/X and social media signals are added by Claude via WebSearch
    during Phase 1 of the SKILL.md workflow. This script handles the automatable
    Google Trends portion only.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    focus = topic if topic else "General"

    lines = [
        f"# Raw Trend Signals — {today}",
        "",
        f"> Focus: **{focus}**",
        "",
    ]

    # Google Trends section
    lines.append("## Google Trends (via trend-finder)")
    lines.append("")

    if google_trends_content:
        # Include the Google Trends content directly (already formatted as tables)
        # Strip the header line if present
        gt_lines = google_trends_content.split("\n")
        skip_header = True
        for gl in gt_lines:
            if skip_header and (gl.startswith("# ") or gl.startswith("> ")):
                continue
            skip_header = False
            lines.append(gl)
    else:
        lines.append("*Google Trends data unavailable — rate-limited or network error.*")
        lines.append("")

    # Placeholder sections for Claude to fill via WebSearch
    lines.extend([
        "",
        "## Twitter/X Signals",
        "",
        "*To be filled by Claude via WebSearch during Phase 1.*",
        "",
        "| # | Topic | Source | Context |",
        "|---|-------|--------|---------|",
        "",
        "## Social Media Signals",
        "",
        "*To be filled by Claude via WebSearch during Phase 1.*",
        "",
        "| # | Topic | Platform | Context |",
        "|---|-------|----------|---------|",
        "",
        "## Combined Topic List",
        "",
        "*To be merged by Claude after all signals are collected.*",
        "",
    ])

    # Extract topics for the combined list
    topics = parse_google_trends_table(google_trends_content)
    if topics:
        for i, t in enumerate(topics[:20], 1):
            src = "Google Trends"
            lines.append(f"{i}. {t['topic']} ({src})")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Discover trending topics for social content engine"
    )
    parser.add_argument("--topic", type=str, default=None, help="Niche focus keyword")
    parser.add_argument("--geo", type=str, default="united_states", help="Country for trends")
    parser.add_argument("--limit", type=int, default=20, help="Max trending items")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    args = parser.parse_args()

    today = datetime.now().strftime("%Y%m%d")

    # Resolve output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(f"OUTPUT/social-content/{today}")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "raw-trends.md"

    print(f"=== Social Content Engine: Discover Phase ===")
    print(f"Date: {today}")
    if args.topic:
        print(f"Topic: {args.topic}")
    print()

    # Step 1: Run trend-finder for Google Trends
    print("Step 1: Fetching Google Trends...")
    google_trends_content = run_trend_finder(
        topic=args.topic,
        geo=args.geo,
        limit=args.limit,
    )

    # Step 2: Build raw-trends.md
    print("\nStep 2: Building raw-trends.md...")
    raw_trends = build_raw_trends_md(google_trends_content, topic=args.topic)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(raw_trends)
    print(f"\nRaw trends saved to: {output_path}")
    print("\nNote: Twitter/X and social media signals should be added by Claude via WebSearch.")
    print("Run the full /social-content-engine skill for the complete pipeline.")


if __name__ == "__main__":
    main()
