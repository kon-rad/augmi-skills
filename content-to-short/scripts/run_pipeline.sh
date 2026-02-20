#!/usr/bin/env bash
#
# Run the full content-to-short video pipeline.
#
# Usage:
#   ./run_pipeline.sh <content_file> [options]
#   ./run_pipeline.sh article.md --duration 45 --style hype --visual-mode mixed
#
# Runs: content_to_script → search_images → generate_images → generate_videos
#       → generate_audio → generate_music → compose_video

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <content_file> [--duration N] [--style S] [--visual-mode M] [--subtitles] [--no-music] [--skip-existing]"
    exit 1
fi

CONTENT_FILE="$1"
shift

# Defaults
DURATION=30
STYLE="educational"
VISUAL_MODE="mixed"
SUBTITLES=""
NO_MUSIC=""
SKIP_EXISTING=""
EXTRA_ARGS=()

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --duration|-d) DURATION="$2"; shift 2 ;;
        --style|-s) STYLE="$2"; shift 2 ;;
        --visual-mode) VISUAL_MODE="$2"; shift 2 ;;
        --subtitles) SUBTITLES="--subtitles"; shift ;;
        --no-music) NO_MUSIC="--no-music"; shift ;;
        --skip-existing) SKIP_EXISTING="--skip-existing"; shift ;;
        *) EXTRA_ARGS+=("$1"); shift ;;
    esac
done

SCRIPT_JSON="$(dirname "$(realpath "$CONTENT_FILE")")/script.json"

echo "=========================================="
echo "Content-to-Short Pipeline"
echo "=========================================="
echo "  Input:  $CONTENT_FILE"
echo "  Duration: ${DURATION}s"
echo "  Style: $STYLE"
echo "  Visual: $VISUAL_MODE"
echo ""

# Step 1: Parse content into script.json
echo "[1/7] Parsing content..."
python3 "$SCRIPT_DIR/content_to_script.py" "$CONTENT_FILE" \
    --duration "$DURATION" --style "$STYLE" --visual-mode "$VISUAL_MODE" \
    $SUBTITLES --cost-estimate

# Step 2: Search web images (for web/mixed modes)
if [ "$VISUAL_MODE" = "images-web" ] || [ "$VISUAL_MODE" = "mixed" ]; then
    echo ""
    echo "[2/7] Searching web images..."
    python3 "$SCRIPT_DIR/search_images.py" "$SCRIPT_JSON" $SKIP_EXISTING
else
    echo "[2/7] Skipping web images (mode: $VISUAL_MODE)"
fi

# Step 3: Generate AI images (for ai/video/mixed modes)
if [ "$VISUAL_MODE" = "images-ai" ] || [ "$VISUAL_MODE" = "video-ai" ] || [ "$VISUAL_MODE" = "mixed" ]; then
    echo ""
    echo "[3/7] Generating AI images..."
    python3 "$SCRIPT_DIR/generate_images.py" "$SCRIPT_JSON" $SKIP_EXISTING
else
    echo "[3/7] Skipping AI images (mode: $VISUAL_MODE)"
fi

# Step 4: Generate AI video clips (for video/mixed modes)
if [ "$VISUAL_MODE" = "video-ai" ] || [ "$VISUAL_MODE" = "mixed" ]; then
    echo ""
    echo "[4/7] Generating AI video clips..."
    python3 "$SCRIPT_DIR/generate_videos.py" "$SCRIPT_JSON" $SKIP_EXISTING
else
    echo "[4/7] Skipping AI video (mode: $VISUAL_MODE)"
fi

# Step 5: Generate narration audio
echo ""
echo "[5/7] Generating narration..."
python3 "$SCRIPT_DIR/generate_audio.py" "$SCRIPT_JSON"

# Step 6: Generate background music
if [ -z "$NO_MUSIC" ]; then
    echo ""
    echo "[6/7] Generating background music..."
    python3 "$SCRIPT_DIR/generate_music.py" "$SCRIPT_JSON"
else
    echo "[6/7] Skipping music (--no-music)"
fi

# Step 7: Compose final video
echo ""
echo "[7/7] Composing final video..."
python3 "$SCRIPT_DIR/compose_video.py" "$SCRIPT_JSON" $SUBTITLES $NO_MUSIC

echo ""
echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="
