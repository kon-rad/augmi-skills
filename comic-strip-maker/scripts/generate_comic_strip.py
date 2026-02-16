#!/usr/bin/env python3
"""
Generate comic strips and manga-style cartoon pages from text prompts using
Google's Nano Banana 3 model via Gemini API. Supports reference images for
characters, logos, and visual style.

Usage:
    # Basic comic strip
    python generate_comic_strip.py --prompt "A cat discovers it can fly" --output comic.png

    # With a character face reference
    python generate_comic_strip.py --prompt "A hero saves the day" --character hero.jpg --output comic.png

    # With logo and style reference
    python generate_comic_strip.py --prompt "..." --logo brand.png --style-ref manga-sample.jpg

Requirements:
    pip install google-genai pillow

Environment:
    GEMINI_API_KEY or GOOGLE_AI_API_KEY must be set
"""

import os
import sys
import argparse
import mimetypes
from pathlib import Path
from typing import Optional, List

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed.")
    print("Install with: pip install google-genai")
    sys.exit(1)

try:
    from PIL import Image
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Model configurations
NANO_BANANA_MODEL = "nano-banana-pro-preview"
GEMINI_TEXT_MODEL = "gemini-2.5-flash"

# Valid aspect ratios
VALID_ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9"]

# Layout configurations
LAYOUTS = {
    "manga": {
        "description": "Traditional manga page with varied panel sizes",
        "default_panels": 4,
        "default_aspect": "3:4",
        "prompt_hint": (
            "Create a manga page with varied panel sizes. Use larger panels for "
            "dramatic moments and smaller panels for transitions. Include dynamic "
            "panel borders with some panels overlapping slightly for energy."
        ),
    },
    "strip": {
        "description": "Horizontal comic strip (3-4 equal panels)",
        "default_panels": 3,
        "default_aspect": "16:9",
        "prompt_hint": (
            "Create a horizontal comic strip with equally-sized panels arranged "
            "left to right. Clean panel borders with gutters between each panel. "
            "Reads naturally left to right."
        ),
    },
    "4-koma": {
        "description": "Vertical 4-panel comic (Japanese yonkoma)",
        "default_panels": 4,
        "default_aspect": "3:4",
        "prompt_hint": (
            "Create a vertical 4-koma (yonkoma) comic with 4 equally-sized panels "
            "stacked vertically. Classic Japanese comedy comic format. Each panel "
            "follows the ki-sho-ten-ketsu structure: setup, development, twist, conclusion."
        ),
    },
    "splash": {
        "description": "Single large panel with inset detail panels",
        "default_panels": 3,
        "default_aspect": "3:4",
        "prompt_hint": (
            "Create a splash page layout with one large dramatic main panel taking "
            "up most of the page, with 2-3 smaller inset panels showing detail "
            "shots or sequential moments."
        ),
    },
    "grid": {
        "description": "Even grid layout (2x2 or 2x3)",
        "default_panels": 4,
        "default_aspect": "3:4",
        "prompt_hint": (
            "Create a clean grid layout comic page with evenly-sized panels "
            "arranged in rows. Clear panel borders and consistent spacing."
        ),
    },
}

# Anime sub-styles
STYLES = {
    "modern-anime": (
        "Modern anime art style with clean crisp lines, vibrant colors, detailed "
        "shading with cel-shading technique, expressive eyes, and dynamic poses. "
        "High quality anime illustration."
    ),
    "shonen": (
        "Bold shonen manga art style with thick dynamic lines, intense action poses, "
        "speed lines, dramatic lighting, and powerful expressions. High energy "
        "battle manga aesthetic."
    ),
    "shoujo": (
        "Elegant shoujo manga style with soft delicate lines, sparkle and flower "
        "effects, beautiful flowing hair, large expressive eyes with star reflections, "
        "and romantic dreamy atmosphere."
    ),
    "chibi": (
        "Cute chibi anime style with super-deformed proportions (large heads, small "
        "bodies), oversized expressive eyes, simplified features, and exaggerated "
        "cute reactions. Kawaii aesthetic."
    ),
    "seinen": (
        "Detailed seinen manga style with realistic proportions, fine line work, "
        "complex shading and crosshatching, mature character designs, and "
        "atmospheric backgrounds."
    ),
    "retro": (
        "Retro 80s/90s anime style with warm color palette, visible line weight "
        "variation, soft gradients, slight grain texture, and nostalgic cel "
        "animation aesthetic reminiscent of Studio Ghibli and classic anime."
    ),
}

