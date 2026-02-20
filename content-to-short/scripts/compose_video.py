#!/usr/bin/env python3
"""
Compose short-form vertical video (1080x1920) from scene clips and audio.

Handles mixed visual types:
- "web" scenes: Creates Ken Burns zoom from still images
- "video" scenes: Uses pre-generated AI video clips
- "generate" scenes: Creates Ken Burns zoom from AI-generated images

Supports optional subtitle burning (SRT/ASS via FFmpeg).
Mixes narration + background music into the final output.

Usage:
    python compose_video.py <script_json_path>
    python compose_video.py <script_json_path> --subtitles
    python compose_video.py <script_json_path> --no-music

Requirements:
    - ffmpeg (brew install ffmpeg)
"""

import os
import sys
import argparse
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import (
        load_script_json, save_script_json, ensure_output_dirs, slugify,
        PORTRAIT_WIDTH, PORTRAIT_HEIGHT, WORDS_PER_SECOND
    )
except ModuleNotFoundError:
    from utils import (
        load_script_json, save_script_json, ensure_output_dirs, slugify,
        PORTRAIT_WIDTH, PORTRAIT_HEIGHT, WORDS_PER_SECOND
    )


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg not found. Install with: brew install ffmpeg")
        sys.exit(1)


def get_media_duration(file_path: str) -> float:
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


_KB_DIRECTIONS = [
    # zoom in center
    "z='min(zoom+0.001,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    # zoom out center
    "z='if(eq(on,1),1.15,max(zoom-0.001,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    # pan left to right
    "z='1.10':x='(iw-iw/zoom)*on/({frames})':y='ih/2-(ih/zoom/2)'",
    # pan top to bottom
    "z='1.10':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/({frames})'",
]


def create_ken_burns_clip(image_path: str, duration: float, output_path: str,
                          width: int = PORTRAIT_WIDTH,
                          height: int = PORTRAIT_HEIGHT,
                          scene_index: int = 0) -> str:
    """Create a vertical video clip with Ken Burns zoom for short-form energy."""
    frames = int(duration * 25)
    direction = _KB_DIRECTIONS[scene_index % len(_KB_DIRECTIONS)]
    direction = direction.replace("{frames}", str(frames))
    filter_complex = (
        f"scale={width * 2}:{height * 2},"
        f"zoompan={direction}"
        f":d={frames}:s={width}x{height}:fps=25"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", filter_complex,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr[-500:]}")
    return output_path


def normalize_video_clip(video_path: str, output_path: str,
                         width: int = PORTRAIT_WIDTH,
                         height: int = PORTRAIT_HEIGHT) -> str:
    """Normalize an AI-generated video clip to match our format."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
               f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-r", "25",
        "-an",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg normalize error: {result.stderr[-500:]}")
    return output_path


def concatenate_videos(video_paths: list, output_path: str) -> str:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in video_paths:
            escaped_path = path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
        list_file = f.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg concat error: {result.stderr[-500:]}")
    finally:
        os.unlink(list_file)

    return output_path


def generate_srt(scenes: list, scale_factor: float, output_path: str) -> str:
    """Generate SRT subtitle file from scene narrations with timestamps."""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    lines = []
    current_time = 0.0
    subtitle_index = 0

    for scene in scenes:
        narration = scene.get("narration", "").strip()
        if not narration:
            current_time += scene.get("duration", 5) * scale_factor
            continue

        duration = scene.get("duration", 5) * scale_factor
        start = current_time
        end = current_time + duration
        subtitle_index += 1

        start_str = format_srt_time(start)
        end_str = format_srt_time(end)

        lines.append(f"{subtitle_index}")
        lines.append(f"{start_str} --> {end_str}")
        lines.append(narration)
        lines.append("")

        current_time = end

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"  Subtitles saved: {output_path}")
    return output_path


def format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_ass(scenes: list, scale_factor: float, output_path: str,
                 width: int = PORTRAIT_WIDTH, height: int = PORTRAIT_HEIGHT) -> str:
    """Generate ASS subtitle file with styled text for video burning."""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    # ASS header with styling optimized for vertical video
    font_size = 48
    margin_bottom = 120
    outline = 3

    header = f"""[Script Info]
