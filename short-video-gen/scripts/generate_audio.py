#!/usr/bin/env python3
"""
Generate narration audio using Deepgram TTS for short-form video.

Usage:
    python generate_audio.py <script_json_path>
    python generate_audio.py <script_json_path> --voice aura-arcas-en
    python generate_audio.py --list-voices

Requirements:
    pip install requests python-dotenv
"""

import os
import sys
import argparse
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import load_script_json, save_script_json, ensure_output_dirs
except ModuleNotFoundError:
    from utils import load_script_json, save_script_json, ensure_output_dirs


DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"

VOICES = {
    "aura-asteria-en": "Female, warm and clear (default)",
    "aura-luna-en": "Female, calm and professional",
    "aura-athena-en": "Female, confident",
    "aura-hera-en": "Female, authoritative",
    "aura-orion-en": "Male, deep and authoritative",
    "aura-arcas-en": "Male, energetic (great for hype)",
    "aura-perseus-en": "Male, warm narrator",
    "aura-orpheus-en": "Male, smooth",
    "aura-helios-en": "Male, professional",
    "aura-zeus-en": "Male, commanding",
}

DEFAULT_VOICE = "aura-asteria-en"

# Style-to-voice recommendations
STYLE_VOICES = {
    "educational": "aura-asteria-en",
    "promotional": "aura-athena-en",
    "storytelling": "aura-perseus-en",
    "hype": "aura-arcas-en",
}


def get_api_key() -> str:
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPGRAM_API_KEY not found.\n"
            "Get your key at: https://console.deepgram.com"
        )
    return api_key


def generate_tts(text: str, voice: str, api_key: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    params = {
        "model": voice,
        "encoding": "mp3",
        "container": "none",
    }
    payload = {"text": text}

    print(f"  Sending {len(text)} characters to Deepgram TTS...")
    print(f"  Voice: {voice}")

    response = requests.post(
        DEEPGRAM_TTS_URL, headers=headers, params=params,
        json=payload, stream=True
    )
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size = os.path.getsize(output_path)
    print(f"  Audio saved: {output_path} ({file_size / 1024:.1f} KB)")
    return output_path


def build_narration_text(script_data: dict) -> str:
    """Build narration from scenes or top-level narration field."""
    # Prefer top-level narration text if available
    narration = script_data.get("narration", {})
    if isinstance(narration, dict) and narration.get("text"):
        return narration["text"].strip()

    # Fallback: concatenate scene narrations
    parts = []
    for scene in script_data.get("scenes", []):
        narr = scene.get("narration", "").strip()
        if narr:
            parts.append(narr)
    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Generate narration for short-form video"
    )
    parser.add_argument("script_json", nargs="?")
    parser.add_argument("--voice", default=None)
    parser.add_argument("--list-voices", action="store_true")
    args = parser.parse_args()

    if args.list_voices:
        print("Available Deepgram Aura Voices:")
        print("-" * 50)
        for voice_id, desc in VOICES.items():
            print(f"  {voice_id}: {desc}")
        print(f"\nStyle recommendations:")
        for style, voice in STYLE_VOICES.items():
            print(f"  {style} -> {voice}")
        sys.exit(0)

    if not args.script_json:
        parser.error("script_json is required (unless using --list-voices)")

    api_key = get_api_key()

    print(f"Loading script from {args.script_json}...")
    script_data = load_script_json(args.script_json)
    dirs = ensure_output_dirs(args.script_json)

    narration_text = build_narration_text(script_data)
    if not narration_text:
        print("Error: No narration text found")
        sys.exit(1)

    word_count = len(narration_text.split())
    estimated_seconds = word_count / 2.5
    print(f"\nNarration: {word_count} words (~{estimated_seconds:.0f}s)")

    # Pick voice: explicit > style-based > script default > global default
    style = script_data.get("style", "educational")
    voice = args.voice or script_data.get("voice") or STYLE_VOICES.get(style, DEFAULT_VOICE)
    if voice not in VOICES:
        print(f"Warning: Unknown voice '{voice}', using '{DEFAULT_VOICE}'")
        voice = DEFAULT_VOICE

    output_path = os.path.join(dirs['audio'], "narration.mp3")

    try:
        generate_tts(narration_text, voice, api_key, output_path)

        script_data["audioPath"] = output_path
        script_data["voice"] = voice
        save_script_json(args.script_json, script_data)

        print(f"\nNarration complete!")
        print(f"  Voice: {voice} ({VOICES[voice]})")
        print(f"  Words: {word_count}")

    except requests.exceptions.HTTPError as e:
        print(f"\nDeepgram API error: {e}")
        if e.response is not None:
            print(f"  Response: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
