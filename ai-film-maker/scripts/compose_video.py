#!/usr/bin/env python3
"""Compose final video by concatenating clips and mixing audio"""

import os
import sys
import subprocess
import tempfile
from utils import (
    load_scene_json, save_scene_json,
    get_output_dirs, get_final_video_path
)

def get_video_clips(data: dict) -> list:
    """Get ordered list of video clip paths"""
    clips = []
    for scene in data['scenes']:
        for sub_scene in scene['subScenes']:
            video_path = sub_scene.get('outputVideoPath')
            if video_path and os.path.exists(video_path):
                clips.append(video_path)
    return clips

def concatenate_videos(video_paths: list, output_path: str) -> None:
    """Concatenate video clips using ffmpeg"""
    print(f"Concatenating {len(video_paths)} video clips...")

    # Create concat file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in video_paths:
            f.write(f"file '{path}'\n")
        concat_file = f.name

    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '18',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    finally:
        os.unlink(concat_file)

def compose_final_video(
    video_path: str,
    narration_path: str,
    music_path: str,
    output_path: str,
    narration_volume: float = 1.0,
    music_volume: float = 0.2
) -> None:
    """Compose final video with audio tracks"""
    print(f"Composing final video...")
    print(f"  Narration volume: {narration_volume}")
    print(f"  Music volume: {music_volume}")

    filter_complex = (
        f"[1:a]volume={narration_volume}[narr];"
        f"[2:a]volume={music_volume}[music];"
        f"[narr][music]amix=inputs=2:duration=longest[audio]"
    )

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', narration_path,
        '-i', music_path,
        '-filter_complex', filter_complex,
        '-map', '0:v',
        '-map', '[audio]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]

    subprocess.run(cmd, check=True, capture_output=True)

def process_scene_json(json_path: str) -> None:
    """Compose final video from scene JSON"""
    data = load_scene_json(json_path)

    film_slug = data['output']['filmSlug']
    base_dir = data['output']['baseDir']

    dirs = get_output_dirs(base_dir, film_slug)

    print(f"\nComposing final video: {data['title']}")
    print("-" * 50)

    # Get video clips
    clips = get_video_clips(data)
    if not clips:
        print("ERROR: No video clips found!")
        return

    print(f"Found {len(clips)} video clips")

    # Concatenate videos
    combined_path = os.path.join(dirs['videos'], 'combined.mp4')
    concatenate_videos(clips, combined_path)
    print(f"Combined video: {combined_path}")

    # Get audio paths
    narration_path = data['narration'].get('audioPath')
    music_path = data['output'].get('musicPath') or os.path.join(dirs['audio'], 'music.mp3')

    if not narration_path or not os.path.exists(narration_path):
        print(f"WARNING: Narration not found at {narration_path}")
        narration_path = None

    if not os.path.exists(music_path):
        print(f"WARNING: Music not found at {music_path}")
        music_path = None

    # Compose final video
    final_path = get_final_video_path(dirs, film_slug)

    if narration_path and music_path:
        compose_final_video(
            combined_path,
            narration_path,
            music_path,
            final_path,
            narration_volume=data['config'].get('narrationVolume', 1.0),
            music_volume=data['config'].get('musicVolume', 0.2)
        )
    elif narration_path:
        # Just add narration
        cmd = [
            'ffmpeg', '-y',
            '-i', combined_path,
            '-i', narration_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            final_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    else:
        # Just copy video
        import shutil
        shutil.copy(combined_path, final_path)

    # Update JSON
    data['output']['finalVideo'] = final_path
    data['output']['combinedVideo'] = combined_path
    save_scene_json(json_path, data)

    # Get file size
    size_mb = os.path.getsize(final_path) / (1024 * 1024)

    print("\n" + "=" * 50)
    print(f"Final video complete!")
    print(f"Output: {final_path}")
    print(f"Size: {size_mb:.1f} MB")

    # Clean up combined video
    if os.path.exists(combined_path):
        os.remove(combined_path)
        print("Cleaned up temporary files")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compose_video.py <scene.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    process_scene_json(json_path)
