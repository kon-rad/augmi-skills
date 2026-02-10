#!/usr/bin/env python3
"""
Generate graphic visuals from blog post content using Google's Nano Banana 3 model.

This script:
1. Reads blog post content (from file or direct text)
2. Analyzes the content using Gemini to extract key themes
3. Generates an optimized image prompt
4. Creates a visual using Nano Banana 3

Usage:
    # From a file
    python generate_blog_visual.py --file blog-post.md --output visual.png

    # From text
    python generate_blog_visual.py --text "Your blog content..." --output visual.png

Requirements:
    pip install google-genai pillow

Environment:
    GEMINI_API_KEY or GOOGLE_AI_API_KEY must be set
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

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

# Default style hints for different content types
STYLE_HINTS = {
    "tech": "modern digital illustration, clean lines, tech aesthetic, electric blue and cyan accents",
    "philosophy": "ethereal abstract art, contemplative mood, soft gradients, purple and gold",
    "business": "professional corporate illustration, confident, warm colors, modern office aesthetic",
    "creative": "artistic digital painting, vibrant colors, imaginative, dynamic composition",
    "science": "scientific visualization, precise, informative, cool blues and whites",
    "default": "modern digital art, professional quality, visually striking, balanced composition"
}


def get_api_key() -> str:
    """Get Google AI API key from environment"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Set GEMINI_API_KEY or GOOGLE_AI_API_KEY environment variable.\n"
            "Get your key at: https://aistudio.google.com/apikey"
        )
    return api_key


def create_client() -> genai.Client:
    """Create and return a configured Gemini client"""
    api_key = get_api_key()
    return genai.Client(api_key=api_key)


def read_blog_content(file_path: str) -> str:
    """Read blog post content from a markdown file"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Blog post file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if len(content.strip()) < 100:
        raise ValueError("Blog content too short. Provide at least a few paragraphs.")

    return content


def analyze_content_and_generate_prompt(
    client: genai.Client,
    content: str,
    style_hint: str = "modern digital art",
    verbose: bool = False
) -> str:
    """
    Analyze blog content and generate an optimized image prompt.

    Uses Gemini to understand the content and create a visual description
    that captures the essence of the blog post.
    """

    analysis_prompt = f"""You are an expert at creating visual representations of written content.

Analyze the following blog post and create a detailed image generation prompt that:
1. Captures the MAIN THEME and core message visually
2. Uses appropriate VISUAL METAPHORS for abstract concepts
3. Sets the right MOOD and emotional tone
4. Includes specific VISUAL ELEMENTS that represent key ideas
5. Specifies STYLE, LIGHTING, and COLOR PALETTE

The prompt should be 50-150 words, highly descriptive, and optimized for AI image generation.

Style direction: {style_hint}

BLOG POST CONTENT:
---
{content[:8000]}
---

Generate ONLY the image prompt, nothing else. No explanations, no preamble.
Start directly with the visual description."""

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=analysis_prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=500
        )
    )

    generated_prompt = response.text.strip()

    if verbose:
        print(f"\n📝 Generated Image Prompt:")
        print("-" * 50)
        print(generated_prompt)
        print("-" * 50)

    return generated_prompt


def generate_image_nano_banana(
    client: genai.Client,
    prompt: str,
    aspect_ratio: str = "16:9",
    verbose: bool = False
) -> bytes:
    """
    Generate an image using Nano Banana 3 model.

    Args:
        client: Gemini client
        prompt: Image generation prompt
        aspect_ratio: Image aspect ratio
        verbose: Print detailed output

    Returns:
        Image bytes
    """
    if verbose:
        print(f"\n🎨 Generating image with Nano Banana 3...")
        print(f"   Model: {NANO_BANANA_MODEL}")
        print(f"   Aspect ratio: {aspect_ratio}")

    # Nano Banana uses generate_content with IMAGE modality
    response = client.models.generate_content(
        model=NANO_BANANA_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio
            )
        )
    )

    # Extract image from response
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            return part.inline_data.data

    raise RuntimeError("No image generated in response")


def save_image(image_bytes: bytes, output_path: str) -> str:
    """Save image bytes to file"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if PIL_AVAILABLE:
        image = Image.open(BytesIO(image_bytes))
        image.save(output_path)
    else:
        with open(output_path, 'wb') as f:
            f.write(image_bytes)

    return str(output_path)


