#!/usr/bin/env python3
"""
Find trending topics using Google Trends for social media content ideation.

Uses Google Trends RSS feed for daily trends and session-based requests
for topic exploration. No third-party dependencies beyond requests.

Usage:
    # General trending searches
    python find_trends.py

    # Trends for a specific topic
    python find_trends.py --topic "AI agents" --related

Requirements:
    pip install requests
"""

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests not installed.")
    print("Install it with: pip3 install requests --break-system-packages")
    sys.exit(1)


# Endpoints
RSS_URL = "https://trends.google.com/trending/rss"
EXPLORE_URL = "https://trends.google.com/trends/api/explore"
INTEREST_URL = "https://trends.google.com/trends/api/widgetdata/multiline"
RELATED_URL = "https://trends.google.com/trends/api/widgetdata/relatedsearches"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Country code mapping
GEO_MAP = {
    "united_states": "US",
    "united_kingdom": "GB",
    "canada": "CA",
    "australia": "AU",
    "india": "IN",
    "germany": "DE",
    "france": "FR",
    "brazil": "BR",
    "japan": "JP",
    "mexico": "MX",
    "spain": "ES",
    "italy": "IT",
    "south_korea": "KR",
    "netherlands": "NL",
    "sweden": "SE",
}

# RSS namespace
HT_NS = "https://trends.google.com/trending/rss"


def resolve_geo(geo_input):
    """Resolve country name or code to a 2-letter code."""
    geo_lower = geo_input.lower().replace(" ", "_")
    if geo_lower in GEO_MAP:
        return GEO_MAP[geo_lower]
    if len(geo_input) == 2:
        return geo_input.upper()
    return "US"


def geo_display_name(code):
    """Get a display name for a geo code."""
    for name, c in GEO_MAP.items():
        if c == code:
            return name.replace("_", " ").title()
    return code


