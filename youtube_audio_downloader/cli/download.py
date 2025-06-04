#!/usr/bin/env python3
"""
Main CLI for downloading YouTube videos as audio.
"""

import sys
from pathlib import Path
from typing import Optional, List

import click

from ..core.config import config, get_default_output_dir, get_default_quality, get_default_format
from ..core.downloader import download_audio
from ..utils.validators import validate_quality


@click.command()
@click.argument('urls', nargs=-1, required=True)
@click.option(
    '-o', '--output',
    type=click.Path(path_type=Path),
    default=None,
    help=f'Output directory for audio files (default: {config.get("output_directory")})'
)
@click.option(
    '-q', '--quality',
    default=None,
    callback=validate_quality,
    help=f'Audio quality in kbps (0-320, default: {get_default_quality()})'
)
@click.option(
    '-f', '--format',
    type=click.Choice(['mp3', 'wav', 'flac', 'aac', 'm4a', 'opus', 'vorbis', 'best'], case_sensitive=False),
    default=None,
    help=f'Audio format (default: {get_default_format()})'
)
@click.option(
    '--keep-video',
    is_flag=True,
    help='Keep the original video file'
)
@click.option(
    '--playlist',
    is_flag=True,
    help='Download entire playlist instead of just the first video'
)
@click.option(
    '--filename',
    help='Custom filename template (e.g., "%(title)s - %(uploader)s")'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
def main(
    urls: List[str],
    output: Optional[Path],
    quality: Optional[str],
    format: Optional[str],
    keep_video: bool,
    playlist: bool,
    filename: Optional[str],
    verbose: bool
):
    """
    Download YouTube videos as audio files.
    
    Examples:
    
        \b
        # Download a single video as MP3
        youtube-audio-downloader https://www.youtube.com/watch?v=VIDEO_ID
        
        \b
        # Download with custom quality and format
        youtube-audio-downloader URL -q 320 -f flac
        
        \b
        # Download to specific directory
        youtube-audio-downloader URL -o ~/Music/YouTube
        
        \b
        # Download multiple URLs
        youtube-audio-downloader URL1 URL2 URL3
        
        \b
        # Download entire playlist
        youtube-audio-downloader PLAYLIST_URL --playlist
        
        \b
        # Custom filename template
        youtube-audio-downloader URL --filename "%(title)s - %(upload_date)s"
    """
    # Use config defaults if not specified
    if output is None:
        output = get_default_output_dir()
    if quality is None:
        quality = get_default_quality()
    if format is None:
        format = get_default_format()
    
    # Update config with command line options if provided
    if playlist is not None:
        config.set('download_playlists', playlist)
    if keep_video is not None:
        config.set('keep_video', keep_video)
    if verbose is not None:
        config.set('verbose_mode', verbose)
    
    click.echo(f"🎵 YouTube Audio Downloader")
    click.echo(f"{'=' * 40}\n")
    
    if verbose:
        click.echo(f"📁 Output directory: {output.absolute()}")
        click.echo(f"🎚️  Quality: {quality} kbps")
        click.echo(f"📀 Format: {format}")
        click.echo(f"🎬 Keep video: {'Yes' if keep_video else 'No'}")
        click.echo(f"📋 Download playlists: {'Yes' if playlist else 'No'}")
        click.echo("")
    
    success_count = 0
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        if len(urls) > 1:
            click.echo(f"\n[{i}/{len(urls)}] Processing URL: {url}")
        
        if download_audio(url, output, quality, format, keep_video, playlist, verbose, filename):
            success_count += 1
        else:
            failed_urls.append(url)
    
    # Summary for multiple URLs
    if len(urls) > 1:
        click.echo(f"\n{'=' * 40}")
        click.echo(f"✅ Successfully downloaded: {success_count}/{len(urls)}")
        if failed_urls:
            click.echo(f"❌ Failed downloads:")
            for url in failed_urls:
                click.echo(f"   - {url}")
    
    sys.exit(0 if not failed_urls else 1)


if __name__ == '__main__':
    main()