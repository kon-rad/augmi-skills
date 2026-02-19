#!/usr/bin/env python3
"""
Social Analytics Collector — Pulls metrics from Postiz for all enabled platforms.

Usage:
    python3 collect.py --config <path-to-integrations.json> --output-dir <path>
    python3 collect.py --config config/integrations.json --output-dir ../../data/social-analytics

On first run (no existing data), pulls maximum historical data.
On subsequent runs, pulls default_days lookback.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def extract_json(text: str) -> str:
    """Extract JSON from CLI output that may have emoji/text headers."""
    lines = text.split('\n')
    # Find the first line that starts with [ or {
    json_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('[') or stripped.startswith('{'):
            json_start = i
            break
    if json_start == -1:
        return text.strip()
    return '\n'.join(lines[json_start:]).strip()


def run_postiz(args: list[str]) -> dict | list | None:
    """Run a postiz CLI command and return parsed JSON output."""
    cmd = ["postiz"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"  Warning: postiz {' '.join(args)} failed: {result.stderr.strip()}")
            return None
        output = result.stdout.strip()
        if not output:
            return None
        # Strip non-JSON header lines (postiz outputs emoji headers like "📊 Analytics for...")
        json_text = extract_json(output)
        if not json_text:
            return None
        return json.loads(json_text)
    except subprocess.TimeoutExpired:
        print(f"  Warning: postiz {' '.join(args)} timed out")
        return None
    except json.JSONDecodeError:
        print(f"  Warning: Could not parse JSON from postiz {' '.join(args)}")
        print(f"  Raw output: {result.stdout[:300]}")
        return None


def load_config(config_path: str) -> dict:
    """Load integrations config."""
    with open(config_path, "r") as f:
        return json.load(f)


def is_first_run(output_dir: Path) -> bool:
    """Check if this is the first run by looking for existing raw data."""
    raw_dir = output_dir / "raw"
    if not raw_dir.exists():
        return True
    return len(list(raw_dir.iterdir())) == 0


def collect_platform_analytics(platform_key: str, platform_config: dict, days: int, date_dir: Path) -> dict | None:
    """Collect analytics for a single platform."""
    integration_id = platform_config["id"]
    name = platform_config["name"]

    print(f"  Collecting {name} analytics ({days} days)...")
    data = run_postiz(["analytics:platform", integration_id, "-d", str(days)])

    if data is None:
        print(f"  Skipped {name} — no data returned")
        return None

    # Check for missing/error responses
    if isinstance(data, dict) and data.get("missing"):
        print(f"  Skipped {name} — analytics not available (API tier limitation?)")
        return None

    # Check for empty arrays (platform has no analytics data)
    if isinstance(data, list) and len(data) == 0:
        print(f"  Skipped {name} — empty analytics (no data available)")
        return None

    # Save raw response
    raw_file = date_dir / f"{platform_key}.json"
    with open(raw_file, "w") as f:
        json.dump({
            "platform": platform_key,
            "name": name,
            "integration_id": integration_id,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "days_lookback": days,
            "data": data
        }, f, indent=2)

    print(f"  Saved {name} → {raw_file}")
    return data


def collect_post_analytics(days: int, date_dir: Path) -> list:
    """Collect analytics for recent posts."""
    print("  Collecting recent post analytics...")
    posts_dir = date_dir / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    # List recent posts — postiz wraps in {"posts": [...]}
    posts_response = run_postiz(["posts:list"])
    if not posts_response:
        print("  No recent posts found")
        return []

    # Handle both {"posts": [...]} and [...] formats
    if isinstance(posts_response, dict):
        posts = posts_response.get("posts", [])
    elif isinstance(posts_response, list):
        posts = posts_response
    else:
        print("  No recent posts found")
        return []

    collected = []
    for post in posts[:20]:  # Limit to 20 most recent
        post_id = post.get("id")
        if not post_id:
            continue

        post_data = run_postiz(["analytics:post", post_id, "-d", str(days)])
        if post_data and not (isinstance(post_data, dict) and post_data.get("missing")):
            post_file = posts_dir / f"{post_id}.json"
            with open(post_file, "w") as f:
                json.dump({
                    "post_id": post_id,
                    "post_info": post,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "analytics": post_data
                }, f, indent=2)
            collected.append(post_id)

    print(f"  Collected analytics for {len(collected)} posts")
    return collected


def update_aggregated_data(output_dir: Path, today: str, platform_results: dict):
    """Update aggregated time-series files with today's data."""
    agg_dir = output_dir / "aggregated"
    agg_dir.mkdir(parents=True, exist_ok=True)

    # Load or create followers.json
    followers_file = agg_dir / "followers.json"
    if followers_file.exists():
        with open(followers_file, "r") as f:
            followers_data = json.load(f)
    else:
        followers_data = {
            "metric": "followers",
            "last_updated": "",
            "platforms": {},
            "total": {"history": []}
        }

    # Load or create all-metrics.json
    all_metrics_file = agg_dir / "all-metrics.json"
    if all_metrics_file.exists():
        with open(all_metrics_file, "r") as f:
            all_metrics = json.load(f)
    else:
        all_metrics = {
            "last_updated": "",
            "platforms": {}
        }

    total_followers = 0
    prev_total = 0
    if followers_data["total"]["history"]:
        prev_total = followers_data["total"]["history"][-1].get("total", 0)

    for platform_key, data in platform_results.items():
        if data is None:
            continue

        # Initialize platform in aggregated data if needed
        if platform_key not in followers_data["platforms"]:
            followers_data["platforms"][platform_key] = {"history": []}
        if platform_key not in all_metrics["platforms"]:
            all_metrics["platforms"][platform_key] = {"history": []}

        # Extract metrics from Postiz response
        # Postiz returns array of {label, data: [{total, date}], percentageChange}
        platform_metrics = {}
        follower_count = None

        if isinstance(data, list):
            for metric in data:
                label = metric.get("label", "").lower()
                metric_data = metric.get("data", [])
                percentage_change = metric.get("percentageChange", 0)

                # Get latest value
                latest_value = 0
                if metric_data:
                    latest_value = metric_data[-1].get("total", 0)

                platform_metrics[label] = {
                    "value": latest_value,
                    "percentage_change": percentage_change,
                    "time_series": metric_data
                }

                if "follower" in label:
                    follower_count = latest_value

        # Update followers history
        if follower_count is not None:
            prev_count = 0
            hist = followers_data["platforms"][platform_key]["history"]
            if hist:
                prev_count = hist[-1].get("value", 0)

            # Only add if this is a new date
            if not hist or hist[-1].get("date") != today:
                hist.append({
                    "date": today,
                    "value": follower_count,
                    "change": follower_count - prev_count
                })
            total_followers += follower_count

        # Update all-metrics history
        metrics_hist = all_metrics["platforms"][platform_key]["history"]
        if not metrics_hist or metrics_hist[-1].get("date") != today:
            metrics_hist.append({
                "date": today,
                "metrics": platform_metrics
            })

    # Update total followers
    if total_followers > 0:
        total_hist = followers_data["total"]["history"]
        if not total_hist or total_hist[-1].get("date") != today:
            total_hist.append({
                "date": today,
                "total": total_followers,
                "change": total_followers - prev_total
            })

    # Save updated aggregated files
    now = datetime.now(timezone.utc).isoformat()
    followers_data["last_updated"] = now
    all_metrics["last_updated"] = now

    with open(followers_file, "w") as f:
        json.dump(followers_data, f, indent=2)
    print(f"  Updated {followers_file}")

    with open(all_metrics_file, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"  Updated {all_metrics_file}")


