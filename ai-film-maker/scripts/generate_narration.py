#!/usr/bin/env python3
"""Generate voice narration using Fal.ai Kokoro TTS"""

import os
import sys
import fal_client
from utils import (
    load_scene_json, save_scene_json, download_file,
    get_output_dirs, ensure_output_dirs, get_audio_path
)

# Available voice IDs
MALE_VOICES = [
    'am_adam', 'am_echo', 'am_eric', 'am_fenrir',
    'am_liam', 'am_michael', 'am_onyx', 'am_puck', 'am_santa'
]

FEMALE_VOICES = [
    'af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica',
    'af_kore', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky'
]

def generate_narration(text: str, voice_id: str = "am_adam", speed: float = 1.0) -> str:
    """Generate narration audio using Kokoro TTS"""
    print(f"Generating narration with voice '{voice_id}' at {speed}x speed...")
    print(f"Text: {text[:100]}...")

    result = fal_client.subscribe(
        "fal-ai/kokoro/american-english",
        arguments={
            "prompt": text,
            "voice": voice_id,
            "speed": speed
        },
        with_logs=False
    )

    return result['audio']['url']

def process_scene_json(json_path: str) -> None:
    """Generate narration from scene JSON"""
    data = load_scene_json(json_path)

    film_slug = data['output']['filmSlug']
    base_dir = data['output']['baseDir']

    dirs = ensure_output_dirs(base_dir, film_slug)

    print(f"\nGenerating narration for: {data['title']}")
    print("-" * 50)

    narration = data['narration']
    text = narration['text']
    voice_id = data['config'].get('voiceId', 'am_adam')
    speed = data['config'].get('voiceSpeed', 1.0)

    try:
        audio_url = generate_narration(text, voice_id, speed)
        audio_path = get_audio_path(dirs, "narration.mp3")
        download_file(audio_url, audio_path)

        # Update narration section
        narration['audioPath'] = audio_path
        narration['voice'] = voice_id
        narration['speed'] = speed

        print(f"\nNarration saved: {audio_path}")
        save_scene_json(json_path, data)

    except Exception as e:
        print(f"ERROR: {e}")
        narration['error'] = str(e)
        save_scene_json(json_path, data)
        raise

    print("\n" + "=" * 50)
    print("Narration generation complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_narration.py <scene.json>")
        print("\nAvailable voices:")
        print(f"  Male: {', '.join(MALE_VOICES)}")
        print(f"  Female: {', '.join(FEMALE_VOICES)}")
        sys.exit(1)

    json_path = sys.argv[1]
    process_scene_json(json_path)
