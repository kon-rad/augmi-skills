#!/usr/bin/env python3
"""
Augmi Instagram Carousel Image Generator (v2)

Generates branded 1080x1350px (4:5 portrait) Instagram carousel slides from
markdown content and a cover image. Supports multiple slide types: Cover,
Content, List, Stat, Quote, and CTA.

See: content/instagram-carousel/STYLE-GUIDE.md for design rationale.

Usage:
    python3 generate_carousel.py \
        --markdown path/to/instagram-carousel.md \
        --cover-image path/to/cover.png \
        --output-dir path/to/output/ \
        --logo path/to/augmi-logo.png
"""

import argparse
import math
import os
import re
import sys
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow is required. Install with: pip3 install pillow --break-system-packages")
    sys.exit(1)

# --- Constants ---
SLIDE_WIDTH = 1080
SLIDE_HEIGHT = 1350  # 4:5 portrait for maximum feed real estate
SLIDE_SIZE = (SLIDE_WIDTH, SLIDE_HEIGHT)

PADDING = 80
LOGO_PADDING = 50
LOGO_ICON_SIZE = 48
LOGO_TEXT_GAP = 12

# Brand colors
BG_COLOR = (9, 9, 11)           # #09090b
WHITE = (255, 255, 255)
CYAN = (6, 182, 212)            # #06b6d4
EMERALD = (16, 185, 129)        # #10b981
ZINC_300 = (212, 212, 216)      # #d4d4d8
ZINC_500 = (113, 113, 122)      # #71717a
ZINC_800 = (39, 39, 42)         # #27272a

# Font sizes (tuned for 1080x1350 portrait)
COVER_TITLE_SIZE = 76
COVER_SUBTEXT_SIZE = 38
CONTENT_HEADLINE_SIZE = 68
CONTENT_DETAIL_SIZE = 40
LIST_ITEM_SIZE = 44
LIST_NUMBER_SIZE = 52
STAT_NUMBER_SIZE = 120
STAT_LABEL_SIZE = 40
STAT_DETAIL_SIZE = 36
QUOTE_TEXT_SIZE = 48
QUOTE_ATTR_SIZE = 32
CTA_HEADLINE_SIZE = 64
CTA_SUBTEXT_SIZE = 36
LOGO_TEXT_SIZE = 24
COUNTER_SIZE = 22
SWIPE_TEXT_SIZE = 24

# Visual element sizes
ACCENT_LINE_HEIGHT = 4
ACCENT_LINE_WIDTH = 120
GRADIENT_STRIP_HEIGHT = 5
NUMBER_CIRCLE_SIZE = 64
QUOTE_MARK_SIZE = 100

# Paths
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
DEFAULT_LOGO = ASSETS_DIR / "augmi-logo.png"
FONT_DIR = ASSETS_DIR

INTER_BOLD = FONT_DIR / "Inter-Bold.ttf"
INTER_REGULAR = FONT_DIR / "Inter-Regular.ttf"

# Google Fonts CDN URLs for Inter
INTER_BOLD_URL = "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuFuYMZhrib2Bg-4.ttf"
INTER_REGULAR_URL = "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZhrib2Bg-4.ttf"


def ensure_fonts():
    """Download Inter fonts if not present."""
    for font_path, url, name in [
        (INTER_BOLD, INTER_BOLD_URL, "Inter-Bold"),
        (INTER_REGULAR, INTER_REGULAR_URL, "Inter-Regular"),
    ]:
        if not font_path.exists():
            print(f"Downloading {name} font...")
            font_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                urllib.request.urlretrieve(url, font_path)
                print(f"  Saved to {font_path}")
            except Exception as e:
                print(f"  Warning: Could not download {name}: {e}")
                print(f"  Will use default font as fallback")


def ensure_logo():
    """Generate Augmi logo if not present."""
    if DEFAULT_LOGO.exists():
        return
    print("Generating Augmi logo...")
    DEFAULT_LOGO.parent.mkdir(parents=True, exist_ok=True)
    generate_augmi_logo(DEFAULT_LOGO, size=200)
    print(f"  Saved to {DEFAULT_LOGO}")


