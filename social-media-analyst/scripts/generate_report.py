#!/usr/bin/env python3
"""Generate a comprehensive markdown report from analysis.json.

Usage:
    python3 generate_report.py --analysis OUTPUT/JakeExplains/data/analysis.json --output OUTPUT/JakeExplains/reports/report.md
    python3 generate_report.py --analysis analysis.json  # Defaults to <dir>/report.md
"""

import argparse
import json
import os
import sys
from datetime import datetime


def fmt(n):
    """Format large numbers for readability."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:,}"


def generate_report(data):
    """Generate markdown report from analysis data."""
    channel = data.get("channel", {})
    overview = data.get("overview", {})
    hooks = data.get("hook_patterns", {})
    categories = data.get("categories", {})
    duration = data.get("duration_analysis", {})
    view_dist = data.get("view_distribution", {})
    monthly = data.get("monthly_views", {})
    eras = data.get("growth_eras", [])
    top_shorts = data.get("top_shorts", [])
    top_videos = data.get("top_videos", [])
    top_content = data.get("top_content", [])
    scatter = data.get("engagement_scatter", {})

    lines = []

    # Header
    lines.append(f"# {channel.get('name', 'Channel')} — Performance Analysis")
    lines.append("")
    lines.append(f"**Report Date:** {data.get('report_date', datetime.now().strftime('%Y-%m-%d'))}")
    lines.append(f"**Channel:** [{channel.get('handle', '')}]({channel.get('url', '')})")
    lines.append(f"**Subscribers:** {fmt(channel.get('subscribers', 0))}")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Content | {fmt(overview.get('total_content', 0))} |")
    lines.append(f"| Total Views | {fmt(overview.get('total_views', 0))} |")
    lines.append(f"| Total Likes | {fmt(overview.get('total_likes', 0))} |")
    lines.append(f"| Total Comments | {fmt(overview.get('total_comments', 0))} |")
    lines.append(f"| Videos | {overview.get('total_videos', 0)} (avg {fmt(overview.get('avg_video_views', 0))} views) |")
    lines.append(f"| Shorts | {overview.get('total_shorts', 0)} (avg {fmt(overview.get('avg_shorts_views', 0))} views) |")
    lines.append(f"| Shorts View Share | {overview.get('shorts_view_share', 0)}% |")
    lines.append("")

    # Top Content
    lines.append("## Top Performing Content")
    lines.append("")
    if top_content:
        lines.append("| # | Title | Type | Views |")
        lines.append("|---|-------|------|-------|")
        for i, item in enumerate(top_content[:20]):
            title = item.get("title", "")[:60]
            views = fmt(item.get("views", 0))
            ctype = item.get("type", "unknown")
            lines.append(f"| {i+1} | {title} | {ctype} | {views} |")
        lines.append("")

    # Hook Pattern Analysis
    lines.append("## Hook Pattern Performance")
    lines.append("")
    lines.append("Which title hooks drive the most views?")
    lines.append("")
    if hooks:
        lines.append("| Pattern | Count | Avg Views | Avg Likes |")
        lines.append("|---------|-------|-----------|-----------|")
        for pattern, stats in hooks.items():
            lines.append(f"| {pattern.capitalize()} | {stats['count']} | {fmt(stats['avg_views'])} | {fmt(stats['avg_likes'])} |")
        lines.append("")

        # Best performing hook
        best_hook = max(hooks.items(), key=lambda x: x[1]["avg_views"])
        lines.append(f"**Best performing hook:** {best_hook[0].capitalize()} ({fmt(best_hook[1]['avg_views'])} avg views)")
        lines.append("")
        if best_hook[1].get("example_titles"):
            lines.append("Example titles:")
            for t in best_hook[1]["example_titles"][:3]:
                lines.append(f"- {t}")
            lines.append("")

    # Category Analysis
    lines.append("## Content Category Performance")
    lines.append("")
    if categories:
        lines.append("| Category | Count | Avg Views | Engagement Rate |")
        lines.append("|----------|-------|-----------|-----------------|")
        for cat, stats in categories.items():
            lines.append(f"| {cat.capitalize()} | {stats['count']} | {fmt(stats['avg_views'])} | {stats['engagement_rate']}% |")
        lines.append("")

    # Duration Analysis
    if duration:
        lines.append("## Duration Performance")
        lines.append("")
        lines.append("| Duration | Count | Avg Views | Avg Likes |")
        lines.append("|----------|-------|-----------|-----------|")
        for dur_range, stats in duration.items():
            lines.append(f"| {dur_range} | {stats['count']} | {fmt(stats['avg_views'])} | {fmt(stats['avg_likes'])} |")
        lines.append("")

    # View Distribution
    lines.append("## View Distribution")
    lines.append("")
    shorts_dist = view_dist.get("shorts", {})
    videos_dist = view_dist.get("videos", {})
    if shorts_dist:
        lines.append("**Shorts:**")
        for bucket, count in shorts_dist.items():
            lines.append(f"- {bucket}: {count} shorts")
        lines.append("")
    if videos_dist:
        lines.append("**Videos:**")
        for bucket, count in videos_dist.items():
            if count > 0:
                lines.append(f"- {bucket}: {count} videos")
        lines.append("")

    # Growth Eras
    if eras:
        lines.append("## Growth Eras")
        lines.append("")
        lines.append("| Era | Period | Content | Total Views | Avg Views |")
        lines.append("|-----|--------|---------|-------------|-----------|")
        for i, era in enumerate(eras):
            lines.append(f"| {i+1} | {era['start']} to {era['end']} | {era['count']} | {fmt(era['total_views'])} | {fmt(era['avg_views'])} |")
        lines.append("")

    # Engagement Analysis
    lines.append("## Engagement Analysis")
    lines.append("")
    shorts_scatter = scatter.get("shorts", [])
    videos_scatter = scatter.get("videos", [])

    quadrant_counts = {"balanced_hit": 0, "underrated": 0, "clickbait": 0, "overperformer": 0}
    for item in shorts_scatter + videos_scatter:
        q = item.get("quadrant", "")
        if q in quadrant_counts:
            quadrant_counts[q] += 1

    lines.append("**Content Quadrants:**")
    lines.append(f"- Balanced Hits (high views + high engagement): {quadrant_counts['balanced_hit']}")
    lines.append(f"- Underrated (low views + high engagement): {quadrant_counts['underrated']}")
    lines.append(f"- Clickbait (high views + low engagement): {quadrant_counts['clickbait']}")
    lines.append(f"- Overperformers: {quadrant_counts['overperformer']}")
    lines.append("")

    # Most underrated content
    underrated = [item for item in shorts_scatter + videos_scatter if item.get("quadrant") == "underrated"]
    underrated.sort(key=lambda x: x.get("engagement_rate", 0), reverse=True)
    if underrated[:5]:
        lines.append("**Most Underrated Content** (high engagement, deserves more views):")
        for item in underrated[:5]:
            lines.append(f"- {item['title'][:50]} — {item['engagement_rate']}% engagement, {fmt(item['views'])} views")
        lines.append("")

    # Monthly Trend
    if monthly:
        lines.append("## Monthly Upload & View Trend")
        lines.append("")
        months = list(monthly.keys())
        if len(months) > 6:
            lines.append(f"Active months: {len(months)} (from {months[0]} to {months[-1]})")
            recent = {k: monthly[k] for k in months[-6:]}
        else:
            recent = monthly

        lines.append("")
        lines.append("| Month | Uploads | Views | Likes |")
        lines.append("|-------|---------|-------|-------|")
        for month, stats in recent.items():
            lines.append(f"| {month} | {stats['count']} | {fmt(stats['views'])} | {fmt(stats['likes'])} |")
        lines.append("")

    # Top Videos Detail
    if top_videos:
        lines.append("## Top Videos (Long-form)")
        lines.append("")
        lines.append("| # | Title | Views | Likes | Comments | Duration |")
        lines.append("|---|-------|-------|-------|----------|----------|")
        for i, v in enumerate(top_videos[:10]):
            dur = v.get("duration", 0)
            dur_str = f"{dur // 60}:{dur % 60:02d}" if dur else "N/A"
            lines.append(f"| {i+1} | {v['title'][:50]} | {fmt(v.get('views', 0))} | {fmt(v.get('likes', 0))} | {v.get('comments', 0)} | {dur_str} |")
        lines.append("")

    # Top Shorts Detail
    if top_shorts:
        lines.append("## Top Shorts")
        lines.append("")
        lines.append("| # | Title | Views | Likes |")
        lines.append("|---|-------|-------|-------|")
        for i, s in enumerate(top_shorts[:10]):
            lines.append(f"| {i+1} | {s['title'][:50]} | {fmt(s.get('views', 0))} | {fmt(s.get('likes', 0))} |")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*Generated by Social Media Analyst — {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate markdown report from analysis.json")
    parser.add_argument("--analysis", required=True, help="Path to analysis.json")
    parser.add_argument("--output", help="Output markdown file path")
    args = parser.parse_args()

    if not os.path.exists(args.analysis):
        print(f"Error: {args.analysis} not found", file=sys.stderr)
        sys.exit(1)

    with open(args.analysis) as f:
        data = json.load(f)

    report = generate_report(data)

    output_path = args.output
    if not output_path:
        output_dir = os.path.dirname(args.analysis)
        channel_name = data.get("channel", {}).get("name", "channel")
        slug = "".join(c if c.isalnum() or c == "-" else "-" for c in channel_name.lower()).strip("-")
        output_path = os.path.join(output_dir, f"{slug}-report.md")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report written to: {output_path}", file=sys.stderr)
    print(json.dumps({"report_path": output_path}))


if __name__ == "__main__":
    main()
