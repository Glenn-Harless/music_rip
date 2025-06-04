#!/usr/bin/env python3
"""
Configuration manager CLI for YouTube Audio Downloader.

This script allows users to view and modify configuration settings.
"""

import click
from pathlib import Path
from ..core.config import config


@click.group()
def cli():
    """Manage YouTube Audio Downloader configuration."""
    pass


@cli.command()
def show():
    """Show current configuration."""
    click.echo("🔧 Current Configuration")
    click.echo("=" * 50)
    
    settings = [
        ("Output Directory", config.get('output_directory')),
        ("Audio Quality", f"{config.get('audio_quality')} kbps"),
        ("Audio Format", config.get('audio_format')),
        ("Filename Template", config.get('filename_template')),
        ("Download Playlists", config.get('download_playlists')),
        ("Keep Video Files", config.get('keep_video')),
        ("Embed Metadata", config.get('embed_metadata')),
        ("Embed Thumbnail", config.get('embed_thumbnail')),
        ("Config File", str(config.config_path)),
    ]
    
    for label, value in settings:
        click.echo(f"{label:.<25} {value}")


@cli.command()
@click.argument('key')
@click.argument('value')
def set(key: str, value: str):
    """Set a configuration value."""
    # Convert string values to appropriate types
    if value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    
    try:
        config.set(key, value)
        config.save()
        click.echo(f"✅ Set {key} = {value}")
    except KeyError as e:
        click.echo(f"❌ {e}", err=True)


@cli.command()
@click.option('--key', help='Reset specific key only')
def reset(key: str):
    """Reset configuration to defaults."""
    if key:
        try:
            config.reset(key)
            config.save()
            click.echo(f"✅ Reset {key} to default value")
        except KeyError as e:
            click.echo(f"❌ {e}", err=True)
    else:
        if click.confirm("Reset all settings to defaults?"):
            config.reset()
            config.save()
            click.echo("✅ All settings reset to defaults")


@cli.command()
def templates():
    """Show available filename templates."""
    click.echo("📝 Available Filename Templates")
    click.echo("=" * 50)
    
    templates = config.get('filename_templates')
    for name, template in templates.items():
        click.echo(f"{name:.<20} {template}")
    
    click.echo("\nVariables:")
    click.echo("%(title)s       - Video title")
    click.echo("%(uploader)s    - Channel/uploader name")
    click.echo("%(upload_date)s - Upload date (YYYYMMDD)")
    click.echo("%(id)s          - Video ID")
    click.echo("%(playlist)s    - Playlist name")
    click.echo("%(playlist_index)s - Position in playlist")


if __name__ == '__main__':
    cli()