def main():
    parser = argparse.ArgumentParser(description="Collect social media analytics from Postiz")
    parser.add_argument("--config", required=True, help="Path to integrations.json")
    parser.add_argument("--output-dir", required=True, help="Path to data/social-analytics/")
    parser.add_argument("--days", type=int, help="Override days lookback")
    args = parser.parse_args()

    # Verify POSTIZ_API_KEY is set
    if not os.environ.get("POSTIZ_API_KEY"):
        print("Error: POSTIZ_API_KEY environment variable not set")
        sys.exit(1)

    config = load_config(args.config)
    output_dir = Path(args.output_dir)
    today = datetime.now().strftime("%Y-%m-%d")

    # Determine lookback period
    first_run = is_first_run(output_dir)
    if args.days:
        days = args.days
    elif first_run:
        days = config["collection"]["first_run_days"]
        print(f"First run detected — pulling {days} days of historical data")
    else:
        days = config["collection"]["default_days"]

    # Create today's raw data directory
    date_dir = output_dir / "raw" / today
    date_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Social Analytics Collection — {today} ===")
    print(f"Lookback: {days} days")
    print()

    # Collect analytics for each enabled platform
    platform_results = {}
    enabled_count = 0
    success_count = 0

    for platform_key, platform_config in config["platforms"].items():
        if not platform_config.get("enabled", False):
            continue
        if not platform_config.get("id"):
            print(f"  Skipping {platform_config['name']} — no integration ID configured")
            continue

        enabled_count += 1
        data = collect_platform_analytics(platform_key, platform_config, days, date_dir)
        platform_results[platform_key] = data
        if data is not None:
            success_count += 1

    print()

    # Collect post-level analytics
    post_ids = collect_post_analytics(min(days, 30), date_dir)

    print()

    # Update aggregated data
    print("Updating aggregated data...")
    update_aggregated_data(output_dir, today, platform_results)

    print()
    print(f"=== Collection Complete ===")
    print(f"Platforms: {success_count}/{enabled_count} successful")
    print(f"Posts analyzed: {len(post_ids)}")
    print(f"Raw data: {date_dir}")
    print(f"Aggregated: {output_dir / 'aggregated'}")


if __name__ == "__main__":
    main()