# Mood descriptors
MOODS = {
    "comedic": "lighthearted and funny with exaggerated expressions and comedic timing",
    "dramatic": "intense and emotional with dramatic lighting and powerful compositions",
    "heartwarming": "warm and touching with soft lighting and gentle expressions",
    "action": "high energy with dynamic motion, speed lines, and impact effects",
    "mysterious": "dark and atmospheric with shadows, silhouettes, and dramatic angles",
    "slice-of-life": "calm and everyday with warm colors and natural compositions",
}


def get_api_key() -> str:
    """Get Google AI API key from environment."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Set GEMINI_API_KEY or GOOGLE_AI_API_KEY environment variable.\n"
            "Get your key at: https://aistudio.google.com/apikey"
        )
    return api_key


def create_client() -> genai.Client:
    """Create and return a configured Gemini client."""
    api_key = get_api_key()
    return genai.Client(api_key=api_key)


def get_mime_type(file_path: str) -> str:
    """Detect MIME type from file extension."""
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith("image/"):
        return mime
    # Fallback based on extension
    ext = Path(file_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    return mime_map.get(ext, "image/png")


def load_image_part(file_path: str) -> types.Part:
    """Load an image file and return it as a Gemini Part."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")

    with open(path, "rb") as f:
        image_bytes = f.read()

    mime_type = get_mime_type(file_path)
    return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)


def read_story_file(file_path: str) -> str:
    """Read story content from a markdown file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Story file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content.strip()) < 10:
        raise ValueError("Story content too short. Provide at least a sentence.")

    return content


def generate_comic_prompt(
    client: genai.Client,
    story: str,
    layout: str = "strip",
    panels: int = 3,
    style: str = "modern-anime",
    mood: Optional[str] = None,
    character_images: Optional[List[str]] = None,
    logo_images: Optional[List[str]] = None,
    style_ref_images: Optional[List[str]] = None,
    verbose: bool = False,
) -> str:
    """
    Analyze the story (and any reference images) and generate an optimized
    Nano Banana 3 prompt for a comic strip.
    """
    layout_config = LAYOUTS.get(layout, LAYOUTS["strip"])
    style_desc = STYLES.get(style, STYLES["modern-anime"])
    mood_desc = ""
    if mood and mood in MOODS:
        mood_desc = f"\nMood/Tone: {MOODS[mood]}"
    elif mood:
        mood_desc = f"\nMood/Tone: {mood}"

    # Build reference image context for the prompt
    ref_instructions = ""
    if character_images:
        ref_instructions += (
            "\n\nCHARACTER REFERENCE IMAGES: I have attached image(s) showing the "
            "main character's face/appearance. The comic's main character MUST closely "
            "match this person's appearance: their face, hair style, hair color, skin tone, "
            "and distinctive features. Describe the character in every panel using these "
            "exact visual traits so the image generator reproduces them faithfully."
        )
    if logo_images:
        ref_instructions += (
            "\n\nLOGO REFERENCE IMAGES: I have attached a logo image. This logo MUST "
            "appear somewhere in the comic — on a character's shirt, on a sign, on a "
            "screen, or as a watermark/badge. Describe the logo's appearance (colors, "
            "shape, text) so the image generator can reproduce it in the comic."
        )
    if style_ref_images:
        ref_instructions += (
            "\n\nSTYLE REFERENCE IMAGES: I have attached image(s) showing the desired "
            "visual style. The comic MUST match this art style — same line weight, "
            "coloring technique, shading approach, and overall aesthetic. Override the "
            "default style preset with whatever you observe in these reference images. "
            "Describe the visual style in detail so the image generator reproduces it."
        )

    analysis_prompt = f"""You are an expert comic artist and storyboard designer. Your task is to create a detailed image generation prompt that will produce a single comic strip or comic page.

STORY/CONCEPT:
{story}

LAYOUT STYLE: {layout}
{layout_config['prompt_hint']}

NUMBER OF PANELS: {panels}

ART STYLE:
{style_desc}
{mood_desc}
{ref_instructions}

Your job is to write a SINGLE, detailed image generation prompt (100-200 words) that will create a complete comic strip/page as one image. The prompt must:

1. **Describe the full page layout** - Specify panel arrangement (e.g., "3-panel comic strip with equally-sized panels arranged left to right" or "4-panel manga page with varied panel sizes")
2. **Describe each panel's content** - What's happening in each panel, character positions, expressions, and actions
3. **Include speech bubbles** - Write actual dialogue text that should appear in speech bubbles (keep text SHORT, 3-8 words per bubble max)
4. **Specify visual effects** - Speed lines, emotion marks, screen tones, sparkles, etc. as appropriate
5. **Maintain character consistency** - Describe characters the same way in each panel mention (hair color, outfit, distinctive features). If character reference images were provided, use the exact appearance from those images.
6. **Set the art style** - Include the art style directives. If style reference images were provided, describe that exact style instead of the default.
7. **Include logo if provided** - If a logo reference was given, describe where and how it appears.

