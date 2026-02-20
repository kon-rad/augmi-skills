---
name: comic-book-creator
description: >
  Creates comic book episodes for the Augmi Universe through a 3-step workflow:
  Brainstorm, Draft, and Publish. Use this skill when the user wants to create
  a new comic episode, develop an existing brainstorm into a draft, or finalize
  an episode for publication. Triggers on requests like "create a new comic episode",
  "draft episode 2", "publish the comic", "brainstorm a comic", or "work on the comic".
---

# Comic Book Creator Skill

Create episodes for the Augmi Universe comic series through a structured creative workflow.

## Universe Reference

Before starting ANY episode work, read these files for canon consistency:
- `content/comic-books/universe/UNIVERSE.md` -- World-building, technology, themes
- `content/comic-books/universe/CHARACTERS.md` -- Character bible, abilities, visual guides
- `content/comic-books/universe/STORY-ARCS.md` -- Episode index, arc progression, status

## Workflow: 3 Steps

### Step 1: Brainstorm

**Command:** `brainstorm episode [number] [optional topic/theme]`

**Process:**
1. Read the universe files and the story arcs to understand where we are in the narrative
2. Read any previous episode brainstorms for continuity
3. Discuss with the user:
   - What theme/concept should this episode explore?
   - Which characters are featured?
   - What Augmi ability or aspect of the technology is highlighted?
   - What's the emotional core?
4. Generate a brainstorm file with:
   - Logline (1 sentence)
   - Synopsis (2-3 paragraphs)
   - Key scenes (bullet points)
   - Panel breakdown (rough -- pages and key panels)
   - Visual notes
   - Dialogue highlights
   - Themes to hit
5. Save to `content/comic-books/brainstorm/epXX-slug.md`
6. Update status in `STORY-ARCS.md`

**Output:** `content/comic-books/brainstorm/epXX-slug.md`

### Step 2: Draft

**Command:** `draft episode [number]`

**Process:**
1. Read the brainstorm file for this episode
2. Read universe/character files for consistency
3. Expand the brainstorm into a full draft:
   - Complete panel-by-panel script (every panel described)
   - Full dialogue for all characters
   - Art direction notes for each panel (camera angle, lighting, mood)
   - Augmi visual effect descriptions
   - Page-by-page flow and pacing
4. Create image prompts for the comic-strip-maker skill:
   - One prompt per key panel (6-12 panels per episode)
   - Prompts follow manga/anime style guide from UNIVERSE.md
   - Include character visual references from CHARACTERS.md
5. Save draft to `content/comic-books/draft/epXX-slug.md`
6. Save image prompts to `content/comic-books/draft/epXX-slug-image-prompts.md`
7. Update status in `STORY-ARCS.md`

**Output:**
- `content/comic-books/draft/epXX-slug.md` (full script)
- `content/comic-books/draft/epXX-slug-image-prompts.md` (image generation prompts)

### Step 3: Publish

**Command:** `publish episode [number]`

**Process:**
1. Read the draft and image prompts
2. Generate comic images using the `blog-image-gen` skill:
   ```bash
   python .claude/skills/blog-image-gen/scripts/generate_blog_images.py \
     --prompts-file content/comic-books/draft/epXX-slug-image-prompts.md \
     --output-dir content/comic-books/final/epXX-slug/ \
     --model imagen-4-ultra \
     --aspect-ratio 3:4
   ```
3. Assemble the final episode:
   - Combine images with narrative text
   - Create final markdown with embedded images
   - Add character spotlights if new characters are introduced
   - Add universe wiki entries if new concepts are introduced
4. Save to `content/comic-books/final/epXX-slug.md`
5. Update status in `STORY-ARCS.md` to `final` (or `published` once live)
6. Notify user that episode is ready for review

**Output:**
- `content/comic-books/final/epXX-slug/` (directory with images)
- `content/comic-books/final/epXX-slug.md` (assembled episode)

## Image Prompt Format

Image prompts for comic panels should follow this template:

```markdown
## Panel [N]: [Title]

**Page:** [page number]
**Panel position:** [full page / half page / quarter / strip]

\`\`\`
[Detailed visual description in manga/anime style]
Character: [name] - [description from character bible]
Setting: [location details]
Lighting: [lighting direction and color]
Mood: [emotional tone]
Camera: [angle - wide/medium/close-up/extreme close-up]
Augmi effects: [any augmentation visuals]
Style: manga, clean linework, [specific style notes]
\`\`\`
```

## Version Control

**NEVER delete existing image versions.** When regenerating a comic page, always save as a new version:
- `page1.png` (original)
- `page1-v2.png` (second attempt)
- `page1-v3.png` (third attempt)
- etc.

This preserves all attempts so the user can compare and choose the best version. Only the user decides which version to use or delete.

## Style Consistency

Every episode MUST maintain:
- **Art style:** Manga/anime-influenced with cyberpunk accents
- **Color palette:** Dark backgrounds + vibrant accents (see UNIVERSE.md)
- **Character designs:** Per CHARACTERS.md visual signatures
- **Augmi visuals:** Amber-gold geometric forms, unique per character
- **Network School:** Mediterranean warmth + high-tech overlay
- **Panel layout:** Manga-style reading flow, dynamic compositions

## Continuity Checklist

Before finalizing any episode:
- [ ] Character appearances match CHARACTERS.md
- [ ] Augmi abilities are consistent with established rules
- [ ] Story follows from previous episodes
- [ ] No contradictions with UNIVERSE.md canon
- [ ] New concepts/characters added to wiki files
- [ ] STORY-ARCS.md updated with current status

## Quick Commands

| Command | Action |
|---------|--------|
| `brainstorm episode N` | Start brainstorming a new episode |
| `draft episode N` | Expand brainstorm into full draft |
| `publish episode N` | Generate images and assemble final |
| `status` | Show all episodes and their current status |
| `universe update` | Update wiki with new concepts from recent episodes |
| `character spotlight [name]` | Generate a character deep-dive page |
