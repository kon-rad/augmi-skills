#!/usr/bin/env python3
"""Shared utilities for AI Film Maker scripts"""

import json
import os
import re
import requests
from pathlib import Path

def slugify(title: str) -> str:
    """Convert title to URL-friendly slug"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def load_scene_json(path: str) -> dict:
    """Load and validate scene JSON"""
    with open(path, 'r') as f:
        data = json.load(f)

    required_fields = ['title', 'scenes', 'narration', 'config']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    return data

def save_scene_json(path: str, data: dict) -> None:
    """Save updated JSON"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def download_file(url: str, output_path: str) -> str:
    """Download file from URL"""
    response = requests.get(url, stream=True)
    response.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path

def get_output_dirs(base_dir: str, film_slug: str) -> dict:
    """Get output directory paths for a film"""
    film_dir = os.path.join(base_dir, film_slug)
    return {
        'base': film_dir,
        'images': os.path.join(film_dir, 'images'),
        'videos': os.path.join(film_dir, 'videos'),
        'audio': os.path.join(film_dir, 'audio'),
    }

def ensure_output_dirs(base_dir: str, film_slug: str) -> dict:
    """Create output directories for a film"""
    dirs = get_output_dirs(base_dir, film_slug)

    for path in dirs.values():
        os.makedirs(path, exist_ok=True)

    return dirs

def get_image_path(dirs: dict, sub_scene_id: str, swapped: bool = False) -> str:
    """Get path for an image file"""
    suffix = '_swapped' if swapped else '_base'
    return os.path.join(dirs['images'], f"{sub_scene_id}{suffix}.png")

def get_video_path(dirs: dict, sub_scene_id: str) -> str:
    """Get path for a video clip"""
    return os.path.join(dirs['videos'], f"{sub_scene_id}.mp4")

def get_audio_path(dirs: dict, filename: str) -> str:
    """Get path for an audio file"""
    return os.path.join(dirs['audio'], filename)

def get_final_video_path(dirs: dict, film_slug: str) -> str:
    """Get path for final composed video"""
    return os.path.join(dirs['videos'], f"{film_slug}.mp4")

def create_scene_json_template(title: str, base_dir: str = "OUTPUT") -> dict:
    """Create a new scene JSON template"""
    film_slug = slugify(title)
    dirs = get_output_dirs(base_dir, film_slug)

    return {
        "title": title,
        "totalDuration": 30,
        "avatarPath": "IMAGES/avatar/avatar.jpg",
        "config": {
            "voiceId": "am_adam",
            "voiceSpeed": 1.0,
            "musicPrompt": "Epic cinematic orchestral soundtrack",
            "musicVolume": 0.2,
            "narrationVolume": 1.0
        },
        "narration": {
            "text": "",
            "audioPath": get_audio_path(dirs, "narration.mp3"),
            "voice": "am_adam",
            "speed": 1.0
        },
        "scenes": [],
        "output": {
            "filmSlug": film_slug,
            "baseDir": base_dir,
            "imagesDir": dirs['images'],
            "videosDir": dirs['videos'],
            "audioDir": dirs['audio'],
            "finalVideo": get_final_video_path(dirs, film_slug)
        }
    }

if __name__ == "__main__":
    # Test utilities
    print(slugify("The Builders of Tomorrow"))  # builders-of-tomorrow
    print(slugify("My Cool Video! #1"))  # my-cool-video-1
