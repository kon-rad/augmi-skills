#!/usr/bin/env python3
"""
Generate TTS narration with word-level timestamps using Deepgram.
Extracts word timing data for caption synchronization.
"""

import os
import sys
import json
import requests

def get_api_key() -> str:
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPGRAM_API_KEY not found.\n"
            "Get your key at: https://console.deepgram.com"
        )
    return api_key

def generate_tts_with_timestamps(text: str, voice: str, api_key: str, output_dir: str) -> dict:
    """
    Generate TTS using Deepgram and extract word-level timestamps.
    Returns dict with timing data for caption sync.
    """
    os.makedirs(output_dir, exist_ok=True)

    url = "https://api.deepgram.com/v1/speak"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    params = {
        "model": voice,
        "encoding": "mp3",
    }
    payload = {"text": text}

    print(f"  Generating narration: {len(text)} characters")
    print(f"  Voice: {voice}")

    # Generate audio
    response = requests.post(url, headers=headers, params=params, json=payload, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"Deepgram API error: {response.status_code} - {response.text}")

    audio_path = os.path.join(output_dir, "narration.mp3")
    with open(audio_path, 'wb') as f:
        f.write(response.content)
    print(f"  Audio saved: {audio_path}")

    # Use Deepgram STT to get accurate word-level timestamps from the generated audio
    print(f"  Transcribing for word-level timestamps...")
    stt_url = "https://api.deepgram.com/v1/listen"
    stt_headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/mp3",
    }
    stt_params = {
        "model": "nova-2",
        "smart_format": "true",
        "punctuate": "true",
    }

    with open(audio_path, 'rb') as af:
        stt_response = requests.post(stt_url, headers=stt_headers, params=stt_params, data=af)

    word_timestamps = []
    total_duration_ms = 0

    if stt_response.status_code == 200:
        stt_data = stt_response.json()
        stt_words = stt_data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("words", [])
        duration_sec = stt_data.get("metadata", {}).get("duration", 0)
        total_duration_ms = int(duration_sec * 1000) if duration_sec else 0

        # Map STT words back to original narration words for correct spelling
        original_words = text.split()
        orig_idx = 0

        for stt_word in stt_words:
            start_ms = int(stt_word["start"] * 1000)
            end_ms = int(stt_word["end"] * 1000)

            # Use original word spelling when indices align
            if orig_idx < len(original_words):
                display_word = original_words[orig_idx]
                orig_idx += 1
            else:
                display_word = stt_word["word"]

            word_timestamps.append({
                "word": display_word,
                "start_ms": start_ms,
                "end_ms": end_ms
            })

        if not total_duration_ms and word_timestamps:
            total_duration_ms = word_timestamps[-1]["end_ms"]

        print(f"  STT timestamps: {len(word_timestamps)} words, {total_duration_ms/1000:.1f}s")
    else:
        print(f"  WARNING: STT failed ({stt_response.status_code}), falling back to estimation")
        # Fallback: estimate based on actual audio duration
        import subprocess
        probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        actual_duration_s = float(probe_result.stdout.strip()) if probe_result.returncode == 0 else 30.0

        words = text.split()
        total_duration_ms = int(actual_duration_s * 1000)
        avg_ms_per_word = total_duration_ms / len(words)
        current_time_ms = 0
        for word in words:
            start_ms = int(current_time_ms)
            weight = max(0.5, len(word) / 5.0)
            duration_ms = avg_ms_per_word * weight
            end_ms = int(start_ms + duration_ms)
            word_timestamps.append({"word": word, "start_ms": start_ms, "end_ms": end_ms})
            current_time_ms = end_ms
        # Scale to fit actual duration
        scale = total_duration_ms / current_time_ms if current_time_ms > 0 else 1.0
        for w in word_timestamps:
            w["start_ms"] = int(w["start_ms"] * scale)
            w["end_ms"] = int(w["end_ms"] * scale)

    # Save timing data
    timing_data = {
        "duration_ms": total_duration_ms,
        "word_count": len(word_timestamps),
        "words": word_timestamps
    }

    timing_path = os.path.join(output_dir, "narration.json")
    with open(timing_path, 'w') as f:
        json.dump(timing_data, f, indent=2)
    print(f"  Timing data saved: {timing_path}")
    print(f"  Total duration: {total_duration_ms / 1000:.1f}s ({len(word_timestamps)} words)")

    return timing_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python tts-narration.py <script.json>")
        sys.exit(1)

    script_path = sys.argv[1]
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found")
        sys.exit(1)

    with open(script_path) as f:
        script = json.load(f)

    api_key = get_api_key()

    # Get voice from script config or use default
    voice = script.get("voice", "aura-luna-en")
    narration_text = script.get("narration", {}).get("text", "")

    if not narration_text:
        print("Error: No narration text found in script")
        sys.exit(1)

    # Determine output directory (same as script location)
    output_dir = os.path.dirname(script_path)
    audio_dir = os.path.join(output_dir, "audio")

    print("\n" + "="*50)
    print("Generating TTS Narration with Timestamps")
    print("="*50 + "\n")

    timing_data = generate_tts_with_timestamps(narration_text, voice, api_key, audio_dir)

    # Update script.json with timing data
    script["narration"]["duration_ms"] = timing_data["duration_ms"]
    script["narration"]["word_timestamps"] = timing_data["words"]

    with open(script_path, 'w') as f:
        json.dump(script, f, indent=2)

    print("\n✅ Narration generation complete!")
    print(f"   Duration: {timing_data['duration_ms'] / 1000:.1f}s")
    print(f"   Words: {timing_data['word_count']}")

if __name__ == "__main__":
    main()
