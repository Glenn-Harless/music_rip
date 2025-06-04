"""
Command-line interfaces for YouTube Audio Downloader.
"""

from .download import main as download_main
from .batch import main as batch_main
from .config_manager import cli as config_cli

__all__ = ["download_main", "batch_main", "config_cli"]