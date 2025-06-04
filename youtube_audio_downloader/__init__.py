"""
YouTube Audio Downloader

A Python package for downloading YouTube videos as audio files.
"""

__version__ = "0.1.0"
__author__ = "Glenn Harless"
__email__ = "glenn@nodus.io"

# Import main components for easier access
from .core.config import Config, config
from .core.downloader import YouTubeDownloader, download_audio
from .cli.download import main as cli_main
from .cli.batch import main as batch_main
from .cli.config_manager import cli as config_cli

__all__ = [
    "Config",
    "config", 
    "YouTubeDownloader",
    "download_audio",
    "cli_main",
    "batch_main",
    "config_cli",
    "__version__",
]