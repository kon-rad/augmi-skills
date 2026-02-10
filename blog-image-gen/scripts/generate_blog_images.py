#!/usr/bin/env python3
"""
Generate blog post images using Google's Imagen API via Gemini.

Usage:
    # Single prompt
    python generate_blog_images.py --prompt "Your prompt here" --output image.png

    # From prompts file
    python generate_blog_images.py --prompts-file image-prompts.md --output-dir ./images

Requirements:
    pip install google-genai pillow
"""

import os
import sys
import re
import argparse
import time
from pathlib import Path
from typing import Optional, List, Tuple

# Try new google-genai SDK first (recommended)
GENAI_SDK = None
try:
    from google import genai
    from google.genai import types
    GENAI_SDK = "google-genai"
except ImportError:
    pass

# Fall back to older google-generativeai SDK
if GENAI_SDK is None:
    try:
        import google.generativeai as genai_legacy
        GENAI_SDK = "google-generativeai"
    except ImportError:
        pass

if GENAI_SDK is None:
    print("Error: No Google AI SDK found.")
    print("Please install the google-genai package:")
    print("  pip install google-genai")
    sys.exit(1)

try:
    from PIL import Image
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install pillow")


# Model configurations
MODELS = {
    # Imagen 4 models
    "imagen-4": "imagen-4.0-generate-001",
    "imagen-4-standard": "imagen-4.0-generate-001",
    "imagen-4-ultra": "imagen-4.0-ultra-generate-001",
    "imagen-4-fast": "imagen-4.0-fast-generate-001",
    # Imagen 3 fallback
    "imagen-3": "imagen-3.0-generate-002",
    # Gemini native image generation
    "gemini-image": "gemini-2.5-flash-image",
}

DEFAULT_MODEL = "imagen-4"

# Valid aspect ratios
VALID_ASPECT_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9"]


def get_api_key() -> str:
    """Get Google AI API key from environment"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Set GEMINI_API_KEY or GOOGLE_AI_API_KEY environment variable.\n"
            "Get your key at: https://aistudio.google.com/apikey"
        )
    return api_key


def create_client():
    """Create and return a configured Gemini client"""
    if GENAI_SDK is None:
        raise ImportError(
            "google-genai package not installed. Run: pip install google-genai"
        )

    api_key = get_api_key()
    return genai.Client(api_key=api_key)


def resolve_model(model_name: str) -> Tuple[str, str]:
    """
    Resolve model shorthand to full model ID.

    Returns:
        Tuple of (model_type, model_id) where model_type is 'imagen' or 'gemini'
    """
    if model_name in MODELS:
        model_id = MODELS[model_name]
    else:
        model_id = model_name

    # Determine model type
    if "imagen" in model_id.lower():
        return ("imagen", model_id)
    elif "gemini" in model_id.lower():
        return ("gemini", model_id)
    else:
        # Default to imagen
        return ("imagen", model_id)


def generate_image_imagen(
    client: genai.Client,
    prompt: str,
    model: str,
    aspect_ratio: str = "16:9",
    size: str = "1K",
    count: int = 1
) -> List[bytes]:
    """
    Generate images using Imagen models.

    Args:
        client: Gemini client
        prompt: Text prompt for image generation
        model: Full model ID
        aspect_ratio: Image aspect ratio
        size: Image size (1K or 2K)
        count: Number of images to generate (1-4)

    Returns:
        List of image bytes
    """
    print(f"  Using Imagen model: {model}")
    print(f"  Aspect ratio: {aspect_ratio}, Size: {size}")

    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=min(count, 4),
            aspect_ratio=aspect_ratio,
            # Note: image_size only works with Standard/Ultra models
        )
    )

    images = []
    for generated_image in response.generated_images:
        if hasattr(generated_image, 'image') and hasattr(generated_image.image, 'image_bytes'):
            images.append(generated_image.image.image_bytes)

    return images


def generate_image_gemini(
    client: genai.Client,
    prompt: str,
    model: str,
    aspect_ratio: str = "16:9",
    size: str = "1K"
) -> List[bytes]:
    """
    Generate images using Gemini's native image generation (Nano Banana).

    Args:
        client: Gemini client
        prompt: Text prompt for image generation
        model: Full model ID
        aspect_ratio: Image aspect ratio
        size: Image size (1K, 2K, or 4K)

    Returns:
        List of image bytes
    """
    print(f"  Using Gemini model: {model}")
    print(f"  Aspect ratio: {aspect_ratio}, Size: {size}")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=size.upper()
            )
        )
    )

    images = []
    for part in response.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            images.append(part.inline_data.data)

    return images


def generate_image(
    client: genai.Client,
    prompt: str,
    model_name: str = DEFAULT_MODEL,
    aspect_ratio: str = "16:9",
    size: str = "1K",
    count: int = 1
) -> List[bytes]:
    """
    Generate image(s) from a text prompt.

    Args:
        client: Gemini client
        prompt: Text prompt for image generation
        model_name: Model shorthand or full ID
        aspect_ratio: Image aspect ratio
        size: Image size
        count: Number of images (Imagen only)

    Returns:
        List of image bytes
    """
    model_type, model_id = resolve_model(model_name)

    if model_type == "imagen":
        return generate_image_imagen(
            client, prompt, model_id, aspect_ratio, size, count
        )
    else:
        return generate_image_gemini(
            client, prompt, model_id, aspect_ratio, size
        )


def save_image(image_bytes: bytes, output_path: str) -> str:
    """Save image bytes to file"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if PIL_AVAILABLE:
        # Use PIL to ensure proper format
        image = Image.open(BytesIO(image_bytes))
        image.save(output_path)
    else:
        # Direct write
        with open(output_path, 'wb') as f:
            f.write(image_bytes)

    return str(output_path)


