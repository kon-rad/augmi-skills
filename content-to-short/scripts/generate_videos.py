#!/usr/bin/env python3
"""
Generate 5-second video clips from scene images using Fal.ai Kling (cheapest model).

Usage:
    python generate_videos.py <script_json_path>
    python generate_videos.py <script_json_path> --model kling-pro --delay 5

Requirements:
    pip install fal-client python-dotenv
"""

import os
import sys
import argparse
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import (
        load_script_json, save_script_json, ensure_output_dirs, print_progress
    )
    from scripts.model_config import get_video_model_config, DEFAULT_VIDEO_MODEL, VIDEO_MODELS
except ModuleNotFoundError:
    from utils import (
        load_script_json, save_script_json, ensure_output_dirs, print_progress
    )
    from model_config import get_video_model_config, DEFAULT_VIDEO_MODEL, VIDEO_MODELS

try:
    import fal_client
except ImportError:
    print("Error: fal-client not installed. Run: pip install fal-client")
    sys.exit(1)


def get_api_key() -> str:
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        raise ValueError(
            "FAL_KEY not found.\n"
            "Get your key at: https://fal.ai/dashboard/keys"
        )
    return api_key


def upload_to_fal(file_path: str) -> str:
    """Upload a local file to Fal.ai CDN and return the URL."""
    url = fal_client.upload_file(file_path)
    return url


def generate_video_clip(image_path: str, motion_prompt: str, duration: int = 5,
                        model_name: str = DEFAULT_VIDEO_MODEL) -> str:
    """Generate a video clip from an image using Fal.ai Kling."""
    model_config = get_video_model_config(model_name)
    model_id = model_config["model_id"]

    print(f"    Model: {model_id}")
    print(f"    Duration: {duration}s")

    image_url = upload_to_fal(image_path)

    result = fal_client.subscribe(
        model_id,
        arguments={
            "image_url": image_url,
            "prompt": motion_prompt or "Subtle camera movement, gentle zoom, cinematic feel",
            "duration": str(duration),
            "aspect_ratio": "9:16",
        },
    )

    if result and "video" in result and "url" in result["video"]:
        return result["video"]["url"]

    raise RuntimeError(f"No video generated. Response: {result}")


def download_video(url: str, output_path: str) -> str:
    """Download video from URL to local path."""
    import requests
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate video clips from scene images via Fal.ai"
    )
    parser.add_argument("script_json", help="Path to script.json")
    parser.add_argument("--model", default=DEFAULT_VIDEO_MODEL,
                        choices=list(VIDEO_MODELS.keys()),
                        help=f"Video model (default: {DEFAULT_VIDEO_MODEL})")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Delay between API calls (default: 2.0)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip scenes that already have a videoPath file on disk")
    args = parser.parse_args()

    get_api_key()

    print(f"Loading script from {args.script_json}...")
    script_data = load_script_json(args.script_json)
    dirs = ensure_output_dirs(args.script_json)

    video_scenes = [s for s in script_data.get("scenes", [])
                    if s.get("visualType") == "video"]

    if not video_scenes:
        print("No scenes with visualType='video' found. Skipping video generation.")
        return

    print(f"\nGenerating {len(video_scenes)} video clips...")
    print("-" * 50)

    generated = 0
    for i, scene in enumerate(video_scenes):
        scene_num = scene["sceneNumber"]
        image_path = scene.get("imagePath")
        video_prompt = scene.get("videoPrompt", "")

        if not image_path or not os.path.exists(image_path):
            print(f"  Scene {scene_num}: No image found, skipping")
            continue

        if args.skip_existing and scene.get("videoPath") and os.path.exists(scene["videoPath"]):
            print(f"  Scene {scene_num}: Skipping (exists): {scene['videoPath']}")
            generated += 1
            continue

        print_progress(i + 1, len(video_scenes),
                       f"Scene {scene_num}: \"{video_prompt[:50]}...\"")

        try:
            video_url = generate_video_clip(
                image_path, video_prompt,
                duration=scene.get("duration", 5),
                model_name=args.model
            )
            output_path = os.path.join(dirs['videos'], f"scene-{scene_num}.mp4")
            download_video(video_url, output_path)
            scene["videoPath"] = output_path
            generated += 1
            print(f"    Saved: scene-{scene_num}.mp4")
        except Exception as e:
            print(f"    Error: {e}")

        if args.delay > 0 and i < len(video_scenes) - 1:
            time.sleep(args.delay)

    save_script_json(args.script_json, script_data)
    print(f"\nGenerated: {generated}/{len(video_scenes)} video clips")


if __name__ == "__main__":
    main()
