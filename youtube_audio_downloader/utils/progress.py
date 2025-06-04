"""
Progress tracking utilities for YouTube downloads.
"""

import sys


class ProgressLogger:
    """Custom logger for yt-dlp with progress tracking."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def debug(self, msg):
        if self.verbose and not msg.startswith('[download]'):
            print(f"DEBUG: {msg}")
        # Suppress yt-dlp's own download progress messages
    
    def warning(self, msg):
        print(f"⚠️  Warning: {msg}")
    
    def error(self, msg):
        print(f"❌ Error: {msg}", file=sys.stderr)


def create_progress_hook():
    """Create a progress hook for download tracking."""
    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            if total > 0:
                percent = (downloaded / total) * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                if speed:
                    speed_str = f"{speed / 1024 / 1024:.2f} MB/s"
                else:
                    speed_str = "N/A"
                
                if eta and isinstance(eta, (int, float)):
                    eta_min = int(eta // 60)
                    eta_sec = int(eta % 60)
                    eta_str = f"{eta_min}:{eta_sec:02d}"
                else:
                    eta_str = "N/A"
                
                bar_length = 40
                filled = int(bar_length * downloaded // total)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f"\r[{bar}] {percent:.1f}% | {speed_str} | ETA: {eta_str}", end='', flush=True)
        
        elif d['status'] == 'finished':
            print("\n✅ Download complete, converting to audio...", end='', flush=True)
    
    return hook