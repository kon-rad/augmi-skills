#!/usr/bin/env python3
"""
Shared utilities for the Content-to-Short Video Generator skill.
"""

import json
import os
import re
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
MIN_DURATION = 30
MAX_DURATION = 90
SCENE_DURATION = 5  # Each scene is exactly 5 seconds
WORDS_PER_SECOND = 2.5
WORDS_PER_SCENE = 12  # ~12 words fits 5 seconds at 2.5 wps

STYLES = ["educational", "promotional", "storytelling", "hype"]
DEFAULT_STYLE = "educational"

VISUAL_MODES = ["images-web", "images-ai", "video-ai", "mixed"]
DEFAULT_VISUAL_MODE = "mixed"

# Voice constants (single source of truth)
DEFAULT_VOICE = "aura-2-asteria-en"

STYLE_VOICES = {
    "educational": "aura-2-asteria-en",
    "promotional": "aura-2-athena-en",
    "storytelling": "aura-2-perseus-en",
    "hype": "aura-2-arcas-en",
}

# Stop words filtered from image search queries
IMAGE_QUERY_STOP_WORDS = {
    'the', 'a', 'an', 'of', 'in', 'at', 'to', 'for', 'on', 'and', 'or',
    'but', 'is', 'are', 'was', 'were', 'with', 'from', 'by', 'as', 'its',
    'this', 'that', 'how', 'what', 'when', 'where', 'why', 'which',
}

# Sections to exclude when parsing scripts/content
SKIP_SECTIONS = {
    'VIDEO DESCRIPTION', 'THUMBNAIL IDEAS', 'CALL TO ACTION', 'HOOKS',
    'B-ROLL LIST', 'MUSIC CUE', 'SEO TAGS', 'REFERENCES', 'CREDITS',
    'DESCRIPTION', 'TAGS', 'KEYWORDS',
}


def assign_visual_types(scenes: list, visual_mode: str) -> list:
    """Assign visualType to each scene based on the chosen mode."""
    for i, scene in enumerate(scenes):
        if visual_mode == "images-web":
            scene['visualType'] = 'web'
        elif visual_mode == "images-ai":
            scene['visualType'] = 'generate'
        elif visual_mode == "video-ai":
            scene['visualType'] = 'video'
        elif visual_mode == "mixed":
            if i == 0 or i == len(scenes) - 1:
                scene['visualType'] = 'video'
            else:
                scene['visualType'] = 'web'
    return scenes


def generate_hashtags(title: str) -> str:
    """Generate per-word hashtags from title."""
    words = [w.lower() for w in re.sub(r'[^\w\s]', '', title).split()
             if len(w) > 3 and w.lower() not in IMAGE_QUERY_STOP_WORDS]
    hashtags = ' '.join(f'#{w}' for w in words[:4])
    return f"{hashtags} #shorts #reels" if hashtags else "#shorts #reels"


def filter_image_query(title: str, body: str = "") -> str:
    """Generate an image search query filtering stop words."""
    clean_title = re.sub(r'[^\w\s]', ' ', title)
    words = [w for w in clean_title.split()
             if w.lower() not in IMAGE_QUERY_STOP_WORDS][:4]
    if len(words) < 2 and body:
        from_body = re.sub(r'[^\w\s]', ' ', body).split()
        words = [w for w in from_body
                 if w.lower() not in IMAGE_QUERY_STOP_WORDS][:4]
    return ' '.join(words) if words else "abstract visual"


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
    import requests
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


def validate_duration(duration: int) -> int:
    """Validate and clamp duration to supported range."""
    if duration < MIN_DURATION:
        print(f"Warning: Duration {duration}s below minimum, using {MIN_DURATION}s")
        return MIN_DURATION
    if duration > MAX_DURATION:
        print(f"Warning: Duration {duration}s above maximum, using {MAX_DURATION}s")
        return MAX_DURATION
    # Round to nearest 5-second boundary
    return (duration // SCENE_DURATION) * SCENE_DURATION


def print_progress(current: int, total: int, message: str) -> None:
    """Print progress indicator."""
    print(f"[{current}/{total}] {message}")


if __name__ == "__main__":
    print("Utils module loaded successfully")
    for d in [30, 45, 60, 90]:
        print(f"  {d}s video: {scenes_for_duration(d)} scenes, {max_words_for_duration(d)} words")