def parse_prompts_file(file_path: str) -> List[Tuple[str, str, str]]:
    """
    Parse a markdown file containing image prompts.

    Expected format:
    ## Prompt N: Title

    **Use case:** Description

    ```
    The actual prompt text here
    ```

    Returns:
        List of tuples: (prompt_id, title, prompt_text)
    """
    with open(file_path, 'r') as f:
        content = f.read()

    prompts = []

    # Find all prompt sections
    # Pattern matches: ## Prompt N: Title ... ``` prompt text ```
    pattern = r'##\s*Prompt\s*(\d+)[:\s]*([^\n]*)\n.*?```\n?(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        prompt_num = match[0].strip()
        title = match[1].strip()
        prompt_text = match[2].strip()

        if prompt_text:
            prompts.append((prompt_num, title, prompt_text))

    return prompts


def slugify(text: str) -> str:
    """Convert text to a valid filename slug"""
    # Remove special characters, convert to lowercase, replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug[:50]  # Limit length


def generate_from_prompts_file(
    client: genai.Client,
    prompts_file: str,
    output_dir: str,
    model_name: str = DEFAULT_MODEL,
    aspect_ratio: str = "16:9",
    size: str = "1K",
    delay: float = 0
) -> List[str]:
    """
    Generate images from all prompts in a markdown file.

    Args:
        client: Gemini client
        prompts_file: Path to markdown file with prompts
        output_dir: Directory to save generated images
        model_name: Model to use
        aspect_ratio: Image aspect ratio
        size: Image size
        delay: Delay between requests in seconds

    Returns:
        List of generated image paths
    """
    prompts = parse_prompts_file(prompts_file)

    if not prompts:
        print(f"No prompts found in {prompts_file}")
        print("Expected format: ## Prompt N: Title followed by ```prompt text```")
        return []

    print(f"\nFound {len(prompts)} prompts in {prompts_file}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for i, (prompt_num, title, prompt_text) in enumerate(prompts):
        print(f"\n[{i+1}/{len(prompts)}] Generating: {title or f'Prompt {prompt_num}'}")
        print(f"  Prompt: {prompt_text[:80]}...")

        try:
            images = generate_image(
                client,
                prompt_text,
                model_name,
                aspect_ratio,
                size,
                count=1
            )

            if images:
                # Create filename from prompt number and title
                if title:
                    filename = f"{prompt_num}-{slugify(title)}.png"
                else:
                    filename = f"prompt-{prompt_num}.png"

                file_path = output_path / filename
                saved_path = save_image(images[0], str(file_path))
                generated_files.append(saved_path)
                print(f"  Saved: {saved_path}")
            else:
                print(f"  Warning: No image generated")

        except Exception as e:
            print(f"  Error: {e}")

        # Delay between requests to avoid rate limits
        if delay > 0 and i < len(prompts) - 1:
            time.sleep(delay)

    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate blog images using Google's Imagen API"
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--prompt', '-p',
        help='Single text prompt for image generation'
    )
    input_group.add_argument(
        '--prompts-file', '-f',
        help='Path to markdown file containing prompts'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        default='output.png',
        help='Output path for single image (default: output.png)'
    )
    parser.add_argument(
        '--output-dir', '-d',
        default='.',
        help='Output directory for multiple images (default: current directory)'
    )

    # Generation options
    parser.add_argument(
        '--model', '-m',
        default=DEFAULT_MODEL,
        choices=list(MODELS.keys()),
        help=f'Model to use (default: {DEFAULT_MODEL})'
    )
    parser.add_argument(
        '--aspect-ratio', '-a',
        default='16:9',
        choices=VALID_ASPECT_RATIOS,
        help='Image aspect ratio (default: 16:9)'
    )
    parser.add_argument(
        '--size', '-s',
        default='1K',
        choices=['1K', '2K'],
        help='Image size (default: 1K)'
    )
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='Number of images per prompt (1-4, Imagen only)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0,
        help='Delay between requests in seconds (for rate limiting)'
    )

    args = parser.parse_args()

    # Validate
    if args.count < 1 or args.count > 4:
        parser.error("Count must be between 1 and 4")

    # Create client
    try:
        client = create_client()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"\nBlog Image Generator")
    print(f"Model: {args.model} ({MODELS.get(args.model, args.model)})")
    print("=" * 50)

    if args.prompt:
        # Single prompt mode
        print(f"\nGenerating image from prompt...")
        print(f"Prompt: {args.prompt[:100]}...")

        try:
            images = generate_image(
                client,
                args.prompt,
                args.model,
                args.aspect_ratio,
                args.size,
                args.count
            )

            if images:
                for i, image_bytes in enumerate(images):
                    if len(images) > 1:
                        # Multiple images: add suffix
                        base, ext = os.path.splitext(args.output)
                        output_path = f"{base}-{i+1}{ext}"
                    else:
                        output_path = args.output

                    saved_path = save_image(image_bytes, output_path)
                    print(f"\nImage saved: {saved_path}")
            else:
                print("\nNo images generated")
                sys.exit(1)

        except Exception as e:
            print(f"\nError generating image: {e}")
            sys.exit(1)

    else:
        # Prompts file mode
        generated = generate_from_prompts_file(
            client,
            args.prompts_file,
            args.output_dir,
            args.model,
            args.aspect_ratio,
            args.size,
            args.delay
        )

        print("\n" + "=" * 50)
        print(f"Generation complete!")
        print(f"Images generated: {len(generated)}")

        if generated:
            print(f"\nGenerated files:")
            for path in generated:
                print(f"  - {path}")


if __name__ == "__main__":
    main()
