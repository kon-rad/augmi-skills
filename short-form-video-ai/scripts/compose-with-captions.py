#!/usr/bin/env python3
"""
Compose final video with word-synced captions burned-in.
Combines video clips + images (Ken Burns) + narration + music + single-word captions.

Single word at a time, centered, highlighted in cyan. Uses Mulish font.
"""

import os
import sys
import json
import subprocess
import tempfile
import re

PORTRAIT_WIDTH = 1080
PORTRAIT_HEIGHT = 1920
TARGET_FPS = 25

# Font path - Mulish ExtraBold (bundled with skill)
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FONT_PATH = os.path.join(SKILL_DIR, "fonts", "Mulish-ExtraBold.ttf")

# Default watermark path
PROJECT_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
DEFAULT_WATERMARK_PATH = os.path.join(PROJECT_ROOT, "public", "augmi-w-transparent.png")


def get_media_duration(path: str) -> float:
    """Get duration of a media file in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 5.0
    return float(result.stdout.strip())


def escape_ffmpeg_text(text: str) -> str:
    """Escape text for FFmpeg drawtext filter."""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "'\\''")
    text = text.replace(":", "\\:")
    text = text.replace("%", "%%")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    return text


def normalize_video_clip(input_path: str, output_path: str, duration: float = 5.0) -> str:
    """Normalize a video clip to 1080x1920 @ 25fps."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", f"scale={PORTRAIT_WIDTH}:{PORTRAIT_HEIGHT}:force_original_aspect_ratio=decrease,pad={PORTRAIT_WIDTH}:{PORTRAIT_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "23", "-preset", "medium",
        "-r", str(TARGET_FPS),
        "-an",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_path