def parse_trends_response(text):
    """Strip Google Trends XSSI prefix and parse JSON."""
    # Google prepends ")]}'" or ")]}'," to prevent XSSI
    text = text.lstrip()
    for prefix in [")]}'", ")]}'"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    text = text.lstrip().lstrip(",").lstrip()
    return json.loads(text)


def get_daily_trends_rss(geo="US", limit=20):
    """Fetch daily trending searches via the public RSS feed."""
    try:
        resp = requests.get(RSS_URL, params={"geo": geo}, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        results = []
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            traffic = item.findtext(f"{{{HT_NS}}}approx_traffic", "").strip()

            # Get first news item for context
            news_item = item.find(f"{{{HT_NS}}}news_item")
            context = ""
            source = ""
            if news_item is not None:
                context = news_item.findtext(f"{{{HT_NS}}}news_item_title", "").strip()
                source = news_item.findtext(f"{{{HT_NS}}}news_item_source", "").strip()

            if title:
                results.append({
                    "topic": title,
                    "traffic": traffic,
                    "context": context,
                    "source": source,
                })
            if len(results) >= limit:
                break

        return results
    except Exception as e:
        print(f"Warning: Could not fetch daily trends: {e}")
        return []


def create_session():
    """Create a requests session with Google Trends cookies."""
    session = requests.Session()
    session.headers.update(HEADERS)
    # Visit the trends page to get cookies (needed for API access)
    try:
        session.get("https://trends.google.com/trends/", timeout=15)
    except Exception:
        pass
    return session


def get_explore_widgets(session, keyword, geo="US", timeframe="now 7-d"):
    """Get explore widget tokens for a keyword."""
    params = {
        "hl": "en-US",
        "tz": "-360",
        "req": json.dumps({
            "comparisonItem": [{
                "keyword": keyword,
                "geo": geo,
                "time": timeframe,
            }],
            "category": 0,
            "property": "",
        }),
    }
    try:
        resp = session.get(EXPLORE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = parse_trends_response(resp.text)

        widgets = {}
        for widget in data.get("widgets", []):
            wid = widget.get("id", "")
            if "TIMESERIES" in wid:
                widgets["interest"] = widget
            elif "RELATED_TOPICS" in wid:
                widgets["related_topics"] = widget
            elif "RELATED_QUERIES" in wid:
                widgets["related_queries"] = widget
        return widgets
    except Exception as e:
        print(f"Warning: Could not get explore widgets: {e}")
        return {}


def get_interest_over_time(session, widget):
    """Fetch interest over time data from a widget token."""
    if not widget:
        return None
    try:
        params = {
            "hl": "en-US",
            "tz": "-360",
            "req": json.dumps(widget["request"]),
            "token": widget["token"],
        }
        resp = session.get(INTEREST_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = parse_trends_response(resp.text)

        timeline = data.get("default", {}).get("timelineData", [])
        if not timeline:
            return None

        values = [int(p["value"][0]) for p in timeline if p.get("value")]
        if not values:
            return None

        recent = values[-7:] if len(values) >= 7 else values
        avg = sum(recent) / len(recent)
        direction = "rising" if recent[-1] > recent[0] else "falling"
        return {
            "average": round(avg, 1),
            "direction": direction,
            "peak": max(recent),
            "current": recent[-1],
        }
    except Exception as e:
        print(f"Warning: Could not fetch interest over time: {e}")
        return None


def get_related_data(session, widget, data_type="topics"):
    """Fetch related topics or queries from a widget token."""
    if not widget:
        return [], []
    try:
        params = {
            "hl": "en-US",
            "tz": "-360",
            "req": json.dumps(widget["request"]),
            "token": widget["token"],
        }
        resp = session.get(RELATED_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = parse_trends_response(resp.text)

        rising = []
        top = []

        ranked_lists = data.get("default", {}).get("rankedList", [])
        for i, ranked_list in enumerate(ranked_lists):
            items = ranked_list.get("rankedKeyword", [])
            for item in items:
                if data_type == "topics":
                    topic_obj = item.get("topic", {})
                    title = topic_obj.get("title", "unknown")
                else:
                    title = item.get("query", "unknown")

                formatted = item.get("formattedValue", "")
                value = item.get("value", 0)

                entry = {"title": title, "value": formatted or str(value)}

                # First ranked list = top, second = rising
                if i == 0:
                    top.append(entry)
                else:
                    rising.append(entry)

        return rising[:15], top[:15]
    except Exception as e:
        print(f"Warning: Could not fetch related {data_type}: {e}")
        return [], []


def build_report(
    daily_trends,
    topic=None,
    interest=None,
    related_topics_rising=None,
    related_topics_top=None,
    related_queries_rising=None,
    related_queries_top=None,
    geo="US",
):
    """Build a markdown report from collected data."""
    today = datetime.now().strftime("%Y-%m-%d")
    display = geo_display_name(geo)
    lines = []

    lines.append(f"# Trending Topics Report — {today}")
    lines.append("")

    if topic:
        lines.append(f"> Research focus: **{topic}**")
        lines.append("")

    # Interest summary
    if interest:
        lines.append(f'## Interest Summary for "{topic}"')
        lines.append("")
        lines.append(f"- **Current interest**: {interest['current']}/100")
        lines.append(f"- **7-day average**: {interest['average']}/100")
        lines.append(f"- **7-day peak**: {interest['peak']}/100")
        lines.append(f"- **Trend direction**: {interest['direction']}")
        lines.append("")

    # Daily trending searches
    if daily_trends:
        lines.append(f"## Daily Trending Searches ({display})")
        lines.append("")
        lines.append("| # | Topic | Traffic | Context |")
        lines.append("|---|-------|---------|---------|")
        for i, item in enumerate(daily_trends, 1):
            t = item["topic"]
            traffic = item.get("traffic", "")
            context = item.get("context", "").replace("|", "\\|")
            source = item.get("source", "")
            ctx = f"{context} ({source})" if source and context else context
            lines.append(f"| {i} | {t} | {traffic} | {ctx} |")
        lines.append("")

    # Related topics
    if related_topics_rising or related_topics_top:
        lines.append(f'## Related Topics for "{topic}"')
        lines.append("")

        if related_topics_rising:
            lines.append("### Rising Topics")
            lines.append("")
            lines.append("| Topic | Growth |")
            lines.append("|-------|--------|")
            for item in related_topics_rising:
                lines.append(f"| {item['title']} | {item['value']} |")
            lines.append("")

        if related_topics_top:
            lines.append("### Top Topics")
            lines.append("")
            lines.append("| Topic | Score |")
            lines.append("|-------|-------|")
            for item in related_topics_top:
                lines.append(f"| {item['title']} | {item['value']} |")
            lines.append("")

    # Related queries
    if related_queries_rising or related_queries_top:
        lines.append(f'## Related Queries for "{topic}"')
        lines.append("")

        if related_queries_rising:
            lines.append("### Rising Queries")
            lines.append("")
            lines.append("| Query | Growth |")
            lines.append("|-------|--------|")
            for item in related_queries_rising:
                lines.append(f"| {item['title']} | {item['value']} |")
            lines.append("")

        if related_queries_top:
            lines.append("### Top Queries")
            lines.append("")
            lines.append("| Query | Score |")
            lines.append("|-------|-------|")
            for item in related_queries_top:
                lines.append(f"| {item['title']} | {item['value']} |")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find trending topics via Google Trends")
    parser.add_argument("--topic", type=str, default=None, help="Keyword/niche to research")
    parser.add_argument("--geo", type=str, default="united_states", help="Country for trends")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--limit", type=int, default=20, help="Max trending items")
    parser.add_argument(
        "--related", action="store_true", help="Include related topics/queries (requires --topic)"
    )
    args = parser.parse_args()

    geo = resolve_geo(args.geo)

    # Resolve output path
    if args.output:
        output_path = Path(args.output)
    else:
        today = datetime.now().strftime("%Y%m%d")
        output_dir = Path("OUTPUT/trends")
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = f"-{args.topic.lower().replace(' ', '-')}" if args.topic else ""
        output_path = output_dir / f"{today}-trends{suffix}.md"

    print(f"Fetching trends (geo: {geo})...")

    # Daily trending searches via RSS (no auth needed)
    print("  -> Fetching daily trending searches (RSS)...")
    daily_trends = get_daily_trends_rss(geo=geo, limit=args.limit)
    print(f"     Found {len(daily_trends)} trending topics")

    # Topic-specific data via explore API (needs session cookies)
    interest = None
    related_topics_rising = []
    related_topics_top = []
    related_queries_rising = []
    related_queries_top = []

    if args.topic:
        print("  -> Creating session for topic exploration...")
        session = create_session()
        time.sleep(1)

        print(f'  -> Fetching explore data for "{args.topic}"...')
        widgets = get_explore_widgets(session, args.topic, geo=geo)

        if "interest" in widgets:
            print(f'  -> Fetching interest over time...')
            interest = get_interest_over_time(session, widgets["interest"])
            time.sleep(1)

        if args.related:
            if "related_topics" in widgets:
                print(f'  -> Fetching related topics...')
                related_topics_rising, related_topics_top = get_related_data(
                    session, widgets["related_topics"], "topics"
                )
                time.sleep(1)

            if "related_queries" in widgets:
                print(f'  -> Fetching related queries...')
                related_queries_rising, related_queries_top = get_related_data(
                    session, widgets["related_queries"], "queries"
                )

    # Build report
    report = build_report(
        daily_trends=daily_trends,
        topic=args.topic,
        interest=interest,
        related_topics_rising=related_topics_rising,
        related_topics_top=related_topics_top,
        related_queries_rising=related_queries_rising,
        related_queries_top=related_queries_top,
        geo=geo,
    )

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    print(f"\nTrends report saved to: {output_path}")

    # Also print to stdout
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
