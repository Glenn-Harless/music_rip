"""
Core downloader functionality for YouTube Audio Downloader.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

import yt_dlp

from ..utils.progress import ProgressLogger, create_progress_hook


class YouTubeDownloader:
    """Main class for downloading YouTube videos as audio."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize downloader with optional configuration."""
        self.config = config or {}
    
    def download(
        self,
        url: str,
        output_dir: Path,
        quality: str = "192",
        format: str = "mp3",
        keep_video: bool = False,
        playlist: bool = False,
        verbose: bool = False,
        filename_template: Optional[str] = None
    ) -> bool:
        """
        Download audio from YouTube URL.
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save the audio file
            quality: Audio quality in kbps
            format: Audio format (mp3, flac, etc.)
            keep_video: Whether to keep the original video
            playlist: Whether to download entire playlist
            verbose: Enable verbose output
            filename_template: Custom filename template
        
        Returns:
            True if successful, False otherwise
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build output template
        if filename_template:
            output_template = str(output_dir / filename_template) + '.%(ext)s'
        else:
            output_template = str(output_dir / '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': not verbose,
            'no_warnings': False,
            'logger': ProgressLogger(verbose),
            'progress_hooks': [create_progress_hook()],
            'noplaylist': not playlist,
        }
        
        # Add post-processors for audio extraction
        if not keep_video:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': quality,
            }]
            
            # Add metadata embedding for MP3
            if format == 'mp3':
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to display details
                print("\n🔍 Fetching video information...")
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    # It's a playlist
                    print(f"📋 Playlist: {info.get('title', 'Unknown')}")
                    print(f"📺 Videos: {len(info['entries'])}")
                    if not playlist:
                        print("ℹ️  Only downloading first video (use --playlist to download all)")
                else:
                    # Single video
                    print(f"🎵 Title: {info.get('title', 'Unknown')}")
                    print(f"👤 Uploader: {info.get('uploader', 'Unknown')}")
                    duration = info.get('duration', 0)
                    print(f"⏱️  Duration: {duration // 60}:{duration % 60:02d}")
                
                print("\n📥 Starting download...")
                ydl.download([url])
                
                print("\n✨ All done!")
                return True
                
        except yt_dlp.utils.DownloadError as e:
            print(f"\n❌ Download failed: {e}", file=sys.stderr)
            return False
        except KeyboardInterrupt:
            print("\n⚠️  Download cancelled by user", file=sys.stderr)
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
            return False


def download_audio(
    url: str,
    output_dir: Path,
    quality: str = "192",
    format: str = "mp3",
    keep_video: bool = False,
    playlist: bool = False,
    verbose: bool = False,
    filename_template: Optional[str] = None
) -> bool:
    """
    Convenience function to download audio using YouTubeDownloader.
    
    See YouTubeDownloader.download for parameter descriptions.
    """
    downloader = YouTubeDownloader()
    return downloader.download(
        url=url,
        output_dir=output_dir,
        quality=quality,
        format=format,
        keep_video=keep_video,
        playlist=playlist,
        verbose=verbose,
        filename_template=filename_template
    )