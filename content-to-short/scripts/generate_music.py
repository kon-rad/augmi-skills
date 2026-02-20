#!/usr/bin/env python3
"""
Generate background music using Fal.ai CassetteAI for short-form video.

Usage:
    python generate_music.py <script_json_path>
    python generate_music.py <script_json_path> --prompt "custom music description"
    python generate_music.py <script_json_path> --skip-trim

Requirements:
    pip install fal-client python-dotenv
    ffmpeg (for trimming)
"""

import os
import sys
import argparse
import shutil
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import load_script_json, save_script_json, ensure_output_dirs
    from scripts.model_config import get_music_prompt, MUSIC_MODEL
except ModuleNotFoundError:
    from utils import load_script_json, save_script_json, ensure_output_dirs
    from model_config import get_music_prompt, MUSIC_MODEL

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


def get_audio_duration(file_path: str) -> float:
    """Get duration of an audio file using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe error: {result.stderr}")
    return float(result.stdout.strip())


def trim_audio(input_path: str, output_path: str, duration: float) -> str:
    """Trim audio to exact duration with fade-out using ffmpeg."""
    fade_duration = min(1.5, duration * 0.1)
    fade_start = max(0, duration - fade_duration)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-af", f"afade=t=out:st={fade_start}:d={fade_duration}",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg trim error: {result.stderr[-500:]}")
    return output_path


def generate_music(prompt: str, duration: int, output_path: str) -> str:
    """Generate music using Fal.ai Beatoven Maestro."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    model_id = MUSIC_MODEL["model_id"]
    api_duration = max(5, min(150, duration))

    print(f"  Model: {model_id}")
    print(f"  Prompt: {prompt[:80]}...")
    print(f"  Duration: {api_duration}s")

    result = fal_client.subscribe(
        model_id,
        arguments={
            "prompt": prompt,
            "duration": api_duration,
        },
    )

    audio_url = None
    if result:
        # Beatoven returns result["audio"]["url"]
        if "audio" in result and isinstance(result["audio"], dict) and "url" in result["audio"]:
            audio_url = result["audio"]["url"]
        # Fallback for other models: result["audio_file"]["url"]
        elif "audio_file" in result and "url" in result["audio_file"]:
            audio_url = result["audio_file"]["url"]
    if not audio_url:
        raise RuntimeError(f"No music generated. Response: {result}")

    import requests
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size = os.path.getsize(output_path)
    print(f"  Music saved: {output_path} ({file_size / 1024:.1f} KB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate background music for short-form video"
    )
    parser.add_argument("script_json", help="Path to script.json")
    parser.add_argument("--prompt", default=None,
                        help="Custom music prompt (overrides style-based)")
    parser.add_argument("--skip-trim", action="store_true",
                        help="Don't trim music to video length")
    args = parser.parse_args()

    get_api_key()

    print(f"Loading script from {args.script_json}...")
    script_data = load_script_json(args.script_json)
    dirs = ensure_output_dirs(args.script_json)

    target_duration = script_data.get("targetDuration", 30)
    style = script_data.get("style", "educational")

    music_prompt = args.prompt
    if not music_prompt:
        config = script_data.get("config", {})
        music_prompt = config.get("musicPrompt") or get_music_prompt(style)

    output_path = os.path.join(dirs['audio'], "music_raw.mp3")
    final_path = os.path.join(dirs['audio'], "music.mp3")

    print(f"\nGenerating background music...")
    print("-" * 50)

    try:
        generate_music(music_prompt, target_duration, output_path)

        if not args.skip_trim:
            music_duration = get_audio_duration(output_path)
            if music_duration > target_duration + 1:
                print(f"\n  Trimming from {music_duration:.1f}s to {target_duration}s...")
                trim_audio(output_path, final_path, target_duration)
                os.remove(output_path)
            else:
                shutil.move(output_path, final_path)
        else:
            shutil.move(output_path, final_path)

        script_data["musicPath"] = final_path
        save_script_json(args.script_json, script_data)

        final_duration = get_audio_duration(final_path)
        print(f"\nMusic complete!")
        print(f"  Duration: {final_duration:.1f}s")
        print(f"  Style: {style}")
        print(f"  Output: {final_path}")

    except Exception as e:
        print(f"\nError generating music: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
