#!/usr/bin/env python3
"""Provider factory and exports for AI Film Maker"""

from typing import Union
from .base import BaseImageProvider, BaseVideoProvider


def get_image_provider(provider_name: str) -> BaseImageProvider:
    """
    Factory function to get an image generation provider.

    Args:
        provider_name: Provider name (fal, together)

    Returns:
        Image provider instance

    Raises:
        ValueError: If provider is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "fal":
        from .fal_provider import FalImageProvider
        return FalImageProvider()

    elif provider_name == "together":
        from .together_provider import TogetherImageProvider
        return TogetherImageProvider()

    else:
        raise ValueError(
            f"Unknown image provider: {provider_name}. "
            f"Supported providers: fal, together"
        )


def get_video_provider(provider_name: str) -> BaseVideoProvider:
    """
    Factory function to get a video generation provider.

    Args:
        provider_name: Provider name (fal, together, google)

    Returns:
        Video provider instance

    Raises:
        ValueError: If provider is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "fal":
        from .fal_provider import FalVideoProvider
        return FalVideoProvider()

    elif provider_name == "together":
        from .together_provider import TogetherVideoProvider
        return TogetherVideoProvider()

    elif provider_name == "google":
        from .google_provider import GoogleVideoProvider
        return GoogleVideoProvider()

    else:
        raise ValueError(
            f"Unknown video provider: {provider_name}. "
            f"Supported providers: fal, together, google"
        )


__all__ = [
    "BaseImageProvider",
    "BaseVideoProvider",
    "get_image_provider",
    "get_video_provider",
]
