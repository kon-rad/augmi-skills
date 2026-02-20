# YouTube Music Downloader

Download YouTube videos as MP3 files to the local MUSIC folder.

## Triggers

Use this skill when the user wants to:
- Download music from YouTube
- Download audio from a YouTube video
- Save a song from YouTube as MP3
- Download music by searching for a song name or artist

## Prerequisites

This skill requires `yt-dlp` to be installed. If not installed, run:
```bash
brew install yt-dlp
```
or
```bash
pip install yt-dlp
```

ffmpeg is also required for audio conversion (already installed).

## Input Formats

The skill accepts:
1. **Direct YouTube URLs** (one or multiple):
   - `https://www.youtube.com/watch?v=VIDEO_ID`
   - `https://youtu.be/VIDEO_ID`

2. **Search queries** (song name, artist, etc.):
   - "Never Gonna Give You Up Rick Astley"
   - "lofi hip hop beats"

## Output Location

All downloads go to: `/Users/konradgnat/dev/notes/MUSIC/2025/`

Files are named as: `%(title)s.%(ext)s`

## Commands

### Download from URL(s)

For a single URL:
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "/Users/konradgnat/dev/notes/MUSIC/2025/%(title)s.%(ext)s" "URL"
```

For multiple URLs:
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "/Users/konradgnat/dev/notes/MUSIC/2025/%(title)s.%(ext)s" "URL1" "URL2" "URL3"
```

### Download by Search Query

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "/Users/konradgnat/dev/notes/MUSIC/2025/%(title)s.%(ext)s" "ytsearch:SEARCH_QUERY"
```

For multiple results from search:
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "/Users/konradgnat/dev/notes/MUSIC/2025/%(title)s.%(ext)s" "ytsearch5:SEARCH_QUERY"
```
(The number after ytsearch specifies how many results to download)

## Options Explained

- `-x` or `--extract-audio`: Extract audio only
- `--audio-format mp3`: Convert to MP3 format
- `--audio-quality 0`: Best audio quality (0-9, 0 is best)
- `-o`: Output template for filename

## Workflow

1. Check if yt-dlp is installed, install if needed
2. Parse user input (URLs or search query)
3. Run yt-dlp command
4. Confirm download completion and show file location

## Example Usage

User: "Download this song https://www.youtube.com/watch?v=w-7AnlFkc3s"

Response:
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "/Users/konradgnat/dev/notes/MUSIC/2025/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=w-7AnlFkc3s"
```

User: "Download Bohemian Rhapsody by Queen"

Response:
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "/Users/konradgnat/dev/notes/MUSIC/2025/%(title)s.%(ext)s" "ytsearch:Bohemian Rhapsody Queen"
```
