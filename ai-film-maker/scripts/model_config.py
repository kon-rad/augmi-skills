#!/usr/bin/env python3
"""Model configuration and quality tiers for AI Film Maker"""

from typing import Dict, Tuple, Optional, Any

# Quality tier definitions
QUALITY_TIERS = {
    "cheapest": {
        "name": "Cheapest",
        "description": "Lowest cost, good for testing (~$1-2/video)",
        "text_to_image": {
            "provider": "together",
            "model": "qwen-image",
            "price_per_image": 0.0058
        },
        "image_to_video": {
            "provider": "fal",
            "model": "wan-2.5",
            "price_per_second": 0.05
        }
    },
    "balanced": {
        "name": "Balanced",
        "description": "Good quality at reasonable cost (~$2-3/video)",
        "text_to_image": {
            "provider": "fal",
            "model": "flux-dev",
            "price_per_image": 0.025
        },
        "image_to_video": {
            "provider": "fal",
            "model": "kling-2.5-turbo",
            "price_per_second": 0.07
        }
    },
    "highest": {
        "name": "Highest Quality",
        "description": "Best available quality (~$8-15/video)",
        "text_to_image": {
            "provider": "together",
            "model": "imagen-4-ultra",
            "price_per_image": 0.06
        },
        "image_to_video": {
            "provider": "google",
            "model": "veo-3",
            "price_per_second": 0.40
        }
    }
}

# Default tier when not specified
DEFAULT_TIER = "cheapest"

# All available models by provider and operation
AVAILABLE_MODELS = {
    "text_to_image": {
        "together": {
            "qwen-image": {
                "id": "Qwen/Qwen2.5-VL-72B-Instruct",
                "price": 0.0058,
                "description": "Fast, affordable image generation"
            },
            "nano-banana": {
                "id": "black-forest-labs/FLUX.1-schnell",
                "price": 0.039,
                "description": "High quality, efficient"
            },
            "flux-schnell": {
                "id": "black-forest-labs/FLUX.1-schnell",
                "price": 0.039,
                "description": "Fast FLUX model"
            },
            "flux-pro": {
                "id": "black-forest-labs/FLUX.1.1-pro",
                "price": 0.05,
                "description": "Professional FLUX model"
            },
            "imagen-4-ultra": {
                "id": "google/imagen-4-ultra",
                "price": 0.06,
                "description": "Highest quality Google model"
            }
        },
        "fal": {
            "flux-dev": {
                "id": "fal-ai/flux/dev",
                "price": 0.025,
                "description": "FLUX development model"
            },
            "flux-schnell": {
                "id": "fal-ai/flux/schnell",
                "price": 0.003,
                "description": "Fast FLUX model"
            },
            "flux-2-flex": {
                "id": "fal-ai/flux-2-flex",
                "price": 0.03,
                "description": "Flexible FLUX 2 model"
            },
            "recraft-v3": {
                "id": "fal-ai/recraft/v3/text-to-image",
                "price": 0.04,
                "description": "Specialized art generation"
            },
            "nano-banana-pro": {
                "id": "fal-ai/nano-banana-pro",
                "price": 0.04,
                "description": "High quality, good text rendering"
            }
        }
    },
    "image_to_video": {
        "google": {
            "veo-2": {
                "id": "veo-2.0-generate-001",
                "price_per_second": 0.35,
                "max_duration": 8,
                "description": "Google Veo 2 - great quality"
            },
            "veo-3-fast": {
                "id": "veo-3.0-fast-generate-001",
                "price_per_second": 0.15,
                "max_duration": 8,
                "description": "Google Veo 3 fast mode"
            },
            "veo-3": {
                "id": "veo-3.0-generate-001",
                "price_per_second": 0.40,
                "max_duration": 8,
                "description": "Google Veo 3 - excellent quality"
            }
        },
        "together": {
            "pixverse-v5": {
                "id": "pixverse/pixverse-v5",
                "price_per_video": 0.30,
                "duration": 5,
                "description": "Fast, affordable"
            },
            "hailuo": {
                "id": "minimax/hailuo",
                "price_per_video": 0.40,
                "duration": 10,
                "description": "Extended length capability"
            },
            "seedance-1-pro": {
                "id": "bytedance/seedance-1.0-pro",
                "price_per_video": 0.57,
                "duration": 5,
                "description": "Cinematic quality"
            },
            "veo-3": {
                "id": "google/veo-3.0",
                "price_per_video": 1.60,
                "duration": 8,
                "description": "Google Veo via Together"
            },
            "sora-2-pro": {
                "id": "openai/sora-2-pro",
                "price_per_video": 2.40,
                "duration": 8,
                "description": "Premium cinematic quality"
            }
        },
        "fal": {
            "wan-2.5": {
                "id": "fal-ai/wan-i2v",
                "price_per_second": 0.05,
                "description": "Cheapest option"
            },
            "kling-2.5-turbo": {
                "id": "fal-ai/kling-video/v2.5/turbo-pro/image-to-video",
                "price_per_second": 0.07,
                "description": "Good balance of speed and quality"
            },
            "kling-2.5": {
                "id": "fal-ai/kling-video/v2.5/pro/image-to-video",
                "price_per_second": 0.09,
                "description": "Higher quality Kling"
            },
            "kling-2.6": {
                "id": "fal-ai/kling-video/v2.6/pro/image-to-video",
                "price_per_second": 0.10,
                "description": "Latest Kling model"
            },
            "veo2": {
                "id": "fal-ai/veo2/image-to-video",
                "price_per_second": 0.50,
                "description": "Google Veo 2 via Fal"
            },
            "hunyuan-1.5": {
                "id": "fal-ai/hunyuan-video-v1.5/image-to-video",
                "price_per_second": 0.08,
                "description": "High quality open model"
            }
        }
    }
}


