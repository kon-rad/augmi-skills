#!/usr/bin/env python3
"""
Generate infographics from topics using AI-powered research and design.

Workflow:
1. Research: Gather facts and statistics about the topic
2. Design: AI infographic designer creates an optimized prompt
3. Generate: Nano Banana 3 creates the final infographic

Usage:
    # From topic (with research)
    python generate_infographic.py --topic "The Rise of AI Agents" --output infographic.png

    # From existing content
    python generate_infographic.py --content "Your research here..." --output infographic.png

    # From file
    python generate_infographic.py --file research.md --output infographic.png

Requirements:
    pip install google-genai pillow
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

# Try to import google-genai SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed.")
    print("Please install: pip install google-genai")
    sys.exit(1)

try:
    from PIL import Image
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install pillow")


# Model configurations
RESEARCH_MODEL = "gemini-2.5-flash"  # Fast model for research
DESIGNER_MODEL = "gemini-2.5-flash"  # Designer AI for prompt creation
IMAGE_MODEL = "nano-banana-pro-preview"  # Nano Banana 3 for image generation

# Valid aspect ratios
VALID_ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9"]

# Style templates
STYLE_TEMPLATES = {
    "modern": """
        Modern infographic style with:
        - Clean, bold sans-serif typography
        - Vibrant gradient color palette (blues, purples, teals)
        - Flat design icons and illustrations
        - Strong visual hierarchy
        - Generous white space
        - Subtle shadows for depth
    """,
    "minimal": """
        Minimalist infographic style with:
        - Lots of white/negative space
        - Simple line icons
        - Muted, sophisticated color palette (grays, soft blues)
        - Thin, elegant typography
        - Focus on essential information only
        - Clean geometric shapes
    """,
    "corporate": """
        Professional corporate infographic style with:
        - Traditional business color palette (navy, gray, accent color)
        - Clear data visualizations (charts, graphs)
        - Structured grid layout
        - Professional stock-style imagery feel
        - Conservative typography
        - Credibility-focused design
    """,
    "playful": """
        Playful, engaging infographic style with:
        - Bright, cheerful color palette (yellows, oranges, greens)
        - Hand-drawn or illustrated elements
        - Fun icons and characters
        - Rounded shapes and friendly typography
        - Energetic, dynamic composition
        - Educational and approachable feel
    """,
    "technical": """
        Technical infographic style with:
        - Blueprint or schematic aesthetic
        - Detailed diagrams and flowcharts
        - Monospace or technical fonts
        - Dark background with light elements (or inverse)
        - Precise measurements and annotations
        - Circuit board or network visual elements
    """,
    "dark": """
        Dark mode infographic style with:
        - Dark background (#1a1a2e or similar)
        - Neon accent colors (cyan, magenta, lime)
        - Glowing effects on key elements
        - Futuristic, tech-forward aesthetic
        - High contrast for readability
        - Subtle grid or pattern background
    """
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


def research_topic(client: genai.Client, topic: str, verbose: bool = False) -> str:
    """
    Research a topic using Gemini to gather facts and statistics.

    Args:
        client: Gemini client
        topic: Topic to research
        verbose: Show detailed output

    Returns:
        Structured research content
    """
    print(f"\n📚 Phase 1: Researching topic...")
    print(f"   Topic: {topic}")

    research_prompt = f"""You are a research assistant gathering information for an infographic.

Research the following topic and provide structured, factual information that would be compelling in a visual infographic format.

TOPIC: {topic}

Provide your research in this structure:

## Key Statistics
- List 4-6 compelling statistics with sources where possible
- Focus on numbers that tell a story
- Include percentages, dollar amounts, time comparisons

## Main Points
- 3-5 key facts or insights about the topic
- Each point should be concise and memorable
- Focus on what's most important or surprising

## Timeline/Milestones (if applicable)
- Key dates or progression
- Historical context if relevant

## Comparisons
- Before/after comparisons
- Industry comparisons
- Geographic or demographic differences

## Quotes or Expert Insights
- 1-2 notable quotes from experts
- Include attribution

## Visual Concepts
- Suggest 2-3 visual metaphors that could represent this topic
- What imagery captures the essence of this information?

Keep all information factual and suitable for a professional infographic.
Today's date is {datetime.now().strftime('%B %d, %Y')}.
"""

    response = client.models.generate_content(
        model=RESEARCH_MODEL,
        contents=research_prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2000
        )
    )

    research = response.text

    if verbose:
        print(f"\n   Research Output:\n{'-'*40}")
        print(research[:500] + "..." if len(research) > 500 else research)
        print(f"{'-'*40}")

    print(f"   ✓ Research complete ({len(research)} chars)")
    return research


def design_infographic_prompt(
    client: genai.Client,
    content: str,
    style: str = "modern",
    aspect_ratio: str = "16:9",
    verbose: bool = False
) -> str:
    """
    Use AI infographic designer to create an optimized image generation prompt.

    Args:
        client: Gemini client
        content: Research content to visualize
        style: Visual style for the infographic
        aspect_ratio: Target aspect ratio
        verbose: Show detailed output

    Returns:
        Optimized prompt for image generation
    """
    print(f"\n🎨 Phase 2: Designing infographic...")
    print(f"   Style: {style}")
    print(f"   Aspect ratio: {aspect_ratio}")

    style_guidance = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["modern"])

    designer_prompt = f"""You are an expert infographic designer. Your task is to create a detailed prompt for an AI image generator to create a stunning infographic.

CONTENT TO VISUALIZE:
{content}

STYLE REQUIREMENTS:
{style_guidance}

ASPECT RATIO: {aspect_ratio}

Create a detailed image generation prompt that will produce a professional infographic. Your prompt should specify:

1. HEADLINE: A compelling title/headline for the infographic (short, impactful)

2. LAYOUT: Describe the overall composition and flow
   - Where elements are positioned
   - Visual hierarchy (what draws attention first)
   - How information flows (top to bottom, left to right, etc.)

3. COLOR PALETTE: Specific colors that work together
   - Primary color
   - Secondary color
   - Accent color
   - Background color

4. VISUAL ELEMENTS:
   - Icons and symbols to use
   - Charts or graphs if data is involved
   - Illustrations or imagery
   - Decorative elements

5. TYPOGRAPHY FEEL:
   - Bold vs subtle
   - Modern vs classic
   - How text is emphasized

6. DATA VISUALIZATION:
   - How to represent any statistics
   - Chart types (bar, pie, line, etc.)
   - Number callouts

7. MOOD AND TONE:
   - Professional, playful, urgent, inspirational, etc.

Write the prompt as a single, detailed paragraph that an image AI can use directly. Do NOT include any preamble or explanation - just output the prompt itself.

The prompt should be 150-300 words, highly descriptive, and focus on visual elements that can be rendered in a single static image.
"""

    response = client.models.generate_content(
        model=DESIGNER_MODEL,
        contents=designer_prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=1000
        )
    )

    prompt = response.text.strip()

    # Clean up the prompt if it has any preamble
    if prompt.lower().startswith("here"):
        lines = prompt.split("\n")
        prompt = "\n".join(lines[1:]).strip()

    if verbose:
        print(f"\n   Designer Prompt:\n{'-'*40}")
        print(prompt)
        print(f"{'-'*40}")

    print(f"   ✓ Design complete ({len(prompt)} chars)")
    return prompt


def generate_infographic_image(
    client: genai.Client,
    prompt: str,
    aspect_ratio: str = "16:9",
    verbose: bool = False
) -> bytes:
    """
    Generate the infographic image using Nano Banana 3.

    Args:
        client: Gemini client
        prompt: Optimized image prompt
        aspect_ratio: Target aspect ratio
        verbose: Show detailed output

    Returns:
        Image bytes
    """
    print(f"\n🖼️  Phase 3: Generating infographic...")
    print(f"   Model: {IMAGE_MODEL}")

    # Enhance prompt for infographic-specific generation
    full_prompt = f"""Create a professional infographic image:

{prompt}

Important: This should be a complete, polished infographic with clear text, icons, and data visualizations. The text should be readable and the layout should be balanced and professional."""

    if verbose:
        print(f"\n   Full prompt:\n{'-'*40}")
        print(full_prompt[:300] + "...")
        print(f"{'-'*40}")

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=full_prompt,
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
            print(f"   ✓ Image generated successfully")
            return part.inline_data.data

    raise ValueError("No image was generated in the response")


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


def save_text(content: str, output_path: str) -> str:
    """Save text content to file"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(content)

    return str(output_path)


def read_file(file_path: str) -> str:
    """Read content from a file"""
    with open(file_path, 'r') as f:
        return f.read()


def generate_infographic(
    topic: Optional[str] = None,
    content: Optional[str] = None,
    file_path: Optional[str] = None,
    output_path: str = "infographic.png",
    style: str = "modern",
    aspect_ratio: str = "16:9",
    verbose: bool = False,
    save_research: bool = False,
    save_prompt: bool = False
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Main function to generate an infographic.

    Args:
        topic: Topic to research (triggers research phase)
        content: Direct content to visualize
        file_path: Path to file with content
        output_path: Where to save the generated image
        style: Visual style
        aspect_ratio: Image aspect ratio
        verbose: Show detailed output
        save_research: Save research to file
        save_prompt: Save generated prompt to file

    Returns:
        Tuple of (image_path, research_path, prompt_path)
    """
    # Create client
    client = create_client()

    print("\n" + "="*50)
    print("🎯 INFOGRAPHIC GENERATOR")
    print("="*50)

    # Determine content source
    if topic:
        # Research phase
        research_content = research_topic(client, topic, verbose)
        content = research_content
    elif file_path:
        print(f"\n📄 Reading content from file: {file_path}")
        content = read_file(file_path)
        print(f"   ✓ Loaded {len(content)} chars")
    elif content:
        print(f"\n📝 Using provided content ({len(content)} chars)")
    else:
        raise ValueError("Must provide --topic, --content, or --file")

    # Design phase
    design_prompt = design_infographic_prompt(
        client, content, style, aspect_ratio, verbose
    )

    # Generation phase
    image_bytes = generate_infographic_image(
        client, design_prompt, aspect_ratio, verbose
    )

    # Save outputs
    image_path = save_image(image_bytes, output_path)
    print(f"\n💾 Saved infographic: {image_path}")

    research_path = None
    prompt_path = None

    if save_research and topic:
        base_path = Path(output_path).parent
        research_path = save_text(
            content,
            str(base_path / "research.md")
        )
        print(f"   Saved research: {research_path}")

    if save_prompt:
        base_path = Path(output_path).parent
        prompt_path = save_text(
            design_prompt,
            str(base_path / "prompt.txt")
        )
        print(f"   Saved prompt: {prompt_path}")

    print("\n" + "="*50)
    print("✅ INFOGRAPHIC GENERATION COMPLETE")
    print("="*50 + "\n")

    return image_path, research_path, prompt_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate infographics from topics using AI research and design"
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--topic', '-t',
        help='Topic to research and visualize'
    )
    input_group.add_argument(
        '--content', '-c',
        help='Direct content to visualize (skip research)'
    )
    input_group.add_argument(
        '--file', '-f',
        help='Path to file with content to visualize'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        default='infographic.png',
        help='Output path for generated image (default: infographic.png)'
    )

    # Style options
    parser.add_argument(
        '--style', '-s',
        default='modern',
        choices=list(STYLE_TEMPLATES.keys()),
        help='Infographic style (default: modern)'
    )
    parser.add_argument(
        '--aspect-ratio', '-a',
        default='16:9',
        choices=VALID_ASPECT_RATIOS,
        help='Image aspect ratio (default: 16:9)'
    )

    # Debug/save options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including prompts'
    )
    parser.add_argument(
        '--save-research',
        action='store_true',
        help='Save research content to file'
    )
    parser.add_argument(
        '--save-prompt',
        action='store_true',
        help='Save generated design prompt to file'
    )

    args = parser.parse_args()

    try:
        generate_infographic(
            topic=args.topic,
            content=args.content,
            file_path=args.file,
            output_path=args.output,
            style=args.style,
            aspect_ratio=args.aspect_ratio,
            verbose=args.verbose,
            save_research=args.save_research,
            save_prompt=args.save_prompt
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
