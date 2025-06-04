"""
Validation utilities for YouTube Audio Downloader.
"""

import click


def validate_quality(ctx, param, value):
    """Validate audio quality parameter."""
    if value is None:
        return None
    try:
        quality = int(value)
        if quality < 0 or quality > 320:
            raise click.BadParameter('Quality must be between 0 and 320')
        return str(quality)
    except ValueError:
        raise click.BadParameter('Quality must be a number')


def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    return url.startswith(('http://', 'https://', 'www.'))