def create_ken_burns_clip(image_path: str, output_path: str, duration: float = 5.0) -> str:
    """Create a Ken Burns zoom clip from a still image."""
    scale_w = PORTRAIT_WIDTH * 2
    scale_h = PORTRAIT_HEIGHT * 2
    total_frames = int(duration * TARGET_FPS)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-t", str(duration),
        "-vf", (
            f"scale={scale_w}:{scale_h}:force_original_aspect_ratio=decrease,"
            f"pad={scale_w}:{scale_h}:(ow-iw)/2:(oh-ih)/2:black,"
            f"zoompan=z='1+0.15*on/{total_frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={PORTRAIT_WIDTH}x{PORTRAIT_HEIGHT}:fps={TARGET_FPS}"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "23", "-preset", "medium",
        "-an",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_path


def strip_punctuation(text: str) -> str:
    """Remove trailing punctuation from a word."""
    return text.rstrip('.,;:!?')


def generate_subtitle_filters(script_data: dict) -> str:
    """
    Generate FFmpeg drawtext filters for single-word-at-a-time subtitles.

    One word displayed at a time, centered, in cyan with black border.
    Punctuation stripped, uppercase for readability.

    Prevents overlap: each word's display end is clamped to the next word's
    start minus 1ms. Uses gte()*lt() instead of between() so boundaries
    are [start, end) — no frame shows two words simultaneously.
    """
    narration = script_data.get("narration", {})
    words = narration.get("word_timestamps", [])
    if not words:
        print("  No word_timestamps found. Skipping subtitles.")
        return None

    config = script_data.get("config", {})
    font_size = config.get("fontSize", 90)
    highlight_color = config.get("highlightColor", "0x00FFFF")
    font_path = config.get("fontPath", DEFAULT_FONT_PATH)
    shadow_size = config.get("shadowSize", 8)
    caption_y = config.get("captionPosition", 440)

    # Font fallback
    if not os.path.exists(font_path):
        for fallback in [DEFAULT_FONT_PATH, "/Library/Fonts/Raleway-Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
            if os.path.exists(fallback):
                font_path = fallback
                break

    y_pos = PORTRAIT_HEIGHT - caption_y

    filters = []
    overlaps_fixed = 0

    for i, w in enumerate(words):
        w_start_ms = w["start_ms"]
        w_end_ms = w["end_ms"]

        # Clamp end to next word's start to prevent overlap
        if i < len(words) - 1:
            next_start_ms = words[i + 1]["start_ms"]
            if w_end_ms >= next_start_ms:
                w_end_ms = next_start_ms - 1
                overlaps_fixed += 1

        # Skip if duration is too short (< 1 frame at 25fps = 40ms)
        if w_end_ms - w_start_ms < 30:
            continue

        w_start = w_start_ms / 1000.0
        w_end = w_end_ms / 1000.0

        clean_word = strip_punctuation(w["word"]).upper()
        if not clean_word:
            continue

        escaped_word = escape_ffmpeg_text(clean_word)

        # Use gte()*lt() for half-open interval [start, end) — no overlap
        f = (
            f"drawtext=fontfile='{font_path}'"
            f":text='{escaped_word}'"
            f":fontsize={font_size}"
            f":fontcolor={highlight_color}"
            f":borderw={shadow_size}"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y={int(y_pos)}"
            f":enable='gte(t\\,{w_start:.3f})*lt(t\\,{w_end:.3f})'"
        )
        filters.append(f)

    if overlaps_fixed:
        print(f"  Fixed {overlaps_fixed} word boundary overlaps")

    return ",".join(filters)


def generate_watermark_filter(script_data: dict, temp_dir: str) -> tuple:
    """
    Generate FFmpeg overlay filter for watermark in top-right corner.
    Returns (watermark_input_args, filter_string) or ([], None) if no watermark.
    """
    config = script_data.get("config", {})
    watermark_path = config.get("watermarkPath", DEFAULT_WATERMARK_PATH)
    watermark_opacity = config.get("watermarkOpacity", 0.4)
    watermark_width = config.get("watermarkWidth", 320)
    watermark_margin = config.get("watermarkMargin", 100)

    if not watermark_path or not os.path.exists(watermark_path):
        print(f"  No watermark found at {watermark_path}")
        return [], None

    print(f"  Watermark: {watermark_path} (opacity: {watermark_opacity}, width: {watermark_width}px)")

    # Scale watermark and position top-right with margin
    wm_filter = (
        f"[wm]scale={watermark_width}:-1,format=rgba,"
        f"colorchannelmixer=aa={watermark_opacity}[wmscaled];"
        f"[vid][wmscaled]overlay=W-w-{watermark_margin}:{watermark_margin}[watermarked]"
    )

    input_args = ["-i", watermark_path]
    return input_args, wm_filter


def compose_final_video(script_path: str):
    """Compose final video with all components including word-synced subtitles."""
    script_path = os.path.abspath(script_path)

    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found")
        sys.exit(1)

    with open(script_path) as f:
        script = json.load(f)

    base_dir = os.path.dirname(script_path)

    print("\n" + "=" * 60)
    print("Composing Final Video with Single-Word Subtitles (v5)")
    print("=" * 60 + "\n")

    # Step 1: Prepare scene clips
    print("[1/4] Preparing scene clips...")
    temp_clips = []
    temp_dir = tempfile.mkdtemp(prefix="compose_v5_")

    for scene in script.get("scenes", []):
        scene_num = scene["sceneNumber"]
        duration = scene.get("duration", 5)
        video_path = scene.get("videoPath")
        image_path = scene.get("imagePath")
        visual_type = scene.get("visualType", "video")
        temp_clip = os.path.join(temp_dir, f"clip_{scene_num}.mp4")

        if visual_type == "video" and video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            if file_size > 0:
                print(f"  Scene {scene_num}: Normalizing video clip...")
                normalize_video_clip(video_path, temp_clip, duration)
                temp_clips.append(temp_clip)
                continue

        # Fallback to image (Ken Burns)
        if image_path and os.path.exists(image_path):
            print(f"  Scene {scene_num}: Creating Ken Burns from image...")
            create_ken_burns_clip(image_path, temp_clip, duration)
            temp_clips.append(temp_clip)
        else:
            print(f"  Scene {scene_num}: WARNING - No media found, skipping")

    if not temp_clips:
        print("\nError: No clips created")
        sys.exit(1)

    # Step 2: Concatenate clips
    print(f"\n[2/4] Concatenating {len(temp_clips)} clips...")
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip}'\n")

    concat_output = os.path.join(temp_dir, "concat.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "23", "-preset", "medium",
        "-r", str(TARGET_FPS),
        "-an",
        concat_output
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    video_duration = get_media_duration(concat_output)
    print(f"  Concatenated: {video_duration:.1f}s")

    # Step 3: Mix audio
    print("\n[3/4] Mixing audio...")
    narration_path = script.get("audioPath") or script.get("narration", {}).get("audio_path")
    music_path = script.get("musicPath")

    if not narration_path or not os.path.exists(narration_path):
        print(f"  ERROR: Narration not found at {narration_path}")
        sys.exit(1)

    mixed_audio = os.path.join(temp_dir, "mixed.mp3")
    music_vol = script.get("config", {}).get("musicVolume", 0.15)

    if music_path and os.path.exists(music_path):
        cmd = [
            "ffmpeg", "-y",
            "-i", narration_path,
            "-i", music_path,
            "-filter_complex",
            f"[0]volume=1.0[nar];[1]volume={music_vol}[mus];[nar][mus]amix=inputs=2:duration=longest[a]",
            "-map", "[a]",
            "-b:a", "192k",
            mixed_audio
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  Mixed narration + music (music vol: {music_vol})")
    else:
        import shutil
        shutil.copy2(narration_path, mixed_audio)
        print("  Using narration only (no music found)")

    # Step 4: Final compose with subtitles + watermark
    print("\n[4/4] Adding subtitles, watermark, and combining...")
    subtitle_filter = generate_subtitle_filters(script)
    wm_input_args, wm_filter = generate_watermark_filter(script, temp_dir)

    title = script.get("title", "video")
    title_slug = re.sub(r'[^\w\s-]', '', title.lower())
    title_slug = re.sub(r'[-\s]+', '-', title_slug).strip('-')

    # Output to the same parent directory's final/ folder
    parent_dir = os.path.dirname(base_dir)
    final_dir = os.path.join(parent_dir, "final")
    os.makedirs(final_dir, exist_ok=True)
    version = script.get("version", "v5")
    final_output = os.path.join(final_dir, f"{title_slug}_{version}.mp4")

    # Build filter chain: watermark (overlay) + subtitles (drawtext)
    # FFmpeg inputs: [0]=video, [1]=audio, [2]=watermark (if present)
    input_args = ["-i", concat_output, "-i", mixed_audio] + wm_input_args

    if wm_filter and subtitle_filter:
        # Watermark uses overlay (needs filter_complex), then subtitles on top
        # [0:v] = video, [2] = watermark image
        filter_complex = f"[0:v][2]{wm_filter.replace('[vid]', '').replace('[wm]', '')};"
        # But we need proper label routing:
        filter_complex = (
            f"[2]scale={script.get('config', {}).get('watermarkWidth', 320)}:-1,format=rgba,"
            f"colorchannelmixer=aa={script.get('config', {}).get('watermarkOpacity', 0.4)}[wmscaled];"
            f"[0:v][wmscaled]overlay=W-w-{script.get('config', {}).get('watermarkMargin', 100)}"
            f":{script.get('config', {}).get('watermarkMargin', 100)},"
            f"{subtitle_filter}[outv]"
        )
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "1:a:0",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_output
        ]
    elif wm_filter:
        # Watermark only, no subtitles
        filter_complex = (
            f"[2]scale={script.get('config', {}).get('watermarkWidth', 320)}:-1,format=rgba,"
            f"colorchannelmixer=aa={script.get('config', {}).get('watermarkOpacity', 0.4)}[wmscaled];"
            f"[0:v][wmscaled]overlay=W-w-{script.get('config', {}).get('watermarkMargin', 100)}"
            f":{script.get('config', {}).get('watermarkMargin', 100)}[outv]"
        )
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "1:a:0",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_output
        ]
    elif subtitle_filter:
        # Subtitles only, no watermark
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-vf", subtitle_filter,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "23", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            final_output
        ]
    else:
        # No filters
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-c:v", "libx264", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            final_output
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FFmpeg error: {result.stderr[-1000:]}")
        sys.exit(1)

    # Verify
    if os.path.exists(final_output):
        size_mb = os.path.getsize(final_output) / (1024 * 1024)
        duration = get_media_duration(final_output)
        print(f"\n{'=' * 60}")
        print(f"Video composition complete!")
        print(f"  File: {final_output}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Resolution: {PORTRAIT_WIDTH}x{PORTRAIT_HEIGHT}")
        print(f"{'=' * 60}")

    # Cleanup temp
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python compose-with-captions.py <script.json>")
        sys.exit(1)

    compose_final_video(sys.argv[1])


if __name__ == "__main__":
    main()
