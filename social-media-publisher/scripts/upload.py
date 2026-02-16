#!/usr/bin/env python3
"""
Upload Reels to Instagram and Facebook Pages via Meta Graph API.

Usage:
  # Upload to Instagram
  python upload.py --video path/to/video.mp4 --caption "My Reel #hashtag" --platform instagram

  # Upload to Facebook
  python upload.py --video path/to/video.mp4 --caption "My Reel" --platform facebook

  # Upload to both
  python upload.py --video path/to/video.mp4 --caption "My Reel" --platform both

  # Use an existing public URL instead of uploading
  python upload.py --video-url https://example.com/video.mp4 --caption "My Reel" --platform instagram

  # Schedule for later (Facebook only via API; Instagram saves schedule file)
  python upload.py --video path/to/video.mp4 --caption "Scheduled" --platform both --schedule "2026-02-20T14:00:00" --timezone "America/Los_Angeles"
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"
POLL_INTERVAL = 5  # seconds
MAX_POLL_ATTEMPTS = 60  # 5 minutes max


def get_env(key: str, required: bool = True) -> str | None:
    val = os.getenv(key)
    if required and not val:
        print(f"Error: {key} environment variable is not set.")
        sys.exit(1)
    return val


def validate_video(video_path: str) -> dict:
    """Validate video file exists and check basic properties."""
    path = Path(video_path)
    if not path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 1000:
        print(f"Warning: Video is {size_mb:.1f}MB. Instagram limit is 1GB, Facebook is 4GB.")

    # Try to get video info via ffprobe
    info = {"path": str(path), "size_mb": round(size_mb, 2)}
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_streams", "-show_format", str(path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            probe = json.loads(result.stdout)
            for stream in probe.get("streams", []):
                if stream.get("codec_type") == "video":
                    info["width"] = stream.get("width")
                    info["height"] = stream.get("height")
                    info["codec"] = stream.get("codec_name")
                    info["duration"] = float(stream.get("duration", 0))
                    break
            if not info.get("duration") and probe.get("format", {}).get("duration"):
                info["duration"] = float(probe["format"]["duration"])

            if info.get("duration") and info["duration"] > 90:
                print(f"Warning: Video is {info['duration']:.1f}s. Reels max is 90 seconds.")
            if info.get("duration") and info["duration"] < 3:
                print(f"Warning: Video is {info['duration']:.1f}s. Reels min is 3 seconds.")
            if info.get("width") and info.get("height"):
                ratio = info["height"] / info["width"]
                if abs(ratio - 16/9) > 0.1:
                    print(f"Warning: Aspect ratio is {info['width']}x{info['height']}. "
                          f"Recommended is 9:16 (1080x1920) for Reels.")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Note: ffprobe not found. Skipping video validation.")

    print(f"Video: {path.name} ({info['size_mb']}MB)")
    if info.get("duration"):
        print(f"Duration: {info['duration']:.1f}s")
    if info.get("width"):
        print(f"Resolution: {info['width']}x{info['height']}")

    return info


def get_public_video_url(video_path: str) -> str:
    """Upload video to a temporary host and return public URL.

    Uses transfer.sh (or tmpfiles.org as fallback) for temporary hosting.
    The URL remains valid for ~24 hours - enough for Meta to process it.
    """
    path = Path(video_path)

    # Try transfer.sh first
    print("Uploading video to temporary host...")
    try:
        with open(path, "rb") as f:
            resp = requests.put(
                f"https://transfer.sh/{path.name}",
                data=f,
                headers={"Max-Days": "1"},
                timeout=300,
            )
        if resp.ok:
            url = resp.text.strip()
            print(f"Uploaded: {url}")
            return url
    except Exception as e:
        print(f"transfer.sh failed: {e}")

    # Fallback to tmpfiles.org
    try:
        with open(path, "rb") as f:
            resp = requests.post(
                "https://tmpfiles.org/api/v1/upload",
                files={"file": (path.name, f, "video/mp4")},
                timeout=300,
            )
        if resp.ok:
            data = resp.json()
            # tmpfiles.org returns a page URL, convert to direct download
            url = data["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/")
            print(f"Uploaded: {url}")
            return url
    except Exception as e:
        print(f"tmpfiles.org failed: {e}")

    print("Error: Could not upload video to a public URL.")
    print("Please upload the video manually and provide --video-url instead.")
    sys.exit(1)


def upload_instagram_reel(
    video_url: str,
    caption: str = "",
    cover_url: str | None = None,
    schedule_time: int | None = None,
) -> dict:
    """Upload a Reel to Instagram via Graph API."""
    access_token = get_env("META_ACCESS_TOKEN")
    ig_user_id = get_env("INSTAGRAM_BUSINESS_ACCOUNT_ID")

    print(f"\n=== Uploading to Instagram (@{ig_user_id}) ===")

    # Step 1: Create media container
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token,
    }
    if cover_url:
        params["cover_url"] = cover_url

    print("Creating media container...")
    resp = requests.post(f"{GRAPH_API_BASE}/{ig_user_id}/media", data=params)

    if not resp.ok:
        error = resp.json().get("error", {})
        print(f"Error creating container: {error.get('message', resp.text)}")
        return {"success": False, "error": error}

    container_id = resp.json()["id"]
    print(f"Container ID: {container_id}")

    # Step 2: Poll for processing completion
    print("Processing video", end="", flush=True)
    for attempt in range(MAX_POLL_ATTEMPTS):
        status_resp = requests.get(
            f"{GRAPH_API_BASE}/{container_id}",
            params={
                "fields": "status_code,status",
                "access_token": access_token,
            },
        )
        if status_resp.ok:
            status_data = status_resp.json()
            status_code = status_data.get("status_code", "")

            if status_code == "FINISHED":
                print(" Done!")
                break
            elif status_code == "ERROR":
                print(f"\nProcessing error: {status_data.get('status', 'Unknown error')}")
                return {"success": False, "error": status_data.get("status")}
            elif status_code == "EXPIRED":
                print("\nContainer expired before publishing.")
                return {"success": False, "error": "Container expired"}

        print(".", end="", flush=True)
        time.sleep(POLL_INTERVAL)
    else:
        print(f"\nTimeout: Video processing took longer than {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s")
        return {"success": False, "error": "Processing timeout", "container_id": container_id}

    # Step 3: Publish
    print("Publishing reel...")
    pub_resp = requests.post(
        f"{GRAPH_API_BASE}/{ig_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": access_token,
        },
    )

    if not pub_resp.ok:
        error = pub_resp.json().get("error", {})
        print(f"Error publishing: {error.get('message', pub_resp.text)}")
        return {"success": False, "error": error}

    media_id = pub_resp.json()["id"]
    print(f"Published! Media ID: {media_id}")

    # Get permalink
    permalink_resp = requests.get(
        f"{GRAPH_API_BASE}/{media_id}",
        params={
            "fields": "permalink,timestamp",
            "access_token": access_token,
        },
    )
    permalink = ""
    if permalink_resp.ok:
        permalink = permalink_resp.json().get("permalink", "")
        if permalink:
            print(f"URL: {permalink}")

    return {
        "success": True,
        "platform": "instagram",
        "media_id": media_id,
        "container_id": container_id,
        "permalink": permalink,
    }


def upload_facebook_reel(
    video_path: str,
    caption: str = "",
    schedule_time: int | None = None,
) -> dict:
    """Upload a Reel to a Facebook Page via Graph API."""
    access_token = get_env("META_ACCESS_TOKEN")
    page_id = get_env("FACEBOOK_PAGE_ID")

    print(f"\n=== Uploading to Facebook Page ({page_id}) ===")

    # Get Page access token
    pages_resp = requests.get(
        f"{GRAPH_API_BASE}/me/accounts",
        params={"access_token": access_token},
    )
    page_token = access_token
    if pages_resp.ok:
        for page in pages_resp.json().get("data", []):
            if page["id"] == page_id:
                page_token = page.get("access_token", access_token)
                break

    # Step 1: Initialize upload
    print("Initializing upload...")
    init_params = {
        "upload_phase": "start",
        "access_token": page_token,
    }
    resp = requests.post(f"{GRAPH_API_BASE}/{page_id}/video_reels", data=init_params)

    if not resp.ok:
        error = resp.json().get("error", {})
        print(f"Error starting upload: {error.get('message', resp.text)}")
        return {"success": False, "error": error}

    video_id = resp.json()["video_id"]
    print(f"Video ID: {video_id}")

    # Step 2: Upload video binary
    print("Uploading video data...")
    path = Path(video_path)
    with open(path, "rb") as f:
        upload_resp = requests.post(
            f"https://rupload.facebook.com/video-upload/v21.0/{video_id}",
            data=f,
            headers={
                "Authorization": f"OAuth {page_token}",
                "offset": "0",
                "file_size": str(path.stat().st_size),
            },
            timeout=600,
        )

    if not upload_resp.ok:
        print(f"Error uploading: {upload_resp.text}")
        return {"success": False, "error": upload_resp.text}

    print("Upload complete.")

    # Step 3: Finish and publish
    print("Publishing reel...")
    finish_params = {
        "upload_phase": "finish",
        "video_id": video_id,
        "title": caption[:255] if caption else "",
        "description": caption,
        "access_token": page_token,
    }
    if schedule_time:
        finish_params["scheduled_publish_time"] = schedule_time
        print(f"Scheduling for: {datetime.fromtimestamp(schedule_time, tz=timezone.utc).isoformat()}")

    finish_resp = requests.post(
        f"{GRAPH_API_BASE}/{page_id}/video_reels", data=finish_params
    )

    if not finish_resp.ok:
        error = finish_resp.json().get("error", {})
        print(f"Error publishing: {error.get('message', finish_resp.text)}")
        return {"success": False, "error": error}

    result_data = finish_resp.json()
    print(f"Published! Success: {result_data.get('success', False)}")

    return {
        "success": True,
        "platform": "facebook",
        "video_id": video_id,
        "scheduled": schedule_time is not None,
    }


def save_schedule_file(
    video_path: str,
    video_url: str,
    caption: str,
    platform: str,
    schedule_time: str,
    timezone_str: str,
) -> str:
    """Save a schedule file for later publishing (used for Instagram scheduling)."""
    output_dir = Path("OUTPUT/scheduled")
    output_dir.mkdir(parents=True, exist_ok=True)

    schedule_data = {
        "video_path": video_path,
        "video_url": video_url,
        "caption": caption,
        "platform": platform,
        "scheduled_time": schedule_time,
        "timezone": timezone_str,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }

    filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(schedule_data, f, indent=2)

    print(f"\nSchedule file saved: {filepath}")
    print(f"To publish at the scheduled time, run:")
    print(f"  python upload.py --from-schedule {filepath}")
    return str(filepath)


def check_status(container_id: str) -> dict:
    """Check the status of an Instagram media container."""
    access_token = get_env("META_ACCESS_TOKEN")

    resp = requests.get(
        f"{GRAPH_API_BASE}/{container_id}",
        params={
            "fields": "status_code,status,id",
            "access_token": access_token,
        },
    )

    if not resp.ok:
        error = resp.json().get("error", {})
        print(f"Error: {error.get('message', resp.text)}")
        return {"success": False, "error": error}

    data = resp.json()
    print(f"Container ID: {data.get('id')}")
    print(f"Status: {data.get('status_code', 'unknown')}")
    if data.get("status"):
        print(f"Details: {data['status']}")

    return data


def main():
    parser = argparse.ArgumentParser(description="Upload Reels to Instagram/Facebook")

    parser.add_argument("--video", help="Path to video file")
    parser.add_argument("--video-url", help="Public URL of video (skip upload)")
    parser.add_argument("--caption", default="", help="Caption text with hashtags")
    parser.add_argument(
        "--platform",
        choices=["instagram", "facebook", "both"],
        default="both",
        help="Target platform (default: both)",
    )
    parser.add_argument("--cover-url", help="Cover image URL (Instagram only)")
    parser.add_argument(
        "--schedule",
        help="Schedule publish time (ISO format: 2026-02-20T14:00:00)",
    )
    parser.add_argument("--timezone", default="UTC", help="Timezone for scheduling")
    parser.add_argument(
        "--check-status", help="Check status of a container ID"
    )
    parser.add_argument(
        "--from-schedule", help="Publish from a schedule file"
    )

    args = parser.parse_args()

    # Check status mode
    if args.check_status:
        check_status(args.check_status)
        return

    # Publish from schedule file
    if args.from_schedule:
        with open(args.from_schedule) as f:
            sched = json.load(f)
        args.video = sched.get("video_path")
        args.video_url = sched.get("video_url")
        args.caption = sched.get("caption", "")
        args.platform = sched.get("platform", "both")

    # Need either --video or --video-url
    if not args.video and not args.video_url:
        print("Error: Provide either --video (file path) or --video-url (public URL)")
        parser.print_help()
        sys.exit(1)

    # Validate video if local file
    video_url = args.video_url
    if args.video:
        validate_video(args.video)
        if not video_url:
            video_url = get_public_video_url(args.video)

    # Calculate schedule timestamp
    schedule_timestamp = None
    if args.schedule:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(args.timezone)
        dt = datetime.fromisoformat(args.schedule).replace(tzinfo=tz)
        schedule_timestamp = int(dt.timestamp())
        print(f"\nScheduled for: {dt.isoformat()}")

    results = []

    # Upload to Instagram
    if args.platform in ("instagram", "both"):
        if schedule_timestamp:
            # Instagram scheduling via API is unreliable; save schedule file
            save_schedule_file(
                args.video or "",
                video_url,
                args.caption,
                "instagram",
                args.schedule,
                args.timezone,
            )
        else:
            result = upload_instagram_reel(
                video_url=video_url,
                caption=args.caption,
                cover_url=args.cover_url,
            )
            results.append(result)

    # Upload to Facebook
    if args.platform in ("facebook", "both"):
        if args.video:
            result = upload_facebook_reel(
                video_path=args.video,
                caption=args.caption,
                schedule_time=schedule_timestamp,
            )
            results.append(result)
        else:
            print("\nFacebook upload requires a local video file (--video), not just a URL.")

    # Summary
    print("\n=== Upload Summary ===")
    for r in results:
        status = "Success" if r.get("success") else "Failed"
        platform = r.get("platform", "unknown")
        print(f"{platform.title()}: {status}")
        if r.get("permalink"):
            print(f"  URL: {r['permalink']}")
        if r.get("media_id"):
            print(f"  Media ID: {r['media_id']}")
        if r.get("video_id"):
            print(f"  Video ID: {r['video_id']}")
        if r.get("error"):
            print(f"  Error: {r['error']}")


if __name__ == "__main__":
    main()
