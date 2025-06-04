"""
Core functionality for YouTube Audio Downloader.
"""

from .downloader import YouTubeDownloader, download_audio
from .config import Config, config

__all__ = ["YouTubeDownloader", "download_audio", "Config", "config"]