#!/usr/bin/env python3
"""
Parse a deep-research youtube-script.md and condense it into a short-form script.json
(30-60 seconds, 5-second scenes, vertical 9:16).

Usage:
    python parse_script.py path/to/youtube-script.md
    python parse_script.py path/to/youtube-script.md --duration 60 --style hype --visual-mode mixed
    python parse_script.py path/to/youtube-script.md --output path/to/script.json

Requirements:
    pip install python-dotenv
"""

import os
import sys
import re
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scripts.utils import (
        slugify, save_script_json, DEFAULT_DURATION, DEFAULT_STYLE,
        STYLES, WORDS_PER_SECOND, SCENE_DURATION, WORDS_PER_SCENE,
        VISUAL_MODES, DEFAULT_VISUAL_MODE
    )
    from scripts.model_config import get_music_prompt
except ModuleNotFoundError:
    from utils import (
        slugify, save_script_json, DEFAULT_DURATION, DEFAULT_STYLE,
        STYLES, WORDS_PER_SECOND, SCENE_DURATION, WORDS_PER_SCENE,
        VISUAL_MODES, DEFAULT_VISUAL_MODE
    )
    from model_config import get_music_prompt


DEFAULT_VOICE = "aura-asteria-en"

# Style-to-voice mapping
STYLE_VOICES = {
    "educational": "aura-asteria-en",
    "promotional": "aura-athena-en",
    "storytelling": "aura-perseus-en",
    "hype": "aura-arcas-en",
}


def extract_title(content: str) -> str:
    match = re.search(r'^#\s+(?:YouTube Script:\s*)?(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled Short"


def extract_sections(content: str) -> list:
    pattern = re.compile(
        r'^##\s+(.+?)(?:\s*\((\d+:\d{2})\s*-\s*(\d+:\d{2})\))?\s*$',
        re.MULTILINE
    )
    sections = []
    matches = list(pattern.finditer(content))

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        if title.upper() in ('VIDEO DESCRIPTION', 'THUMBNAIL IDEAS'):
            continue

        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start_pos:end_pos].strip()

        sections.append({'title': title, 'body': body})

    return sections