Title: Short Video Subtitles
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},1,2,40,40,{margin_bottom},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    current_time = 0.0

    for scene in scenes:
        narration = scene.get("narration", "").strip()
        if not narration:
            current_time += scene.get("duration", 5) * scale_factor
            continue

        duration = scene.get("duration", 5) * scale_factor
        start = current_time
        end = current_time + duration

        start_str = format_ass_time(start)
        end_str = format_ass_time(end)

        # Word wrap long narrations
        if len(narration) > 40:
            words = narration.split()
            mid = len(words) // 2
            narration = ' '.join(words[:mid]) + '\\N' + ' '.join(words[mid:])

        events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{narration}")
        current_time = end

    with open(output_path, 'w') as f:
        f.write(header)
        f.write('\n'.join(events))
        f.write('\n')

    print(f"  ASS subtitles saved: {output_path}")
    return output_path


def generate_ass_word_synced(word_timestamps: list, output_path: str,
                              words_per_chunk: int = 3,
                              width: int = PORTRAIT_WIDTH,
                              height: int = PORTRAIT_HEIGHT) -> str:
    """Generate ASS subtitles with word-synced chunks (TikTok/Reels style).

    Groups words into chunks of `words_per_chunk` and creates one Dialogue
    event per chunk, timed to the actual speech.
    """
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    font_size = 140
    margin_bottom = 450
    outline = 8

    header = f"""[Script Info]
Title: Word-Synced Subtitles
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Raleway,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},1,2,60,60,{margin_bottom},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []

    # Group words into chunks
    chunks = []
    for i in range(0, len(word_timestamps), words_per_chunk):
        chunk_words = word_timestamps[i:i + words_per_chunk]
        if not chunk_words:
            continue
        chunks.append({
            "text": " ".join(w["word"] for w in chunk_words),
            "start": chunk_words[0]["start"],
            "end": chunk_words[-1]["end"],
        })

    for chunk in chunks:
        start_str = format_ass_time(chunk["start"])
        end_str = format_ass_time(chunk["end"])
        text = chunk["text"]
        events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

    with open(output_path, 'w') as f:
        f.write(header)
        f.write('\n'.join(events))
        f.write('\n')

    print(f"  Word-synced ASS saved: {output_path} ({len(chunks)} chunks)")
    return output_path


def format_ass_time(seconds: float) -> str:
    """Format seconds as ASS timestamp H:MM:SS.cc."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def burn_subtitles(video_path: str, ass_path: str, output_path: str) -> str:
    """Burn ASS subtitles into video using FFmpeg."""
    escaped_ass = ass_path.replace("'", "'\\''").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"ass='{escaped_ass}'",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg subtitle burn error: {result.stderr[-500:]}")
    return output_path


