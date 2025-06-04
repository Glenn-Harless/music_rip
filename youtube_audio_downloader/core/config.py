"""
Configuration settings for YouTube Audio Downloader.

This module contains default settings and configuration management
for the YouTube audio downloader application.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json


class Config:
    """Configuration manager for YouTube Audio Downloader."""
    
    # Default settings
    DEFAULTS = {
        # Output settings
        'output_directory': str(Path.home() / 'dev' / 'music_rip' / 'outputs'),
        'create_output_dir': True,
        
        # Audio settings
        'audio_quality': '192',  # kbps
        'audio_format': 'mp3',
        'keep_video': False,
        
        # File naming
        'filename_template': '%(title)s',
        'sanitize_filenames': True,
        'restrict_filenames': False,  # ASCII-only filenames
        
        # Playlist settings
        'download_playlists': False,
        'playlist_start': 1,
        'playlist_end': None,
        'playlist_items': None,  # e.g., "1,2,5,8-10"
        
        # Download behavior
        'overwrite_existing': False,
        'continue_on_error': True,
        'quiet_mode': False,
        'verbose_mode': False,
        
        # Network settings
        'concurrent_downloads': 1,
        'rate_limit': None,  # e.g., "1M" for 1MB/s
        'retries': 3,
        
        # Metadata
        'embed_metadata': True,
        'embed_thumbnail': True,
        'write_info_json': False,
        
        # Post-processing
        'extract_audio': True,
        'audio_post_processor': 'ffmpeg',
        
        # Advanced filename templates
        'filename_templates': {
            'default': '%(title)s',
            'detailed': '%(title)s - %(uploader)s',
            'dated': '%(upload_date)s - %(title)s',
            'playlist': '%(playlist_index)s - %(title)s',
            'full': '%(uploader)s - %(title)s [%(id)s]',
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to config file. If not provided,
                        uses ~/.youtube-audio-downloader/config.json
        """
        if config_path is None:
            config_dir = Path.home() / '.youtube-audio-downloader'
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / 'config.json'
        else:
            self.config_path = Path(config_path)
        
        self._config = self.DEFAULTS.copy()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Update only with valid keys
                    for key, value in user_config.items():
                        if key in self.DEFAULTS:
                            self._config[key] = value
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        if key in self.DEFAULTS:
            self._config[key] = value
        else:
            raise KeyError(f"Invalid configuration key: {key}")
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset(self, key: Optional[str] = None) -> None:
        """Reset configuration to defaults."""
        if key is None:
            self._config = self.DEFAULTS.copy()
        elif key in self.DEFAULTS:
            self._config[key] = self.DEFAULTS[key]
        else:
            raise KeyError(f"Invalid configuration key: {key}")
    
    def get_output_path(self) -> Path:
        """Get the output directory path, creating it if needed."""
        output_dir = Path(self._config['output_directory'])
        if self._config['create_output_dir']:
            output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def get_filename_template(self, template_name: Optional[str] = None) -> str:
        """Get a filename template by name or the default template."""
        if template_name and template_name in self._config['filename_templates']:
            return self._config['filename_templates'][template_name]
        return self._config['filename_template']
    
    def get_ydl_opts(self, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get yt-dlp options based on configuration.
        
        Args:
            overrides: Optional dictionary of values to override
        
        Returns:
            Dictionary of yt-dlp options
        """
        opts = {
            'outtmpl': str(self.get_output_path() / f"{self.get_filename_template()}.%(ext)s"),
            'quiet': self._config['quiet_mode'],
            'verbose': self._config['verbose_mode'],
            'ignoreerrors': self._config['continue_on_error'],
            'retries': self._config['retries'],
            'overwrites': self._config['overwrite_existing'],
            'restrictfilenames': self._config['restrict_filenames'],
            'noplaylist': not self._config['download_playlists'],
        }
        
        # Add rate limit if specified
        if self._config['rate_limit']:
            opts['ratelimit'] = self._config['rate_limit']
        
        # Add playlist range if specified
        if self._config['playlist_start']:
            opts['playliststart'] = self._config['playlist_start']
        if self._config['playlist_end']:
            opts['playlistend'] = self._config['playlist_end']
        if self._config['playlist_items']:
            opts['playlist_items'] = self._config['playlist_items']
        
        # Audio extraction options
        if self._config['extract_audio']:
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self._config['audio_format'],
                'preferredquality': self._config['audio_quality'],
            }]
            
            # Add metadata embedding
            if self._config['embed_metadata']:
                opts['postprocessors'].append({
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                })
            
            # Add thumbnail embedding for supported formats
            if self._config['embed_thumbnail'] and self._config['audio_format'] in ['mp3', 'm4a']:
                opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',
                })
                opts['writethumbnail'] = True
        
        # Write info JSON if requested
        opts['writeinfojson'] = self._config['write_info_json']
        
        # Apply any overrides
        if overrides:
            opts.update(overrides)
        
        return opts
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(path={self.config_path}, settings={len(self._config)})"


# Global configuration instance
config = Config()


# Convenience functions
def get_default_output_dir() -> Path:
    """Get the default output directory."""
    return config.get_output_path()


def get_default_quality() -> str:
    """Get the default audio quality."""
    return config.get('audio_quality')


def get_default_format() -> str:
    """Get the default audio format."""
    return config.get('audio_format')


def get_filename_template(name: Optional[str] = None) -> str:
    """Get a filename template."""
    return config.get_filename_template(name)