Output ONLY the image prompt. No explanations, headers, or metadata. Start directly with the visual description."""

    # Build multimodal content: images first, then text prompt
    content_parts = []

    if character_images:
        for img_path in character_images:
            content_parts.append(load_image_part(img_path))
            content_parts.append(f"[This is the CHARACTER reference — the main character must look like this person]")

    if logo_images:
        for img_path in logo_images:
            content_parts.append(load_image_part(img_path))
            content_parts.append(f"[This is the LOGO reference — include this logo in the comic]")

    if style_ref_images:
        for img_path in style_ref_images:
            content_parts.append(load_image_part(img_path))
            content_parts.append(f"[This is the STYLE reference — match this visual art style]")

    content_parts.append(analysis_prompt)

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=content_parts,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=800,
        ),
    )

    generated_prompt = response.text.strip()

    if verbose:
        print(f"\n--- Generated Image Prompt ---")
        print(generated_prompt)
        print(f"--- End Prompt ---\n")

    return generated_prompt


def generate_cartoon_image(
    client: genai.Client,
    prompt: str,
    aspect_ratio: str = "16:9",
    character_images: Optional[List[str]] = None,
    logo_images: Optional[List[str]] = None,
    style_ref_images: Optional[List[str]] = None,
    verbose: bool = False,
) -> bytes:
    """
    Generate a comic image using Nano Banana 3, optionally with reference images.

    Returns:
        Image bytes
    """
    if verbose:
        print(f"  Model: {NANO_BANANA_MODEL}")
        print(f"  Aspect ratio: {aspect_ratio}")

    # Build multimodal content: reference images + text prompt
    content_parts = []

    if character_images:
        for img_path in character_images:
            content_parts.append(load_image_part(img_path))
        if verbose:
            print(f"  Character refs: {len(character_images)} image(s)")

    if logo_images:
        for img_path in logo_images:
            content_parts.append(load_image_part(img_path))
        if verbose:
            print(f"  Logo refs: {len(logo_images)} image(s)")

    if style_ref_images:
        for img_path in style_ref_images:
            content_parts.append(load_image_part(img_path))
        if verbose:
            print(f"  Style refs: {len(style_ref_images)} image(s)")

    content_parts.append(prompt)

    response = client.models.generate_content(
        model=NANO_BANANA_MODEL,
        contents=content_parts,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        ),
    )

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return part.inline_data.data

    raise RuntimeError("No image generated in response. The prompt may have been blocked by safety filters.")


def save_image(image_bytes: bytes, output_path: str) -> str:
    """Save image bytes to file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if PIL_AVAILABLE:
        image = Image.open(BytesIO(image_bytes))
        image.save(output_path)
    else:
        with open(output_path, "wb") as f:
            f.write(image_bytes)

    return str(output_path)


def generate_comic_strip(
    client: genai.Client,
    story: str,
    output_path: str,
    layout: str = "strip",
    panels: int = 3,
    style: str = "modern-anime",
    mood: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    character_images: Optional[List[str]] = None,
    logo_images: Optional[List[str]] = None,
    style_ref_images: Optional[List[str]] = None,
    verbose: bool = False,
) -> str:
    """
    Main function to generate a comic strip from a story prompt.

    Returns:
        Path to saved image
    """
    layout_config = LAYOUTS.get(layout, LAYOUTS["strip"])

    # Use layout default aspect ratio if not specified
    if aspect_ratio is None:
        aspect_ratio = layout_config["default_aspect"]

    # Use layout default panels if not specified
    if panels is None:
        panels = layout_config["default_panels"]

    # Step 1: Generate optimized comic prompt (with reference images for context)
    print("  Analyzing story and generating panel layout...")
    comic_prompt = generate_comic_prompt(
        client, story, layout, panels, style, mood,
        character_images, logo_images, style_ref_images, verbose
    )

    # Step 2: Generate the comic image (with reference images for visual matching)
    print("  Generating comic strip with Nano Banana 3...")
    image_bytes = generate_cartoon_image(
        client, comic_prompt, aspect_ratio,
        character_images, logo_images, style_ref_images, verbose
    )

    # Step 3: Save the image
    saved_path = save_image(image_bytes, output_path)
    print(f"  Saved: {saved_path}")

    return saved_path