def detect_content_type(content: str) -> str:
    """Detect the type of content to choose appropriate style"""
    content_lower = content.lower()

    tech_keywords = ['code', 'software', 'api', 'developer', 'programming', 'blockchain', 'crypto', 'ai', 'technology']
    philosophy_keywords = ['wisdom', 'philosophy', 'meaning', 'consciousness', 'existence', 'thought', 'mind']
    business_keywords = ['market', 'business', 'startup', 'investment', 'revenue', 'growth', 'strategy']
    science_keywords = ['research', 'study', 'experiment', 'data', 'analysis', 'scientific', 'hypothesis']

    tech_score = sum(1 for kw in tech_keywords if kw in content_lower)
    philosophy_score = sum(1 for kw in philosophy_keywords if kw in content_lower)
    business_score = sum(1 for kw in business_keywords if kw in content_lower)
    science_score = sum(1 for kw in science_keywords if kw in content_lower)

    scores = {
        'tech': tech_score,
        'philosophy': philosophy_score,
        'business': business_score,
        'science': science_score
    }

    best_type = max(scores, key=scores.get)
    if scores[best_type] >= 3:
        return best_type
    return 'default'


def generate_blog_visual(
    client: genai.Client,
    content: str,
    output_path: str,
    aspect_ratio: str = "16:9",
    style: Optional[str] = None,
    verbose: bool = False
) -> str:
    """
    Main function to generate a visual from blog content.

    Args:
        client: Gemini client
        content: Blog post content
        output_path: Where to save the image
        aspect_ratio: Image aspect ratio
        style: Optional style override
        verbose: Print detailed output

    Returns:
        Path to saved image
    """
    # Detect content type if no style specified
    if style is None:
        content_type = detect_content_type(content)
        style = STYLE_HINTS.get(content_type, STYLE_HINTS['default'])
        if verbose:
            print(f"📊 Detected content type: {content_type}")
            print(f"   Using style: {style[:50]}...")

    # Step 1: Analyze content and generate prompt
    print("🔍 Analyzing blog content...")
    image_prompt = analyze_content_and_generate_prompt(
        client, content, style, verbose
    )

    # Step 2: Generate image
    print("🎨 Generating visual with Nano Banana 3...")
    image_bytes = generate_image_nano_banana(
        client, image_prompt, aspect_ratio, verbose
    )

    # Step 3: Save image
    saved_path = save_image(image_bytes, output_path)
    print(f"✅ Visual saved: {saved_path}")

    return saved_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate graphic visuals from blog post content using Nano Banana 3"
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file', '-f',
        help='Path to blog post markdown file'
    )
    input_group.add_argument(
        '--text', '-t',
        help='Direct text content to visualize'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        default='blog-visual.png',
        help='Output path for generated image (default: blog-visual.png)'
    )

    # Generation options
    parser.add_argument(
        '--aspect-ratio', '-a',
        default='16:9',
        choices=VALID_ASPECT_RATIOS,
        help='Image aspect ratio (default: 16:9)'
    )
    parser.add_argument(
        '--style', '-s',
        help='Style hint for image generation (default: auto-detected)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including generated prompt'
    )

    args = parser.parse_args()

    # Create client
    try:
        client = create_client()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("📷 Blog Visual Generator (Nano Banana 3)")
    print("=" * 50)

    # Get content
    try:
        if args.file:
            print(f"\n📄 Reading: {args.file}")
            content = read_blog_content(args.file)
        else:
            content = args.text
            if len(content) < 100:
                print("⚠️  Warning: Content is short. Results may be generic.")
    except Exception as e:
        print(f"❌ Error reading content: {e}")
        sys.exit(1)

    # Generate visual
    try:
        saved_path = generate_blog_visual(
            client,
            content,
            args.output,
            args.aspect_ratio,
            args.style,
            args.verbose
        )

        print("\n" + "=" * 50)
        print("🎉 Generation complete!")
        print(f"   Output: {saved_path}")

        # Show file size
        file_size = Path(saved_path).stat().st_size / 1024
        print(f"   Size: {file_size:.1f} KB")

    except Exception as e:
        print(f"\n❌ Error generating visual: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
