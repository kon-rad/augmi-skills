# Blog & Social Media Image Style Guide

**Tools**: blog-image-gen skill
**Aspect Ratios**: Multiple (4:5 for social, 16:9 for blog)
**Format**: PNG, high-res (2400px wide minimum)
**Color Palette**: [Your brand colors]

---

## Visual Specifications

### Colors
- **Primary Brand Color**: [Hex code]
- **Secondary Color**: [Hex code]
- **Accent Color**: Cyan (#00D9FF) or [your choice]
- **Background**: Dark/Light [choose]
- **Text**: White (#FFFFFF) or [high contrast]

### Typography
- **Headline Font**: Bold sans-serif
- **Body Font**: Regular sans-serif
- **Accent Font**: Monospace or specialty (headlines only)

### Visual Style
- **Aesthetic**: [Sci-fi / minimalist / gradient / geometric]
- **Photography**: [Professional photos / illustrations / AI-generated]
- **Graphics**: [Icons / diagrams / gradients / overlays]
- **Depth**: Layered elements with shadow/depth

---

## Image Types

### Type 1: Featured Blog Image
**Dimensions**: 1200x675px (16:9 landscape)
**Purpose**: Header image for blog posts, website feature
**Location**: Top of blog post, social media link preview

```markdown
## Featured Blog Image

**Title**: [Article headline]
**Subtitle**: [One-line description]
**Visual Concept**: [Description for image generation]
**Style**: Professional, authoritative
**Elements**:
- Large headline (readable at small sizes)
- Supporting visual (graph, scene, illustration)
- Optional brand logo (bottom right corner)
```

### Type 2: Social Media Card
**Dimensions**: 1080x1080px (1:1 square) for Instagram/Facebook
**Purpose**: Social media post image
**Location**: Instagram posts, Facebook share preview

```markdown
## Social Media Card

**Title**: [Post headline - max 5 words]
**Subtitle**: [Context - max 10 words]
**Visual**: [Supporting graphic]
**Style**: Bold, eye-catching
**Text Placement**: Top 25% or bottom 25%
```

### Type 3: LinkedIn Hero Image
**Dimensions**: 1200x627px (1.91:1) or 1080x1080px (1:1 square)
**Purpose**: LinkedIn article image or post image
**Location**: LinkedIn article cover, post image

```markdown
## LinkedIn Hero Image

**Title**: [Professional headline]
**Subtitle**: [Key insight]
**Visual**: [Professional scene or abstract graphic]
**Style**: Corporate, authoritative, trustworthy
**Elements**:
- Professional typography
- Subtle gradients or patterns
- Clear visual hierarchy
- Minimal text (let image speak)
```

### Type 4: Pinterest Image
**Dimensions**: 1000x1500px (2:3 vertical)
**Purpose**: Pinterest pin for long-form content
**Location**: Pinterest board, rich pins

```markdown
## Pinterest Image

**Title**: [Headline - 5-10 words]
**Keywords**: [SEO keywords - subtle]
**Visual**: [Vertical hero image]
**Style**: Bright, engaging, visual
**Format**: 70% image, 30% text
```

---

## Design Principles

### Visual Hierarchy
1. **Headline** (largest) - Main topic
2. **Visuals** (prominent) - Supporting image/graphic
3. **Secondary Text** - Context or benefit
4. **Tertiary Elements** - Logo, branding

### Color Application
- **Primary Color**: Main design element, headlines
- **Secondary Color**: Supporting elements, accents
- **Accent Color**: Highlights, important points
- **Background**: Neutral or subtle gradient

### Typography Rules
- **Headlines**: Bold, sans-serif, 48-72px
- **Body Text**: Regular, sans-serif, 24-32px
- **Accent Text**: Specialty font, carefully used
- **Contrast**: Always readable (WCAG AA minimum)

### Spacing & Layout
- **Margins**: 40px minimum on all sides
- **Padding**: 20px between elements
- **Alignment**: Left, right, or centered (consistent)
- **Whitespace**: Use it generously
- **Layering**: Overlapping elements for depth

---

## Content Guidelines

### Headline
- **Length**: 3-7 words (headline image) or 2-5 words (social)
- **Approach**: Benefit-driven or curiosity-driven
- **Style**: Sentence case (not ALL CAPS)
- **Specificity**: Numbers beat generics ("5 ways..." > "ways...")

### Subtitle/Body
- **Length**: 10-20 words maximum
- **Purpose**: Explain headline or add context
- **Readability**: Easy to understand at thumbnail size
- **Engagement**: Ask question or make bold statement

### Visual Approach
- **Photography**: Professional, high-quality
- **Illustrations**: Clean, on-brand
- **Abstract**: Geometric, gradients, patterns
- **Scenes**: AI-generated or stock photos

---

## Templates by Format

### Blog Featured Image Template
```markdown
## Featured Blog Image

**Headline**: [Article Title - 5-7 words]
**Subtitle**: [Key Takeaway - 1 sentence]

**Image Concept**:
[Describe the scene or visual concept]
- Main element: [What's the star of the image?]
- Supporting elements: [What complements it?]
- Color mood: [Bright/dark/professional/playful?]
- Style: [Sci-fi/minimalist/professional?]

**Text Overlay**:
- Position: Top third or bottom third
- Size: Large (readable at 400px wide)
- Color: White with dark shadow for readability
```

### Instagram Post Template
```markdown
## Instagram Social Card

**Main Headline**: [Hook - 2-5 words]
**Secondary Text**: [Context - 5-10 words]

**Visual Concept**:
[Describe visual for image generation]
- Style: Bold, eye-catching
- Color: Use primary brand color prominently
- Format: 1:1 square, works at thumbnail size
- Text Coverage: Maximum 30% of image

**Engagement Hook**: What makes you swipe/tap?
```

### LinkedIn Article Template
```markdown
## LinkedIn Hero

**Title**: [Professional Headline - 5-7 words]
**Subtitle**: [Key Insight - 1 sentence]

**Visual Concept**:
[Professional yet interesting visual]
- Style: Corporate but engaging
- Tone: Authoritative, trustworthy
- Color: Professional palette
- Format: 1200x627px or 1:1 square
- Text: Minimal (image-focused)
```

---

## Workflow Integration

### With Deep Research
1. `deep-research:full` generates image prompts
2. `blog-image-gen` creates images from prompts
3. Images used for blog featured + social cards
4. Same image repurposed for different platforms

### With Carousel
1. `carousel-image-gen` creates slide-specific images
2. Blog guide used for cover image
3. Featured image used in carousel slide 1
4. Carousel images all follow blog style guide

### With Short-Form Video
1. Featured image becomes video thumbnail
2. Color palette matches video branding
3. Text overlay style carries through

---

## Platform-Specific Adjustments

### Instagram
- **Size**: 1080x1080px (1:1 square)
- **Text Coverage**: 20-30%
- **Colors**: Bright, high saturation
- **Style**: Trendy, engaging, modern

### Facebook
- **Size**: 1200x628px (1.91:1 landscape)
- **Text Coverage**: 20%
- **Colors**: Professional but accessible
- **Style**: Trustworthy, clear benefit

### LinkedIn
- **Size**: 1200x627px (1.91:1) or 1080x1080px (1:1)
- **Text Coverage**: 10-20%
- **Colors**: Professional, corporate
- **Style**: Authoritative, thought leadership

### Blog/Website
- **Size**: 1200x675px (16:9 landscape)
- **Text Coverage**: 30%
- **Colors**: On-brand, clear hierarchy
- **Style**: Professional, aligned with article tone

### Pinterest
- **Size**: 1000x1500px (2:3 vertical)
- **Text Coverage**: 30-40%
- **Colors**: Bright, eye-catching
- **Style**: Visual, inspiring, clickable-looking

---

## Image Generation Workflow

### Step 1: Write Prompt
```
[Concept]: [Specific description]
[Style]: [Sci-fi / minimalist / professional / abstract]
[Colors]: [Primary color], [Secondary color], [Accent]
[Elements]: [Specific visual elements]
[Composition]: [Rule of thirds / centered / full-bleed]
[Mood]: [Professional / playful / urgent / inspiring]
```

### Step 2: Generate with blog-image-gen
```bash
blog-image-gen \
  --aspect-ratio 16:9 \
  --topic "Your Article Topic" \
  --style "your-style-guide.md"
```

### Step 3: Review & Approve
- Check headline readability
- Verify colors match brand
- Confirm text contrast
- Test at different sizes

### Step 4: Repurpose
- Crop for Instagram (1:1 square)
- Resize for LinkedIn (1.91:1)
- Keep original for blog (16:9)

---

## Color Palette

Use these hex codes consistently:

| Purpose | Color | Hex | RGB |
|---------|-------|-----|-----|
| Primary | [Brand Primary] | #[HEX] | RGB(r,g,b) |
| Secondary | [Brand Secondary] | #[HEX] | RGB(r,g,b) |
| Accent | Cyan | #00D9FF | RGB(0, 217, 255) |
| Text (Light) | White | #FFFFFF | RGB(255, 255, 255) |
| Text (Dark) | Dark | #1A1A1A | RGB(26, 26, 26) |
| Background | Neutral | #[HEX] | RGB(r,g,b) |

### Color Usage Rules
- Primary: Headlines, main elements
- Secondary: Supporting elements, accent areas
- Accent: Important callouts, highlights
- Text: Always high contrast with background

---

## Typography

### Font Stack
```
Headline Font: [Your sans-serif bold]
Body Font: [Your sans-serif regular]
Monospace: [For code/special text]
```

### Size Guide
- **Headline**: 48-72px
- **Subheading**: 32-48px
- **Body**: 24-32px
- **Small**: 14-18px

### Weight Guide
- **Headlines**: Bold (700)
- **Subheadings**: Semi-bold (600)
- **Body**: Regular (400)
- **Emphasis**: Bold (700) or italics

---

## Examples & Variations

### Example 1: How-To Topic
**Title**: "5 Ways to Master [Topic]"
**Visual**: Step-by-step visual progression
**Color**: Primary brand with cyan accents
**Style**: Clean, organized, professional

### Example 2: News/Breaking
**Title**: "Breaking: [News Headline]"
**Visual**: Dynamic, energetic scene
**Color**: High-contrast, eye-catching
**Style**: Urgent, important, timely

### Example 3: Thought Leadership
**Title**: "Why [Bold Statement]"
**Visual**: Abstract or metaphorical
**Color**: Professional, sophisticated
**Style**: Authoritative, insightful

### Example 4: Tutorial
**Title**: "[Feature] Explained"
**Visual**: Step-by-step diagram or flow
**Color**: Clean, organized with accents
**Style**: Educational, clear, simple

---

## Accessibility Guidelines

### Color Contrast
- Text on background: Minimum 4.5:1 contrast (WCAG AA)
- Large text (18px+): Minimum 3:1 contrast
- Test with: WebAIM contrast checker

### Text Readability
- Always use drop shadow or outline on text
- Never rely on color alone to convey meaning
- Include alt text describing the image
- Make sure text is readable at thumbnail size

### Inclusive Design
- Don't use red/green combinations alone
- Provide text alternatives to visual information
- Use patterns in addition to colors
- Consider colorblind viewers (use WebAIM simulator)

---

## Performance Targets

### Engagement
- **Click-Through Rate**: >2% (on social)
- **Save Rate**: 10% of engagements
- **Share Rate**: 5% of engagements

### Visual Quality
- **Resolution**: 2400px wide minimum (blog-image-gen default)
- **File Size**: <500KB (compressed, but not quality-reduced)
- **Format**: PNG for transparency, JPG for photos

---

## Common Mistakes to Avoid

❌ **Text too small** - Test at 400px wide
❌ **Poor contrast** - Always check with accessibility tool
❌ **Too much text** - Images are visual, not billboards
❌ **Generic images** - Specific > generic
❌ **Misaligned colors** - Use hex codes from palette
❌ **Inconsistent fonts** - Stay within brand font stack
❌ **Cluttered design** - Whitespace is your friend
❌ **No headline** - Every image needs a headline

---

## Tools & Resources

### Image Generation
- `blog-image-gen` skill (recommended)
- Prompt format: [Style] [Concept] [Colors] [Mood]

### Testing
- Thumbnail preview (400px)
- Mobile preview (crop variations)
- Contrast checker (WebAIM)
- Color blind simulator (Coblis)

### Storage
- OUTPUT/{date}/{slug}/images/
- Organize by image type
- Keep original + platform-specific crops

---

## Updating This Guide

When brand evolves:
1. Update color palette section
2. Update font stack section
3. Update example images
4. Version number increase
5. Date update (YYYY-MM-DD)

**Current Version**: 1.0
**Last Updated**: 2026-03-06

---

Ready to create beautiful images? Start with a topic and use blog-image-gen! 🎨✨