def validate_image_paths(paths: Optional[List[str]], label: str) -> Optional[List[str]]:
    """Validate that all image paths exist and return the list or None."""
    if not paths:
        return None
    validated = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"  Warning: {label} image not found: {p} (skipping)")
        else:
            validated.append(str(path))
    return validated if validated else None


def main():
    parser = argparse.ArgumentParser(
        description="Generate comic strips from text prompts using Nano Banana 3"
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--prompt", "-p",
        help="Story/scene description for the comic strip",
    )
    input_group.add_argument(
        "--story-file", "-f",
        help="Path to markdown file with story",
    )

    # Output
    parser.add_argument(
        "--output", "-o",
        default="comic-strip.png",
        help="Output path for generated image (default: comic-strip.png)",
    )

    # Layout options
    parser.add_argument(
        "--layout", "-l",
        default="strip",
        choices=list(LAYOUTS.keys()),
        help="Panel layout style (default: strip)",
    )
    parser.add_argument(
        "--panels", "-n",
        type=int,
        default=None,
        choices=[2, 3, 4, 5, 6],
        help="Number of panels (default: depends on layout)",
    )

    # Style options
    parser.add_argument(
        "--aspect-ratio", "-a",
        default=None,
        choices=VALID_ASPECT_RATIOS,
        help="Image aspect ratio (default: depends on layout)",
    )
    parser.add_argument(
        "--style", "-s",
        default="modern-anime",
        choices=list(STYLES.keys()),
        help="Art sub-style (default: modern-anime)",
    )
    parser.add_argument(
        "--mood", "-m",
        default=None,
        help="Mood/tone (comedic, dramatic, heartwarming, action, mysterious, slice-of-life, or custom)",
    )

    # Reference image options
    parser.add_argument(
        "--character",
        nargs="+",
        metavar="IMAGE",
        help="Character/face reference image(s) — the main character will match this appearance",
    )
    parser.add_argument(
        "--logo",
        nargs="+",
        metavar="IMAGE",
        help="Logo image(s) to include in the comic",
    )
    parser.add_argument(
        "--style-ref",
        nargs="+",
        metavar="IMAGE",
        help="Style reference image(s) — the comic will match this visual style",
    )

    # Debug
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including generated prompt",
    )

    args = parser.parse_args()

    # Create client
    try:
        client = create_client()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print()
    print("=" * 50)
    print("  Comic Strip Maker (Nano Banana 3)")
    print("=" * 50)

    # Get story content
    try:
        if args.story_file:
            print(f"\n  Reading story: {args.story_file}")
            story = read_story_file(args.story_file)
        else:
            story = args.prompt

        if not story or len(story.strip()) < 5:
            print("Error: Story prompt is too short.")
            sys.exit(1)

    except Exception as e:
        print(f"Error reading story: {e}")
        sys.exit(1)

    # Validate reference images
    character_images = validate_image_paths(args.character, "Character")
    logo_images = validate_image_paths(args.logo, "Logo")
    style_ref_images = validate_image_paths(args.style_ref, "Style ref")

    # Resolve defaults
    layout = args.layout
    panels = args.panels or LAYOUTS[layout]["default_panels"]
    aspect_ratio = args.aspect_ratio

    print(f"\n  Layout: {layout} ({LAYOUTS[layout]['description']})")
    print(f"  Panels: {panels}")
    print(f"  Style: {args.style}")
    if args.mood:
        print(f"  Mood: {args.mood}")
    if character_images:
        print(f"  Character refs: {', '.join(character_images)}")
    if logo_images:
        print(f"  Logo refs: {', '.join(logo_images)}")
    if style_ref_images:
        print(f"  Style refs: {', '.join(style_ref_images)}")
    print()

    # Generate
    try:
        saved_path = generate_comic_strip(
            client,
            story,
            args.output,
            layout=layout,
            panels=panels,
            style=args.style,
            mood=args.mood,
            aspect_ratio=aspect_ratio,
            character_images=character_images,
            logo_images=logo_images,
            style_ref_images=style_ref_images,
            verbose=args.verbose,
        )

        print()
        print("=" * 50)
        print("  Generation complete!")
        print(f"  Output: {saved_path}")

        # Show file size
        file_size = Path(saved_path).stat().st_size / 1024
        print(f"  Size: {file_size:.1f} KB")
        print(f"  Cost: ~$0.04")
        print("=" * 50)

    except Exception as e:
        print(f"\nError generating comic strip: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
