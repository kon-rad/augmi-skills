#!/usr/bin/env python3
"""Analyze seed image with Gemini Vision and generate story + scene prompts"""

import os
import sys
import json
import shutil
from typing import Optional

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from utils import (
    slugify, ensure_output_dirs, get_image_path,
    save_scene_json, create_scene_json_template
)


def configure_gemini():
    """Configure Gemini API"""
    if not GOOGLE_AVAILABLE:
        raise ImportError(
            "google-generativeai package not installed. "
            "Run: pip install google-generativeai"
        )

    api_key = os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_AI_API_KEY or GEMINI_API_KEY environment variable not set"
        )

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def analyze_image_and_generate_story(
    model,
    image_path: str,
    user_prompt: str
) -> dict:
    """
    Analyze seed image and generate a story with scene prompts.

    Args:
        model: Gemini model instance
        image_path: Path to the seed image
        user_prompt: User's story direction/theme

    Returns:
        Dictionary with story, narration, and scene prompts
    """
    print(f"Analyzing seed image: {image_path}")
    print(f"User prompt: {user_prompt}")
    print("-" * 50)

    # Upload the image
    image_file = genai.upload_file(path=image_path)

    analysis_prompt = f"""You are a creative filmmaker. Analyze this image and create a compelling 30-second short film story.

User's direction: {user_prompt}

Based on this image and the user's direction, create:

1. A story title
2. A 30-second narration script (approximately 60-80 words, meant to be read aloud)
3. Six 5-second scenes that tell this story visually

IMPORTANT: Scene 1 MUST describe exactly what is shown in this seed image, as we will use this image as the first scene.

For each scene, provide:
- A brief description of what happens
- A detailed text-to-image prompt (for scenes 2-6 only, scene 1 uses the seed image)
- An image-to-video motion prompt describing camera movement and subject motion

Respond in this exact JSON format:
{{
    "title": "Film Title",
    "story_summary": "Brief 1-2 sentence summary",
    "narration": "Full narration script for 30 seconds (60-80 words)...",
    "music_prompt": "Describe the musical mood and style for background music",
    "scenes": [
        {{
            "scene_number": 1,
            "description": "What happens in this scene (matches the seed image)",
            "text_to_image_prompt": null,
            "image_to_video_prompt": "Camera and motion description for the seed image...",
            "has_main_character": true or false
        }},
        {{
            "scene_number": 2,
            "description": "What happens in scene 2",
            "text_to_image_prompt": "Detailed prompt for generating scene 2 image...",
            "image_to_video_prompt": "Camera and motion description...",
            "has_main_character": true or false
        }},
        ... (scenes 3-6 follow same format as scene 2)
    ]
}}

Make the story emotionally engaging with a clear beginning, middle, and end.
Keep visual continuity between scenes.
Text-to-image prompts should be detailed, mentioning style, lighting, composition.
Image-to-video prompts should describe smooth, cinematic camera movements.
"""

    print("Generating story with Gemini Vision...")
    response = model.generate_content([image_file, analysis_prompt])

    # Parse JSON from response
    response_text = response.text

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    try:
        story_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Raw response:\n{response_text}")
        raise

    return story_data


