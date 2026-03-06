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


def aggregate_post_metrics_by_platform(date_dir: Path, config: dict) -> dict:
    """Aggregate post-level analytics by platform as fallback for empty platform APIs.

    Returns dict of {platform_key: synthetic_api_data} for platforms that had
    no platform-level data but do have post-level data.
    """
    posts_dir = date_dir / "posts"
    if not posts_dir.exists():
        return {}

    # Build integration_id -> platform_key mapping
    id_to_platform = {}
    for platform_key, platform_config in config["platforms"].items():
        if platform_config.get("enabled") and platform_config.get("id"):
            id_to_platform[platform_config["id"]] = platform_key

    # Aggregate post metrics by platform
    platform_totals = {}  # {platform_key: {metric_label: total_value}}
    for post_file in posts_dir.glob("*.json"):
        try:
            with open(post_file, "r") as f:
                post_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        integration = post_data.get("post_info", {}).get("integration", {})
        integration_id = integration.get("id", "")
        platform_key = id_to_platform.get(integration_id)
        if not platform_key:
            continue

        if platform_key not in platform_totals:
            platform_totals[platform_key] = {}

        analytics = post_data.get("analytics", [])
        if not isinstance(analytics, list):
            continue

        for metric in analytics:
            label = metric.get("label", "")
            data_points = metric.get("data", [])
            for dp in data_points:
                val = dp.get("total", 0)
                if isinstance(val, str):
                    try:
                        val = float(val) if '.' in val else int(val)
                    except ValueError:
                        val = 0
                platform_totals[platform_key][label] = (
                    platform_totals[platform_key].get(label, 0) + val
                )

    # Convert to Postiz-like API format for compatibility with update_aggregated_data
    result = {}
    today = date_dir.name  # directory name is the date
    for platform_key, metrics in platform_totals.items():
        synthetic_data = []
        for label, total in metrics.items():
            synthetic_data.append({
                "label": label,
                "percentageChange": 0,
                "data": [{"total": total, "date": today}]
            })
        if synthetic_data:
            result[platform_key] = synthetic_data
            post_count = sum(1 for pf in posts_dir.glob("*.json")
                            if _post_belongs_to_platform(pf, id_to_platform, platform_key))
            print(f"  Aggregated {platform_key} from {post_count} posts: "
                  f"{', '.join(f'{k}={v}' for k, v in sorted(metrics.items()))}")

    return result


def _post_belongs_to_platform(post_file: Path, id_to_platform: dict, target_platform: str) -> bool:
    """Check if a post file belongs to a specific platform."""
    try:
        with open(post_file, "r") as f:
            data = json.load(f)
        integration_id = data.get("post_info", {}).get("integration", {}).get("id", "")
        return id_to_platform.get(integration_id) == target_platform
    except (json.JSONDecodeError, IOError):
        return False


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

        # Metrics that represent cumulative totals (use latest non-zero value)
        SNAPSHOT_METRICS = {"followers", "following", "organic followers", "paid followers", "videos"}
        # Metrics that are averages (use latest non-zero value)
        AVERAGE_METRICS = {"average view duration", "average view percentage", "engagement"}

        if isinstance(data, list):
            for metric in data:
                label = metric.get("label", "").lower()
                metric_data = metric.get("data", [])
                percentage_change = metric.get("percentageChange", 0)
                is_average = metric.get("average", False) or label in AVERAGE_METRICS

                # Get the best representative value from the time series
                # For snapshot/cumulative metrics: use latest non-zero value
                # For average metrics: use latest non-zero value
                # For activity metrics (likes, views, etc.): sum the period
                latest_value = 0
                if metric_data:
                    if label in SNAPSHOT_METRICS or is_average:
                        # Use latest non-zero value (handles API lag)
                        for entry in reversed(metric_data):
                            val = entry.get("total", 0)
                            if isinstance(val, str):
                                try:
                                    val = float(val) if '.' in val else int(val)
                                except ValueError:
                                    val = 0
                            if val != 0:
                                latest_value = val
                                break
                    else:
                        # Activity metrics: sum across the period
                        total = 0
                        for entry in metric_data:
                            val = entry.get("total", 0)
                            if isinstance(val, str):
                                try:
                                    val = float(val) if '.' in val else int(val)
                                except ValueError:
                                    val = 0
                            total += val
                        latest_value = total

                platform_metrics[label] = {
                    "value": latest_value,
                    "percentage_change": percentage_change,
                    "time_series": metric_data
                }

                if "follower" in label and label in SNAPSHOT_METRICS:
                    follower_count = latest_value

        # Update followers history
        if follower_count is not None:
            prev_count = 0
            hist = followers_data["platforms"][platform_key]["history"]
            if hist:
                prev_count = hist[-1].get("value", 0)

            # Add or update today's entry
            if hist and hist[-1].get("date") == today:
                hist[-1]["value"] = follower_count
                hist[-1]["change"] = follower_count - prev_count
            else:
                hist.append({
                    "date": today,
                    "value": follower_count,
                    "change": follower_count - prev_count
                })
            total_followers += follower_count

        # Update all-metrics history (add or update today's entry)
        metrics_hist = all_metrics["platforms"][platform_key]["history"]
        if metrics_hist and metrics_hist[-1].get("date") == today:
            metrics_hist[-1]["metrics"] = platform_metrics
        elif not metrics_hist or metrics_hist[-1].get("date") != today:
            metrics_hist.append({
                "date": today,
                "metrics": platform_metrics
            })

    # Update total followers
    if total_followers > 0:
        total_hist = followers_data["total"]["history"]
        if total_hist and total_hist[-1].get("date") == today:
            total_hist[-1]["total"] = total_followers
            total_hist[-1]["change"] = total_followers - prev_total
        elif not total_hist or total_hist[-1].get("date") != today:
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

    # Backfill platforms that returned empty API data with post-level aggregation
    empty_platforms = [k for k, v in platform_results.items() if v is None]
    if empty_platforms:
        print()
        print(f"  Backfilling empty platforms from post data: {', '.join(empty_platforms)}")
        post_aggregation = aggregate_post_metrics_by_platform(date_dir, config)
        for platform_key, synthetic_data in post_aggregation.items():
            if platform_key in empty_platforms:
                platform_results[platform_key] = synthetic_data
                success_count += 1

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
