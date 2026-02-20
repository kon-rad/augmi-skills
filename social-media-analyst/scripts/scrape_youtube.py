#!/usr/bin/env python3
"""YouTube channel scraper using yt-dlp.

Collects channel metadata, video listings, and per-video details.
Produces the same data format as the existing JakeExplains dataset.

Usage:
    python3 scrape_youtube.py --channel "@Jakexplains" --output OUTPUT/JakeExplains/data
    python3 scrape_youtube.py --channel-url "https://www.youtube.com/@Jakexplains" --output OUTPUT/JakeExplains/data
    python3 scrape_youtube.py --channel "@Jakexplains" --output OUTPUT/JakeExplains/data --skip-details
"""

import argparse
import json
import os
import subprocess
import sys
import time


def run_ytdlp(args, timeout=120):
    """Run yt-dlp with given args and return stdout lines."""
    cmd = ["yt-dlp"] + args
    print(f"  Running: {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"  yt-dlp stderr: {result.stderr[:500]}", file=sys.stderr)
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def scrape_channel_info(channel_url, output_dir):
    """Scrape channel metadata."""
    print("Phase 1: Scraping channel info...", file=sys.stderr)
    lines = run_ytdlp([
        "--skip-download", "--print-json", "--playlist-items", "1",
        f"{channel_url}/videos"
    ], timeout=60)

    if not lines or not lines[0]:
        print("  Warning: Could not fetch channel info", file=sys.stderr)
        return None

    data = json.loads(lines[0])
    info = {
        "channel": data.get("channel", ""),
        "channel_id": data.get("channel_id", ""),
        "channel_url": data.get("channel_url", ""),
        "uploader_id": data.get("uploader_id", ""),
        "uploader_url": data.get("uploader_url", ""),
        "channel_follower_count": data.get("channel_follower_count", 0),
        "description": data.get("channel_description", data.get("description", ""))
    }

    path = os.path.join(output_dir, "channel-info.json")
    with open(path, "w") as f:
        json.dump(info, f, indent=2)
    print(f"  Saved channel info: {info['channel']} ({info['channel_follower_count']} subs)", file=sys.stderr)
    return info


def scrape_flat_playlist(channel_url, tab, output_dir):
    """Scrape flat playlist for videos or shorts tab."""
    label = "shorts" if tab == "shorts" else "videos"
    print(f"Phase 2: Scraping {label} flat playlist...", file=sys.stderr)

    url = f"{channel_url}/{tab}"
    lines = run_ytdlp(["--flat-playlist", "--print-json", url], timeout=300)

    if not lines or not lines[0]:
        print(f"  No {label} found", file=sys.stderr)
        return []

    entries = []
    path = os.path.join(output_dir, f"{label}-flat.jsonl")
    with open(path, "w") as f:
        for line in lines:
            if not line.strip():
                continue
            f.write(line + "\n")
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    print(f"  Found {len(entries)} {label}", file=sys.stderr)

    # Also write sorted version
    sorted_entries = sorted(entries, key=lambda x: x.get("view_count", 0) or 0, reverse=True)
    sorted_slim = [
        {"id": e.get("id"), "title": e.get("title"), "view_count": e.get("view_count", 0), "duration": e.get("duration", 0)}
        for e in sorted_entries
    ]
    sorted_path = os.path.join(output_dir, f"{label}-flat-sorted.json")
    with open(sorted_path, "w") as f:
        json.dump(sorted_slim, f, indent=2)

    return entries


def scrape_details(entries, content_type, output_dir, delay=1.0):
    """Fetch full metadata for each video/short."""
    label = "shorts" if content_type == "shorts" else "videos"
    detail_dir = os.path.join(output_dir, f"{label}-detail")
    os.makedirs(detail_dir, exist_ok=True)

    print(f"Phase 3: Fetching {label} details ({len(entries)} items)...", file=sys.stderr)

    for i, entry in enumerate(entries):
        vid_id = entry.get("id")
        if not vid_id:
            continue

        detail_path = os.path.join(detail_dir, f"{vid_id}.json")
        if os.path.exists(detail_path):
            print(f"  [{i+1}/{len(entries)}] {vid_id} already exists, skipping", file=sys.stderr)
            continue

        try:
            url = entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}"
            lines = run_ytdlp(["--skip-download", "--print-json", url], timeout=30)

            if lines and lines[0]:
                full = json.loads(lines[0])
                detail = {
                    "id": full.get("id", vid_id),
                    "title": full.get("title", entry.get("title", "")),
                    "upload_date": full.get("upload_date", ""),
                    "duration": full.get("duration", 0),
                    "view_count": full.get("view_count", 0),
                    "like_count": full.get("like_count", 0),
                    "comment_count": full.get("comment_count", 0)
                }
                with open(detail_path, "w") as f:
                    json.dump(detail, f, indent=2)
                print(f"  [{i+1}/{len(entries)}] {vid_id}: {detail['view_count']} views", file=sys.stderr)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            print(f"  [{i+1}/{len(entries)}] {vid_id}: error - {e}", file=sys.stderr)

        if delay > 0:
            time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Scrape YouTube channel data via yt-dlp")
    parser.add_argument("--channel", help="Channel handle (e.g., @Jakexplains)")
    parser.add_argument("--channel-url", help="Full channel URL")
    parser.add_argument("--output", required=True, help="Output directory for data files")
    parser.add_argument("--skip-details", action="store_true", help="Skip per-video detail fetching")
    parser.add_argument("--shorts-only", action="store_true", help="Only scrape shorts")
    parser.add_argument("--videos-only", action="store_true", help="Only scrape videos")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between detail requests (seconds)")
    args = parser.parse_args()

    if not args.channel and not args.channel_url:
        parser.error("Either --channel or --channel-url is required")

    channel_url = args.channel_url or f"https://www.youtube.com/{args.channel}"
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    # Channel info
    scrape_channel_info(channel_url, output_dir)

    # Flat playlists
    shorts_entries = []
    video_entries = []

    if not args.videos_only:
        shorts_entries = scrape_flat_playlist(channel_url, "shorts", output_dir)

    if not args.shorts_only:
        video_entries = scrape_flat_playlist(channel_url, "videos", output_dir)

    # Details
    if not args.skip_details:
        if shorts_entries:
            scrape_details(shorts_entries, "shorts", output_dir, delay=args.delay)
        if video_entries:
            scrape_details(video_entries, "videos", output_dir, delay=args.delay)

    # Summary
    total = len(shorts_entries) + len(video_entries)
    print(f"\nDone! Scraped {total} items ({len(shorts_entries)} shorts, {len(video_entries)} videos)", file=sys.stderr)
    print(f"Data saved to: {output_dir}", file=sys.stderr)

    # Output JSON summary for downstream consumption
    summary = {
        "channel_url": channel_url,
        "output_dir": output_dir,
        "shorts_count": len(shorts_entries),
        "videos_count": len(video_entries),
        "details_fetched": not args.skip_details
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
