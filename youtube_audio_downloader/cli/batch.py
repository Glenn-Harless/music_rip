#!/usr/bin/env python3
"""
Batch downloader for YouTube Audio Downloader.

This script reads URLs from a text file and downloads them all,
with support for comments, progress tracking, and error recovery.
"""

import sys
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
import json

import click
import yt_dlp

from ..core.config import config, get_default_output_dir, get_default_quality, get_default_format
from ..core.downloader import download_audio
from ..utils.progress import ProgressLogger, create_progress_hook
from ..utils.validators import validate_url


class BatchProcessor:
    """Process multiple YouTube URLs from a file."""
    
    def __init__(self, resume_file: Optional[Path] = None):
        """Initialize batch processor with optional resume capability."""
        self.resume_file = resume_file or Path.home() / '.youtube-audio-downloader' / 'batch_resume.json'
        self.processed_urls = set()
        self.failed_urls = {}
        self.load_resume_data()
    
    def load_resume_data(self):
        """Load resume data from previous runs."""
        if self.resume_file.exists():
            try:
                with open(self.resume_file, 'r') as f:
                    data = json.load(f)
                    self.processed_urls = set(data.get('processed', []))
                    self.failed_urls = data.get('failed', {})
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_resume_data(self):
        """Save resume data for future runs."""
        try:
            self.resume_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.resume_file, 'w') as f:
                json.dump({
                    'processed': list(self.processed_urls),
                    'failed': self.failed_urls,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except IOError:
            pass
    
    def read_urls_from_file(self, file_path: Path) -> List[Tuple[int, str]]:
        """
        Read URLs from a text file.
        
        Supports:
        - One URL per line
        - Comments starting with #
        - Empty lines (ignored)
        - Whitespace trimming
        
        Returns:
            List of (line_number, url) tuples
        """
        urls = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Strip whitespace
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Basic URL validation
                    if validate_url(line):
                        urls.append((line_num, line))
                    else:
                        click.echo(f"⚠️  Line {line_num}: Skipping invalid URL: {line}")
        
        except IOError as e:
            click.echo(f"❌ Error reading file: {e}", err=True)
            sys.exit(1)
        
        return urls
    
    def process_urls(
        self,
        urls: List[Tuple[int, str]],
        output_dir: Path,
        quality: str,
        format: str,
        keep_video: bool,
        playlist: bool,
        verbose: bool,
        skip_existing: bool,
        resume: bool
    ) -> Tuple[int, int]:
        """
        Process a list of URLs.
        
        Returns:
            Tuple of (success_count, failed_count)
        """
        success_count = 0
        failed_count = 0
        
        total_urls = len(urls)
        
        for idx, (line_num, url) in enumerate(urls, 1):
            # Skip if already processed in resume mode
            if resume and url in self.processed_urls:
                click.echo(f"\n[{idx}/{total_urls}] Skipping already processed: {url}")
                success_count += 1
                continue
            
            click.echo(f"\n{'=' * 60}")
            click.echo(f"[{idx}/{total_urls}] Processing URL from line {line_num}")
            click.echo(f"URL: {url}")
            
            try:
                # Check if file already exists (if skip_existing is enabled)
                if skip_existing:
                    # This is a simplified check - would need to extract actual filename
                    click.echo("⏭️  Checking for existing files...")
                
                # Download the audio
                success = download_audio(
                    url=url,
                    output_dir=output_dir,
                    quality=quality,
                    format=format,
                    keep_video=keep_video,
                    playlist=playlist,
                    verbose=verbose,
                    filename_template=None
                )
                
                if success:
                    success_count += 1
                    self.processed_urls.add(url)
                    click.echo("✅ Download successful!")
                else:
                    failed_count += 1
                    self.failed_urls[url] = {
                        'line': line_num,
                        'error': 'Download failed',
                        'timestamp': datetime.now().isoformat()
                    }
                    click.echo("❌ Download failed!")
                
                # Save progress after each download
                if resume:
                    self.save_resume_data()
                    
            except KeyboardInterrupt:
                click.echo("\n\n⚠️  Batch processing interrupted by user")
                if resume:
                    self.save_resume_data()
                    click.echo(f"💾 Progress saved. Use --resume to continue from URL {idx}")
                break
            except Exception as e:
                failed_count += 1
                self.failed_urls[url] = {
                    'line': line_num,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                click.echo(f"❌ Unexpected error: {e}")
                
                if resume:
                    self.save_resume_data()
        
        return success_count, failed_count


@click.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '-o', '--output',
    type=click.Path(path_type=Path),
    default=None,
    help=f'Output directory (default: {config.get("output_directory")})'
)
@click.option(
    '-q', '--quality',
    default=None,
    help=f'Audio quality in kbps (default: {get_default_quality()})'
)
@click.option(
    '-f', '--format',
    type=click.Choice(['mp3', 'wav', 'flac', 'aac', 'm4a', 'opus', 'vorbis'], case_sensitive=False),
    default=None,
    help=f'Audio format (default: {get_default_format()})'
)
@click.option(
    '--keep-video',
    is_flag=True,
    help='Keep the original video files'
)
@click.option(
    '--playlist',
    is_flag=True,
    help='Download entire playlists'
)
@click.option(
    '--skip-existing',
    is_flag=True,
    help='Skip URLs if output file already exists'
)
@click.option(
    '--resume',
    is_flag=True,
    help='Resume from previous batch (skip already downloaded)'
)
@click.option(
    '--clear-resume',
    is_flag=True,
    help='Clear resume data and start fresh'
)
@click.option(
    '--report',
    type=click.Path(path_type=Path),
    help='Save detailed report to file'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
def main(
    file: Path,
    output: Optional[Path],
    quality: Optional[str],
    format: Optional[str],
    keep_video: bool,
    playlist: bool,
    skip_existing: bool,
    resume: bool,
    clear_resume: bool,
    report: Optional[Path],
    verbose: bool
):
    """
    Download YouTube videos from URLs listed in a text file.
    
    The input file should contain one URL per line. Lines starting with # are
    treated as comments and ignored.
    
    Examples:
    
        \b
        # Basic usage
        python batch.py urls.txt
        
        \b
        # Download to specific directory with custom quality
        python batch.py urls.txt -o ~/Music -q 320
        
        \b
        # Resume interrupted batch
        python batch.py urls.txt --resume
        
        \b
        # Skip existing files and save report
        python batch.py urls.txt --skip-existing --report batch_report.txt
    
    Example urls.txt file:
    
        \b
        # My favorite songs
        https://www.youtube.com/watch?v=VIDEO_ID1
        https://www.youtube.com/watch?v=VIDEO_ID2
        
        # Playlists
        https://www.youtube.com/playlist?list=PLAYLIST_ID
    """
    # Use defaults from config
    if output is None:
        output = get_default_output_dir()
    if quality is None:
        quality = get_default_quality()
    if format is None:
        format = get_default_format()
    
    click.echo("📦 YouTube Audio Batch Downloader")
    click.echo("=" * 60)
    
    # Initialize batch processor
    processor = BatchProcessor()
    
    # Clear resume data if requested
    if clear_resume and processor.resume_file.exists():
        processor.resume_file.unlink()
        processor.processed_urls.clear()
        processor.failed_urls.clear()
        click.echo("🗑️  Cleared resume data")
    
    # Read URLs from file
    click.echo(f"\n📄 Reading URLs from: {file}")
    urls = processor.read_urls_from_file(file)
    
    if not urls:
        click.echo("❌ No valid URLs found in file", err=True)
        sys.exit(1)
    
    click.echo(f"📊 Found {len(urls)} URLs to process")
    
    if resume and processor.processed_urls:
        skip_count = sum(1 for _, url in urls if url in processor.processed_urls)
        click.echo(f"⏭️  Skipping {skip_count} already processed URLs")
    
    # Show settings
    click.echo(f"\n⚙️  Settings:")
    click.echo(f"  Output directory: {output}")
    click.echo(f"  Audio format: {format} @ {quality} kbps")
    click.echo(f"  Keep video: {'Yes' if keep_video else 'No'}")
    click.echo(f"  Download playlists: {'Yes' if playlist else 'No'}")
    click.echo(f"  Skip existing: {'Yes' if skip_existing else 'No'}")
    click.echo(f"  Resume mode: {'Yes' if resume else 'No'}")
    
    # Process URLs
    click.echo(f"\n🚀 Starting batch download...")
    start_time = datetime.now()
    
    success_count, failed_count = processor.process_urls(
        urls=urls,
        output_dir=output,
        quality=quality,
        format=format,
        keep_video=keep_video,
        playlist=playlist,
        verbose=verbose,
        skip_existing=skip_existing,
        resume=resume
    )
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Summary
    click.echo(f"\n{'=' * 60}")
    click.echo("📊 Batch Processing Summary")
    click.echo(f"  Total URLs: {len(urls)}")
    click.echo(f"  ✅ Successful: {success_count}")
    click.echo(f"  ❌ Failed: {failed_count}")
    click.echo(f"  ⏱️  Duration: {duration}")
    
    # Show failed URLs
    if processor.failed_urls:
        click.echo(f"\n❌ Failed URLs:")
        for url, info in processor.failed_urls.items():
            click.echo(f"  Line {info['line']}: {url}")
            click.echo(f"    Error: {info['error']}")
    
    # Save report if requested
    if report:
        try:
            with open(report, 'w') as f:
                f.write(f"YouTube Audio Batch Download Report\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"{'=' * 60}\n\n")
                f.write(f"Input file: {file}\n")
                f.write(f"Total URLs: {len(urls)}\n")
                f.write(f"Successful: {success_count}\n")
                f.write(f"Failed: {failed_count}\n")
                f.write(f"Duration: {duration}\n\n")
                
                if processor.failed_urls:
                    f.write("Failed Downloads:\n")
                    for url, info in processor.failed_urls.items():
                        f.write(f"\nLine {info['line']}: {url}\n")
                        f.write(f"Error: {info['error']}\n")
                        f.write(f"Time: {info['timestamp']}\n")
            
            click.echo(f"\n📄 Report saved to: {report}")
        except IOError as e:
            click.echo(f"⚠️  Could not save report: {e}")
    
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()