# YouTube Audio Downloader

A Python package for downloading YouTube videos as audio files with CLI interface.

## Features

- Download YouTube videos as MP3, FLAC, WAV, and other audio formats
- Batch download from text file with URLs
- Configurable audio quality (0-320 kbps)
- Playlist support
- Progress tracking with download speed and ETA
- Resume interrupted batch downloads
- Custom filename templates
- Configuration management

## Installation

```bash
poetry install
```

## Usage

### Single Download

```bash
youtube-audio-downloader https://www.youtube.com/watch?v=VIDEO_ID
```

### Batch Download

```bash
youtube-batch-downloader urls.txt
```

### Configuration

```bash
youtube-audio-config show
youtube-audio-config set audio_quality 320
```

## Command Line Options

- `-o, --output`: Output directory
- `-q, --quality`: Audio quality in kbps (0-320)
- `-f, --format`: Audio format (mp3, flac, wav, etc.)
- `--playlist`: Download entire playlist
- `--keep-video`: Keep original video file
- `-v, --verbose`: Enable verbose output

## Configuration

Default settings are stored in `~/.youtube-audio-downloader/config.json`

## License

MIT