def create_seed_scene_json(
    story_data: dict,
    seed_image_path: str,
    output_dir: str = "OUTPUT",
    quality_tier: str = "cheapest",
    voice_id: str = "am_adam"
) -> str:
    """
    Create a scene.json file for seed mode.

    Args:
        story_data: Story data from Gemini analysis
        seed_image_path: Path to the original seed image
        output_dir: Base output directory
        quality_tier: Quality tier for generation
        voice_id: Voice for narration

    Returns:
        Path to the created scene.json file
    """
    title = story_data["title"]
    film_slug = slugify(title)

    # Create output directories
    dirs = ensure_output_dirs(output_dir, film_slug)

    # Copy seed image to images directory as scene 1
    seed_ext = os.path.splitext(seed_image_path)[1]
    scene1_image_path = os.path.join(dirs['images'], f"1-1_base{seed_ext}")
    shutil.copy(seed_image_path, scene1_image_path)
    print(f"Copied seed image to: {scene1_image_path}")

    # Build scene.json structure
    scene_json = {
        "title": title,
        "totalDuration": 30,
        "mode": "seed",
        "seedImagePath": seed_image_path,
        "avatarPath": "IMAGES/avatar/avatar.jpg",
        "modelConfig": {
            "qualityTier": quality_tier
        },
        "config": {
            "voiceId": voice_id,
            "voiceSpeed": 1.0,
            "musicPrompt": story_data.get("music_prompt", "Cinematic orchestral soundtrack"),
            "musicVolume": 0.2,
            "narrationVolume": 1.0
        },
        "narration": {
            "text": story_data["narration"]
        },
        "scenes": [],
        "output": {
            "filmSlug": film_slug,
            "baseDir": output_dir,
            "imagesDir": dirs['images'],
            "videosDir": dirs['videos'],
            "audioDir": dirs['audio'],
            "finalVideo": os.path.join(dirs['videos'], f"{film_slug}.mp4")
        }
    }

    # Convert Gemini scenes to our format
    for scene_data in story_data["scenes"]:
        scene_num = scene_data["scene_number"]

        sub_scene = {
            "subSceneId": f"{scene_num}-1",
            "duration": 5,
            "hasMainCharacter": scene_data.get("has_main_character", False),
            "description": scene_data["description"],
            "textToImagePrompt": scene_data.get("text_to_image_prompt"),
            "imageToVideoPrompt": scene_data["image_to_video_prompt"]
        }

        # Scene 1 uses the seed image
        if scene_num == 1:
            sub_scene["outputImagePath"] = scene1_image_path
            sub_scene["useSeedImage"] = True

        scene = {
            "sceneNumber": scene_num,
            "duration": 5,
            "subScenes": [sub_scene]
        }

        scene_json["scenes"].append(scene)

    # Save scene.json
    json_path = os.path.join(dirs['base'], "scene.json")
    save_scene_json(json_path, scene_json)

    print(f"\nScene JSON created: {json_path}")
    print(f"Title: {title}")
    print(f"Scenes: {len(scene_json['scenes'])}")
    print(f"Narration: {len(story_data['narration'])} chars")

    return json_path


def process_seed_image(
    seed_image_path: str,
    user_prompt: str,
    output_dir: str = "OUTPUT",
    quality_tier: str = "cheapest",
    voice_id: str = "am_adam"
) -> str:
    """
    Main entry point for seed mode processing.

    Args:
        seed_image_path: Path to the seed image
        user_prompt: User's story direction
        output_dir: Base output directory
        quality_tier: Quality tier for generation
        voice_id: Voice for narration

    Returns:
        Path to the created scene.json file
    """
    # Validate seed image exists
    if not os.path.exists(seed_image_path):
        raise FileNotFoundError(f"Seed image not found: {seed_image_path}")

    # Configure Gemini
    model = configure_gemini()

    # Analyze image and generate story
    story_data = analyze_image_and_generate_story(model, seed_image_path, user_prompt)

    print("\n" + "=" * 50)
    print("Story Generated!")
    print("=" * 50)
    print(f"Title: {story_data['title']}")
    print(f"Summary: {story_data.get('story_summary', 'N/A')}")
    print(f"\nNarration:\n{story_data['narration']}")
    print("\nScenes:")
    for scene in story_data['scenes']:
        print(f"  Scene {scene['scene_number']}: {scene['description'][:60]}...")

    # Create scene.json
    json_path = create_seed_scene_json(
        story_data,
        seed_image_path,
        output_dir,
        quality_tier,
        voice_id
    )

    return json_path


def print_usage():
    """Print usage information"""
    print("Usage: python analyze_seed_image.py <seed_image> <prompt> [options]")
    print("\nArguments:")
    print("  seed_image    Path to the seed image file")
    print("  prompt        Story direction/theme (in quotes)")
    print("\nOptions:")
    print("  --output-dir  Output directory (default: OUTPUT)")
    print("  --tier        Quality tier: cheapest, balanced, highest (default: cheapest)")
    print("  --voice       Voice ID for narration (default: am_adam)")
    print("\nExample:")
    print('  python analyze_seed_image.py photo.jpg "An epic adventure in nature"')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    seed_image = sys.argv[1]
    prompt = sys.argv[2]

    # Parse optional arguments
    output_dir = "OUTPUT"
    tier = "cheapest"
    voice = "am_adam"

    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--tier" and i + 1 < len(sys.argv):
            tier = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--voice" and i + 1 < len(sys.argv):
            voice = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    json_path = process_seed_image(seed_image, prompt, output_dir, tier, voice)

    print("\n" + "=" * 50)
    print("Seed image analysis complete!")
    print(f"Scene JSON: {json_path}")
    print("\nNext steps:")
    print(f"  1. python generate_images.py {json_path}")
    print(f"  2. python generate_videos.py {json_path}")
    print(f"  3. python generate_narration.py {json_path}")
    print(f"  4. python generate_music.py {json_path}")
    print(f"  5. python compose_video.py {json_path}")
