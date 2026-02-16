# AUGMI Skills

A collection of open-source [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for content creation, research, media generation, and developer productivity. These skills extend Claude Code with specialized workflows powered by AI APIs (Google Gemini, Fal.ai, Together AI, Replicate, and more).

## Quick Start

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/kon-rad/augmi-skills.git ~/.claude/skills/augmi-skills

# Or clone individual skills
# Copy any skill folder into ~/.claude/skills/
```

Once installed, skills are automatically available in Claude Code sessions via slash commands (e.g., `/deep-research`, `/blog-visual-gen:generate`).

## Skills Catalog

### Content Creation

| Skill | Description | Slash Commands | APIs Used |
|-------|-------------|----------------|-----------|
| [deep-research](#deep-research) | Research-to-content pipeline: web research, analysis, multi-format output | `/deep-research:research`, `/deep-research:summarize`, `/deep-research:analyze`, `/deep-research:produce`, `/deep-research:full` | Web Search, Twitter/X |
| [viral-tweet-crafter](#viral-tweet-crafter) | Craft authentic tweets with 8 templates, posting strategy, and quality checks | `/viral-tweet:write`, `/viral-tweet:daily`, `/viral-tweet:thread`, `/viral-tweet:react`, `/viral-tweet:audit` | - |
| [spec-interview](#spec-interview) | Interview-driven spec writing for dev tasks with verification criteria | - | - |

### Image & Visual Generation

| Skill | Description | Slash Commands | APIs Used |
|-------|-------------|----------------|-----------|
| [blog-image-gen](#blog-image-gen) | Generate images from prompts for blogs, thumbnails, social media | - | Google Imagen 4 |
| [blog-visual-gen](#blog-visual-gen) | Analyze blog content and generate contextual visuals | `/blog-visual-gen:generate`, `/blog-visual-gen:from-file` | Google Nano Banana 3 |
| [infographic-gen](#infographic-gen) | Research a topic and generate professional infographics | `/infographic-gen:generate`, `/infographic-gen:from-content` | Google Nano Banana 3 |
| [comic-strip-maker](#comic-strip-maker) | Generate comic strips and manga-style cartoon pages from story prompts | `/comic-strip-maker:create`, `/comic-strip-maker:panels`, `/comic-strip-maker:strip` | Google Nano Banana 3 |

### Video & Audio

| Skill | Description | Slash Commands | APIs Used |
|-------|-------------|----------------|-----------|
| [ai-film-maker](#ai-film-maker) | Create personalized 30-second AI short films | - | Fal.ai, Google Veo, Together AI, Replicate |
| [youtube-transcript](#youtube-transcript) | Extract transcripts from YouTube videos | - | youtube-transcript-api |
| [youtube-music-downloader](#youtube-music-downloader) | Download YouTube audio as MP3 | - | yt-dlp |

### Document Processing

| Skill | Description | Slash Commands | APIs Used |
|-------|-------------|----------------|-----------|
| [pdf](#pdf) | Full PDF toolkit: extract, create, merge, split, forms, OCR | - | pypdf, pdfplumber, reportlab |
| [large-pdf-reader](#large-pdf-reader) | Extract text from large PDFs in chunks | - | pypdf, pdfplumber |

### Google Workspace

| Skill | Description | Slash Commands | APIs Used |
|-------|-------------|----------------|-----------|
| [google-docs](#google-docs) | Google Docs & Drive management — create, format, markdown support, tables, images, Drive upload/download/share | - | Google Docs API, Google Drive API (Ruby) |
| [gogcli](#gogcli) | Full Google Workspace CLI — Gmail, Calendar, Drive, Docs, Sheets, Slides, Contacts, Tasks, Forms, Groups, Keep | - | Google Workspace APIs (Go binary) |

### Developer Tools

| Skill | Description | Slash Commands | APIs Used |
|-------|-------------|----------------|-----------|
| [codebase-tutor](#codebase-tutor) | Voice-based codebase learning and quiz sessions | `/codebase-tutor:start`, `/codebase-tutor:quick` | Voice Mode MCP |

---

## Skill Details

### ai-film-maker

Creates personalized 30-second AI short films. Supports two modes:
- **Default**: Full creative pipeline from a concept/theme
- **Seed**: Starts from a user-provided image, analyzed by Gemini Vision

**Pipeline**: Story Development -> Scene Breakdown -> Image Generation + Face Swap -> Video Generation -> Narration -> Music -> Final Composition

**Quality Tiers**:

| Tier | Cost | Text-to-Image | Image-to-Video |
|------|------|---------------|----------------|
| Cheapest | ~$1-2 | Together AI Qwen | Fal.ai Wan 2.5 |
| Balanced | ~$2-3 | Fal.ai FLUX | Fal.ai Kling 2.5 |
| Highest | ~$8-15 | Together AI Imagen 4 | Google Veo 3 |

**Setup**:
```bash
pip install fal-client replicate requests google-generativeai
brew install ffmpeg
```

**Environment**: `FAL_KEY`, `REPLICATE_API_TOKEN`, optionally `GOOGLE_AI_API_KEY`, `TOGETHER_API_KEY`

---

### blog-image-gen

Generate high-quality images for blog posts, articles, social media, and YouTube thumbnails using Google's Imagen API.

**Models**: Imagen 4 (~$0.02/img), Imagen 4 Ultra (~$0.04/img), Imagen 4 Fast (~$0.01/img), Gemini 2.5 Flash (~$0.02/img)

**Features**: Single prompt or batch generation from markdown file, multiple aspect ratios (16:9, 1:1, 9:16, 4:3, 3:4), 1K or 2K output

**Setup**: `pip install google-genai pillow`

**Environment**: `GEMINI_API_KEY`

---

### blog-visual-gen

Analyzes blog post content, extracts key themes, and generates a contextual visual. Unlike simple prompt-to-image, this skill understands your content before generating.

**Workflow**: Content Analysis -> Theme Extraction -> Custom Prompt Generation -> Image Generation (Nano Banana 3)

**Setup**: `pip install google-genai pillow`

**Environment**: `GEMINI_API_KEY`

---

### codebase-tutor

Interactive voice-based codebase learning sessions. Maps the codebase, analyzes recent git changes, presents an overview, and quizzes you.

**Session Flow**:
1. Codebase mapping (via cartographer skill)
2. Documentation reading (CLAUDE.md, README, codebase map)
3. Git history analysis (last 20 commits)
4. Voice presentation of overview and recent changes
5. Interactive voice quiz (5-7 questions with feedback)
6. Performance summary and review suggestions

**Requires**: Voice Mode MCP server

---

### gogcli

Fast, script-friendly CLI for the entire Google Workspace suite. Single Go binary with JSON-first output, multiple account support, and built-in safety features.

**Services**: Gmail, Calendar, Drive, Docs, Sheets, Slides, Contacts, Tasks, Forms, Apps Script, Groups, Keep, People, Classroom

**Key Features**:
- `--readonly` flag for least-privilege access
- `--json` + `--no-input` for scripting/automation
- Command allowlist for sandboxed agent runs
- Secure credential storage (OS keyring or encrypted file)
- Multiple Google account support

**Setup**: `brew install steipete/tap/gogcli` then `gog auth add you@gmail.com ~/Downloads/client_secret.json`

**Source**: [steipete/gogcli](https://github.com/steipete/gogcli) (2.5k stars, MIT license)

---

### google-docs

Google Docs & Drive management skill with rich document formatting capabilities. Written in Ruby with comprehensive Docs API coverage.

**Google Docs**: Read, create, insert/append text, find & replace, bold/italic/underline formatting, page breaks, inline images, tables, markdown-to-doc conversion

**Google Drive**: Upload, download, search, list, share, create folders, move files, export (PDF, PNG, etc.)

**Setup**: Requires Ruby and Google API gems. Create OAuth 2.0 credentials and save to `~/.claude/.google/client_secret.json`.

**Source**: [robtaylor/google-docs-skill](https://github.com/robtaylor/google-docs-skill) (MIT license)

---

### deep-research

Comprehensive research-to-content pipeline. Takes a topic + optional links and produces analysis and multi-format content.

**Pipeline**: Research (web + social) -> Executive Summaries -> Pattern Analysis -> Content Production

**Outputs**: Analysis document, Twitter thread (5-15 tweets), blog post, YouTube script, viral tweets (10), LinkedIn posts (3 variants), image prompts (5-7)

**Directory Convention**:
```
INPUT/<YYYYMMDD>/<topic>/sources/    # Raw scraped content
OUTPUT/<YYYYMMDD>/<topic>/           # Final content outputs
```

---

### comic-strip-maker

Generate comic strips and manga-style cartoon pages from text prompts. Analyzes your story, generates optimized panel layouts, and renders the full page.

**Layouts**: `strip` (horizontal, default), `manga` (varied panels), `4-koma` (vertical 4-panel), `splash` (large + insets), `grid` (even grid)

**Styles**: `modern-anime`, `shonen`, `shoujo`, `chibi`, `seinen`, `retro`

**Cost**: ~$0.04 per comic strip

**Setup**: `pip install google-genai pillow`

**Environment**: `GEMINI_API_KEY`

---

### infographic-gen

Three-phase infographic generation: research the topic, design the layout with AI, generate the final visual.

**Styles**: `modern`, `minimal`, `corporate`, `playful`, `technical`, `dark`

**Setup**: `pip install google-genai pillow requests`

**Environment**: `GEMINI_API_KEY`

---

### large-pdf-reader

Extracts text from large PDFs that exceed normal processing limits by working page-by-page.

**Features**: Chunked extraction, specific page ranges, organized output with metadata and TOC, OCR fallback for scanned docs

**Output**:
```
extracted/
├── metadata.md          # Book metadata
├── full-text.md         # Complete text
├── chunks/              # Paginated chunks
└── summary.md           # Auto-generated TOC
```

**Setup**: `pip install pypdf pdfplumber`

---

### pdf

Comprehensive PDF manipulation toolkit with guides for every common PDF operation.

**Capabilities**: Text extraction, table extraction (to Excel), PDF creation, merge/split, rotate, watermark, password protection, form filling, OCR for scanned docs

**Tools covered**: pypdf, pdfplumber, reportlab, qpdf, pdftk, pytesseract

**Includes**: `forms.md` (form filling guide), `reference.md` (advanced features)

---

### spec-interview

Interview-driven spec writer. Asks targeted questions to gather concrete requirements, verification commands, edge cases, and constraints, then produces a structured specification.

**Output includes**: Requirements list, verification commands, success criteria, automation commands

**Supports**: Features, TDD, bug fixes, refactors, and multi-phase projects (auto-splits large projects into sequential phases)

---

### viral-tweet-crafter

Configurable tweet crafting skill with 8 tweet templates, posting strategy, and quality checks. Loads user profile/mission context if available, or asks quick questions to establish voice.

**Tweet Types**: Builder's Log, Manifesto, Teaching Moment, Community Spotlight, Progress Report, Contrarian Take, Personal Story, Thread Teaser

**Includes**: Weekly posting cadence, engagement principles, quality checklist, hashtag strategy, metrics guidance

**Configuration**: Define your mission, contrarian bet, values, and voice in a `SELF/` directory or answer setup questions on first use.

---

### youtube-music-downloader

Downloads YouTube audio as high-quality MP3 files. Accepts direct URLs, multiple URLs, or search queries.

**Setup**: `brew install yt-dlp ffmpeg`

**Configuration**: Set `MUSIC_OUTPUT_DIR` env var or uses `~/Music/downloads/` by default

---

### youtube-transcript

Extracts transcripts from YouTube videos with optional timestamps.

**Formats**: Plain text (default, cleaned into paragraphs) or timestamped (`[MM:SS] text`)

**Supports**: youtube.com, youtu.be, embed URLs, raw video IDs, auto-generated and manual captions

**Setup**: Uses `uv run` with `youtube-transcript-api`

---

## Environment Variables

| Variable | Required By | Get It From |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | blog-image-gen, blog-visual-gen, infographic-gen, comic-strip-maker, ai-film-maker | [Google AI Studio](https://aistudio.google.com/apikey) |
| `FAL_KEY` | ai-film-maker | [fal.ai](https://fal.ai) |
| `REPLICATE_API_TOKEN` | ai-film-maker | [replicate.com](https://replicate.com) |
| `TOGETHER_API_KEY` | ai-film-maker | [together.ai](https://together.ai) |
| `MUSIC_OUTPUT_DIR` | youtube-music-downloader (optional) | Local path |

## Contributing

1. Each skill lives in its own directory with a `SKILL.md` (or similar) as the entry point
2. Python scripts go in a `scripts/` subdirectory
3. Keep skills self-contained - no cross-skill dependencies
4. Use environment variables for API keys, never hardcode paths
5. Include prerequisites, usage examples, and troubleshooting in the skill doc

## License

Individual skills may have their own licenses. See each skill's directory for details.
