#!/usr/bin/env python3
"""Generate images for each sub-scene using configurable providers + Replicate face swap"""

import os
import sys
import fal_client
from typing import Optional, Tuple

# Try to import replicate, but handle Python 3.14 compatibility issues
try:
    import replicate
    REPLICATE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Replicate not available ({e}). Face swap will be skipped.")
    REPLICATE_AVAILABLE = False

from providers import get_image_provider
from model_config import get_provider_and_model, get_tier_config, DEFAULT_TIER
from utils import (
    load_scene_json, save_scene_json, download_file,
    get_output_dirs, ensure_output_dirs, get_image_path
)


def get_configured_provider(data: dict) -> Tuple[any, str]:
    """
    Get image provider based on scene.json modelConfig.

    Args:
        data: Scene JSON data

    Returns:
        Tuple of (provider_instance, model_name)
    """
    model_config = data.get('modelConfig', {})

    # Check for explicit text_to_image config
    if 'textToImage' in model_config:
        provider_name = model_config['textToImage']['provider']
        model = model_config['textToImage']['model']
    else:
        # Fall back to quality tier
        tier = model_config.get('qualityTier', DEFAULT_TIER)
        provider_name, model = get_provider_and_model(tier, 'text_to_image')

    provider = get_image_provider(provider_name)
    return provider, model


def apply_face_swap(base_image_url: str, avatar_path: str) -> Optional[str]:
    """Apply face swap using Replicate"""
    if not REPLICATE_AVAILABLE:
        print(f"  Face swap skipped (replicate not available)")
        return None

    print(f"  Applying face swap...")

    # Upload avatar to fal storage for use with replicate
    avatar_url = fal_client.upload_file(avatar_path)

    output = replicate.run(
        "easel/advanced-face-swap",
        input={
            "target_image": base_image_url,
            "source_image": avatar_url
        }
    )

    return output


def process_scene_json(json_path: str) -> None:
    """Process all sub-scenes in the JSON file"""
    data = load_scene_json(json_path)

    film_slug = data['output']['filmSlug']
    base_dir = data['output']['baseDir']
    avatar_path = data['avatarPath']
    mode = data.get('mode', 'default')

    dirs = ensure_output_dirs(base_dir, film_slug)

    # Get configured provider
    provider, model = get_configured_provider(data)

    # Get tier info for display
    model_config = data.get('modelConfig', {})
    tier = model_config.get('qualityTier', DEFAULT_TIER)
    tier_info = get_tier_config(tier)

    print(f"\nGenerating images for: {data['title']}")
    print(f"Mode: {mode}")
    print(f"Quality tier: {tier_info['name']} ({tier})")
    print(f"Provider: {provider.provider_name}")
    print(f"Model: {model}")
    print(f"Output directory: {dirs['images']}")
    print(f"Avatar: {avatar_path}")
    print("-" * 50)

    images_generated = 0
    images_skipped = 0

    for scene in data['scenes']:
        print(f"\nScene {scene['sceneNumber']}:")

        for sub_scene in scene['subScenes']:
            sub_id = sub_scene['subSceneId']
            print(f"\n  Sub-scene {sub_id}:")

            # Check if this sub-scene uses the seed image (seed mode)
            if sub_scene.get('useSeedImage', False):
                print(f"    SKIPPED: Using seed image")
                print(f"    Seed image: {sub_scene.get('outputImagePath', 'N/A')}")
                images_skipped += 1
                continue

            # Check if textToImagePrompt exists (required for generation)
            prompt = sub_scene.get('textToImagePrompt')
            if not prompt:
                print(f"    SKIPPED: No textToImagePrompt defined")
                images_skipped += 1
                continue

            # Generate base image
            try:
                print(f"  Generating image: {prompt[:60]}...")

                image_url = provider.generate_image(prompt, model=model)
                base_path = get_image_path(dirs, sub_id, swapped=False)
                download_file(image_url, base_path)
                sub_scene['outputImagePath'] = base_path
                print(f"    Base image saved: {base_path}")
                images_generated += 1

                # Apply face swap if needed
                if sub_scene.get('hasMainCharacter', False):
                    swapped_url = apply_face_swap(image_url, avatar_path)
                    if swapped_url:
                        swapped_path = get_image_path(dirs, sub_id, swapped=True)
                        download_file(swapped_url, swapped_path)
                        sub_scene['faceSwappedImagePath'] = swapped_path
                        print(f"    Face-swapped image saved: {swapped_path}")
                    else:
                        sub_scene['faceSwappedImagePath'] = None
                else:
                    sub_scene['faceSwappedImagePath'] = None

            except Exception as e:
                print(f"    ERROR: {e}")
                sub_scene['imageError'] = str(e)

            # Save progress after each sub-scene
            save_scene_json(json_path, data)

    print("\n" + "=" * 50)
    print("Image generation complete!")
    print(f"Images generated: {images_generated}")
    print(f"Images skipped: {images_skipped}")
    print(f"Scene JSON updated: {json_path}")


def print_usage():
    """Print usage information"""
    print("Usage: python generate_images.py <scene.json>")
    print("\nThe scene.json can include a 'modelConfig' section:")
    print("""
{
  "modelConfig": {
    "qualityTier": "cheapest",  // or "balanced", "highest"
    "textToImage": {
      "provider": "fal",        // or "together"
      "model": "flux-dev"       // model shorthand or full ID
    }
  }
}
""")
    print("\nAvailable tiers: cheapest, balanced, highest")
    print("Available providers: fal, together")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    json_path = sys.argv[1]
    process_scene_json(json_path)
