#!/usr/bin/env python3
"""
Parse content (blog posts, articles, stories) and generate a short-form script.json
(30-90 seconds, 5-second scenes, vertical 9:16).

Usage:
    python content_to_script.py path/to/article.md
    python content_to_script.py path/to/article.md --duration 60 --style hype --visual-mode mixed
    cat article.md | python content_to_script.py --stdin --duration 45
    python content_to_script.py path/to/article.md --output path/to/script.json

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
        assign_visual_types, generate_hashtags, filter_image_query
    )
    from scripts.model_config import get_music_prompt
except ModuleNotFoundError:
    from utils import (
        slugify, save_script_json, validate_duration, DEFAULT_DURATION,
        DEFAULT_STYLE, STYLES, WORDS_PER_SECOND, SCENE_DURATION,
        WORDS_PER_SCENE, VISUAL_MODES, DEFAULT_VISUAL_MODE,
        MIN_DURATION, MAX_DURATION, DEFAULT_VOICE, STYLE_VOICES,
        assign_visual_types, generate_hashtags, filter_image_query
    )
    from model_config import get_music_prompt


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end + 3:].strip()
    return content


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, keeping readable text."""
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)  # images
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # links
    text = re.sub(r'```[\s\S]*?```', '', text)  # code blocks
    text = re.sub(r'`[^`]+`', '', text)  # inline code
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # heading markers
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)  # list items
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # numbered lists
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)  # blockquotes
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)  # horizontal rules
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_title(content: str) -> str:
    """Extract title from first heading or first sentence."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
        # Skip if it's just an image reference
        if not title.startswith('!['):
            return title[:80]

    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) > 10 and not line.startswith('![') and not line.startswith('```'):
            return line[:80]

    return "Untitled Short"


def extract_sections(content: str) -> list:
    """Extract sections from content using headings or paragraph breaks."""
    # Try heading-based sections first
    pattern = re.compile(r'^##\s+(.+?)$', re.MULTILINE)
    matches = list(pattern.finditer(content))

    if matches:
        sections = []
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            body = content[start_pos:end_pos].strip()
            if body:
                sections.append({'title': title, 'body': body})
        if sections:
            return sections

    # Fallback: split by double newlines into paragraphs
    paragraphs = re.split(r'\n\n+', content.strip())
    sections = []
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para or len(para) < 20:
            continue
        first_sentence = re.split(r'[.!?]', para)[0].strip()
        title = first_sentence[:50] if first_sentence else f"Point {i + 1}"
        sections.append({'title': title, 'body': para})

    return sections


def score_section(section: dict, index: int, total: int) -> float:
    """Score a section by importance for inclusion in the short video."""
    score = 0.0
    body = section['body']
    word_count = len(body.split())

    # Position bonus: first and last sections are important
    if index == 0:
        score += 3.0
    elif index == total - 1:
        score += 2.0

    # Length bonus: moderate length is best (not too short, not too long)
    if 20 <= word_count <= 100:
        score += 2.0
    elif 10 <= word_count <= 150:
        score += 1.0

    # Keyword bonus: sections with strong language
    strong_words = ['important', 'key', 'critical', 'essential', 'remarkable',
                    'surprising', 'billion', 'million', 'breakthrough', 'revolutionary',
                    'first', 'biggest', 'most', 'never', 'always', 'every']
    body_lower = body.lower()
    for word in strong_words:
        if word in body_lower:
            score += 0.5

    # Number/stat bonus
    if re.search(r'\d+', body):
        score += 0.5

    # Quote bonus
    if '"' in body or '\u201c' in body:
        score += 0.3

    return score


def select_sections(sections: list, num_scenes: int) -> list:
    """Select the best sections to fill the target number of scenes."""
    if len(sections) <= num_scenes:
        return sections

    scored = []
    for i, section in enumerate(sections):
        score = score_section(section, i, len(sections))
        scored.append((score, i, section))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected_indices = sorted([s[1] for s in scored[:num_scenes]])
    return [sections[i] for i in selected_indices]


def condense_narration(text: str, max_words: int = WORDS_PER_SCENE) -> str:
    """Condense text to fit within word limit for a scene."""
    clean = strip_markdown(strip_html(text))
    words = clean.split()

    if len(words) <= max_words:
        return clean

    truncated = ' '.join(words[:max_words])
    last_period = truncated.rfind('.')
    if last_period > len(truncated) // 2:
        truncated = truncated[:last_period + 1]

    return truncated


def condense_narration_sentences(text: str, max_words: int = WORDS_PER_SCENE) -> str:
    """Condense text by greedily picking complete sentences within word budget."""
    clean = strip_markdown(strip_html(text))
    sentences = re.split(r'(?<=[.!?])\s+', clean.strip())
    if not sentences:
        return clean

    selected = []
    word_count = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        s_words = len(sentence.split())
        if word_count + s_words <= max_words:
            selected.append(sentence)
            word_count += s_words
        else:
            break

    if selected:
        return ' '.join(selected)

    # First sentence alone exceeds budget — fall back to truncation
    return condense_narration(text, max_words)


def build_script_from_content(content: str, duration: int = DEFAULT_DURATION,
                              style: str = DEFAULT_STYLE, voice: str = DEFAULT_VOICE,
                              visual_mode: str = DEFAULT_VISUAL_MODE,
                              subtitles: bool = False,
                              source_path: str = None) -> dict:
    """Parse content and produce a short-form script.json."""
    content = strip_frontmatter(content)
    title = extract_title(content)
    sections = extract_sections(content)

    if not sections:
        raise ValueError("No usable sections found in content")

    duration = validate_duration(duration)
    num_scenes = duration // SCENE_DURATION

    selected = select_sections(sections, num_scenes)

    scenes = []
    for i, section in enumerate(selected):
        narration = condense_narration_sentences(section['body'])
        query = filter_image_query(section['title'], section['body'])

        scene = {
            'sceneNumber': i + 1,
            'title': section['title'][:50],
            'narration': narration,
            'duration': SCENE_DURATION,
            'visualType': 'web',
            'imageSearchQuery': query,
            'imageGenPrompt': (
                f"A cinematic, vibrant illustration depicting: {query}. "
                f"Vertical portrait composition, 9:16 aspect ratio, "
                f"bold colors, modern aesthetic, social media style."
            ),
            'videoPrompt': (
                f"Subtle camera push-in, gentle movement, cinematic feel, "
                f"depicting {query}"
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
        'sourceFile': os.path.abspath(source_path) if source_path else None,
        'parsedAt': datetime.now().isoformat(),
        'scenes': scenes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse content into short-form script.json"
    )
    parser.add_argument("content_file", nargs="?",
                        help="Path to content file (markdown, text, HTML)")
    parser.add_argument("--stdin", action="store_true",
                        help="Read content from stdin")
    parser.add_argument("--output", "-o",
                        help="Output path for script.json")
    parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION,
                        help=f"Target duration in seconds ({MIN_DURATION}-{MAX_DURATION}, default: {DEFAULT_DURATION})")
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

    if args.stdin:
        content = sys.stdin.read()
        source_path = None
    elif args.content_file:
        if not os.path.exists(args.content_file):
            print(f"Error: File not found: {args.content_file}")
            sys.exit(1)
        with open(args.content_file, 'r') as f:
            content = f.read()
        source_path = args.content_file
    else:
        parser.error("Provide a content file or use --stdin")

    if not content.strip():
        print("Error: Empty content")
        sys.exit(1)

    print(f"Parsing content ({len(content)} chars)...")
    print(f"Target: {args.duration}s {args.style} short ({args.visual_mode})")

    try:
        script_data = build_script_from_content(
            content, args.duration, args.style, args.voice,
            args.visual_mode, args.subtitles, source_path
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_path = args.output
    if not output_path:
        if source_path:
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(source_path)), 'script.json'
            )
        else:
            output_path = 'script.json'

    if args.cost_estimate:
        try:
            from model_config import estimate_cost, print_cost_estimate
        except ModuleNotFoundError:
            from scripts.model_config import estimate_cost, print_cost_estimate
        print_cost_estimate(len(script_data['scenes']), args.visual_mode)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    save_script_json(output_path, script_data)

    scenes = script_data['scenes']
    web_count = sum(1 for s in scenes if s.get('visualType') == 'web')
    gen_count = sum(1 for s in scenes if s.get('visualType') == 'generate')
    video_count = sum(1 for s in scenes if s.get('visualType') == 'video')
    total_words = sum(len(s['narration'].split()) for s in scenes)

    print(f"\nScript generated from content!")
    print(f"  Title: {script_data['title']}")
    print(f"  Scenes: {len(scenes)} x {SCENE_DURATION}s = {len(scenes) * SCENE_DURATION}s")
    print(f"  Visual: {web_count} web, {gen_count} AI image, {video_count} AI video")
    print(f"  Words: {total_words} (~{total_words / WORDS_PER_SECOND:.0f}s)")
    print(f"  Style: {args.style}")
    print(f"  Mode: {args.visual_mode}")
    print(f"  Subtitles: {'yes' if args.subtitles else 'no'}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
