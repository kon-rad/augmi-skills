#!/usr/bin/env python3
"""Together AI provider for image and video generation"""

import os
import time
import base64
import requests
from typing import Optional

from .base import BaseImageProvider, BaseVideoProvider


class TogetherImageProvider(BaseImageProvider):
    """Together AI text-to-image provider"""

    MODELS = {
        "qwen-image": "Qwen/Qwen2.5-VL-72B-Instruct",
        "nano-banana": "black-forest-labs/FLUX.1-schnell",
        "flux-schnell": "black-forest-labs/FLUX.1-schnell",
        "flux-dev": "black-forest-labs/FLUX.1-dev",
        "flux-pro": "black-forest-labs/FLUX.1.1-pro",
        "imagen-4-ultra": "google/imagen-4-ultra",
    }

    def __init__(self):
        self.api_key = os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set")
        self.base_url = "https://api.together.ai/v1"

    @property
    def provider_name(self) -> str:
        return "together"

    @property
    def default_model(self) -> str:
        return self.MODELS["qwen-image"]

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
        Generate image from text using Together AI.

        Args:
            prompt: Text description of the image
            model: Model name or shorthand
            width: Output width
            height: Output height

        Returns:
            URL of the generated image
        """
        resolved_model = self._resolve_model(model)
        print(f"  Using Together AI {resolved_model}...")

        response = requests.post(
            f"{self.base_url}/images/generations",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": resolved_model,
                "prompt": prompt,
                "width": width,
                "height": height,
                "steps": kwargs.get("steps", 20),
                "n": 1,
                "response_format": "url"
            }
        )

        if response.status_code != 200:
            raise Exception(f"Together AI error: {response.status_code} - {response.text}")

        result = response.json()
        if "data" in result and len(result["data"]) > 0:
            return result["data"][0]["url"]

        raise Exception(f"Unexpected response format: {result}")


class TogetherVideoProvider(BaseVideoProvider):
    """Together AI image-to-video provider"""

    MODELS = {
        "pixverse-v5": "pixverse/pixverse-v5",
        "hailuo": "minimax/hailuo",
        "seedance-1-pro": "bytedance/seedance-1.0-pro",
        "veo-3": "google/veo-3.0",
        "sora-2-pro": "openai/sora-2-pro",
        "kling-v2.1": "kuaishou/kling-v2.1",
    }

    def __init__(self):
        self.api_key = os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set")
        self.base_url = "https://api.together.ai/v1"

    @property
    def provider_name(self) -> str:
        return "together"

    @property
    def default_model(self) -> str:
        return self.MODELS["pixverse-v5"]

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
        Generate video from image using Together AI.

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
        print(f"  Using Together AI {resolved_model}...")

        # Read and encode image as base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Determine mime type
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"

        image_url = f"data:{mime_type};base64,{image_data}"

        print(f"  Generating {duration}s video: {prompt[:50]}...")

        # Start video generation
        response = requests.post(
            f"{self.base_url}/videos/generations",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": resolved_model,
                "prompt": prompt,
                "image": image_url,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
            }
        )

        if response.status_code != 200:
            raise Exception(f"Together AI error: {response.status_code} - {response.text}")

        result = response.json()

        # Check if it's an async operation
        if "id" in result and "status" in result:
            return self._poll_for_completion(result["id"])

        # Direct result
        if "data" in result and len(result["data"]) > 0:
            return result["data"][0]["url"]

        raise Exception(f"Unexpected response format: {result}")

    def _poll_for_completion(self, job_id: str) -> str:
        """Poll for async video generation completion"""
        print("  Waiting for video generation...")
        poll_count = 0

        while True:
            time.sleep(10)
            poll_count += 1

            response = requests.get(
                f"{self.base_url}/videos/generations/{job_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            if response.status_code != 200:
                raise Exception(f"Polling error: {response.status_code} - {response.text}")

            result = response.json()
            status = result.get("status", "unknown")

            if status == "completed":
                if "data" in result and len(result["data"]) > 0:
                    return result["data"][0]["url"]
                raise Exception(f"Completed but no video URL: {result}")

            if status == "failed":
                raise Exception(f"Video generation failed: {result.get('error', 'Unknown error')}")

            if poll_count % 6 == 0:
                print(f"  Still generating... ({poll_count * 10}s elapsed)")

            if poll_count > 60:  # 10 minute timeout
                raise Exception("Video generation timed out")

    def upload_image(self, image_path: str) -> str:
        """Encode image as base64 data URL"""
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"

        return f"data:{mime_type};base64,{image_data}"