def generate_augmi_logo(output_path: Path, size: int = 200):
    """Generate the Augmi isometric cube logo programmatically."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    corner_radius = size // 5
    for y in range(size):
        ratio = y / size
        r = int(CYAN[0] + (EMERALD[0] - CYAN[0]) * ratio)
        g = int(CYAN[1] + (EMERALD[1] - CYAN[1]) * ratio)
        b = int(CYAN[2] + (EMERALD[2] - CYAN[2]) * ratio)
        draw.line([(0, y), (size - 1, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=corner_radius, fill=255)
    img.putalpha(mask)

    icon_size = int(size * 0.6)
    offset_x = (size - icon_size) // 2
    offset_y = (size - icon_size) // 2
    scale = icon_size / 24.0

    def svg_pt(x, y):
        return (offset_x + x * scale, offset_y + y * scale)

    icon_color = (0, 0, 0, 230)
    line_width = max(2, int(size * 0.02))

    diamond = [svg_pt(12, 2), svg_pt(2, 7), svg_pt(12, 12), svg_pt(22, 7)]
    draw.polygon(diamond, fill=icon_color)
    draw.line([svg_pt(2, 17), svg_pt(12, 22), svg_pt(22, 17)], fill=icon_color, width=line_width)
    draw.line([svg_pt(2, 12), svg_pt(12, 17), svg_pt(22, 12)], fill=icon_color, width=line_width)
    draw.line([svg_pt(2, 7), svg_pt(2, 17)], fill=icon_color, width=line_width)
    draw.line([svg_pt(12, 12), svg_pt(12, 22)], fill=icon_color, width=line_width)
    draw.line([svg_pt(22, 7), svg_pt(22, 17)], fill=icon_color, width=line_width)

    img.save(output_path, "PNG")


def load_font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    """Load Inter font at given size, falling back to default if unavailable."""
    font_path = INTER_BOLD if bold else INTER_REGULAR
    try:
        return ImageFont.truetype(str(font_path), size)
    except (OSError, IOError):
        print(f"  Warning: Font not found at {font_path}, using default")
        return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width and current_line:
            current_line.append(word)
        elif not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def text_height(text: str, font: ImageFont.FreeTypeFont) -> int:
    """Get the pixel height of a text string."""
    bbox = font.getbbox(text)
    return bbox[3] - bbox[1]


def text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
    """Get the pixel width of a text string."""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


# --- Visual Elements ---

def draw_gradient_strip(draw: ImageDraw.Draw, y: int, width: int):
    """Draw a thin cyan-to-emerald gradient strip across the slide."""
    for x in range(width):
        ratio = x / width
        r = int(CYAN[0] + (EMERALD[0] - CYAN[0]) * ratio)
        g = int(CYAN[1] + (EMERALD[1] - CYAN[1]) * ratio)
        b = int(CYAN[2] + (EMERALD[2] - CYAN[2]) * ratio)
        for dy in range(GRADIENT_STRIP_HEIGHT):
            draw.point((x, y + dy), fill=(r, g, b))


def draw_accent_line(draw: ImageDraw.Draw, x: int, y: int):
    """Draw a short accent line (cyan) to add visual structure."""
    draw.rectangle(
        [x, y, x + ACCENT_LINE_WIDTH, y + ACCENT_LINE_HEIGHT],
        fill=CYAN,
    )


def draw_number_circle(draw: ImageDraw.Draw, x: int, y: int, number: int, font: ImageFont.FreeTypeFont):
    """Draw a filled circle with a number inside (for list items)."""
    # Draw filled cyan circle
    draw.ellipse(
        [x, y, x + NUMBER_CIRCLE_SIZE, y + NUMBER_CIRCLE_SIZE],
        fill=CYAN,
    )
    # Draw number centered in circle
    num_text = str(number)
    num_w = text_width(num_text, font)
    num_h = text_height(num_text, font)
    num_x = x + (NUMBER_CIRCLE_SIZE - num_w) // 2
    num_y = y + (NUMBER_CIRCLE_SIZE - num_h) // 2 - 2  # slight upward nudge
    draw.text((num_x, num_y), num_text, fill=BG_COLOR, font=font)


def draw_swipe_cue(draw: ImageDraw.Draw, slide_width: int, slide_height: int):
    """Draw a 'Swipe' text + arrow cue at the bottom center."""
    font = load_font(bold=False, size=SWIPE_TEXT_SIZE)
    swipe_text = "Swipe"
    sw = text_width(swipe_text, font)

    # Arrow characters
    arrow = ">>>"
    aw = text_width(arrow, font)

    total_w = sw + 12 + aw
    x = (slide_width - total_w) // 2
    y = slide_height - LOGO_PADDING - SWIPE_TEXT_SIZE - 10

    draw.text((x, y), swipe_text, fill=ZINC_500, font=font)
    draw.text((x + sw + 12, y), arrow, fill=CYAN, font=font)


def draw_logo_header(draw: ImageDraw.Draw, logo_img: Image.Image, y_offset: int = 0):
    """Draw the Augmi logo + 'augmi.world' text in the top-left corner."""
    x = LOGO_PADDING
    y = LOGO_PADDING + y_offset

    logo_resized = logo_img.copy()
    logo_resized = logo_resized.resize((LOGO_ICON_SIZE, LOGO_ICON_SIZE), Image.LANCZOS)

    font = load_font(bold=True, size=LOGO_TEXT_SIZE)
    text_x = x + LOGO_ICON_SIZE + LOGO_TEXT_GAP
    text_y = y + (LOGO_ICON_SIZE - LOGO_TEXT_SIZE) // 2

    draw.text((text_x, text_y), "augmi.world", fill=WHITE, font=font)

    return logo_resized, (x, y)


def draw_slide_counter(draw: ImageDraw.Draw, slide_num: int, total_slides: int):
    """Draw slide counter in bottom-right."""
    counter_font = load_font(bold=False, size=COUNTER_SIZE)
    counter_text = f"{slide_num} / {total_slides}"
    cw = text_width(counter_text, counter_font)
    counter_x = SLIDE_WIDTH - LOGO_PADDING - cw
    counter_y = SLIDE_HEIGHT - LOGO_PADDING - COUNTER_SIZE
    draw.text((counter_x, counter_y), counter_text, fill=ZINC_500, font=counter_font)


def paste_logo(img: Image.Image, draw: ImageDraw.Draw, logo_path: str):
    """Load, draw, and paste the logo onto an RGBA image."""
    logo_img = Image.open(logo_path).convert("RGBA")
    logo_resized, logo_pos = draw_logo_header(draw, logo_img)
    img.paste(logo_resized, logo_pos, logo_resized)


# --- Content Area Helpers ---

def content_area():
    """Return (top, bottom) y coordinates for the usable content area."""
    top = LOGO_PADDING + LOGO_ICON_SIZE + 80
    bottom = SLIDE_HEIGHT - LOGO_PADDING - COUNTER_SIZE - 50
    return top, bottom


# --- Slide Creators ---

def resize_and_crop(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Resize and center-crop image to fill target size."""
    target_w, target_h = target_size
    img_w, img_h = img.size
    target_ratio = target_w / target_h
    img_ratio = img_w / img_h

    if img_ratio > target_ratio:
        new_h = target_h
        new_w = int(img_w * (target_h / img_h))
    else:
        new_w = target_w
        new_h = int(img_h * (target_w / img_w))

    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

    return img


