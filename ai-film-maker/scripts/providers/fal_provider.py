#!/usr/bin/env python3
"""Fal.ai provider for image and video generation"""

import os
from typing import Optional

try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False

from .base import BaseImageProvider, BaseVideoProvider


class FalImageProvider(BaseImageProvider):
    """Fal.ai text-to-image provider"""

    MODELS = {
        "flux-dev": "fal-ai/flux/dev",
        "flux-schnell": "fal-ai/flux/schnell",
        "flux-pro": "fal-ai/flux-pro",
        "flux-2-flex": "fal-ai/flux-2-flex",
        "recraft-v3": "fal-ai/recraft/v3/text-to-image",
        "seedream-v4": "fal-ai/seedream-v4",
        "nano-banana-pro": "fal-ai/nano-banana-pro",
        "qwen-image": "fal-ai/qwen-image",
    }

    def __init__(self):
        if not FAL_AVAILABLE:
            raise ImportError(
                "fal-client package not installed. "
                "Run: pip install fal-client"
            )

        if not os.environ.get("FAL_KEY"):
            raise ValueError("FAL_KEY environment variable not set")

    @property
    def provider_name(self) -> str:
        return "fal"

    @property
    def default_model(self) -> str:
        return self.MODELS["flux-dev"]

    def _resolve_model(self, model: Optional[str]) -> str:
        """Resolve model shorthand to full model ID"""
        if model is None:
            return self.default_model
        if model in self.MODELS:
            return self.MODELS[model]
        return model

    def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        **kwargs
    ) -> str:
        """
        Generate image from text using Fal.ai.

        Args:
            prompt: Text description of the image
            model: Model name or shorthand
            width: Output width (used to determine aspect ratio)
            height: Output height

        Returns:
            URL of the generated image
        """
        resolved_model = self._resolve_model(model)
        print(f"  Using Fal.ai {resolved_model}...")

        # Determine image size preset based on aspect ratio
        if width > height:
            image_size = "landscape_16_9"
        elif height > width:
            image_size = "portrait_16_9"
        else:
            image_size = "square"

        result = fal_client.subscribe(
            resolved_model,
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": 1,
                **kwargs
            },
            with_logs=False
        )

        if "images" in result and len(result["images"]) > 0:
            return result["images"][0]["url"]

        raise Exception(f"Unexpected response format: {result}")


class FalVideoProvider(BaseVideoProvider):
    """Fal.ai image-to-video provider"""

    MODELS = {
        "wan-2.5": "fal-ai/wan-i2v",
        "wan-i2v": "fal-ai/wan-i2v",
        "kling-2.5-turbo": "fal-ai/kling-video/v2.5/turbo-pro/image-to-video",
        "kling-2.5": "fal-ai/kling-video/v2.5/pro/image-to-video",
        "kling-2.6": "fal-ai/kling-video/v2.6/pro/image-to-video",
        "kling-2.1": "fal-ai/kling-video/v2.1/pro/image-to-video",
        "veo2": "fal-ai/veo2/image-to-video",
        "hunyuan-1.5": "fal-ai/hunyuan-video-v1.5/image-to-video",
        "ltx-2-19b": "fal-ai/ltx-2-19b/image-to-video",
    }

    def __init__(self):
        if not FAL_AVAILABLE:
            raise ImportError(
                "fal-client package not installed. "
                "Run: pip install fal-client"
            )

        if not os.environ.get("FAL_KEY"):
            raise ValueError("FAL_KEY environment variable not set")

    @property
    def provider_name(self) -> str:
        return "fal"

    @property
    def default_model(self) -> str:
        return self.MODELS["kling-2.5-turbo"]

    def _resolve_model(self, model: Optional[str]) -> str:
        """Resolve model shorthand to full model ID"""
        if model is None:
            return self.default_model
        if model in self.MODELS:
            return self.MODELS[model]
        return model

    def generate_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 5,
        model: Optional[str] = None,
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> str:
        """
        Generate video from image using Fal.ai.

        Args:
            image_path: Path to the source image
            prompt: Motion/animation description
            duration: Video duration in seconds
            model: Model name or shorthand
            aspect_ratio: Output aspect ratio

        Returns:
            URL of the generated video
        """
        resolved_model = self._resolve_model(model)
        print(f"  Using Fal.ai {resolved_model}...")
        print(f"  Generating {duration}s video: {prompt[:50]}...")

        # Upload image to fal storage
        image_url = fal_client.upload_file(image_path)

        result = fal_client.subscribe(
            resolved_model,
            arguments={
                "image_url": image_url,
                "prompt": prompt,
                "duration": str(duration),
                "aspect_ratio": aspect_ratio,
                **kwargs
            },
            with_logs=True
        )

        # Handle different response formats
        if "video" in result:
            if isinstance(result["video"], dict) and "url" in result["video"]:
                return result["video"]["url"]
            elif isinstance(result["video"], str):
                return result["video"]

        if "videos" in result and len(result["videos"]) > 0:
            video = result["videos"][0]
            if isinstance(video, dict) and "url" in video:
                return video["url"]
            elif isinstance(video, str):
                return video

        raise Exception(f"Unexpected response format: {result}")

    def upload_image(self, image_path: str) -> str:
        """Upload image to Fal.ai storage"""
        return fal_client.upload_file(image_path)