def get_tier_config(tier: str) -> Dict[str, Any]:
    """
    Get the configuration for a quality tier.

    Args:
        tier: Tier name (cheapest, balanced, highest)

    Returns:
        Tier configuration dictionary
    """
    return QUALITY_TIERS.get(tier, QUALITY_TIERS[DEFAULT_TIER])


def get_provider_and_model(tier: str, operation: str) -> Tuple[str, str]:
    """
    Get provider and model for a tier and operation.

    Args:
        tier: Quality tier name
        operation: Either "text_to_image" or "image_to_video"

    Returns:
        Tuple of (provider_name, model_name)
    """
    tier_config = get_tier_config(tier)
    op_config = tier_config[operation]
    return op_config["provider"], op_config["model"]


def estimate_cost(tier: str, num_images: int, video_seconds: int) -> float:
    """
    Estimate total cost for a video.

    Args:
        tier: Quality tier name
        num_images: Number of images to generate
        video_seconds: Total video duration in seconds

    Returns:
        Estimated cost in USD
    """
    tier_config = get_tier_config(tier)

    image_cost = num_images * tier_config["text_to_image"]["price_per_image"]

    video_config = tier_config["image_to_video"]
    if "price_per_second" in video_config:
        video_cost = video_seconds * video_config["price_per_second"]
    else:
        # Estimate based on per-video pricing
        video_cost = (video_seconds / 5) * video_config.get("price_per_video", 0.30)

    return image_cost + video_cost


def list_available_tiers() -> Dict[str, Dict[str, Any]]:
    """Return all available quality tiers with descriptions"""
    return {
        name: {
            "name": config["name"],
            "description": config["description"],
            "estimated_cost": estimate_cost(name, 6, 30)
        }
        for name, config in QUALITY_TIERS.items()
    }


def list_available_models(operation: str) -> Dict[str, Dict[str, Any]]:
    """
    List all available models for an operation.

    Args:
        operation: Either "text_to_image" or "image_to_video"

    Returns:
        Dictionary of provider -> model -> info
    """
    return AVAILABLE_MODELS.get(operation, {})


def get_model_info(provider: str, model: str, operation: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific model.

    Args:
        provider: Provider name
        model: Model shorthand name
        operation: Either "text_to_image" or "image_to_video"

    Returns:
        Model information dictionary or None
    """
    provider_models = AVAILABLE_MODELS.get(operation, {}).get(provider, {})
    return provider_models.get(model)


if __name__ == "__main__":
    # Print available tiers
    print("Available Quality Tiers:")
    print("-" * 50)
    for name, info in list_available_tiers().items():
        print(f"\n{info['name']} ({name}):")
        print(f"  {info['description']}")
        print(f"  Estimated cost for 30s video: ${info['estimated_cost']:.2f}")

    print("\n" + "=" * 50)
    print("\nAvailable Text-to-Image Models:")
    print("-" * 50)
    for provider, models in list_available_models("text_to_image").items():
        print(f"\n{provider.upper()}:")
        for model_name, info in models.items():
            print(f"  {model_name}: ${info['price']:.4f}/image - {info['description']}")

    print("\n" + "=" * 50)
    print("\nAvailable Image-to-Video Models:")
    print("-" * 50)
    for provider, models in list_available_models("image_to_video").items():
        print(f"\n{provider.upper()}:")
        for model_name, info in models.items():
            price_key = "price_per_second" if "price_per_second" in info else "price_per_video"
            unit = "/sec" if "price_per_second" in info else "/video"
            print(f"  {model_name}: ${info[price_key]:.2f}{unit} - {info['description']}")
