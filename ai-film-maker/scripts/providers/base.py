#!/usr/bin/env python3
"""Abstract base classes for AI providers"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseImageProvider(ABC):
    """Abstract base class for text-to-image providers"""

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        **kwargs
    ) -> str:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate
            model: Model identifier (provider-specific)
            width: Output image width
            height: Output image height
            **kwargs: Additional provider-specific parameters

        Returns:
            URL of the generated image
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider"""
        pass


class BaseVideoProvider(ABC):
    """Abstract base class for image-to-video providers"""

    @abstractmethod
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
        Generate a video from an image.

        Args:
            image_path: Path to the source image
            prompt: Text description of the motion/animation
            duration: Video duration in seconds
            model: Model identifier (provider-specific)
            aspect_ratio: Output aspect ratio
            **kwargs: Additional provider-specific parameters

        Returns:
            URL of the generated video
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider"""
        pass

    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to the provider's storage.
        Override in subclasses that need image upload.

        Args:
            image_path: Local path to the image

        Returns:
            URL or identifier for the uploaded image
        """
        raise NotImplementedError("This provider requires image upload implementation")