def strip_formatting(text: str) -> str:
    """Remove markdown formatting, visual cues, and code blocks."""
    text = re.sub(r'\*\*\[(?:SCREEN|B-ROLL|VISUAL|CUT TO)[^\]]*\]\*\*', '', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_visual_query(body: str, title: str) -> str:
    """Extract an image search query from visual cues or title."""
    pattern = re.compile(r'\*\*\[(SCREEN|B-ROLL|VISUAL):\s*([^\]]+)\]\*\*')
    match = pattern.search(body)
    if match:
        query = re.sub(r'[^\w\s]', ' ', match.group(2))
        return ' '.join(query.split()[:5])

    clean_title = re.sub(r'^SECTION\s+\d+:\s*', '', title, flags=re.IGNORECASE)
    clean_title = re.sub(r'^(HOOK|INTRO|CONCLUSION)\s*', '', clean_title, flags=re.IGNORECASE)
    return clean_title.strip()[:40] if clean_title.strip() else "abstract visual"


def condense_for_short(sections: list, target_duration: int, style: str) -> list:
    """Select and condense sections to fit 5-second scenes."""
    if not sections:
        return []

    num_scenes = target_duration // SCENE_DURATION

    # Always include first and last
    selected = [sections[0]]

    # Pick middle sections
    middles = sections[1:-1] if len(sections) > 2 else []
    mid_slots = num_scenes - 2

    # Score middles by narration length (prefer shorter, punchier)
    scored = []
    for s in middles:
        narr = strip_formatting(s['body'])
        word_count = len(narr.split())
        scored.append((s, word_count))

    scored.sort(key=lambda x: x[1])
    for s, _ in scored[:mid_slots]:
        selected.append(s)

    # Add conclusion
    if len(sections) > 1:
        selected.append(sections[-1])

    # Truncate narration per scene to fit 5-second budget
    condensed = []
    for section in selected:
        narr = strip_formatting(section['body'])
        words = narr.split()

        if len(words) > WORDS_PER_SCENE:
            truncated = ' '.join(words[:WORDS_PER_SCENE])
            last_period = truncated.rfind('.')
            if last_period > len(truncated) // 2:
                truncated = truncated[:last_period + 1]
            narr = truncated

        condensed.append({
            'title': section['title'],
            'narration': narr,
            'imageQuery': extract_visual_query(section['body'], section['title']),
        })

    return condensed


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
            # Hook (first) and closer (last) get video, rest get web
            if i == 0 or i == len(scenes) - 1:
                scene['visualType'] = 'video'
            else:
                scene['visualType'] = 'web'
    return scenes


def build_short_script(md_path: str, duration: int = DEFAULT_DURATION,
                       style: str = DEFAULT_STYLE, voice: str = DEFAULT_VOICE,
                       visual_mode: str = DEFAULT_VISUAL_MODE) -> dict:
    """Parse youtube-script.md and produce a short-form script.json."""
    with open(md_path, 'r') as f:
        content = f.read()

    title = extract_title(content)
    sections = extract_sections(content)

    if not sections:
        raise ValueError(f"No sections found in {md_path}")

    condensed = condense_for_short(sections, duration, style)

    # Build scenes (all 5 seconds each)
    scenes = []
    for i, scene_data in enumerate(condensed):
        scene = {
            'sceneNumber': i + 1,
            'title': scene_data['title'],
            'narration': scene_data['narration'],
            'duration': SCENE_DURATION,
            'visualType': 'web',  # Will be overwritten by assign_visual_types
            'imageSearchQuery': scene_data['imageQuery'],
            'imageGenPrompt': (
                f"A cinematic, vibrant illustration depicting: {scene_data['imageQuery']}. "
                f"Vertical portrait composition, 9:16 aspect ratio, "
                f"bold colors, modern aesthetic, social media style."
            ),
            'videoPrompt': (
                f"Subtle camera push-in, gentle movement, cinematic feel, "
                f"depicting {scene_data['imageQuery']}"
            ),
        }
        scenes.append(scene)

    scenes = assign_visual_types(scenes, visual_mode)

    # Build full narration text
    full_narration = ' '.join(s['narration'] for s in scenes if s.get('narration'))

    return {
        'title': title,
        'description': f"#{slugify(title).replace('-', '')} #shorts #reels",
        'targetDuration': duration,
        'style': style,
        'visualMode': visual_mode,
        'voice': voice,
        'orientation': 'portrait',
        'config': {
            'musicPrompt': get_music_prompt(style),
            'musicVolume': 0.15,
            'narrationVolume': 1.0,
        },
        'narration': {
            'text': full_narration,
        },
        'sourceFile': os.path.abspath(md_path),
        'parsedAt': datetime.now().isoformat(),
        'scenes': scenes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse deep-research youtube-script.md into short-form script.json"
    )
    parser.add_argument("youtube_script_md",
                        help="Path to youtube-script.md")
    parser.add_argument("--output", "-o",
                        help="Output path for script.json")
    parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION,
                        choices=[30, 45, 60],
                        help=f"Target duration in seconds (default: {DEFAULT_DURATION})")
    parser.add_argument("--style", "-s", default=DEFAULT_STYLE,
                        choices=STYLES,
                        help=f"Video style (default: {DEFAULT_STYLE})")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        help=f"Deepgram voice ID (default: {DEFAULT_VOICE})")
    parser.add_argument("--visual-mode", default=DEFAULT_VISUAL_MODE,
                        choices=VISUAL_MODES,
                        help=f"Visual mode (default: {DEFAULT_VISUAL_MODE})")
    args = parser.parse_args()

    if not os.path.exists(args.youtube_script_md):
        print(f"Error: File not found: {args.youtube_script_md}")
        sys.exit(1)

    print(f"Parsing: {args.youtube_script_md}")
    print(f"Target: {args.duration}s {args.style} short ({args.visual_mode})")

    try:
        script_data = build_short_script(
            args.youtube_script_md, args.duration, args.style,
            args.voice, args.visual_mode
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(args.youtube_script_md)), 'script.json'
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_script_json(output_path, script_data)

    scenes = script_data['scenes']
    web_count = sum(1 for s in scenes if s.get('visualType') == 'web')
    gen_count = sum(1 for s in scenes if s.get('visualType') == 'generate')
    video_count = sum(1 for s in scenes if s.get('visualType') == 'video')
    total_words = sum(len(s['narration'].split()) for s in scenes)

    print(f"\nCondensed to short-form!")
    print(f"  Title: {script_data['title']}")
    print(f"  Scenes: {len(scenes)} x {SCENE_DURATION}s = {len(scenes) * SCENE_DURATION}s")
    print(f"  Visual: {web_count} web, {gen_count} AI image, {video_count} AI video")
    print(f"  Words: {total_words} (~{total_words / WORDS_PER_SECOND:.0f}s)")
    print(f"  Style: {args.style}")
    print(f"  Mode: {args.visual_mode}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
