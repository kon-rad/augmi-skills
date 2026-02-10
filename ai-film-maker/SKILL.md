---
name: ai-film-maker
description: >
  Creates personalized 30-second AI short films with the user as the main character.
  This skill should be used when users want to generate short videos, AI films,
  or personalized video content featuring themselves. Triggers on requests like
  "make me a short film", "create a video about me", "generate an AI movie",
  or "make a personalized video". Supports two modes: default (full creative
  pipeline) and seed (starts from a user-provided image analyzed by Gemini Vision).
  Handles the complete pipeline from story development through final video
  composition using multiple AI providers (Fal.ai, Google AI Studio, Together AI).
---

# AI Film Maker Skill

Create personalized 30-second AI short films with the user as the main character.

## Mode Selection

When this skill is invoked, **ask the user which mode they want to use**:

### Default Mode
The traditional creative pipeline where you develop the story from scratch based on user input, generate all images, and compose the final video.

### Seed Mode
Starts with a user-provided "seed image" that becomes the first scene. Gemini Vision analyzes the image and generates a story around it, creating a cohesive 30-second film that begins with that image.

**Ask the user:**
> Which mode would you like to use?
> 1. **Default** - I'll create the entire story and visuals from your concept
> 2. **Seed** - Start from an existing image (I'll analyze it and build a story around it)

## Prerequisites

### Required Environment Variables
```bash
# Required
FAL_KEY=<fal.ai API key>
REPLICATE_API_TOKEN=<replicate API token>

# Optional (for additional providers)
GOOGLE_AI_API_KEY=<Google AI Studio API key>  # Required for Seed mode & Veo video generation
TOGETHER_API_KEY=<Together AI API key>        # For alternative models
```

Load from `.env` file: `export $(cat .env | xargs)`

### Required Dependencies
```bash
pip install fal-client replicate requests google-generativeai
brew install ffmpeg  # or apt-get install ffmpeg
```

### Avatar Image
Place user's avatar image at one of:
- `IMAGES/avatar/avatar.jpg`
- `IMAGES/avatar/avatar.png`
- `IMAGES/avatar/ai-avatar-1.JPG`

## Output Folder Structure

All assets are organized per-film:
```
OUTPUT/
└── <film-slug>/
    ├── scene.json          # Project configuration
    ├── images/
    │   ├── 1-1_base.png    # Generated images (or seed image for scene 1)
    │   ├── 1-1_swapped.png # Face-swapped versions
    │   └── ...
    ├── videos/
    │   ├── 1-1.mp4         # Individual clips
    │   ├── 1-2.mp4
    │   └── <film-slug>.mp4 # Final composed video
    └── audio/
        ├── narration.mp3   # Voice narration
        ├── music_raw.mp3   # Generated music (full)
        └── music.mp3       # Trimmed to video length
```

---

## Default Mode Workflow

### Phase 0: Model Selection

Before story development, ask the user about quality/cost preferences:

**Quality Tiers:**

| Tier | Cost Estimate | Best For |
|------|---------------|----------|
| **Cheapest** (default) | ~$1-2/video | Testing, drafts, iteration |
| **Balanced** | ~$2-3/video | Good quality, reasonable cost |
| **Highest Quality** | ~$8-15/video | Final production, best visuals |

**Ask the user:**
1. Which quality tier would you prefer?
   - Cheapest (~$1-2) - Uses Together AI Qwen + Fal.ai Wan 2.5
   - Balanced (~$2-3) - Uses Fal.ai Flux + Fal.ai Kling 2.5
   - Highest (~$8-15) - Uses Together AI Imagen 4 + Google Veo 3
   - Custom - Let me choose specific models

2. If Custom, ask about:
   - Text-to-Image preference (Fal.ai or Together AI)
   - Image-to-Video preference (Fal.ai, Google, or Together AI)

Store selection in `scene.json` under `modelConfig`.

### Phase 1: Story Development

1. **Receive user's concept** - Theme, setting, or story idea
2. **Ask 2-3 clarifying questions:**
   - Tone/mood (epic, contemplative, humorous, dramatic)
   - Setting preferences
   - Action style (fast-paced, slow cinematic, documentary)
3. **Generate 30-second narrative script**
   - Clear beginning, middle, end
   - Narration that fits in ~25 seconds when spoken
4. **Present for approval** with scene breakdown
5. **Iterate** based on feedback

### Phase 2: Scene Breakdown

Structure the video as:
- **3 main scenes** (10 seconds each)
- **1-5 sub-scenes per scene** (5s or 10s each)
- **Total = 30 seconds**

For each sub-scene, define:
- `textToImagePrompt` - Detailed prompt for image generation
- `imageToVideoPrompt` - Motion/camera prompt for video
- `hasMainCharacter` - Whether face swap is needed
- `duration` - 5 or 10 seconds

### Phase 3: Create scene.json

Create `OUTPUT/<film-slug>/scene.json`:

```json
{
  "title": "Film Title",
  "totalDuration": 30,
  "avatarPath": "IMAGES/avatar/avatar.jpg",
  "modelConfig": {
    "qualityTier": "cheapest",
    "textToImage": {
      "provider": "together",
      "model": "qwen-image"
    },
    "imageToVideo": {
      "provider": "fal",
      "model": "wan-2.5"
    }
  },
  "config": {
    "voiceId": "am_adam",
    "voiceSpeed": 1.0,
    "musicPrompt": "Epic cinematic orchestral soundtrack",
    "musicVolume": 0.2,
    "narrationVolume": 1.0
  },
  "narration": {
    "text": "Full narration script here..."
  },
  "scenes": [
    {
      "sceneNumber": 1,
      "duration": 10,
      "subScenes": [
        {
          "subSceneId": "1-1",
          "duration": 5,
          "hasMainCharacter": false,
          "textToImagePrompt": "Aerial view of...",
          "imageToVideoPrompt": "Slow cinematic drone push..."
        }
      ]
    }
  ],
  "output": {
    "filmSlug": "film-title",
    "baseDir": "OUTPUT",
    "imagesDir": "OUTPUT/film-title/images",
    "videosDir": "OUTPUT/film-title/videos",
    "audioDir": "OUTPUT/film-title/audio",
    "finalVideo": "OUTPUT/film-title/videos/film-title.mp4"
  }
}
```

### Phase 4: Asset Generation

Run scripts in order from the skills directory:

```bash
cd /path/to/.claude/skills/ai-film-maker/scripts

# 1. Generate images + face swaps
python generate_images.py /path/to/OUTPUT/<film-slug>/scene.json

# 2. Generate video clips (takes longest ~2-5 min per clip)
python generate_videos.py /path/to/OUTPUT/<film-slug>/scene.json

# 3. Generate narration
python generate_narration.py /path/to/OUTPUT/<film-slug>/scene.json

# 4. Generate background music
python generate_music.py /path/to/OUTPUT/<film-slug>/scene.json
```

### Phase 5: Compose Final Video

```bash
# 5. Compose final video with audio
python compose_video.py /path/to/OUTPUT/<film-slug>/scene.json
```

---

## Seed Mode Workflow

Seed mode creates a film starting from a user-provided image, using Gemini Vision to analyze the image and generate a cohesive story.

### Phase 0: Gather Inputs

Ask the user for:
1. **Seed image path** - The image to start the story from
2. **Story direction** - A prompt describing what kind of story to tell (theme, mood, genre)
3. **Quality tier** - Same options as default mode (cheapest, balanced, highest)
4. **Voice preference** - Male/female, specific voice ID

### Phase 1: Analyze Seed Image

Run the seed image analysis script:

```bash
cd /path/to/.claude/skills/ai-film-maker/scripts

python analyze_seed_image.py "<seed_image_path>" "<story_prompt>" \
  --tier cheapest \
  --voice am_adam \
  --output-dir OUTPUT
```

This script:
1. Sends the seed image to **Gemini 2.0 Flash** vision model
2. Analyzes what's in the image
3. Generates a story that starts with this image
4. Creates **6 scenes** (5 seconds each = 30 seconds total)
5. Scene 1 uses the seed image directly (no text-to-image generation needed)
6. Scenes 2-6 get text-to-image prompts
7. All 6 scenes get image-to-video motion prompts
8. Generates narration text (~60-80 words for 30 seconds)
9. Creates the `scene.json` file with mode set to "seed"

### Phase 2: Review Generated Story

After analysis, present the user with:
- **Title** generated by Gemini
- **Story summary**
- **Narration script** (for 30 seconds)
- **Scene breakdown** (6 scenes, 5 seconds each)
- **Music prompt** for background music

Allow user to request modifications before proceeding.

### Phase 3: Generate Assets

Run the same scripts as default mode:

```bash
# 1. Generate images (5 images - scene 1 is skipped, uses seed image)
python generate_images.py /path/to/OUTPUT/<film-slug>/scene.json

# 2. Generate video clips (6 videos - 5 seconds each)
python generate_videos.py /path/to/OUTPUT/<film-slug>/scene.json

# 3. Generate narration
python generate_narration.py /path/to/OUTPUT/<film-slug>/scene.json

# 4. Generate background music
python generate_music.py /path/to/OUTPUT/<film-slug>/scene.json
```

### Phase 4: Compose Final Video

```bash
# 5. Compose final video with audio
python compose_video.py /path/to/OUTPUT/<film-slug>/scene.json
```

### Seed Mode scene.json Structure

```json
{
  "title": "Story Title from Gemini",
  "totalDuration": 30,
  "mode": "seed",
  "seedImagePath": "path/to/original/seed/image.jpg",
  "avatarPath": "IMAGES/avatar/avatar.jpg",
  "modelConfig": {
    "qualityTier": "cheapest"
  },
  "config": {
    "voiceId": "am_adam",
    "voiceSpeed": 1.0,
    "musicPrompt": "Generated music description...",
    "musicVolume": 0.2,
    "narrationVolume": 1.0
  },
  "narration": {
    "text": "Full narration script generated by Gemini..."
  },
  "scenes": [
    {
      "sceneNumber": 1,
      "duration": 5,
      "subScenes": [
        {
          "subSceneId": "1-1",
          "duration": 5,
          "hasMainCharacter": true,
          "useSeedImage": true,
          "outputImagePath": "OUTPUT/film/images/1-1_base.jpg",
          "textToImagePrompt": null,
          "imageToVideoPrompt": "Slow push in on the subject..."
        }
      ]
    },
    {
      "sceneNumber": 2,
      "duration": 5,
      "subScenes": [
        {
          "subSceneId": "2-1",
          "duration": 5,
          "hasMainCharacter": false,
          "textToImagePrompt": "Detailed prompt for scene 2...",
          "imageToVideoPrompt": "Camera movement description..."
        }
      ]
    }
  ],
  "output": {
    "filmSlug": "story-title",
    "baseDir": "OUTPUT",
    "imagesDir": "OUTPUT/story-title/images",
    "videosDir": "OUTPUT/story-title/videos",
    "audioDir": "OUTPUT/story-title/audio",
    "finalVideo": "OUTPUT/story-title/videos/story-title.mp4"
  }
}
```

---

## Quality Tier Details

### Cheapest Tier (~$1-2/video)
Best for testing and iteration.

| Operation | Provider | Model | Cost |
|-----------|----------|-------|------|
| Text-to-Image | Together AI | Qwen Image | $0.006/image |
| Image-to-Video | Fal.ai | Wan 2.5 | $0.05/second |

### Balanced Tier (~$2-3/video)
Good quality at reasonable cost.

| Operation | Provider | Model | Cost |
|-----------|----------|-------|------|
| Text-to-Image | Fal.ai | FLUX Dev | $0.025/image |
| Image-to-Video | Fal.ai | Kling 2.5 Turbo | $0.07/second |

### Highest Quality Tier (~$8-15/video)
Best available visual quality.

| Operation | Provider | Model | Cost |
|-----------|----------|-------|------|
| Text-to-Image | Together AI | Imagen 4 Ultra | $0.06/image |
| Image-to-Video | Google | Veo 3 | $0.40/second |

## Available Models

### Text-to-Image Models

**Fal.ai:**
- `flux-dev` - FLUX development model ($0.025/image)
- `flux-schnell` - Fast FLUX ($0.003/image)
- `recraft-v3` - Art generation ($0.04/image)
- `nano-banana-pro` - High quality ($0.04/image)

**Together AI:**
- `qwen-image` - Fast, affordable ($0.006/image)
- `nano-banana` - High quality ($0.039/image)
- `flux-pro` - Professional ($0.05/image)
- `imagen-4-ultra` - Highest quality ($0.06/image)

### Image-to-Video Models

**Fal.ai:**
- `wan-2.5` - Cheapest option ($0.05/sec)
- `kling-2.5-turbo` - Good balance ($0.07/sec)
- `kling-2.6` - Latest Kling ($0.10/sec)
- `veo2` - Google Veo 2 via Fal ($0.50/sec)

**Google AI Studio:**
- `veo-2` - Great quality ($0.35/sec)
- `veo-3-fast` - Fast mode ($0.15/sec)
- `veo-3` - Excellent quality ($0.40/sec)

**Together AI:**
- `pixverse-v5` - Fast, affordable ($0.30/video)
- `hailuo` - Extended length ($0.40/video)
- `seedance-1-pro` - Cinematic ($0.57/video)
- `sora-2-pro` - Premium ($2.40/video)

## Voice Options

### Male Voices (default: `am_adam`)
- `am_adam` - Clear, professional male voice
- `am_echo` - Resonant, deep
- `am_eric` - Warm, friendly
- `am_fenrir` - Strong, dramatic
- `am_liam` - Young, energetic
- `am_michael` - Mature, authoritative
- `am_onyx` - Deep, smooth
- `am_puck` - Playful, light

### Female Voices
- `af_heart` - Warm, engaging
- `af_bella` - Clear, professional
- `af_jessica` - Friendly, approachable
- `af_nova` - Modern, fresh
- `af_sarah` - Natural, conversational

## Prompt Best Practices

### Text-to-Image Prompts
- Include: subject, action, setting, lighting, camera angle
- Add: "cinematic composition", "high quality", "detailed"
- Specify aspect: works best with 16:9 landscape

### Image-to-Video Prompts
- Focus on: camera movement, subject motion, atmosphere
- Use: "slow", "cinematic", "gentle", "dramatic"
- Describe: what changes over the 5-10 seconds

### Music Prompts
- Describe: genre, instruments, mood, tempo
- Example: "Epic cinematic orchestral with hopeful synth, building momentum"

## Troubleshooting

### Video generation fails
- Check API keys are exported (FAL_KEY, GOOGLE_AI_API_KEY, TOGETHER_API_KEY)
- Verify image file exists
- Try regenerating single clip
- For Google Veo: Ensure you have Tier 1 API access (not free tier)

### Face swap quality issues
- Use clear, front-facing avatar photo
- Ensure good lighting in avatar
- Avatar face should be clearly visible

### Audio sync issues
- Narration should be ~25 seconds for 30-second video
- Adjust `voiceSpeed` in config (0.9 = slower, 1.1 = faster)

### Provider-specific issues
- **Google Veo**: Videos expire after 2 days - download promptly
- **Together AI**: Some models may have rate limits
- **Fal.ai**: Check status at status.fal.ai if experiencing delays

### Seed mode issues
- **Gemini API error**: Ensure GOOGLE_AI_API_KEY is set and has Gemini access
- **Story doesn't match image**: Try a more specific story prompt
- **Seed image not used**: Verify the image path is correct and file exists
