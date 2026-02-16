#!/usr/bin/env python3
"""
Shared utilities for the Short Video Generator skill.
"""

import json
import os
import re
import requests
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


# Short video constants
PORTRAIT_WIDTH = 1080
PORTRAIT_HEIGHT = 1920
ASPECT_RATIO = "9:16"
DEFAULT_DURATION = 30
SCENE_DURATION = 5  # Each scene is exactly 5 seconds
WORDS_PER_SECOND = 2.5
WORDS_PER_SCENE = 12  # ~12 words fits 5 seconds at 2.5 wps

STYLES = ["educational", "promotional", "storytelling", "hype"]
DEFAULT_STYLE = "educational"

VISUAL_MODES = ["images-web", "images-ai", "video-ai", "mixed"]
DEFAULT_VISUAL_MODE = "mixed"


def slugify(text: str) -> str:
    """Convert text to a URL/filename-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug[:60]


def load_script_json(path: str) -> Dict[str, Any]:
    """Load and validate script JSON from file."""
    with open(path, 'r') as f:
        data = json.load(f)

    required_keys = ['title', 'scenes']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key in script JSON: {key}")

    return data


def save_script_json(path: str, data: Dict[str, Any]) -> None:
    """Save script JSON to file with pretty formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_output_dir(script_path: str) -> str:
    """Derive OUTPUT directory from INPUT script path."""
    input_dir = os.path.dirname(os.path.abspath(script_path))
    output_dir = input_dir.replace('/INPUT/', '/OUTPUT/', 1)
    if output_dir == input_dir:
        output_dir = os.path.join(os.path.dirname(input_dir), 'OUTPUT',
                                  os.path.basename(input_dir))
    return output_dir


def ensure_output_dirs(script_path: str) -> Dict[str, str]:
    """Create output directories and return their paths."""
    output_dir = get_output_dir(script_path)
    dirs = {
        'images': os.path.join(output_dir, 'images'),
        'videos': os.path.join(output_dir, 'videos'),
        'audio': os.path.join(output_dir, 'audio'),
        'video': os.path.join(output_dir, 'video'),
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs


def download_file(url: str, output_path: str, headers: Optional[Dict] = None) -> str:
    """Download file from URL and save to output path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    response = requests.get(url, stream=True, headers=headers or {})
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path


def get_scenes_by_source(script_data: Dict[str, Any], source: str) -> list:
    """Get scenes filtered by imageSource ('web' or 'generate') for backward compat."""
    return [s for s in script_data.get('scenes', [])
            if s.get('imageSource') == source]


def get_scenes_by_visual_type(script_data: Dict[str, Any], visual_type: str) -> list:
    """Get scenes filtered by visualType ('web', 'generate', or 'video')."""
    return [s for s in script_data.get('scenes', [])
            if s.get('visualType') == visual_type]


def scenes_for_duration(duration: int) -> int:
    """Calculate number of 5-second scenes for a target duration."""
    return duration // SCENE_DURATION


def max_words_for_duration(duration: int) -> int:
    """Calculate maximum narration words for a target duration."""
    return int(duration * WORDS_PER_SECOND)


def print_progress(current: int, total: int, message: str) -> None:
    """Print progress indicator."""
    print(f"[{current}/{total}] {message}")


if __name__ == "__main__":
    print("Utils module loaded successfully")
    print(f"  30s video: {scenes_for_duration(30)} scenes, {max_words_for_duration(30)} words")
    print(f"  60s video: {scenes_for_duration(60)} scenes, {max_words_for_duration(60)} words")
