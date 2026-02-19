#!/usr/bin/env python3
"""
Social Analytics Report Generator — Creates markdown reports from collected data.

Usage:
    python3 generate_report.py --data-dir <path> --output <path> [--date YYYY-MM-DD]
    python3 generate_report.py --data-dir ../../data/social-analytics --output ../../data/social-analytics/reports/2026-02-19-daily.md
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict | None:
    """Load a JSON file, return None if missing."""
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def fmt_num(n) -> str:
    """Format number with commas."""
    if n is None:
        return "N/A"
    if isinstance(n, str):
        try:
            n = float(n) if '.' in n else int(n)
        except ValueError:
            return n
    if isinstance(n, float):
        return f"{n:,.1f}"
    return f"{n:,}"


def fmt_change(change, prev=None) -> str:
    """Format change with sign and optional percentage."""
    if change is None or change == 0:
        return "0"
    sign = "+" if change > 0 else ""
    if prev and prev > 0:
        pct = (change / prev) * 100
        return f"{sign}{change:,} ({sign}{pct:.1f}%)"
    return f"{sign}{change:,}"


def get_history_value(history: list, date: str) -> dict | None:
    """Find a history entry by date."""
    for entry in history:
        if entry.get("date") == date:
            return entry
    return None


def get_change_over_period(history: list, date: str, days: int) -> int | None:
    """Calculate change over a period by looking back N entries."""
    current = None
    past = None

    for entry in history:
        if entry.get("date") == date:
            current = entry.get("value", entry.get("total"))
        if entry.get("date") <= date:
            # Count back
            pass

    if current is None:
        return None

    # Find entry approximately N days back
    target_idx = max(0, len(history) - days - 1)
    if target_idx < len(history):
        past_entry = history[target_idx]
        past = past_entry.get("value", past_entry.get("total"))

    if current is not None and past is not None:
        return current - past
    return None


def generate_report(data_dir: Path, date: str) -> str:
    """Generate markdown report from aggregated data."""
    followers_data = load_json(data_dir / "aggregated" / "followers.json")
    all_metrics = load_json(data_dir / "aggregated" / "all-metrics.json")

    if not followers_data and not all_metrics:
        return f"# Social Media Analytics Report - {date}\n\nNo data collected yet. Run `social-analytics:collect` first.\n"

    lines = []

    # Frontmatter
    lines.append("---")
    lines.append(f'generated_at: "{datetime.now(timezone.utc).isoformat()}"')
    lines.append('report_type: "daily"')
    lines.append(f'date: "{date}"')
    if followers_data:
        platforms = list(followers_data.get("platforms", {}).keys())
        lines.append(f'platforms: {json.dumps(platforms)}')
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# Social Media Analytics Report - {date}")
    lines.append("")

    # KPI: Follower Growth
    lines.append("## KPI: Follower Growth")
    lines.append("")

    if followers_data and followers_data.get("platforms"):
        lines.append("| Platform | Followers | Daily Change | 7-Day Change | 30-Day Change |")
        lines.append("|----------|-----------|--------------|--------------|---------------|")

        for platform_key, platform_data in followers_data["platforms"].items():
            history = platform_data.get("history", [])
            if not history:
                continue

            latest = history[-1]
            current_val = latest.get("value", 0)
            daily_change = latest.get("change", 0)

            # Calculate period changes
            weekly_change = get_change_over_period(history, date, 7)
            monthly_change = get_change_over_period(history, date, 30)

            prev_daily = current_val - daily_change if daily_change else current_val
            prev_weekly = current_val - weekly_change if weekly_change else None
            prev_monthly = current_val - monthly_change if monthly_change else None

            lines.append(
                f"| {platform_key.title()} | {fmt_num(current_val)} | "
                f"{fmt_change(daily_change, prev_daily)} | "
                f"{fmt_change(weekly_change, prev_weekly) if weekly_change is not None else 'N/A'} | "
                f"{fmt_change(monthly_change, prev_monthly) if monthly_change is not None else 'N/A'} |"
            )

        # Total row
        total_history = followers_data.get("total", {}).get("history", [])
        if total_history:
            latest_total = total_history[-1]
            total_val = latest_total.get("total", 0)
            total_change = latest_total.get("change", 0)
            prev_total = total_val - total_change if total_change else total_val
            weekly_total = get_change_over_period(total_history, date, 7)
            monthly_total = get_change_over_period(total_history, date, 30)

            lines.append(
                f"| **Total** | **{fmt_num(total_val)}** | "
                f"**{fmt_change(total_change, prev_total)}** | "
                f"**{fmt_change(weekly_total) if weekly_total is not None else 'N/A'}** | "
                f"**{fmt_change(monthly_total) if monthly_total is not None else 'N/A'}** |"
            )

        lines.append("")

    # Engagement Summary
    if all_metrics and all_metrics.get("platforms"):
        lines.append("## Engagement Summary")
        lines.append("")
        lines.append("| Platform | Impressions | Likes | Comments | Shares | Engagement Rate |")
        lines.append("|----------|-------------|-------|----------|--------|-----------------|")

        for platform_key, platform_data in all_metrics["platforms"].items():
            history = platform_data.get("history", [])
            if not history:
                continue

            latest = history[-1]
            metrics = latest.get("metrics", {})

            impressions = metrics.get("impressions", {}).get("value", 0)
            likes = metrics.get("likes", {}).get("value", 0)
            comments = metrics.get("comments", {}).get("value", 0)
            shares = metrics.get("shares", {}).get("value", 0)

            engagement = 0
            total_engagement = likes + comments + shares
            if impressions > 0:
                engagement = (total_engagement / impressions) * 100

            lines.append(
                f"| {platform_key.title()} | {fmt_num(impressions)} | "
                f"{fmt_num(likes)} | {fmt_num(comments)} | "
                f"{fmt_num(shares)} | {engagement:.1f}% |"
            )

        lines.append("")

    # Platform Details
    if all_metrics and all_metrics.get("platforms"):
        lines.append("## Platform Details")
        lines.append("")

        for platform_key, platform_data in all_metrics["platforms"].items():
            history = platform_data.get("history", [])
            if not history:
                continue

            latest = history[-1]
            metrics = latest.get("metrics", {})

            lines.append(f"### {platform_key.title()}")
            lines.append("")

            if metrics:
                lines.append("| Metric | Value | Change |")
                lines.append("|--------|-------|--------|")
                for metric_name, metric_info in sorted(metrics.items()):
                    value = metric_info.get("value", 0)
                    pct_change = metric_info.get("percentage_change", 0)
                    sign = "+" if pct_change > 0 else ""
                    lines.append(
                        f"| {metric_name.title()} | {fmt_num(value)} | {sign}{pct_change:.1f}% |"
                    )
                lines.append("")

    # 7-Day Trends
    if followers_data and followers_data.get("platforms"):
        lines.append("## Trends")
        lines.append("")

        # Find fastest growing platform
        best_platform = None
        best_growth = 0
        for platform_key, platform_data in followers_data["platforms"].items():
            history = platform_data.get("history", [])
            if len(history) >= 2:
                weekly = get_change_over_period(history, date, 7)
                if weekly and weekly > best_growth:
                    best_growth = weekly
                    best_platform = platform_key

        if best_platform:
            lines.append(f"- **Fastest growing**: {best_platform.title()} (+{best_growth} followers this week)")

        # Find highest engagement
        if all_metrics:
            best_eng_platform = None
            best_eng_rate = 0
            for platform_key, platform_data in all_metrics.get("platforms", {}).items():
                history = platform_data.get("history", [])
                if history:
                    metrics = history[-1].get("metrics", {})
                    impressions = metrics.get("impressions", {}).get("value", 0)
                    likes = metrics.get("likes", {}).get("value", 0)
                    comments = metrics.get("comments", {}).get("value", 0)
                    shares = metrics.get("shares", {}).get("value", 0)
                    if impressions > 0:
                        rate = ((likes + comments + shares) / impressions) * 100
                        if rate > best_eng_rate:
                            best_eng_rate = rate
                            best_eng_platform = platform_key

            if best_eng_platform:
                lines.append(f"- **Highest engagement**: {best_eng_platform.title()} ({best_eng_rate:.1f}%)")

        lines.append("")

    # Post Analytics
    posts_dir = data_dir / "raw" / date / "posts"
    if posts_dir.exists():
        post_files = list(posts_dir.glob("*.json"))
        if post_files:
            lines.append("## Recent Post Performance")
            lines.append("")

            for post_file in sorted(post_files)[:10]:
                post_data = load_json(post_file)
                if not post_data:
                    continue
                post_info = post_data.get("post_info", {})
                analytics = post_data.get("analytics", [])

                content = post_info.get("content", "")[:80]
                if len(post_info.get("content", "")) > 80:
                    content += "..."

                lines.append(f"- **{post_data.get('post_id', 'unknown')}**: {content}")
                if isinstance(analytics, list):
                    metric_strs = []
                    for m in analytics[:5]:
                        label = m.get("label", "")
                        data_points = m.get("data", [])
                        if data_points:
                            val = data_points[-1].get("total", 0)
                            metric_strs.append(f"{label}: {fmt_num(val)}")
                    if metric_strs:
                        lines.append(f"  - {', '.join(metric_strs)}")

            lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Report generated at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append("*Data source: Postiz Analytics API*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate social analytics markdown report")
    parser.add_argument("--data-dir", required=True, help="Path to data/social-analytics/")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    parser.add_argument("--date", default=None, help="Report date (YYYY-MM-DD, default: today)")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    date = args.date or datetime.now().strftime("%Y-%m-%d")

    report = generate_report(data_dir, date)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
