#!/usr/bin/env python3
"""
Parse a deep-research youtube-script.md and condense it into a short-form script.json
(30-90 seconds, 5-second scenes, vertical 9:16).

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
        slugify, save_script_json, validate_duration, DEFAULT_DURATION,
        DEFAULT_STYLE, STYLES, WORDS_PER_SECOND, SCENE_DURATION,
        WORDS_PER_SCENE, VISUAL_MODES, DEFAULT_VISUAL_MODE,
        MIN_DURATION, MAX_DURATION, DEFAULT_VOICE, STYLE_VOICES,
        SKIP_SECTIONS, assign_visual_types, generate_hashtags,
        filter_image_query
    )
    from scripts.model_config import get_music_prompt
except ModuleNotFoundError:
    from utils import (
        slugify, save_script_json, validate_duration, DEFAULT_DURATION,
        DEFAULT_STYLE, STYLES, WORDS_PER_SECOND, SCENE_DURATION,
        WORDS_PER_SCENE, VISUAL_MODES, DEFAULT_VISUAL_MODE,
        MIN_DURATION, MAX_DURATION, DEFAULT_VOICE, STYLE_VOICES,
        SKIP_SECTIONS, assign_visual_types, generate_hashtags,
        filter_image_query
    )
    from model_config import get_music_prompt


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
        if title.upper() in SKIP_SECTIONS:
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



def condense_for_short(sections: list, target_duration: int, style: str) -> list:
    """Select and condense sections to fit 5-second scenes."""
    if not sections:
        return []

    num_scenes = target_duration // SCENE_DURATION

    selected = [sections[0]]
    middles = sections[1:-1] if len(sections) > 2 else []
    mid_slots = num_scenes - 2

    scored = []
    for s in middles:
        narr = strip_formatting(s['body'])
        word_count = len(narr.split())
        scored.append((s, word_count))

    scored.sort(key=lambda x: x[1], reverse=True)
    for s, _ in scored[:mid_slots]:
        selected.append(s)

    if len(sections) > 1:
        selected.append(sections[-1])

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
            'imageQuery': filter_image_query(section['title'], section['body']),
        })

    return condensed


def build_short_script(md_path: str, duration: int = DEFAULT_DURATION,
                       style: str = DEFAULT_STYLE, voice: str = DEFAULT_VOICE,
                       visual_mode: str = DEFAULT_VISUAL_MODE,
                       subtitles: bool = False) -> dict:
    """Parse youtube-script.md and produce a short-form script.json."""
    with open(md_path, 'r') as f:
        content = f.read()

    title = extract_title(content)
    sections = extract_sections(content)

    if not sections:
        raise ValueError(f"No sections found in {md_path}")

    duration = validate_duration(duration)
    condensed = condense_for_short(sections, duration, style)

    scenes = []
    for i, scene_data in enumerate(condensed):
        scene = {
            'sceneNumber': i + 1,
            'title': scene_data['title'],
            'narration': scene_data['narration'],
            'duration': SCENE_DURATION,
            'visualType': 'web',
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
    full_narration = ' '.join(s['narration'] for s in scenes if s.get('narration'))

    return {
        'title': title,
        'description': generate_hashtags(title),
        'targetDuration': duration,
        'style': style,
        'visualMode': visual_mode,
        'voice': voice,
        'orientation': 'portrait',
        'subtitles': subtitles,
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
    parser.add_argument("source_file",
                        help="Path to youtube-script.md or any content file")
    parser.add_argument("--output", "-o",
                        help="Output path for script.json")
    parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION,
                        help=f"Target duration ({MIN_DURATION}-{MAX_DURATION}s, default: {DEFAULT_DURATION})")
    parser.add_argument("--style", "-s", default=DEFAULT_STYLE,
                        choices=STYLES,
                        help=f"Video style (default: {DEFAULT_STYLE})")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        help=f"Deepgram Aura-2 voice ID (default: {DEFAULT_VOICE})")
    parser.add_argument("--visual-mode", default=DEFAULT_VISUAL_MODE,
                        choices=VISUAL_MODES,
                        help=f"Visual mode (default: {DEFAULT_VISUAL_MODE})")
    parser.add_argument("--subtitles", action="store_true",
                        help="Enable subtitle generation")
    parser.add_argument("--cost-estimate", action="store_true",
                        help="Show estimated API cost before generating")
    parser.add_argument("--list-styles", action="store_true",
                        help="Show available styles and exit")
    args = parser.parse_args()

    if args.list_styles:
        print("Available styles:")
        for s in STYLES:
            voice = STYLE_VOICES.get(s, DEFAULT_VOICE)
            print(f"  {s:15s} voice={voice}")
        sys.exit(0)

    if not os.path.exists(args.source_file):
        print(f"Error: File not found: {args.source_file}")
        sys.exit(1)

    duration = validate_duration(args.duration)

    print(f"Parsing: {args.source_file}")
    print(f"Target: {duration}s {args.style} short ({args.visual_mode})")

    try:
        script_data = build_short_script(
            args.source_file, duration, args.style,
            args.voice, args.visual_mode, args.subtitles
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(args.source_file)), 'script.json'
    )
    if args.cost_estimate:
        try:
            from model_config import print_cost_estimate
        except ModuleNotFoundError:
            from scripts.model_config import print_cost_estimate
        print_cost_estimate(len(script_data['scenes']), args.visual_mode)

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
