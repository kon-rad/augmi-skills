#!/usr/bin/env python3
"""
Generate narration audio using Deepgram Aura-2 TTS for short-form video.

Supports 40+ Aura-2 voices with style-based auto-selection.

Usage:
    python generate_audio.py <script_json_path>
    python generate_audio.py <script_json_path> --voice aura-2-orion-en
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
    from scripts.utils import (
        load_script_json, save_script_json, ensure_output_dirs,
        DEFAULT_VOICE, STYLE_VOICES
    )
except ModuleNotFoundError:
    from utils import (
        load_script_json, save_script_json, ensure_output_dirs,
        DEFAULT_VOICE, STYLE_VOICES
    )


DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"
DEEPGRAM_STT_URL = "https://api.deepgram.com/v1/listen"

# Deepgram Aura-2 voices — full catalog
VOICES = {
    # Female voices
    "aura-2-andromeda-en": "Female, warm and engaging",
    "aura-2-asteria-en": "Female, warm and clear (default for educational)",
    "aura-2-athena-en": "Female, confident and polished (default for promotional)",
    "aura-2-cassiopeia-en": "Female, professional and neutral",
    "aura-2-clio-en": "Female, narrative and expressive",
    "aura-2-electra-en": "Female, authoritative and powerful",
    "aura-2-harmonia-en": "Female, smooth and soothing",
    "aura-2-hera-en": "Female, authoritative",
    "aura-2-io-en": "Female, casual and friendly",
    "aura-2-luna-en": "Female, calm and professional",
    "aura-2-lyra-en": "Female, bright and upbeat",
    "aura-2-nova-en": "Female, friendly and approachable",
    "aura-2-pandora-en": "Female, expressive and dramatic",
    "aura-2-selene-en": "Female, soothing and gentle",
    "aura-2-theia-en": "Female, powerful and dynamic",
    "aura-2-venus-en": "Female, elegant and refined",
    "aura-2-vesta-en": "Female, clear and articulate",
    # Male voices
    "aura-2-arcas-en": "Male, energetic (default for hype)",
    "aura-2-arcturus-en": "Male, deep and resonant",
    "aura-2-draco-en": "Male, energetic and bold",
    "aura-2-helios-en": "Male, professional and clear",
    "aura-2-mars-en": "Male, commanding and strong",
    "aura-2-neptune-en": "Male, narrative and calm",
    "aura-2-orion-en": "Male, deep and authoritative",
    "aura-2-orpheus-en": "Male, smooth and rich",
    "aura-2-pegasus-en": "Male, warm and friendly",
    "aura-2-perseus-en": "Male, warm narrator (default for storytelling)",
    "aura-2-phoenix-en": "Male, dynamic and versatile",
    "aura-2-saturn-en": "Male, calm and measured",
    "aura-2-sol-en": "Male, energetic and upbeat",
    "aura-2-titan-en": "Male, authoritative and deep",
    "aura-2-zeus-en": "Male, commanding and powerful",
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
    }
    payload = {"text": text}

    print(f"  Sending {len(text)} characters to Deepgram TTS...")
    print(f"  Voice: {voice}")

    # Deepgram has a 2000 character limit per request — chunk if needed
    if len(text) > 2000:
        print(f"  Text exceeds 2000 chars, chunking into parts...")
        chunks = chunk_text(text, 2000)
        temp_files = []
        for i, chunk in enumerate(chunks):
            chunk_path = output_path.replace('.mp3', f'_chunk{i}.mp3')
            payload_chunk = {"text": chunk}
            response = requests.post(
                DEEPGRAM_TTS_URL, headers=headers, params=params,
                json=payload_chunk, stream=True
            )
            response.raise_for_status()
            with open(chunk_path, 'wb') as f:
                for data in response.iter_content(chunk_size=8192):
                    f.write(data)
            temp_files.append(chunk_path)
            print(f"    Chunk {i+1}/{len(chunks)} done ({len(chunk)} chars)")

        # Concatenate chunks with ffmpeg
        concat_audio_files(temp_files, output_path)
        for tmp in temp_files:
            os.remove(tmp)
    else:
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


def chunk_text(text: str, max_chars: int) -> list:
    """Split text into chunks at sentence boundaries, preserving punctuation."""
    import re
    # Split on sentence boundaries while keeping the terminal punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = f"{current} {sentence}" if current else sentence
        if len(candidate) > max_chars:
            if current:
                chunks.append(current.strip())
                # Handle single sentences longer than max_chars
                if len(sentence) > max_chars:
                    # Hard-split at last space before limit
                    while len(sentence) > max_chars:
                        split_at = sentence.rfind(' ', 0, max_chars)
                        if split_at <= 0:
                            split_at = max_chars
                        chunks.append(sentence[:split_at].strip())
                        sentence = sentence[split_at:].strip()
                current = sentence
            else:
                # Single sentence exceeds limit — hard-split
                while len(sentence) > max_chars:
                    split_at = sentence.rfind(' ', 0, max_chars)
                    if split_at <= 0:
                        split_at = max_chars
                    chunks.append(sentence[:split_at].strip())
                    sentence = sentence[split_at:].strip()
                current = sentence
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    return chunks


def concat_audio_files(file_paths: list, output_path: str) -> str:
    """Concatenate multiple audio files using ffmpeg."""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in file_paths:
            escaped = path.replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")
        list_file = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c:a", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg concat error: {result.stderr[-500:]}")
    finally:
        os.unlink(list_file)

    return output_path


def build_narration_text(script_data: dict) -> str:
    """Build narration from scenes or top-level narration field."""
    narration = script_data.get("narration", {})
    if isinstance(narration, dict) and narration.get("text"):
        return narration["text"].strip()

    parts = []
    for scene in script_data.get("scenes", []):
        narr = scene.get("narration", "").strip()
        if narr:
            parts.append(narr)
    return " ".join(parts)


def get_word_timestamps(audio_path: str, api_key: str) -> list:
    """Send narration audio to Deepgram STT to get word-level timestamps.

    Returns list of dicts: [{"word": "Hello", "start": 0.04, "end": 0.32}, ...]
    """
    print(f"  Extracting word timestamps via Deepgram STT...")

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/mpeg",
    }
    params = {
        "model": "nova-3",
        "smart_format": "true",
        "punctuate": "true",
    }

    with open(audio_path, 'rb') as f:
        audio_data = f.read()

    response = requests.post(
        DEEPGRAM_STT_URL, headers=headers, params=params,
        data=audio_data
    )
    response.raise_for_status()

    result = response.json()

    words = []
    channels = result.get("results", {}).get("channels", [])
    if channels:
        alternatives = channels[0].get("alternatives", [])
        if alternatives:
            for w in alternatives[0].get("words", []):
                words.append({
                    "word": w.get("punctuated_word", w.get("word", "")),
                    "start": w.get("start", 0.0),
                    "end": w.get("end", 0.0),
                })

    print(f"  Extracted {len(words)} word timestamps")
    return words


def main():
    parser = argparse.ArgumentParser(
        description="Generate narration for short-form video (Deepgram Aura-2)"
    )
    parser.add_argument("script_json", nargs="?")
    parser.add_argument("--voice", default=None)
    parser.add_argument("--list-voices", action="store_true")
    args = parser.parse_args()

    if args.list_voices:
        print("Available Deepgram Aura-2 Voices:")
        print("=" * 60)
        print("\nFemale Voices:")
        print("-" * 60)
        for voice_id, desc in sorted(VOICES.items()):
            if "Female" in desc:
                print(f"  {voice_id}: {desc}")
        print("\nMale Voices:")
        print("-" * 60)
        for voice_id, desc in sorted(VOICES.items()):
            if "Male" in desc:
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
    target_duration = script_data.get("targetDuration", 30)
    print(f"\nNarration: {word_count} words (~{estimated_seconds:.0f}s)")
    if estimated_seconds > target_duration * 1.3:
        print(f"  Warning: Narration (~{estimated_seconds:.0f}s) exceeds target ({target_duration}s) by >30%")
        print(f"  Tip: Reduce scene narration or increase --duration")
    elif estimated_seconds < target_duration * 0.5:
        print(f"  Warning: Narration (~{estimated_seconds:.0f}s) is <50% of target ({target_duration}s)")
        print(f"  Tip: Add more narration text or decrease --duration")

    # Pick voice: explicit > style-based > script default > global default
    style = script_data.get("style", "educational")
    voice = args.voice or script_data.get("voice") or STYLE_VOICES.get(style, DEFAULT_VOICE)
    if voice not in VOICES:
        print(f"Warning: Voice '{voice}' not in known catalog (may still work)")

    output_path = os.path.join(dirs['audio'], "narration.mp3")

    try:
        generate_tts(narration_text, voice, api_key, output_path)

        script_data["audioPath"] = output_path
        script_data["voice"] = voice

        # Get word-level timestamps for synced captions
        try:
            word_timestamps = get_word_timestamps(output_path, api_key)
            script_data["wordTimestamps"] = word_timestamps
        except Exception as e:
            print(f"  Warning: Could not get word timestamps: {e}")
            print(f"  Subtitles will use scene-level timing as fallback")

        save_script_json(args.script_json, script_data)

        voice_desc = VOICES.get(voice, "Custom voice")
        print(f"\nNarration complete!")
        print(f"  Voice: {voice} ({voice_desc})")
        print(f"  Words: {word_count}")
        if "wordTimestamps" in script_data:
            print(f"  Word timestamps: {len(script_data['wordTimestamps'])} words synced")

    except requests.exceptions.HTTPError as e:
        print(f"\nDeepgram API error: {e}")
        if e.response is not None:
            print(f"  Response: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
