#!/usr/bin/env python3
"""
Generate AI images in 9:16 vertical format using Gemini Imagen for short-form video.

Processes scenes with visualType 'generate' or 'video' (video scenes need images first).

Usage:
    python generate_images.py <script_json_path>

Requirements:
    pip install google-genai pillow python-dotenv
"""

import os
import sys
import argparse
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import (
        load_script_json, save_script_json, ensure_output_dirs,
        print_progress, ASPECT_RATIO
    )
    from scripts.model_config import IMAGE_MODELS, DEFAULT_IMAGE_MODEL
except ModuleNotFoundError:
    from utils import (
        load_script_json, save_script_json, ensure_output_dirs,
        print_progress, ASPECT_RATIO
    )
    from model_config import IMAGE_MODELS, DEFAULT_IMAGE_MODEL

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

try:
    from PIL import Image
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def get_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Set GEMINI_API_KEY or GOOGLE_AI_API_KEY.\n"
            "Get your key at: https://aistudio.google.com/apikey"
        )
    return api_key


def generate_image(client, prompt: str, model_name: str = DEFAULT_IMAGE_MODEL) -> bytes:
    model_id = IMAGE_MODELS.get(model_name, IMAGE_MODELS[DEFAULT_IMAGE_MODEL])
    print(f"    Model: {model_id} | Aspect: {ASPECT_RATIO}")

    response = client.models.generate_images(
        model=model_id,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=ASPECT_RATIO,
        )
    )

    for generated_image in response.generated_images:
        if hasattr(generated_image, 'image') and hasattr(generated_image.image, 'image_bytes'):
            return generated_image.image.image_bytes

    raise RuntimeError("No image generated")


def save_image(image_bytes: bytes, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if PIL_AVAILABLE:
        image = Image.open(BytesIO(image_bytes))
        image.save(output_path, quality=95)
    else:
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate vertical AI images for short-form video"
    )
    parser.add_argument("script_json", help="Path to script.json")
    parser.add_argument("--model", default=DEFAULT_IMAGE_MODEL, choices=list(IMAGE_MODELS.keys()))
    parser.add_argument("--delay", type=float, default=2.0)
    args = parser.parse_args()

    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    print(f"Loading script from {args.script_json}...")
    script_data = load_script_json(args.script_json)
    dirs = ensure_output_dirs(args.script_json)

    # Generate images for scenes with visualType 'generate' or 'video'
    # (video scenes need a source image for image-to-video)
    gen_scenes = [s for s in script_data.get("scenes", [])
                  if s.get("visualType") in ("generate", "video")]

    if not gen_scenes:
        print("No scenes needing AI image generation found.")
        return

    print(f"\nGenerating {len(gen_scenes)} vertical AI images...")
    print("-" * 50)

    generated = 0
    for i, scene in enumerate(gen_scenes):
        scene_num = scene["sceneNumber"]
        prompt = scene.get("imageGenPrompt", "")

        if not prompt:
            continue

        print_progress(i + 1, len(gen_scenes), f"Scene {scene_num}: \"{prompt[:50]}...\"")

        try:
            image_bytes = generate_image(client, prompt, args.model)
            output_path = os.path.join(dirs['images'], f"scene-{scene_num}.jpg")
            save_image(image_bytes, output_path)
            scene["imagePath"] = output_path
            generated += 1
            print(f"    Saved: scene-{scene_num}.jpg")
        except Exception as e:
            print(f"    Error: {e}")

        if args.delay > 0 and i < len(gen_scenes) - 1:
            time.sleep(args.delay)

    save_script_json(args.script_json, script_data)
    print(f"\nGenerated: {generated}/{len(gen_scenes)} vertical images")


if __name__ == "__main__":
    main()
