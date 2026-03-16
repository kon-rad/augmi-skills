#!/usr/bin/env python3
"""
Generate FFmpeg drawtext subtitle filters from Deepgram word timestamps.
Creates per-frame subtitle overlays with word-synced highlighting.
"""

import os
import sys
import json

def generate_subtitle_filters(script_path: str, fps: float = 30.0) -> str:
    """
    Generate FFmpeg drawtext filter commands for word-synced subtitles.
    Returns complete filter chain for burning subtitles into video.
    """
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found")
        sys.exit(1)

    with open(script_path) as f:
        script = json.load(f)

    # Get word timestamps from narration
    narration = script.get("narration", {})
    word_timestamps = narration.get("word_timestamps", [])

    if not word_timestamps:
        print("Error: No word_timestamps found in narration")
        print("Run tts-narration.py first to generate timestamps")
        sys.exit(1)

    # Get config
    config = script.get("config", {})
    font_path = config.get("fontPath", "/Library/Fonts/Raleway-Bold.ttf")
    font_size = config.get("fontSize", 70)
    base_color = config.get("fontColor", "white")
    highlight_color = config.get("highlightColor", "0x00FFFF")
    shadow_size = config.get("shadowSize", 8)

    print("\n" + "="*60)
    print("Generating Subtitle Filters from Deepgram Timestamps")
    print("="*60 + "\n")

    filters = []

    # Process each word and create time-based filter
    for i, word_data in enumerate(word_timestamps):
        word = word_data["word"]
        start_ms = word_data["start_ms"]
        end_ms = word_data["end_ms"]

        # Convert milliseconds to seconds for FFmpeg
        start_sec = start_ms / 1000.0
        end_sec = end_ms / 1000.0

        # Build context (previous, current, next word)
        prev_word = word_timestamps[i-1]["word"] if i > 0 else ""
        next_word = word_timestamps[i+1]["word"] if i < len(word_timestamps) - 1 else ""

        context_text = f"{prev_word} [{word}] {next_word}".strip()

        # Create filter for this word's duration
        # Current word in highlight color, others in base color
        # For simplicity, we'll create one filter per word showing the context

        filter_expr = (
            f"drawtext="
            f"fontfile='{font_path}':"
            f"fontsize={font_size}:"
            f"fontcolor={base_color}:"
            f"borderw={shadow_size}:"
            f"bordercolor=black:"
            f"shadowx=4:shadowy=4:"
            f"x='(w-text_w)/2':"
            f"y='h-80':"
            f"text='{context_text}':"
            f"enable='between(t,{start_sec},{end_sec})'"
        )

        filters.append(filter_expr)

    # Combine all filters with comma separator
    combined_filter = ",".join(filters)

    # Save filter chain to file
    output_dir = os.path.dirname(script_path)
    filter_file = os.path.join(output_dir, "subtitles", "ffmpeg-filters.txt")
    os.makedirs(os.path.dirname(filter_file), exist_ok=True)

    with open(filter_file, 'w') as f:
        f.write(combined_filter)

    print(f"✓ Generated {len(word_timestamps)} subtitle filters")
    print(f"✓ Saved to: {filter_file}")
    print(f"\nFilter Chain Preview (first 200 chars):")
    print(f"  {combined_filter[:200]}...")

    # Also save as JSON for easier processing
    json_file = os.path.join(output_dir, "subtitles", "subtitle-timing.json")
    timing_data = {
        "total_words": len(word_timestamps),
        "fps": fps,
        "words": word_timestamps,
        "ffmpeg_filter_length": len(combined_filter)
    }

    with open(json_file, 'w') as f:
        json.dump(timing_data, f, indent=2)

    print(f"✓ Saved timing data to: {json_file}")

    return combined_filter

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-subtitle-filters.py <script.json>")
        sys.exit(1)

    script_path = sys.argv[1]

    print("\n" + "="*60)
    print("Deepgram Subtitle Filter Generator")
    print("="*60)

    filter_chain = generate_subtitle_filters(script_path)

    print("\n✅ Subtitle filters generated successfully!")
    print(f"\nTotal filter chain length: {len(filter_chain)} characters")
    print("\nNext: Use this filter with FFmpeg:")
    print("  ffmpeg -i video.mp4 -vf '<filter_chain>' output.mp4")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
