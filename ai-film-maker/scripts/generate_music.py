#!/usr/bin/env python3
"""Generate background music using Fal.ai MiniMax Music"""

import os
import sys
import subprocess
import fal_client
from utils import (
    load_scene_json, save_scene_json, download_file,
    get_output_dirs, ensure_output_dirs, get_audio_path
)

def generate_music(prompt: str) -> str:
    """Generate music from prompt using ACE-Step"""
    print(f"Generating music: {prompt[:80]}...")

    result = fal_client.subscribe(
        "fal-ai/ace-step/prompt-to-audio",
        arguments={
            "prompt": prompt,
            "duration": 35
        },
        with_logs=True
    )

    return result['audio']['url']

def trim_audio(input_path: str, output_path: str, duration: int) -> None:
    """Trim audio to specified duration using ffmpeg"""
    print(f"Trimming audio to {duration} seconds...")

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-b:a', '192k',
        output_path
    ]

    subprocess.run(cmd, check=True, capture_output=True)

def process_scene_json(json_path: str) -> None:
    """Generate music from scene JSON"""
    data = load_scene_json(json_path)

    film_slug = data['output']['filmSlug']
    base_dir = data['output']['baseDir']
    total_duration = data.get('totalDuration', 30)

    dirs = ensure_output_dirs(base_dir, film_slug)

    print(f"\nGenerating music for: {data['title']}")
    print("-" * 50)

    music_prompt = data['config'].get('musicPrompt', 'Cinematic orchestral soundtrack')

    try:
        audio_url = generate_music(music_prompt)

        # Download raw music
        raw_path = get_audio_path(dirs, "music_raw.mp3")
        download_file(audio_url, raw_path)
        print(f"Raw music saved: {raw_path}")

        # Trim to video duration
        trimmed_path = get_audio_path(dirs, "music.mp3")
        trim_audio(raw_path, trimmed_path, total_duration)
        print(f"Trimmed music saved: {trimmed_path}")

        # Update JSON
        data['output']['musicPath'] = trimmed_path
        data['output']['musicRawPath'] = raw_path
        save_scene_json(json_path, data)

    except Exception as e:
        print(f"ERROR: {e}")
        data['output']['musicError'] = str(e)
        save_scene_json(json_path, data)
        raise

    print("\n" + "=" * 50)
    print("Music generation complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_music.py <scene.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    process_scene_json(json_path)
