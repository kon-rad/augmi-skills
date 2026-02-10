#!/usr/bin/env python3
"""Google AI Studio provider for Veo video generation"""

import os
import time
import base64
from typing import Optional

try:
    import google.generativeai as genai
    from google.generativeai import types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from .base import BaseVideoProvider


class GoogleVideoProvider(BaseVideoProvider):
    """Google AI Studio Veo video generation provider"""

    MODELS = {
        "veo-2": "veo-2.0-generate-001",
        "veo-3": "veo-3.0-generate-001",
        "veo-3-fast": "veo-3.0-fast-generate-001",
        "veo-3.1": "veo-3.1-generate-preview",
        "veo-3.1-fast": "veo-3.1-fast-generate-preview",
    }

    def __init__(self):
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

        api_key = os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_AI_API_KEY or GEMINI_API_KEY environment variable not set"
            )

        genai.configure(api_key=api_key)
        self.client = genai.Client()

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def default_model(self) -> str:
        return self.MODELS["veo-2"]

    def _resolve_model(self, model: Optional[str]) -> str:
        """Resolve model shorthand to full model ID"""
        if model is None:
            return self.default_model
        # Check if it's a shorthand
        if model in self.MODELS:
            return self.MODELS[model]
        # Assume it's already a full model ID
        return model

    def generate_video(
        self,
        image_path: str,
        prompt: str,
        duration: int = 8,
        model: Optional[str] = None,
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> str:
        """
        Generate video from image using Google Veo.

        Args:
            image_path: Path to the source image
            prompt: Motion/animation description
            duration: Video duration (5-8 seconds for Veo 2)
            model: Model name or shorthand (veo-2, veo-3, veo-3-fast)
            aspect_ratio: Output aspect ratio (16:9 or 9:16)

        Returns:
            URL of the generated video
        """
        resolved_model = self._resolve_model(model)
        print(f"  Using Google {resolved_model}...")

        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()

        # Upload image to Google
        image_file = genai.upload_file(path=image_path)

        # Wait for file to be ready
        while image_file.state.name == "PROCESSING":
            time.sleep(2)
            image_file = genai.get_file(image_file.name)

        if image_file.state.name != "ACTIVE":
            raise Exception(f"Image upload failed: {image_file.state.name}")

        # Generate video
        print(f"  Generating {duration}s video: {prompt[:50]}...")

        operation = self.client.models.generate_videos(
            model=resolved_model,
            prompt=prompt,
            image=image_file,
            config=types.GenerateVideosConfig(
                duration_seconds=duration,
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
            )
        )

        # Poll for completion
        print("  Waiting for video generation...")
        poll_count = 0
        while not operation.done:
            time.sleep(10)
            poll_count += 1
            if poll_count % 6 == 0:  # Every minute
                print(f"  Still generating... ({poll_count * 10}s elapsed)")
            operation = self.client.operations.get(operation.name)

        if operation.error:
            raise Exception(f"Video generation failed: {operation.error}")

        # Get the video URL
        result = operation.result
        if hasattr(result, 'generated_videos') and result.generated_videos:
            video = result.generated_videos[0]
            if hasattr(video, 'video') and hasattr(video.video, 'uri'):
                return video.video.uri

        raise Exception("No video generated or unexpected response format")

    def upload_image(self, image_path: str) -> str:
        """Upload image to Google's storage"""
        image_file = genai.upload_file(path=image_path)

        # Wait for processing
        while image_file.state.name == "PROCESSING":
            time.sleep(2)
            image_file = genai.get_file(image_file.name)

        return image_file.uri
