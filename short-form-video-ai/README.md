# Short-Form Video AI - Enhanced Skills Package

**Status:** ✅ Ready for Production
**Created:** March 8, 2026
**Version:** 1.0

---

## What This Skill Does

Generates professional short-form vertical videos (30-60 seconds) for YouTube Shorts, Instagram Reels, and TikTok with:

✨ **Female Voice Narration** - Deepgram TTS (aura-luna-en - calm, pleasant)
✨ **Word-Synced Captions** - Current word highlights in bright cyan
✨ **AI-Generated Scenes** - Gemini Imagen 4 Fast (6 images, 9:16 portrait)
✨ **Animated Videos** - Fal.ai Kling image-to-video (5 seconds each)
✨ **Professional Audio Mix** - Narration (1.0) + Background music (0.15)
✨ **Large, Readable Captions** - 70px rounded font with 8px black shadow

---

## Quick Start

### 1. Prepare Your Script

Create `script.json` with 6 scenes:

```json
{
  "title": "Your Video Title",
  "voice": "aura-luna-en",
  "narration": {
    "text": "Your full narration (51 words = ~20s)"
  },
  "scenes": [
    {
      "sceneNumber": 1,
      "narration": "Scene narration...",
      "imageGenPrompt": "Image generation prompt...",
      "videoPrompt": "Motion direction..."
    },
    // ... 5 more scenes (6 total)
  ]
}
```

### 2. Set Up Environment

```bash
export DEEPGRAM_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export FAL_KEY="your-key"
```

### 3. Generate Video

```bash
# Generate narration with timestamps
python3 scripts/tts-narration.py script.json

# Generate images (use existing short-video-gen scripts)
python3 /Users/konradgnat/.claude/skills/short-video-gen/scripts/generate_images.py script.json

# Generate video clips (from images)
python3 /Users/konradgnat/.claude/skills/short-video-gen/scripts/generate_videos.py script.json

# Generate music
python3 /Users/konradgnat/.claude/skills/short-video-gen/scripts/generate_music.py script.json

# Compose final video with captions
python3 scripts/compose-with-captions.py script.json
```

**Output:** `final/{title}.mp4` (1080×1920, ready to upload)

---

## File Structure

```
.claude/skills/short-form-video-ai/
├── SKILL.md                    # Full documentation (2,500+ words)
├── README.md                   # This file
├── scripts/
│   ├── tts-narration.py       # Generate narration + extract timestamps
│   └── compose-with-captions.py # Compose video with captions
└── assets/
    └── .env.example           # API key template
```

---

## Voice Options

| Voice | Description | Best For |
|-------|-------------|----------|
| `aura-luna-en` | Female, calm, pleasant | **DEFAULT** - most content |
| `aura-asteria-en` | Female, warm, clear | Educational content |
| `aura-athena-en` | Female, confident | Promotional content |
| `aura-arcas-en` | Male, energetic | Hype content |

---

## Caption Styling