def create_cover_slide(
    cover_image_path: str,
    title: str,
    subtext: str,
    logo_path: str,
    show_swipe: bool = True,
) -> Image.Image:
    """
    Create the cover slide (Slide 1).
    Full-bleed cover image, gradient overlay, title + subtext, logo, optional swipe cue.
    """
    cover = Image.open(cover_image_path).convert("RGBA")
    cover = resize_and_crop(cover, SLIDE_SIZE)

    # Gradient overlay: transparent top -> dark bottom (starts at 45% for taller slide)
    gradient = Image.new("RGBA", SLIDE_SIZE, (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)

    gradient_start = int(SLIDE_HEIGHT * 0.45)
    for y in range(gradient_start, SLIDE_HEIGHT):
        progress = (y - gradient_start) / (SLIDE_HEIGHT - gradient_start)
        alpha = int(230 * progress)
        gradient_draw.line(
            [(0, y), (SLIDE_WIDTH, y)],
            fill=(BG_COLOR[0], BG_COLOR[1], BG_COLOR[2], alpha),
        )

    cover = Image.alpha_composite(cover, gradient)
    draw = ImageDraw.Draw(cover)

    title_font = load_font(bold=True, size=COVER_TITLE_SIZE)
    subtext_font = load_font(bold=False, size=COVER_SUBTEXT_SIZE)

    max_text_width = SLIDE_WIDTH - (PADDING * 2)

    # Wrap title
    title_lines = wrap_text(title, title_font, max_text_width)
    title_lines = title_lines[:3]  # Max 3 lines

    line_height_title = int(COVER_TITLE_SIZE * 1.3)
    line_height_subtext = int(COVER_SUBTEXT_SIZE * 1.3)

    total_height = len(title_lines) * line_height_title
    if subtext:
        total_height += line_height_subtext + 16

    # Position text in bottom 40%
    text_area_top = int(SLIDE_HEIGHT * 0.60)
    text_area_bottom = SLIDE_HEIGHT - (LOGO_PADDING + 60 if show_swipe else PADDING)
    y = text_area_top + (text_area_bottom - text_area_top - total_height) // 2

    for line in title_lines:
        lw = text_width(line, title_font)
        x = (SLIDE_WIDTH - lw) // 2
        draw.text((x, y), line, fill=WHITE, font=title_font)
        y += line_height_title

    if subtext:
        y += 16
        sw = text_width(subtext, subtext_font)
        x = (SLIDE_WIDTH - sw) // 2
        draw.text((x, y), subtext, fill=(255, 255, 255, 204), font=subtext_font)

    # Swipe cue
    if show_swipe:
        draw_swipe_cue(draw, SLIDE_WIDTH, SLIDE_HEIGHT)

    # Logo
    paste_logo(cover, draw, logo_path)

    return cover.convert("RGB")


def create_content_slide(
    headline: str,
    detail: str,
    slide_num: int,
    total_slides: int,
    logo_path: str,
    show_swipe: bool = False,
) -> Image.Image:
    """
    Create a content slide (headline + detail paragraph).
    Dark background, accent line, left-aligned text.
    """
    img = Image.new("RGBA", SLIDE_SIZE, (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # Gradient strip at top
    draw_gradient_strip(draw, 0, SLIDE_WIDTH)

    # Logo
    paste_logo(img, draw, logo_path)

    headline_font = load_font(bold=True, size=CONTENT_HEADLINE_SIZE)
    detail_font = load_font(bold=False, size=CONTENT_DETAIL_SIZE)

    max_text_width = SLIDE_WIDTH - (PADDING * 2)
    c_top, c_bottom = content_area()

    line_h_headline = int(CONTENT_HEADLINE_SIZE * 1.4)
    line_h_detail = int(CONTENT_DETAIL_SIZE * 1.7)

    headline_lines = wrap_text(headline, headline_font, max_text_width)
    headline_lines = headline_lines[:3]

    detail_lines = []
    if detail:
        all_detail_lines = wrap_text(detail, detail_font, max_text_width)
        detail_lines = all_detail_lines[:6]
        if len(all_detail_lines) > 6:
            detail_lines[-1] = detail_lines[-1].rstrip() + "..."

    # Calculate total content height
    headline_block = len(headline_lines) * line_h_headline
    accent_block = ACCENT_LINE_HEIGHT + 40  # accent line + gap
    detail_block = len(detail_lines) * line_h_detail if detail_lines else 0
    gap = 40 if detail_lines else 0
    total_h = headline_block + accent_block + gap + detail_block

    # Vertically center
    available = c_bottom - c_top
    y = c_top + (available - total_h) // 2

    # Draw headline
    for line in headline_lines:
        draw.text((PADDING, y), line, fill=CYAN, font=headline_font)
        y += line_h_headline

    # Accent line below headline
    y += 20
    draw_accent_line(draw, PADDING, y)
    y += ACCENT_LINE_HEIGHT + 20

    # Detail text
    if detail_lines:
        y += gap
        for line in detail_lines:
            draw.text((PADDING, y), line, fill=ZINC_300, font=detail_font)
            y += line_h_detail

    # Counter
    draw_slide_counter(draw, slide_num, total_slides)

    # Swipe cue on slide 2
    if show_swipe:
        draw_swipe_cue(draw, SLIDE_WIDTH, SLIDE_HEIGHT)

    return img.convert("RGB")


def create_list_slide(
    headline: str,
    items: list[str],
    slide_num: int,
    total_slides: int,
    logo_path: str,
) -> Image.Image:
    """
    Create a list slide with numbered circles + items.
    """
    img = Image.new("RGBA", SLIDE_SIZE, (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient_strip(draw, 0, SLIDE_WIDTH)
    paste_logo(img, draw, logo_path)

    headline_font = load_font(bold=True, size=CONTENT_HEADLINE_SIZE)
    item_font = load_font(bold=False, size=LIST_ITEM_SIZE)
    number_font = load_font(bold=True, size=LIST_NUMBER_SIZE)

    max_text_width = SLIDE_WIDTH - (PADDING * 2)
    item_text_width = max_text_width - NUMBER_CIRCLE_SIZE - 24  # circle + gap
    c_top, c_bottom = content_area()

    line_h_headline = int(CONTENT_HEADLINE_SIZE * 1.4)
    line_h_item = int(LIST_ITEM_SIZE * 1.5)
    item_gap = 36

    # Wrap headline
    headline_lines = wrap_text(headline, headline_font, max_text_width)
    headline_lines = headline_lines[:2]

    # Wrap each item
    wrapped_items = []
    for item in items[:5]:  # Max 5 items per slide
        lines = wrap_text(item, item_font, item_text_width)
        wrapped_items.append(lines[:3])  # Max 3 lines per item

    # Calculate heights
    headline_block = len(headline_lines) * line_h_headline
    accent_block = ACCENT_LINE_HEIGHT + 50
    items_block = sum(len(lines) * line_h_item for lines in wrapped_items)
    items_block += (len(wrapped_items) - 1) * item_gap if wrapped_items else 0

    total_h = headline_block + accent_block + items_block
    available = c_bottom - c_top
    y = c_top + (available - total_h) // 2

    # Draw headline
    for line in headline_lines:
        draw.text((PADDING, y), line, fill=CYAN, font=headline_font)
        y += line_h_headline

    # Accent line
    y += 24
    draw_accent_line(draw, PADDING, y)
    y += ACCENT_LINE_HEIGHT + 26

    # Draw items
    # Use a smaller font for the number inside the circle
    circle_num_font = load_font(bold=True, size=32)
    for i, lines in enumerate(wrapped_items):
        circle_y = y + (line_h_item - NUMBER_CIRCLE_SIZE) // 2
        draw_number_circle(draw, PADDING, circle_y, i + 1, circle_num_font)

        text_x = PADDING + NUMBER_CIRCLE_SIZE + 24
        for line in lines:
            draw.text((text_x, y), line, fill=WHITE, font=item_font)
            y += line_h_item

        y += item_gap

    draw_slide_counter(draw, slide_num, total_slides)

    return img.convert("RGB")


def create_stat_slide(
    number: str,
    label: str,
    detail: str,
    slide_num: int,
    total_slides: int,
    logo_path: str,
) -> Image.Image:
    """
    Create a stat slide with a large number/metric + context.
    """
    img = Image.new("RGBA", SLIDE_SIZE, (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient_strip(draw, 0, SLIDE_WIDTH)
    paste_logo(img, draw, logo_path)

    number_font = load_font(bold=True, size=STAT_NUMBER_SIZE)
    label_font = load_font(bold=True, size=STAT_LABEL_SIZE)
    detail_font = load_font(bold=False, size=STAT_DETAIL_SIZE)

    max_text_width = SLIDE_WIDTH - (PADDING * 2)
    c_top, c_bottom = content_area()

    # Calculate text dimensions
    num_w = text_width(number, number_font)
    num_h = text_height(number, number_font)

    label_lines = wrap_text(label, label_font, max_text_width) if label else []
    label_lines = label_lines[:2]
    line_h_label = int(STAT_LABEL_SIZE * 1.4)

    detail_lines = wrap_text(detail, detail_font, max_text_width) if detail else []
    detail_lines = detail_lines[:3]
    line_h_detail = int(STAT_DETAIL_SIZE * 1.6)

    # Total height
    total_h = num_h + 30  # number + gap
    if label_lines:
        total_h += len(label_lines) * line_h_label + 20
    total_h += ACCENT_LINE_HEIGHT + 40  # accent line + gaps
    if detail_lines:
        total_h += len(detail_lines) * line_h_detail

    available = c_bottom - c_top
    y = c_top + (available - total_h) // 2

    # Draw large number (centered)
    num_x = (SLIDE_WIDTH - num_w) // 2
    draw.text((num_x, y), number, fill=CYAN, font=number_font)
    y += num_h + 30

    # Label (centered)
    if label_lines:
        for line in label_lines:
            lw = text_width(line, label_font)
            lx = (SLIDE_WIDTH - lw) // 2
            draw.text((lx, y), line, fill=WHITE, font=label_font)
            y += line_h_label
        y += 20

    # Accent line (centered)
    line_x = (SLIDE_WIDTH - ACCENT_LINE_WIDTH) // 2
    draw_accent_line(draw, line_x, y)
    y += ACCENT_LINE_HEIGHT + 40

    # Detail (centered)
    if detail_lines:
        for line in detail_lines:
            lw = text_width(line, detail_font)
            lx = (SLIDE_WIDTH - lw) // 2
            draw.text((lx, y), line, fill=ZINC_300, font=detail_font)
            y += line_h_detail

    draw_slide_counter(draw, slide_num, total_slides)

    return img.convert("RGB")


def create_quote_slide(
    quote: str,
    attribution: str,
    slide_num: int,
    total_slides: int,
    logo_path: str,
) -> Image.Image:
    """
    Create a quote slide with large decorative quote marks.
    """
    img = Image.new("RGBA", SLIDE_SIZE, (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient_strip(draw, 0, SLIDE_WIDTH)
    paste_logo(img, draw, logo_path)

    quote_font = load_font(bold=False, size=QUOTE_TEXT_SIZE)
    attr_font = load_font(bold=True, size=QUOTE_ATTR_SIZE)
    mark_font = load_font(bold=True, size=QUOTE_MARK_SIZE)

    max_text_width = SLIDE_WIDTH - (PADDING * 2) - 40  # Extra inset for quote
    c_top, c_bottom = content_area()

    line_h_quote = int(QUOTE_TEXT_SIZE * 1.6)
    line_h_attr = int(QUOTE_ATTR_SIZE * 1.4)

    quote_lines = wrap_text(quote, quote_font, max_text_width)
    quote_lines = quote_lines[:6]

    # Decorative opening quote mark
    mark_h = text_height("\u201C", mark_font)

    total_h = mark_h + 20 + len(quote_lines) * line_h_quote + 40
    if attribution:
        total_h += line_h_attr

    available = c_bottom - c_top
    y = c_top + (available - total_h) // 2

    # Opening quote mark (large, muted)
    draw.text((PADDING, y), "\u201C", fill=ZINC_800, font=mark_font)
    y += mark_h + 20

    # Quote text (left-aligned with indent)
    quote_x = PADDING + 20
    for line in quote_lines:
        draw.text((quote_x, y), line, fill=WHITE, font=quote_font)
        y += line_h_quote

    # Attribution
    if attribution:
        y += 40
        # Accent line before attribution
        draw_accent_line(draw, quote_x, y)
        y += ACCENT_LINE_HEIGHT + 20
        draw.text((quote_x, y), attribution, fill=ZINC_300, font=attr_font)

    draw_slide_counter(draw, slide_num, total_slides)

    return img.convert("RGB")


def create_cta_slide(
    headline: str,
    subtext: str,
    action: str,
    logo_path: str,
    total_slides: int,
) -> Image.Image:
    """
    Create a CTA (call-to-action) slide. Center-aligned, prominent branding.
    """
    img = Image.new("RGBA", SLIDE_SIZE, (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient_strip(draw, 0, SLIDE_WIDTH)

    headline_font = load_font(bold=True, size=CTA_HEADLINE_SIZE)
    subtext_font = load_font(bold=False, size=CTA_SUBTEXT_SIZE)
    action_font = load_font(bold=True, size=CTA_SUBTEXT_SIZE)

    max_text_width = SLIDE_WIDTH - (PADDING * 2)
    c_top, c_bottom = content_area()

    line_h_headline = int(CTA_HEADLINE_SIZE * 1.4)
    line_h_sub = int(CTA_SUBTEXT_SIZE * 1.4)

    headline_lines = wrap_text(headline, headline_font, max_text_width)
    headline_lines = headline_lines[:3]

    # Calculate total height for centering
    # Large logo at top
    large_logo_size = 96
    total_h = large_logo_size + 40  # logo + gap
    total_h += len(headline_lines) * line_h_headline + 20
    if subtext:
        total_h += line_h_sub + 20
    total_h += ACCENT_LINE_HEIGHT + 40
    if action:
        total_h += line_h_sub

    available = c_bottom - c_top
    y = c_top + (available - total_h) // 2

    # Large centered logo
    logo_img = Image.open(logo_path).convert("RGBA")
    logo_large = logo_img.resize((large_logo_size, large_logo_size), Image.LANCZOS)
    logo_x = (SLIDE_WIDTH - large_logo_size) // 2
    img.paste(logo_large, (logo_x, y), logo_large)
    y += large_logo_size + 40

    # Headline (centered)
    for line in headline_lines:
        lw = text_width(line, headline_font)
        lx = (SLIDE_WIDTH - lw) // 2
        draw.text((lx, y), line, fill=WHITE, font=headline_font)
        y += line_h_headline

    # Subtext
    if subtext:
        y += 20
        sw = text_width(subtext, subtext_font)
        sx = (SLIDE_WIDTH - sw) // 2
        draw.text((sx, y), subtext, fill=CYAN, font=subtext_font)
        y += line_h_sub

    # Accent line
    y += 20
    line_x = (SLIDE_WIDTH - ACCENT_LINE_WIDTH) // 2
    draw_accent_line(draw, line_x, y)
    y += ACCENT_LINE_HEIGHT + 40

    # Action text
    if action:
        aw = text_width(action, action_font)
        ax = (SLIDE_WIDTH - aw) // 2
        draw.text((ax, y), action, fill=ZINC_300, font=action_font)

    # Counter
    draw_slide_counter(draw, total_slides, total_slides)

    # Small logo in top-left too
    small_logo = logo_img.resize((LOGO_ICON_SIZE, LOGO_ICON_SIZE), Image.LANCZOS)
    img.paste(small_logo, (LOGO_PADDING, LOGO_PADDING), small_logo)
    logo_text_font = load_font(bold=True, size=LOGO_TEXT_SIZE)
    draw.text(
        (LOGO_PADDING + LOGO_ICON_SIZE + LOGO_TEXT_GAP, LOGO_PADDING + (LOGO_ICON_SIZE - LOGO_TEXT_SIZE) // 2),
        "augmi.world",
        fill=WHITE,
        font=logo_text_font,
    )

    return img.convert("RGB")


# --- Markdown Parser ---

def parse_carousel_markdown(path: str) -> dict:
    """
    Parse instagram-carousel.md into structured data.
    Supports slide types: Cover, Content, List, Stat, Quote, CTA, Final.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {
        "title": "",
        "slides": [],
        "caption": "",
        "hashtags": "",
        "image_prompt": "",
    }

    # Extract title
    title_match = re.search(r"^#\s+Instagram Carousel:\s*(.+)$", content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Split into sections by ---
    sections = re.split(r"\n---\n", content)

    # Parse slides from first section
    slides_section = sections[0] if sections else content
    slide_blocks = re.split(r"^##\s+Slide\s+\d+", slides_section, flags=re.MULTILINE)

    for block in slide_blocks[1:]:
        slide = {
            "type": "content",  # default
            "text": "",
            "subtext": "",
            "detail": "",
            "action": "",
            "items": [],
            "number": "",
            "quote": "",
            "attribution": "",
        }

        # Detect slide type from annotation like (Cover), (List), (Stat), (Quote), (CTA), (Final)
        type_match = re.match(r"\s*\((\w+)\)", block)
        if type_match:
            type_label = type_match.group(1).lower()
            if type_label in ("cover",):
                slide["type"] = "cover"
            elif type_label in ("list",):
                slide["type"] = "list"
            elif type_label in ("stat",):
                slide["type"] = "stat"
            elif type_label in ("quote",):
                slide["type"] = "quote"
            elif type_label in ("cta", "final"):
                slide["type"] = "cta"
            block = block[type_match.end():]

        # Parse fields
        text_match = re.search(r"\*\*Text:\*\*\s*(.+)", block)
        if text_match:
            slide["text"] = text_match.group(1).strip()

        subtext_match = re.search(r"\*\*Subtext:\*\*\s*(.+)", block)
        if subtext_match:
            slide["subtext"] = subtext_match.group(1).strip()

        detail_match = re.search(r"\*\*Detail:\*\*\s*(.+)", block)
        if detail_match:
            slide["detail"] = detail_match.group(1).strip()

        action_match = re.search(r"\*\*Action:\*\*\s*(.+)", block)
        if action_match:
            slide["action"] = action_match.group(1).strip()

        # List items (numbered: 1. ... 2. ... or - ...)
        items_section = re.search(r"\*\*Items:\*\*\s*\n((?:\s*(?:\d+\.|-)\s+.+\n?)+)", block)
        if items_section:
            slide["type"] = "list"
            items_text = items_section.group(1)
            items = re.findall(r"(?:\d+\.|-)\s+(.+)", items_text)
            slide["items"] = [item.strip() for item in items]

        # Stat number
        number_match = re.search(r"\*\*Number:\*\*\s*(.+)", block)
        if number_match:
            slide["type"] = "stat"
            slide["number"] = number_match.group(1).strip()

        # Quote
        quote_match = re.search(r"\*\*Quote:\*\*\s*(.+)", block)
        if quote_match:
            slide["type"] = "quote"
            slide["quote"] = quote_match.group(1).strip().strip('"').strip('\u201c').strip('\u201d')

        # Attribution
        attr_match = re.search(r"\*\*Attribution:\*\*\s*(.+)", block)
        if attr_match:
            slide["attribution"] = attr_match.group(1).strip()

        result["slides"].append(slide)

    # Parse caption section
    if len(sections) > 1:
        caption_section = sections[1]
        caption_text = re.sub(r"^##\s+Caption\s*\n", "", caption_section.strip())
        lines = caption_text.strip().split("\n")
        caption_lines = []
        for line in lines:
            hashtag_match = re.match(r"^Hashtags:\s*(.+)", line)
            if hashtag_match:
                result["hashtags"] = hashtag_match.group(1).strip()
            else:
                caption_lines.append(line)
        result["caption"] = "\n".join(caption_lines).strip()

    # Parse image prompt section
    if len(sections) > 2:
        prompt_section = sections[2]
        prompt_text = re.sub(r"^##\s+Cover Image Prompt\s*\n", "", prompt_section.strip())
        result["image_prompt"] = prompt_text.strip()

    return result


# --- Main Generator ---

def generate_carousel(
    markdown_path: str,
    cover_image_path: str,
    output_dir: str,
    logo_path: str,
):
    """Generate all carousel slides and caption file."""
    data = parse_carousel_markdown(markdown_path)
    slides = data["slides"]

    if not slides:
        print("Error: No slides found in markdown file.")
        sys.exit(1)

    total_slides = len(slides)
    print(f"Found {total_slides} slides in: {markdown_path}")
    print(f"Output size: {SLIDE_WIDTH}x{SLIDE_HEIGHT}px (4:5 portrait)")

    os.makedirs(output_dir, exist_ok=True)

    for i, slide in enumerate(slides):
        slide_num = i + 1
        slide_type = slide["type"]

        # First slide is always cover regardless of annotation
        if slide_num == 1:
            slide_type = "cover"
        # Last slide defaults to CTA if not otherwise specified
        elif slide_num == total_slides and slide_type == "content" and slide.get("action"):
            slide_type = "cta"

        print(f"Generating slide {slide_num}/{total_slides} ({slide_type})...")

        if slide_type == "cover":
            img = create_cover_slide(
                cover_image_path=cover_image_path,
                title=slide["text"],
                subtext=slide.get("subtext", ""),
                logo_path=logo_path,
                show_swipe=(total_slides > 1),
            )
        elif slide_type == "list":
            img = create_list_slide(
                headline=slide["text"],
                items=slide["items"] if slide["items"] else [slide["detail"]],
                slide_num=slide_num,
                total_slides=total_slides,
                logo_path=logo_path,
            )
        elif slide_type == "stat":
            img = create_stat_slide(
                number=slide["number"] or slide["text"],
                label=slide["text"] if slide["number"] else "",
                detail=slide["detail"] or slide["subtext"],
                slide_num=slide_num,
                total_slides=total_slides,
                logo_path=logo_path,
            )
        elif slide_type == "quote":
            img = create_quote_slide(
                quote=slide["quote"] or slide["text"],
                attribution=slide["attribution"] or slide["subtext"],
                slide_num=slide_num,
                total_slides=total_slides,
                logo_path=logo_path,
            )
        elif slide_type == "cta":
            img = create_cta_slide(
                headline=slide["text"],
                subtext=slide.get("subtext", ""),
                action=slide.get("action", ""),
                logo_path=logo_path,
                total_slides=total_slides,
            )
        else:
            # Default: content slide
            img = create_content_slide(
                headline=slide["text"],
                detail=slide["detail"] or slide["subtext"] or slide["action"],
                slide_num=slide_num,
                total_slides=total_slides,
                logo_path=logo_path,
                show_swipe=(slide_num == 2),
            )

        slide_path = os.path.join(output_dir, f"slide-{slide_num:02d}.png")
        img.save(slide_path, "PNG", quality=95)
        print(f"  Saved: {slide_path}")

    # Save caption
    caption_parts = []
    if data["caption"]:
        caption_parts.append(data["caption"])
    if data["hashtags"]:
        caption_parts.append("")
        caption_parts.append(data["hashtags"])

    caption_path = os.path.join(output_dir, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write("\n".join(caption_parts))
    print(f"  Saved: {caption_path}")

    print(f"\nDone! Generated {total_slides} slides ({SLIDE_WIDTH}x{SLIDE_HEIGHT}px) in: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate branded 1080x1350px Instagram carousel slides from markdown content."
    )
    parser.add_argument(
        "--markdown",
        required=True,
        help="Path to instagram-carousel.md file",
    )
    parser.add_argument(
        "--cover-image",
        required=True,
        help="Path to cover image (PNG/JPG)",
    )
    parser.add_argument(
        "--output-dir",
        default="./carousel/",
        help="Output directory for slides (default: ./carousel/)",
    )
    parser.add_argument(
        "--logo",
        default=str(DEFAULT_LOGO),
        help="Path to logo PNG (default: built-in Augmi logo)",
    )

    args = parser.parse_args()

    ensure_fonts()
    if args.logo == str(DEFAULT_LOGO):
        ensure_logo()

    if not os.path.exists(args.markdown):
        print(f"Error: Markdown file not found: {args.markdown}")
        sys.exit(1)
    if not os.path.exists(args.cover_image):
        print(f"Error: Cover image not found: {args.cover_image}")
        sys.exit(1)
    if not os.path.exists(args.logo):
        print(f"Error: Logo file not found: {args.logo}")
        sys.exit(1)

    generate_carousel(
        markdown_path=args.markdown,
        cover_image_path=args.cover_image,
        output_dir=args.output_dir,
        logo_path=args.logo,
    )


if __name__ == "__main__":
    main()
