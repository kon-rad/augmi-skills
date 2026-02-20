---
name: carousel-image-gen
description: >
  Generates branded Instagram carousel images from markdown content.
  Takes an instagram-carousel.md file and a cover image, produces 1080x1350px
  (4:5 portrait) carousel slides with multiple slide types (Cover, Content,
  List, Stat, Quote, CTA). Triggers on requests like "generate carousel",
  "create carousel images", "make instagram slides", or when instagram-carousel.md
  files exist alongside cover images.
user-invocable: true
---

# Instagram Carousel Image Generator (v2)

Generate branded 1080x1350px (4:5 portrait) Instagram carousel slides from markdown content and a cover image. Supports 6 slide types for professional, high-engagement carousels.

**Style Guide**: See `content/instagram-carousel/STYLE-GUIDE.md` for full design rationale.

## Prerequisites

### Required Dependencies
```bash
pip3 install pillow --break-system-packages
```

Pillow is typically already installed if you've used the `blog-image-gen` skill.

## Usage

### Basic Usage

Generate carousel from markdown + cover image:
```bash
python3 .claude/skills/carousel-image-gen/scripts/generate_carousel.py \
  --markdown OUTPUT/social-content/20260216/openclaw-145k-stars/instagram-carousel.md \
  --cover-image OUTPUT/social-content/20260216/openclaw-145k-stars/images/instagram-cover.png \
  --output-dir OUTPUT/social-content/20260216/openclaw-145k-stars/carousel/
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--markdown` | Path to instagram-carousel.md file | **Required** |
| `--cover-image` | Path to cover image (PNG/JPG) | **Required** |
| `--output-dir` | Output directory for slides | `./carousel/` |
| `--logo` | Path to logo PNG | Built-in Augmi logo |

### Output

The script produces:
- `slide-01.png` through `slide-NN.png` -- 1080x1350px carousel slides (4:5 portrait)
- `caption.txt` -- Instagram caption with hashtags

## Slide Types

### 1. Cover Slide
Full-bleed background photo with gradient overlay, centered title, logo, and swipe cue.
- **Format**: Photo background + dark gradient (45% -> bottom)
- **Text**: Large centered title (76px bold) + optional subtext
- **Extras**: Swipe cue arrow at bottom, logo top-left

### 2. Content Slide
Standard slide with headline + detail paragraph. Left-aligned for readability.
- **Format**: Dark background, gradient strip at top
- **Text**: Cyan headline (68px bold) + zinc-300 detail (40px regular)
- **Extras**: Accent line between headline and detail, slide counter

### 3. List Slide
Numbered items with filled circles. Great for tips, steps, or key points.
- **Format**: Headline + numbered items with cyan circles
- **Text**: Cyan headline + white list items (44px)
- **Max**: 5 items per slide, 3 lines per item

### 4. Stat Slide
Large metric/number with context. Perfect for data points and impressive stats.
- **Format**: Centered large number (120px) + label + detail
- **Text**: Cyan number, white label, zinc-300 detail
- **Extras**: Centered accent line separator

### 5. Quote Slide
Decorative quote with attribution. For testimonials or impactful statements.
- **Format**: Large decorative opening quote mark + quote text
- **Text**: White quote (48px) + zinc-300 attribution (32px)
- **Extras**: Decorative quote mark in zinc-800, accent line before attribution

### 6. CTA Slide (Call-to-Action)
Final slide with prominent branding and clear action. Center-aligned.
- **Format**: Large centered logo + headline + action text
- **Text**: White headline (64px) + cyan subtext + zinc-300 action
- **Extras**: Centered accent line, large 96px logo

## Design Spec

### Dimensions
- **Width**: 1080px
- **Height**: 1350px (4:5 portrait ratio)
- **Why**: 30% more screen real estate than 1:1 square. Maximum feed impact on mobile.

### Brand Colors
| Name | Hex | Usage |
|------|-----|-------|
| Background | `#09090b` | All slide backgrounds |
| White | `#ffffff` | Cover text, body text |
| Cyan | `#06b6d4` | Headlines, numbers, accent elements |
| Emerald | `#10b981` | Gradient end, highlights |
| Zinc-300 | `#d4d4d8` | Detail/body text |
| Zinc-500 | `#71717a` | Muted elements (counter, swipe cue) |
| Zinc-800 | `#27272a` | Decorative elements (quote marks) |

