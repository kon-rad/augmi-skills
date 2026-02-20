#!/usr/bin/env python3
"""
Search and download portrait-orientation images from Pexels API for short-form video.

Processes scenes with visualType 'web'.

Usage:
    python search_images.py <script_json_path>

Requirements:
    pip install requests python-dotenv
"""

import os
import sys
import argparse
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import (
        load_script_json, save_script_json, ensure_output_dirs,
        download_file, print_progress
    )
except ModuleNotFoundError:
    from utils import (
        load_script_json, save_script_json, ensure_output_dirs,
        download_file, print_progress
    )


PEXELS_BASE_URL = "https://api.pexels.com/v1"


def get_api_key() -> str:
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise ValueError(
            "PEXELS_API_KEY not found.\n"
            "Get your free key at: https://www.pexels.com/api/new/"
        )
    return api_key


def search_pexels(query: str, api_key: str, per_page: int = 5) -> list:
    """Search Pexels for portrait-orientation photos."""
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "orientation": "portrait",
        "per_page": per_page,
        "size": "large",
    }
    response = requests.get(f"{PEXELS_BASE_URL}/search", headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("photos", [])


def download_best_photo(photos: list, output_path: str) -> str:
    if not photos:
        raise ValueError("No photos to download")

    photo = photos[0]
    image_url = photo["src"].get("portrait") or photo["src"].get("large")
    if not image_url:
        raise ValueError(f"No suitable image URL for photo {photo['id']}")

    download_file(image_url, output_path)
    photographer = photo.get("photographer", "Unknown")
    print(f"    Photo by {photographer} on Pexels")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Search portrait images for short-form video scenes"
    )
    parser.add_argument("script_json", help="Path to script.json")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between requests (default: 1.0)")
    args = parser.parse_args()

    api_key = get_api_key()

    print(f"Loading script from {args.script_json}...")
    script_data = load_script_json(args.script_json)
    dirs = ensure_output_dirs(args.script_json)

    web_scenes = [s for s in script_data.get("scenes", [])
                  if s.get("visualType", s.get("imageSource")) == "web"]

    if not web_scenes:
        print("No scenes with visualType='web' found.")
        return

    print(f"\nSearching portrait images for {len(web_scenes)} scenes...")
    print("-" * 50)

    downloaded = 0
    for i, scene in enumerate(web_scenes):
        scene_num = scene["sceneNumber"]
        query = scene.get("imageSearchQuery", "")

        if not query:
            print(f"  Scene {scene_num}: No search query, skipping")
            continue

        print_progress(i + 1, len(web_scenes), f"Scene {scene_num}: \"{query}\"")

        try:
            photos = search_pexels(query, api_key)

            if not photos:
                simple_query = " ".join(query.split()[:2])
                print(f"    Retrying with: \"{simple_query}\"")
                photos = search_pexels(simple_query, api_key)

            if not photos:
                fallback_queries = [
                    "technology abstract", "digital innovation",
                    "modern workspace", "creative design", "nature landscape",
                ]
                for fq in fallback_queries:
                    photos = search_pexels(fq, api_key)
                    if photos:
                        print(f"    Used generic fallback: \"{fq}\"")
                        break

            if photos:
                output_path = os.path.join(dirs['images'], f"scene-{scene_num}.jpg")
                download_best_photo(photos, output_path)
                scene["imagePath"] = output_path
                downloaded += 1
            else:
                print(f"    Warning: No images found")

        except Exception as e:
            print(f"    Error: {e}")

        if args.delay > 0 and i < len(web_scenes) - 1:
            time.sleep(args.delay)

    save_script_json(args.script_json, script_data)

    print(f"\n{'=' * 50}")
    print(f"Downloaded: {downloaded}/{len(web_scenes)} portrait images")


if __name__ == "__main__":
    main()
