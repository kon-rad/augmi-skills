#!/usr/bin/env python3
"""
Model configuration and cost estimation for the Short Video Generator.

Defines quality tiers, model IDs, cost estimates, and style-to-music mappings.
"""

# Gemini Imagen models for image generation
IMAGE_MODELS = {
    "imagen-4": "imagen-4.0-generate-001",
    "imagen-4-fast": "imagen-4.0-fast-generate-001",
    "imagen-3": "imagen-3.0-generate-002",
}
DEFAULT_IMAGE_MODEL = "imagen-4-fast"

# Fal.ai Kling models for image-to-video (cheapest first)
VIDEO_MODELS = {
    "kling-standard": {
        "model_id": "fal-ai/kling-video/v2.1/standard/image-to-video",
        "cost_per_clip": 0.10,
        "description": "Kling Standard - cheapest, good quality",
    },
    "kling-pro": {
        "model_id": "fal-ai/kling-video/v2.1/pro/image-to-video",
        "cost_per_clip": 0.25,
        "description": "Kling Pro - best quality, slower",
    },
}
DEFAULT_VIDEO_MODEL = "kling-standard"

# Fal.ai music generation
MUSIC_MODEL = {
    "model_id": "cassetteai/music-generator",
    "cost_per_track": 0.05,
}

# Cost estimates per unit
COSTS = {
    "deepgram_tts": 0.01,       # per narration call
    "gemini_imagen": 0.04,      # per image
    "fal_kling_standard": 0.10, # per 5s video clip
    "fal_kling_pro": 0.25,      # per 5s video clip
    "fal_music": 0.05,          # per music track
    "pexels": 0.00,             # free
}

# Visual modes
VISUAL_MODES = ["images-web", "images-ai", "video-ai", "mixed"]

# Style-to-music prompt mapping
STYLE_MUSIC_PROMPTS = {
    "educational": "Calm ambient electronic background music, minimal beats, informative and clean feel, soft synth pads",
    "promotional": "Upbeat modern pop instrumental, confident energy, rising build, catchy rhythm, corporate but cool",
    "storytelling": "Gentle acoustic guitar with soft piano, emotional and warm, cinematic undertones, intimate mood",
    "hype": "Hard-hitting trap beat, bass-heavy, intense energy, trending sound, fast tempo, bold drops",
}

DEFAULT_MUSIC_PROMPT = STYLE_MUSIC_PROMPTS["educational"]


def estimate_cost(num_scenes: int, visual_mode: str, video_model: str = DEFAULT_VIDEO_MODEL) -> dict:
    """Estimate total cost for a video with given parameters."""
    cost = {
        "narration": COSTS["deepgram_tts"],
        "music": COSTS["fal_music"],
        "images": 0.0,
        "video": 0.0,
        "total": 0.0,
    }

    if visual_mode == "images-web":
        cost["images"] = 0.0
    elif visual_mode == "images-ai":
        cost["images"] = num_scenes * COSTS["gemini_imagen"]
    elif visual_mode == "video-ai":
        cost["images"] = num_scenes * COSTS["gemini_imagen"]
        video_cost = COSTS.get(f"fal_{video_model.replace('-', '_')}", COSTS["fal_kling_standard"])
        cost["video"] = num_scenes * video_cost
    elif visual_mode == "mixed":
        # Hook + closer as video, rest as web images
        num_video = 2
        num_web = num_scenes - num_video
        cost["images"] = num_video * COSTS["gemini_imagen"]
        video_cost = COSTS.get(f"fal_{video_model.replace('-', '_')}", COSTS["fal_kling_standard"])
        cost["video"] = num_video * video_cost

    cost["total"] = cost["narration"] + cost["music"] + cost["images"] + cost["video"]
    return cost


def get_video_model_config(model_name: str = DEFAULT_VIDEO_MODEL) -> dict:
    """Get Fal.ai video model configuration."""
    return VIDEO_MODELS.get(model_name, VIDEO_MODELS[DEFAULT_VIDEO_MODEL])


def get_music_prompt(style: str) -> str:
    """Get style-appropriate music prompt."""
    return STYLE_MUSIC_PROMPTS.get(style, DEFAULT_MUSIC_PROMPT)


def print_cost_estimate(num_scenes: int, visual_mode: str):
    """Print formatted cost estimate."""
    cost = estimate_cost(num_scenes, visual_mode)
    print(f"\nCost Estimate ({visual_mode}, {num_scenes} scenes):")
    print(f"  Narration (Deepgram): ${cost['narration']:.2f}")
    print(f"  Music (Fal.ai):       ${cost['music']:.2f}")
    print(f"  Images:               ${cost['images']:.2f}")
    print(f"  Video clips:          ${cost['video']:.2f}")
    print(f"  ─────────────────────────")
    print(f"  Total:                ${cost['total']:.2f}")


if __name__ == "__main__":
    print("Visual Mode Cost Comparison (6 scenes / 30s video):\n")
    for mode in VISUAL_MODES:
        print_cost_estimate(6, mode)
    print("\n\nVisual Mode Cost Comparison (12 scenes / 60s video):\n")
    for mode in VISUAL_MODES:
        print_cost_estimate(12, mode)
