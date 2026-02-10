#!/usr/bin/env python3
"""Generate video clips from images using configurable providers"""

import os
import sys
from typing import Tuple

from providers import get_video_provider
from model_config import get_provider_and_model, get_tier_config, DEFAULT_TIER
from utils import (
    load_scene_json, save_scene_json, download_file,
    get_output_dirs, ensure_output_dirs, get_video_path
)


def get_configured_provider(data: dict) -> Tuple[any, str]:
    """
    Get video provider based on scene.json modelConfig.

    Args:
        data: Scene JSON data

    Returns:
        Tuple of (provider_instance, model_name)
    """
    model_config = data.get('modelConfig', {})

    # Check for explicit image_to_video config
    if 'imageToVideo' in model_config:
        provider_name = model_config['imageToVideo']['provider']
        model = model_config['imageToVideo']['model']
    else:
        # Fall back to quality tier
        tier = model_config.get('qualityTier', DEFAULT_TIER)
        provider_name, model = get_provider_and_model(tier, 'image_to_video')

    provider = get_video_provider(provider_name)
    return provider, model


def process_scene_json(json_path: str) -> None:
    """Process all sub-scenes in the JSON file"""
    data = load_scene_json(json_path)

    film_slug = data['output']['filmSlug']
    base_dir = data['output']['baseDir']
    mode = data.get('mode', 'default')

    dirs = ensure_output_dirs(base_dir, film_slug)

    # Get configured provider
    provider, model = get_configured_provider(data)

    # Get tier info for display
    model_config = data.get('modelConfig', {})
    tier = model_config.get('qualityTier', DEFAULT_TIER)
    tier_info = get_tier_config(tier)

    print(f"\nGenerating videos for: {data['title']}")
    print(f"Mode: {mode}")
    print(f"Quality tier: {tier_info['name']} ({tier})")
    print(f"Provider: {provider.provider_name}")
    print(f"Model: {model}")
    print(f"Output directory: {dirs['videos']}")
    print("-" * 50)

    for scene in data['scenes']:
        print(f"\nScene {scene['sceneNumber']}:")

        for sub_scene in scene['subScenes']:
            sub_id = sub_scene['subSceneId']
            duration = sub_scene['duration']
            print(f"\n  Sub-scene {sub_id} ({duration}s):")

            # Use face-swapped image if available, otherwise base image
            image_path = sub_scene.get('faceSwappedImagePath') or sub_scene.get('outputImagePath')

            if not image_path or not os.path.exists(image_path):
                print(f"    SKIPPED: No image found")
                continue

            try:
                video_url = provider.generate_video(
                    image_path,
                    sub_scene['imageToVideoPrompt'],
                    duration,
                    model=model
                )
                video_path = get_video_path(dirs, sub_id)
                download_file(video_url, video_path)
                sub_scene['outputVideoPath'] = video_path
                print(f"    Video saved: {video_path}")

                # Remove any previous error
                if 'videoError' in sub_scene:
                    del sub_scene['videoError']

            except Exception as e:
                print(f"    ERROR: {e}")
                sub_scene['videoError'] = str(e)

            # Save progress after each sub-scene
            save_scene_json(json_path, data)

    print("\n" + "=" * 50)
    print("Video generation complete!")
    print(f"Scene JSON updated: {json_path}")


def print_usage():
    """Print usage information"""
    print("Usage: python generate_videos.py <scene.json>")
    print("\nThe scene.json can include a 'modelConfig' section:")
    print("""
{
  "modelConfig": {
    "qualityTier": "cheapest",  // or "balanced", "highest"
    "imageToVideo": {
      "provider": "fal",        // or "together", "google"
      "model": "kling-2.5-turbo"  // model shorthand or full ID
    }
  }
}
""")
    print("\nAvailable tiers: cheapest, balanced, highest")
    print("Available providers: fal, together, google")
    print("\nGoogle models: veo-2, veo-3, veo-3-fast")
    print("Fal models: wan-2.5, kling-2.5-turbo, kling-2.6, veo2")
    print("Together models: pixverse-v5, hailuo, seedance-1-pro, sora-2-pro")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    json_path = sys.argv[1]
    process_scene_json(json_path)