| Property | Value |
|----------|-------|
| Font | Raleway Bold (rounded) |
| Size | 70px |
| Base Color | White (#FFFFFF) |
| Current Word | Bright Cyan (#00FFFF) |
| Shadow | 8px black |
| Position | Center-bottom (80px from edge) |
| Animation | Word-synced highlighting |

---

## Example Video

**Reference:** `OUTPUT/20260306/ai-content-factory-ugc/final/ai-made-300k-in-90-days-FEMALE-VOICE.mp4`

- Duration: 20.8 seconds
- Voice: aura-luna-en (female)
- Captions: 70px rounded font
- File size: 7.6 MB
- Status: Ready for YouTube/Instagram/TikTok

---

## Key Features

### 1. Word-Synced Captions
- Exact timing from Deepgram TTS
- Current word pulses in bright cyan
- 3-word context visible
- Burned directly into video

### 2. Professional Voice
- Female voice by default (more engaging)
- Calm, pleasant delivery
- Word-level timestamp extraction
- Ready for caption synchronization

### 3. Image-to-Video Pipeline
- Generates 6 portrait images (9:16)
- Converts each to 5-second animated video
- Smooth camera movements and zoom effects
- Professional motion graphics

### 4. Complete Audio Mix
- Narration at full volume
- Background music at 0.15 volume
- Auto-trimmed to match video duration
- Professional mixing

---

## Customization

### Change Voice
Edit `config.voice` in script.json:
```json
"voice": "aura-asteria-en"  // Warm female voice
```

### Adjust Caption Size
Edit `config.fontSize`:
```json
"fontSize": 60  // Smaller captions (default: 70)
```

### Change Music Volume
Edit `config.musicVolume`:
```json
"musicVolume": 0.25  // Louder music (default: 0.15)
```

### Disable Captions
(Requires editing compose-with-captions.py)

---

## Cost Breakdown

Per 30-second video:

| Component | Cost | Notes |
|-----------|------|-------|
| Deepgram TTS | $0.01 | Narration + timestamps |
| Gemini Imagen | $0.08 | 6 images × ~$0.01-0.02 |
| Fal.ai Kling | $0.45 | 6 videos × ~$0.075 |
| Fal.ai Lyria2 | $0.07 | Background music |
| **Total** | **~$0.61** | Complete video |

**Cost to generate 100 videos:** ~$61

---

## Requirements

### API Accounts (Free/Paid)
- ✅ Deepgram (free tier available)
- ✅ Google Gemini API (free tier available)
- ✅ Fal.ai (free tier available)

### System
- Python 3.10+
- FFmpeg with libfreetype
- 50+ MB free disk space per video

### Fonts
- Raleway-Bold (or substitute rounded font)
- Install: `brew install font-raleway`

---

## Troubleshooting

**Captions not showing?**
- Verify FFmpeg has text support: `ffmpeg -filters | grep drawtext`
- Check font file path in script
- Try system font name without file path

**Narration too fast/slow?**
- Adjust narration word count (timing is automatic)
- Current word duration: ~400ms average

**Music cuts off?**
- Music auto-trims to narration length
- To extend: add more narration words

**File size too large?**
- Reduce resolution (default: 1080x1920)
- Increase FFmpeg CRF value (default: 23, higher = more compression)

---

## Comparison: Old vs New Skill

| Feature | Old (short-video-gen) | New (short-form-video-ai) |
|---------|----------------------|---------------------------|
| Default Voice | Male (aura-orion-en) | Female (aura-luna-en) ✨ |
| Caption Font Size | 150px | 70px (better for mobile) ✨ |
| Caption Font | Arial Bold | Raleway Bold (rounded) ✨ |
| Word Highlighting | Not implemented | Cyan highlight ✨ |
| Timestamp Extraction | Estimated | Deepgram TTS extraction ✨ |
| Image-to-Video | Ken Burns effect | Fal.ai Kling animation ✨ |
| File Size | ~15 MB | ~7.6 MB ✨ |
| Readability | Hard (150px on small phone) | Easy (70px optimized) ✨ |

---

## Next Steps

1. ✅ **Create script.json** for your content
2. ✅ **Run narration generation** to get timestamps
3. ✅ **Generate images** using Imagen
4. ✅ **Create video clips** using Kling
5. ✅ **Compose final video** with captions
6. ✅ **Upload to** YouTube Shorts / Instagram Reels / TikTok

---

## Support & Docs

- **Full Skill Documentation:** `SKILL.md` (2,500+ words)
- **Style Guide:** `/content/short-form-style-guide.md`
- **Example Output:** `OUTPUT/20260306/ai-content-factory-ugc/final/`

---

**Ready to create amazing short-form videos!** 🎬✨

Use this skill for YouTube Shorts, Instagram Reels, TikTok, and all vertical video platforms. Female voice, readable captions, professional quality.

**Let's go!** 🚀