def mix_audio_tracks(video_path: str, narration_path: str, music_path: str,
                     output_path: str, narration_volume: float = 1.0,
                     music_volume: float = 0.15) -> str:
    """Mix narration + background music with the video."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", narration_path,
        "-i", music_path,
        "-filter_complex",
        f"[1:a]volume={narration_volume}[narr];"
        f"[2:a]volume={music_volume}[music];"
        f"[narr][music]amix=inputs=2:duration=shortest[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio mix error: {result.stderr[-500:]}")
    return output_path


def add_narration_only(video_path: str, narration_path: str, output_path: str) -> str:
    """Add only narration audio (no music)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", narration_path,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio error: {result.stderr[-500:]}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Compose vertical short-form video with optional subtitles"
    )
    parser.add_argument("script_json", help="Path to script.json")
    parser.add_argument("--no-music", action="store_true",
                        help="Don't include background music")
    parser.add_argument("--subtitles", action="store_true",
                        help="Burn subtitles into the video")
    parser.add_argument("--no-subtitles", action="store_true",
                        help="Disable subtitles (overrides script.json setting)")
    args = parser.parse_args()

    check_ffmpeg()

    print(f"Loading script from {args.script_json}...")
    script_data = load_script_json(args.script_json)
    dirs = ensure_output_dirs(args.script_json)

    scenes = script_data.get("scenes", [])
    if not scenes:
        print("Error: No scenes found")
        sys.exit(1)

    # CLI flags always win: --no-subtitles overrides script.json
    if args.no_subtitles:
        enable_subtitles = False
    elif args.subtitles:
        enable_subtitles = True
    else:
        enable_subtitles = script_data.get("subtitles", False)

    narration_path = script_data.get("audioPath")
    if not narration_path or not os.path.exists(narration_path):
        print("Error: Narration audio not found. Run generate_audio.py first.")
        sys.exit(1)

    music_path = script_data.get("musicPath")
    has_music = music_path and os.path.exists(music_path) and not args.no_music

    config = script_data.get("config", {})
    narration_volume = config.get("narrationVolume", 1.0)
    music_volume = config.get("musicVolume", 0.15)

    audio_duration = get_media_duration(narration_path)
    print(f"Narration duration: {audio_duration:.1f}s")
    if has_music:
        music_duration = get_media_duration(music_path)
        print(f"Music duration: {music_duration:.1f}s")

    # Scale scene durations to match narration audio
    total_scripted = sum(s.get("duration", 5) for s in scenes)
    scale_factor = audio_duration / total_scripted if total_scripted > 0 else 1.0

    print(f"\nCreating {len(scenes)} vertical scene clips ({PORTRAIT_WIDTH}x{PORTRAIT_HEIGHT})...")
    print("-" * 50)

    temp_clips = []
    for i, scene in enumerate(scenes):
        scene_num = scene["sceneNumber"]
        visual_type = scene.get("visualType", scene.get("imageSource", "web"))
        duration = scene.get("duration", 5) * scale_factor

        clip_path = os.path.join(dirs['video'], f"clip-{scene_num}.mp4")

        print(f"  [{i+1}/{len(scenes)}] Scene {scene_num}: {duration:.1f}s ({visual_type})")

        try:
            if visual_type == "video":
                video_path = scene.get("videoPath")
                if video_path and os.path.exists(video_path):
                    normalize_video_clip(video_path, clip_path)
                    temp_clips.append(clip_path)
                else:
                    image_path = scene.get("imagePath")
                    if image_path and os.path.exists(image_path):
                        print(f"    (video not found, using Ken Burns fallback)")
                        create_ken_burns_clip(image_path, duration, clip_path, scene_index=i)
                        temp_clips.append(clip_path)
                    else:
                        print(f"    No video or image found, skipping")
            else:
                image_path = scene.get("imagePath")
                if image_path and os.path.exists(image_path):
                    create_ken_burns_clip(image_path, duration, clip_path, scene_index=i)
                    temp_clips.append(clip_path)
                else:
                    print(f"    Image not found, skipping")
        except Exception as e:
            print(f"    Error: {e}")

    if not temp_clips:
        print("\nError: No clips created")
        sys.exit(1)

    print(f"\nConcatenating {len(temp_clips)} clips...")
    slug = slugify(script_data.get("title", "short"))
    combined_path = os.path.join(dirs['video'], "combined.mp4")
    concatenate_videos(temp_clips, combined_path)

    # Add audio
    audio_path = os.path.join(dirs['video'], "with-audio.mp4")
    if has_music:
        print("Mixing narration + background music...")
        print(f"  Narration volume: {narration_volume}")
        print(f"  Music volume: {music_volume}")
        mix_audio_tracks(combined_path, narration_path, music_path,
                         audio_path, narration_volume, music_volume)
    else:
        print("Adding narration...")
        add_narration_only(combined_path, narration_path, audio_path)

    # Burn subtitles if enabled
    final_path = os.path.join(dirs['video'], f"{slug}.mp4")
    if enable_subtitles:
        print("\nGenerating and burning subtitles...")
        srt_path = os.path.join(dirs['video'], "subtitles.srt")
        ass_path = os.path.join(dirs['video'], "subtitles.ass")

        word_timestamps = script_data.get("wordTimestamps")
        if word_timestamps:
            print("  Using word-level synced captions")
            generate_ass_word_synced(word_timestamps, ass_path)
        else:
            print("  Using scene-level captions (no word timestamps)")
            generate_ass(scenes, scale_factor, ass_path)

        generate_srt(scenes, scale_factor, srt_path)
        burn_subtitles(audio_path, ass_path, final_path)
        os.remove(audio_path)
    else:
        import shutil
        shutil.move(audio_path, final_path)

    final_duration = get_media_duration(final_path)

    # Cleanup
    for clip in temp_clips:
        if os.path.exists(clip):
            os.remove(clip)
    if os.path.exists(combined_path):
        os.remove(combined_path)

    script_data["outputVideo"] = final_path
    script_data["actualDuration"] = final_duration
    save_script_json(args.script_json, script_data)

    print(f"\n{'=' * 50}")
    print(f"Short video complete!")
    print(f"  Output: {final_path}")
    print(f"  Duration: {final_duration:.1f}s")
    print(f"  Format: {PORTRAIT_WIDTH}x{PORTRAIT_HEIGHT} (9:16 vertical)")
    print(f"  Style: {script_data.get('style', 'N/A')}")
    print(f"  Audio: narration" + (" + music" if has_music else ""))
    print(f"  Subtitles: {'burned in' if enable_subtitles else 'off'}")


if __name__ == "__main__":
    main()
