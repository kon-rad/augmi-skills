#!/usr/bin/env python3
"""Core analysis engine for social media channel performance.

Reads scraped YouTube data (channel-info.json, shorts-detail/, videos-detail/)
and produces a comprehensive analysis.json with:
- Content categorization (auto-detect topics from titles)
- Hook pattern detection
- Engagement analysis
- Growth trajectory with era detection
- Content pattern scoring

Usage:
    python3 analyze_performance.py --data-dir OUTPUT/JakeExplains/data --output OUTPUT/JakeExplains/data/analysis.json
    python3 analyze_performance.py --data-dir OUTPUT/JakeExplains/data --config .claude/skills/social-media-analyst/config/defaults.json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime


def load_config(config_path=None):
    """Load analysis config from defaults.json."""
    default = os.path.join(os.path.dirname(__file__), "..", "config", "defaults.json")
    path = config_path or default
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"analysis": {}, "report": {}}


def load_channel_info(data_dir):
    """Load channel-info.json."""
    path = os.path.join(data_dir, "channel-info.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def load_detail_files(data_dir, content_type):
    """Load all detail JSON files for shorts or videos."""
    detail_dir = os.path.join(data_dir, f"{content_type}-detail")
    items = []
    if not os.path.isdir(detail_dir):
        return items

    for fname in os.listdir(detail_dir):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(detail_dir, fname)) as f:
            try:
                items.append(json.load(f))
            except json.JSONDecodeError:
                continue
    return items


def load_flat_sorted(data_dir, content_type):
    """Load flat-sorted.json as fallback when detail files are missing."""
    path = os.path.join(data_dir, f"{content_type}-flat-sorted.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def parse_upload_date(date_str):
    """Parse YYYYMMDD date string to datetime."""
    if not date_str or len(date_str) < 8:
        return None
    try:
        return datetime.strptime(date_str[:8], "%Y%m%d")
    except ValueError:
        return None


def detect_hook_patterns(title, config):
    """Detect hook patterns in a title. Returns list of matched pattern types."""
    title_lower = title.lower().strip()
    patterns = config.get("analysis", {}).get("hook_patterns", {})
    matched = []

    for pattern_type, keywords in patterns.items():
        for kw in keywords:
            if kw.startswith("\\"):
                # Regex pattern
                if re.search(kw, title_lower):
                    matched.append(pattern_type)
                    break
            else:
                if kw in title_lower:
                    matched.append(pattern_type)
                    break

    if not matched:
        matched.append("neutral")

    return matched


def categorize_content(title):
    """Auto-detect content category from title keywords."""
    title_lower = title.lower()

    categories = {
        "geography": ["country", "countries", "continent", "map", "border", "territory", "island", "ocean", "sea", "mountain", "river", "lake", "desert", "land"],
        "geopolitics": ["war", "military", "army", "navy", "nuclear", "sanction", "invasion", "conflict", "nato", "alliance", "treaty"],
        "science": ["space", "planet", "star", "sun", "moon", "asteroid", "comet", "galaxy", "universe", "atom", "quantum", "physics", "chemistry", "biology", "dna", "evolution", "cell"],
        "technology": ["ai", "robot", "computer", "internet", "software", "chip", "semiconductor", "electric", "battery", "solar", "energy", "ev ", "tesla"],
        "history": ["ancient", "empire", "dynasty", "century", "medieval", "civilization", "historic", "colonial", "kingdom", "pharaoh", "roman", "greek"],
        "economics": ["economy", "gdp", "trade", "market", "inflation", "debt", "currency", "dollar", "billion", "trillion", "richest", "poorest", "wealth"],
        "nature": ["animal", "species", "wildlife", "forest", "jungle", "rainforest", "coral", "ecosystem", "endangered", "shark", "whale", "lion", "bear", "insect", "rat", "bird"],
        "society": ["population", "city", "cities", "urban", "language", "culture", "religion", "food", "health", "crime", "prison", "education"],
        "infrastructure": ["road", "highway", "bridge", "tunnel", "dam", "building", "skyscraper", "airport", "train", "railway", "canal", "pipeline"],
    }

    matched = []
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in title_lower:
                matched.append(cat)
                break

    return matched[0] if matched else "other"


def compute_view_distribution(items, config):
    """Compute view count distribution across buckets."""
    buckets_cfg = config.get("analysis", {}).get("view_buckets", [
        {"label": "1M+", "min": 1000000},
        {"label": "100K-1M", "min": 100000, "max": 1000000},
        {"label": "10K-100K", "min": 10000, "max": 100000},
        {"label": "1K-10K", "min": 1000, "max": 10000},
        {"label": "<1K", "max": 1000},
    ])

    distribution = {b["label"]: 0 for b in buckets_cfg}

    for item in items:
        views = item.get("view_count", 0) or 0
        for bucket in buckets_cfg:
            b_min = bucket.get("min", 0)
            b_max = bucket.get("max", float("inf"))
            if b_min <= views < b_max:
                distribution[bucket["label"]] += 1
                break
        else:
            # Views >= max of highest bucket
            if views >= buckets_cfg[0].get("min", 0):
                distribution[buckets_cfg[0]["label"]] += 1

    return distribution


def detect_eras(items):
    """Detect content eras based on upload gaps and frequency changes."""
    dated = [(item, parse_upload_date(item.get("upload_date", ""))) for item in items]
    dated = [(item, dt) for item, dt in dated if dt is not None]
    dated.sort(key=lambda x: x[1])

    if len(dated) < 3:
        return []

    eras = []
    current_era_start = dated[0][1]
    current_era_items = [dated[0][0]]

    for i in range(1, len(dated)):
        _, prev_dt = dated[i - 1]
        item, curr_dt = dated[i]
        gap_days = (curr_dt - prev_dt).days

        # New era if gap > 90 days
        if gap_days > 90:
            eras.append({
                "start": current_era_start.strftime("%Y-%m-%d"),
                "end": prev_dt.strftime("%Y-%m-%d"),
                "count": len(current_era_items),
                "total_views": sum(it.get("view_count", 0) or 0 for it in current_era_items),
                "avg_views": int(sum(it.get("view_count", 0) or 0 for it in current_era_items) / max(len(current_era_items), 1)),
            })
            current_era_start = curr_dt
            current_era_items = [item]
        else:
            current_era_items.append(item)

    # Final era
    if current_era_items:
        eras.append({
            "start": current_era_start.strftime("%Y-%m-%d"),
            "end": dated[-1][1].strftime("%Y-%m-%d"),
            "count": len(current_era_items),
            "total_views": sum(it.get("view_count", 0) or 0 for it in current_era_items),
            "avg_views": int(sum(it.get("view_count", 0) or 0 for it in current_era_items) / max(len(current_era_items), 1)),
        })

    return eras


def compute_monthly_views(items):
    """Aggregate views by month for growth timeline."""
    monthly = defaultdict(lambda: {"views": 0, "count": 0, "likes": 0, "comments": 0})

    for item in items:
        dt = parse_upload_date(item.get("upload_date", ""))
        if not dt:
            continue
        key = dt.strftime("%Y-%m")
        monthly[key]["views"] += item.get("view_count", 0) or 0
        monthly[key]["count"] += 1
        monthly[key]["likes"] += item.get("like_count", 0) or 0
        monthly[key]["comments"] += item.get("comment_count", 0) or 0

    return dict(sorted(monthly.items()))


def analyze_hooks(items, config):
    """Analyze hook pattern performance."""
    hook_stats = defaultdict(lambda: {"count": 0, "total_views": 0, "total_likes": 0, "titles": []})

    for item in items:
        title = item.get("title", "")
        views = item.get("view_count", 0) or 0
        likes = item.get("like_count", 0) or 0
        hooks = detect_hook_patterns(title, config)

        for hook in hooks:
            hook_stats[hook]["count"] += 1
            hook_stats[hook]["total_views"] += views
            hook_stats[hook]["total_likes"] += likes
            if len(hook_stats[hook]["titles"]) < 3:
                hook_stats[hook]["titles"].append(title)

    result = {}
    for hook, stats in hook_stats.items():
        count = stats["count"]
        result[hook] = {
            "count": count,
            "total_views": stats["total_views"],
            "avg_views": int(stats["total_views"] / max(count, 1)),
            "avg_likes": int(stats["total_likes"] / max(count, 1)),
            "example_titles": stats["titles"],
        }

    return dict(sorted(result.items(), key=lambda x: x[1]["avg_views"], reverse=True))


def analyze_categories(items):
    """Analyze performance by content category."""
    cat_stats = defaultdict(lambda: {"count": 0, "total_views": 0, "total_likes": 0, "total_comments": 0})

    for item in items:
        title = item.get("title", "")
        category = categorize_content(title)
        cat_stats[category]["count"] += 1
        cat_stats[category]["total_views"] += item.get("view_count", 0) or 0
        cat_stats[category]["total_likes"] += item.get("like_count", 0) or 0
        cat_stats[category]["total_comments"] += item.get("comment_count", 0) or 0

    result = {}
    for cat, stats in cat_stats.items():
        count = stats["count"]
        result[cat] = {
            "count": count,
            "total_views": stats["total_views"],
            "avg_views": int(stats["total_views"] / max(count, 1)),
            "total_likes": stats["total_likes"],
            "avg_likes": int(stats["total_likes"] / max(count, 1)),
            "total_comments": stats["total_comments"],
            "avg_comments": int(stats["total_comments"] / max(count, 1)),
            "engagement_rate": round(
                (stats["total_likes"] + stats["total_comments"]) / max(stats["total_views"], 1) * 100, 2
            ),
        }

    return dict(sorted(result.items(), key=lambda x: x[1]["avg_views"], reverse=True))


def compute_engagement_scatter(items):
    """Compute engagement vs views data for scatter plot.

    Returns list of {id, title, views, engagement_rate, quadrant}.
    Quadrants: overperformer, balanced_hit, underrated, clickbait.
    """
    if not items:
        return []

    all_views = [it.get("view_count", 0) or 0 for it in items]
    median_views = sorted(all_views)[len(all_views) // 2] if all_views else 0

    all_rates = []
    for item in items:
        views = item.get("view_count", 0) or 0
        likes = item.get("like_count", 0) or 0
        comments = item.get("comment_count", 0) or 0
        rate = (likes + comments) / max(views, 1) * 100
        all_rates.append(rate)
    median_rate = sorted(all_rates)[len(all_rates) // 2] if all_rates else 0

    scatter = []
    for item in items:
        views = item.get("view_count", 0) or 0
        likes = item.get("like_count", 0) or 0
        comments = item.get("comment_count", 0) or 0
        rate = round((likes + comments) / max(views, 1) * 100, 3)

        if views >= median_views and rate >= median_rate:
            quadrant = "balanced_hit"
        elif views < median_views and rate >= median_rate:
            quadrant = "underrated"
        elif views >= median_views and rate < median_rate:
            quadrant = "clickbait"
        else:
            quadrant = "overperformer"

        scatter.append({
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate": rate,
            "quadrant": quadrant,
        })

    return scatter


def compute_duration_analysis(items):
    """Analyze performance by content duration ranges."""
    buckets = {
        "0-15s": {"min": 0, "max": 16},
        "16-30s": {"min": 16, "max": 31},
        "31-60s": {"min": 31, "max": 61},
        "1-3min": {"min": 61, "max": 181},
        "3-10min": {"min": 181, "max": 601},
        "10min+": {"min": 601, "max": float("inf")},
    }

    stats = {label: {"count": 0, "total_views": 0, "total_likes": 0} for label in buckets}

    for item in items:
        dur = item.get("duration", 0) or 0
        views = item.get("view_count", 0) or 0
        likes = item.get("like_count", 0) or 0

        for label, bounds in buckets.items():
            if bounds["min"] <= dur < bounds["max"]:
                stats[label]["count"] += 1
                stats[label]["total_views"] += views
                stats[label]["total_likes"] += likes
                break

    result = {}
    for label, s in stats.items():
        if s["count"] > 0:
            result[label] = {
                "count": s["count"],
                "total_views": s["total_views"],
                "avg_views": int(s["total_views"] / s["count"]),
                "avg_likes": int(s["total_likes"] / s["count"]),
            }

    return result


def extract_top_topics(categories, hook_analysis, limit=5):
    """Extract top topics for trend research."""
    topics = []

    # Top categories by avg views
    sorted_cats = sorted(categories.items(), key=lambda x: x[1]["avg_views"], reverse=True)
    for cat, _ in sorted_cats[:limit]:
        if cat != "other":
            topics.append(cat)

    return topics[:limit]


def main():
    parser = argparse.ArgumentParser(description="Analyze YouTube channel performance")
    parser.add_argument("--data-dir", required=True, help="Directory with scraped data")
    parser.add_argument("--output", help="Output path for analysis.json (default: <data-dir>/analysis.json)")
    parser.add_argument("--config", help="Path to config/defaults.json")
    args = parser.parse_args()

    config = load_config(args.config)
    data_dir = args.data_dir
    output_path = args.output or os.path.join(data_dir, "analysis.json")

    # Load data
    channel_info = load_channel_info(data_dir)
    shorts = load_detail_files(data_dir, "shorts")
    videos = load_detail_files(data_dir, "videos")

    # Fallback to flat-sorted if no detail files
    if not shorts:
        shorts = load_flat_sorted(data_dir, "shorts")
        print(f"Using flat-sorted fallback for shorts: {len(shorts)} items", file=sys.stderr)
    if not videos:
        videos = load_flat_sorted(data_dir, "videos")
        print(f"Using flat-sorted fallback for videos: {len(videos)} items", file=sys.stderr)

    all_content = shorts + videos
    print(f"Loaded {len(shorts)} shorts, {len(videos)} videos ({len(all_content)} total)", file=sys.stderr)

    # Overview stats
    total_shorts_views = sum(s.get("view_count", 0) or 0 for s in shorts)
    total_video_views = sum(v.get("view_count", 0) or 0 for v in videos)
    total_views = total_shorts_views + total_video_views
    total_likes = sum(it.get("like_count", 0) or 0 for it in all_content)
    total_comments = sum(it.get("comment_count", 0) or 0 for it in all_content)

    overview = {
        "total_subscribers": channel_info.get("channel_follower_count", 0),
        "total_videos": len(videos),
        "total_shorts": len(shorts),
        "total_content": len(all_content),
        "total_video_views": total_video_views,
        "total_shorts_views": total_shorts_views,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "avg_video_views": int(total_video_views / max(len(videos), 1)),
        "avg_shorts_views": int(total_shorts_views / max(len(shorts), 1)),
        "avg_video_likes": int(sum(v.get("like_count", 0) or 0 for v in videos) / max(len(videos), 1)),
        "avg_video_comments": int(sum(v.get("comment_count", 0) or 0 for v in videos) / max(len(videos), 1)),
        "shorts_view_share": round(total_shorts_views / max(total_views, 1) * 100, 1),
    }

    # Analyses
    print("Analyzing hook patterns...", file=sys.stderr)
    hook_analysis = analyze_hooks(all_content, config)

    print("Analyzing content categories...", file=sys.stderr)
    categories = analyze_categories(all_content)

    print("Computing view distribution...", file=sys.stderr)
    shorts_distribution = compute_view_distribution(shorts, config)
    videos_distribution = compute_view_distribution(videos, config)

    print("Analyzing engagement scatter...", file=sys.stderr)
    shorts_scatter = compute_engagement_scatter(shorts)
    videos_scatter = compute_engagement_scatter(videos)

    print("Analyzing duration performance...", file=sys.stderr)
    duration_analysis = compute_duration_analysis(all_content)

    print("Computing monthly views...", file=sys.stderr)
    monthly_views = compute_monthly_views(all_content)

    print("Detecting content eras...", file=sys.stderr)
    eras = detect_eras(all_content)

    # Top content
    top_limit = config.get("analysis", {}).get("top_content_limit", 20)
    top_shorts = sorted(shorts, key=lambda x: x.get("view_count", 0) or 0, reverse=True)[:top_limit]
    top_videos = sorted(videos, key=lambda x: x.get("view_count", 0) or 0, reverse=True)[:top_limit]
    top_all = sorted(all_content, key=lambda x: x.get("view_count", 0) or 0, reverse=True)[:top_limit]

    # Extract topics for trend research
    top_topics = extract_top_topics(categories, hook_analysis)

    # Build analysis result
    analysis = {
        "channel": {
            "name": channel_info.get("channel", "Unknown"),
            "handle": channel_info.get("uploader_id", ""),
            "url": channel_info.get("uploader_url", ""),
            "channel_id": channel_info.get("channel_id", ""),
            "subscribers": channel_info.get("channel_follower_count", 0),
        },
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "overview": overview,
        "hook_patterns": hook_analysis,
        "categories": categories,
        "duration_analysis": duration_analysis,
        "view_distribution": {
            "shorts": shorts_distribution,
            "videos": videos_distribution,
        },
        "engagement_scatter": {
            "shorts": shorts_scatter[:50],  # Limit scatter data for report size
            "videos": videos_scatter,
        },
        "monthly_views": monthly_views,
        "growth_eras": eras,
        "top_shorts": [
            {"id": s.get("id"), "title": s.get("title"), "views": s.get("view_count", 0),
             "likes": s.get("like_count", 0), "comments": s.get("comment_count", 0)}
            for s in top_shorts
        ],
        "top_videos": [
            {"id": v.get("id"), "title": v.get("title"), "views": v.get("view_count", 0),
             "likes": v.get("like_count", 0), "comments": v.get("comment_count", 0),
             "duration": v.get("duration", 0)}
            for v in top_videos
        ],
        "top_content": [
            {"id": c.get("id"), "title": c.get("title"), "views": c.get("view_count", 0),
             "type": "short" if c.get("duration", 0) and c["duration"] <= 60 else "video"}
            for c in top_all
        ],
        "top_topics": top_topics,
    }

    # Write output
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\nAnalysis complete! Written to: {output_path}", file=sys.stderr)
    print(f"  Overview: {overview['total_content']} items, {overview['total_views']:,} total views", file=sys.stderr)
    print(f"  Categories: {len(categories)}", file=sys.stderr)
    print(f"  Hook patterns: {len(hook_analysis)}", file=sys.stderr)
    print(f"  Growth eras: {len(eras)}", file=sys.stderr)
    print(f"  Top topics for trends: {', '.join(top_topics)}", file=sys.stderr)

    # Output JSON path for downstream
    print(json.dumps({"analysis_path": output_path, "top_topics": top_topics}))


if __name__ == "__main__":
    main()