### Typography
- Font: Inter (Bold + Regular), auto-downloaded to assets/
- Cover title: 76px Bold, white, centered
- Content headline: 68px Bold, cyan, left-aligned
- Content detail: 40px Regular, zinc-300
- List items: 44px Regular, white
- Stat number: 120px Bold, cyan, centered
- Quote text: 48px Regular, white
- Slide counter: 22px Regular, zinc-500
- Swipe cue: 24px Regular, zinc-500

### Visual Elements
- **Gradient strip**: 5px cyan-to-emerald bar at top of content slides
- **Accent line**: 4px x 120px cyan separator between sections
- **Number circles**: 64px cyan filled circles with dark numbers (list slides)
- **Swipe cue**: "Swipe >>>" text at bottom of slides 1-2
- **Quote marks**: 100px decorative opening quote in zinc-800
- **Slide counter**: "N / Total" bottom-right on all content slides

### Layout
- Padding: 80px from all edges
- Logo: 50px from top-left corner
- Content: Vertically centered between logo and counter
- Cover text: Bottom 40% with gradient overlay

## Markdown Format

The script expects this format (backward compatible with v1, with new type annotations):

```markdown
# Instagram Carousel: Title Here

## Slide 1 (Cover)
**Text:** Bold hook headline (5-8 words)
**Subtext:** Optional context line

## Slide 2
**Text:** Key insight headline
**Detail:** 1-2 sentence explanation

## Slide 3 (List)
**Text:** 3 Things You Need to Know
**Items:**
1. First important point
2. Second key insight
3. Third takeaway

## Slide 4 (Stat)
**Number:** 847%
**Text:** Growth in AI agent deployments
**Detail:** Source: Platform data, Q4 2025

## Slide 5 (Quote)
**Quote:** The future belongs to those who deploy agents today.
**Attribution:** -- Augmi Team

## Slide 6
**Text:** Another insight
**Detail:** Supporting detail

## Slide 7 (CTA)
**Text:** Start Building Today
**Subtext:** augmi.world
**Action:** Follow @augmi.world for more

---

## Caption

Your Instagram caption text here.

Hashtags: #AIAgents #Web3 #BuildInPublic

---

## Cover Image Prompt

Prompt text for image generation...
```

### Type Annotations

Add type in parentheses after slide number:
- `(Cover)` -- Full-bleed photo background (auto-applied to slide 1)
- `(List)` -- Numbered items with circles
- `(Stat)` -- Large number/metric
- `(Quote)` -- Decorative quote
- `(CTA)` or `(Final)` -- Call-to-action (auto-applied to last slide with **Action:** field)
- No annotation -- Default content slide

### Field Reference

| Field | Used By | Description |
|-------|---------|-------------|
| `**Text:**` | All types | Main headline/text |
| `**Subtext:**` | Cover, CTA | Secondary text line |
| `**Detail:**` | Content, Stat | Supporting detail paragraph |
| `**Action:**` | CTA | Call-to-action text |
| `**Items:**` | List | Numbered list (1. / 2. / 3.) |
| `**Number:**` | Stat | Large metric/number |
| `**Quote:**` | Quote | Quote text |
| `**Attribution:**` | Quote | Quote attribution |

## Integration with social-content-engine

After generating content with `social-content-engine` and images with `blog-image-gen`:
```bash
python3 .claude/skills/carousel-image-gen/scripts/generate_carousel.py \
  --markdown OUTPUT/social-content/YYYYMMDD/{topic}/instagram-carousel.md \
  --cover-image OUTPUT/social-content/YYYYMMDD/{topic}/images/instagram-cover.png \
  --output-dir OUTPUT/social-content/YYYYMMDD/{topic}/carousel/
```

## Backward Compatibility

v2 is fully backward compatible with v1 markdown format. Old carousels with only `**Text:**` and `**Detail:**` fields will render as cover (slide 1) + content slides, same as before but now in 1080x1350 portrait format.
