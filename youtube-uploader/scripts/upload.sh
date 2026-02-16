#!/usr/bin/env bash
#
# YouTube Resumable Video Upload Script
# Handles token refresh, resumable upload, thumbnail, and playlist insertion.
#
# Usage:
#   bash upload.sh --file video.mp4 --title "My Video" [options]
#
# Options:
#   --file PATH          Video file path (required)
#   --title TEXT         Video title (required, max 100 chars)
#   --description TEXT   Video description (max 5000 chars)
#   --tags TEXT          Comma-separated tags
#   --privacy STATUS     private|public|unlisted (default: private)
#   --category ID        Category ID (default: 22 = People & Blogs)
#   --publish-at TIME    ISO 8601 UTC time for scheduled publish
#   --thumbnail PATH     Thumbnail image path (jpg/png, max 2MB)
#   --playlist ID        Playlist ID to add video to after upload
#   --made-for-kids BOOL true|false (default: false)

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${SKILL_DIR}/.env"

# Defaults
DESCRIPTION=""
TAGS=""
PRIVACY="private"
CATEGORY="22"
PUBLISH_AT=""
THUMBNAIL=""
PLAYLIST=""
MADE_FOR_KIDS="false"
MAX_RETRIES=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[yt-upload]${NC} $*"; }
warn()  { echo -e "${YELLOW}[yt-upload]${NC} $*"; }
error() { echo -e "${RED}[yt-upload]${NC} $*" >&2; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --file)         FILE="$2"; shift 2 ;;
        --title)        TITLE="$2"; shift 2 ;;
        --description)  DESCRIPTION="$2"; shift 2 ;;
        --tags)         TAGS="$2"; shift 2 ;;
        --privacy)      PRIVACY="$2"; shift 2 ;;
        --category)     CATEGORY="$2"; shift 2 ;;
        --publish-at)   PUBLISH_AT="$2"; shift 2 ;;
        --thumbnail)    THUMBNAIL="$2"; shift 2 ;;
        --playlist)     PLAYLIST="$2"; shift 2 ;;
        --made-for-kids) MADE_FOR_KIDS="$2"; shift 2 ;;
        *) error "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate required args
if [[ -z "${FILE:-}" ]]; then
    error "Missing required --file argument"
    exit 1
fi
if [[ -z "${TITLE:-}" ]]; then
    error "Missing required --title argument"
    exit 1
fi
if [[ ! -f "${FILE}" ]]; then
    error "File not found: ${FILE}"
    exit 1
fi

# Load credentials
if [[ ! -f "${ENV_FILE}" ]]; then
    error "No .env file found at ${ENV_FILE}"
    error "Run: python3 ${SKILL_DIR}/scripts/setup_oauth.py"
    exit 1
fi

source "${ENV_FILE}"

if [[ -z "${YOUTUBE_CLIENT_ID:-}" ]] || [[ -z "${YOUTUBE_CLIENT_SECRET:-}" ]] || [[ -z "${YOUTUBE_REFRESH_TOKEN:-}" ]]; then
    error "Missing credentials in .env. Run setup_oauth.py first."
    exit 1
fi

# Get file info
FILE_SIZE=$(stat -f%z "${FILE}" 2>/dev/null || stat --printf="%s" "${FILE}" 2>/dev/null)
FILE_EXT="${FILE##*.}"
MIME_TYPE="video/mp4"
case "${FILE_EXT,,}" in
    mp4)  MIME_TYPE="video/mp4" ;;
    mov)  MIME_TYPE="video/quicktime" ;;
    avi)  MIME_TYPE="video/x-msvideo" ;;
    webm) MIME_TYPE="video/webm" ;;
    flv)  MIME_TYPE="video/x-flv" ;;
    mkv)  MIME_TYPE="video/x-matroska" ;;
    *)    MIME_TYPE="video/*" ;;
esac

log "File: ${FILE} ($(echo "scale=1; ${FILE_SIZE}/1048576" | bc)MB, ${MIME_TYPE})"

# Refresh access token
refresh_token() {
    log "Refreshing access token..."
    local response
    response=$(curl -s -X POST https://oauth2.googleapis.com/token \
        -d "client_id=${YOUTUBE_CLIENT_ID}" \
        -d "client_secret=${YOUTUBE_CLIENT_SECRET}" \
        -d "refresh_token=${YOUTUBE_REFRESH_TOKEN}" \
        -d "grant_type=refresh_token")

    ACCESS_TOKEN=$(echo "${response}" | jq -r '.access_token // empty')
    if [[ -z "${ACCESS_TOKEN}" ]]; then
        error "Failed to refresh token: ${response}"
        exit 1
    fi
    log "Token refreshed successfully"
}

refresh_token

# Build tags JSON array
TAGS_JSON="[]"
if [[ -n "${TAGS}" ]]; then
    TAGS_JSON=$(echo "${TAGS}" | jq -R 'split(",") | map(ltrimstr(" ") | rtrimstr(" "))')
fi

# Build status JSON
STATUS_JSON="{\"privacyStatus\": \"${PRIVACY}\", \"selfDeclaredMadeForKids\": ${MADE_FOR_KIDS}}"
if [[ -n "${PUBLISH_AT}" ]]; then
    STATUS_JSON="{\"privacyStatus\": \"private\", \"publishAt\": \"${PUBLISH_AT}\", \"selfDeclaredMadeForKids\": ${MADE_FOR_KIDS}}"
fi

# Build metadata JSON
METADATA=$(jq -n \
    --arg title "${TITLE}" \
    --arg desc "${DESCRIPTION}" \
    --argjson tags "${TAGS_JSON}" \
    --arg cat "${CATEGORY}" \
    --argjson status "${STATUS_JSON}" \
    '{
        snippet: {
            title: $title,
            description: $desc,
            tags: $tags,
            categoryId: $cat
        },
        status: $status
    }')

log "Initiating resumable upload..."

# Step 1: Initiate resumable upload session
INIT_RESPONSE=$(curl -s -i -X POST \
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json; charset=UTF-8" \
    -H "X-Upload-Content-Length: ${FILE_SIZE}" \
    -H "X-Upload-Content-Type: ${MIME_TYPE}" \
    -d "${METADATA}" 2>&1)

UPLOAD_URL=$(echo "${INIT_RESPONSE}" | grep -i "^location:" | sed 's/[Ll]ocation: //' | tr -d '\r\n')

if [[ -z "${UPLOAD_URL}" ]]; then
    # Check for error in response body
    ERROR_BODY=$(echo "${INIT_RESPONSE}" | tail -1)
    error "Failed to initiate upload session"
    error "Response: ${ERROR_BODY}"
    exit 1
fi

log "Upload session created"

# Step 2: Upload file with retry
ATTEMPT=0
VIDEO_ID=""

while [[ ${ATTEMPT} -lt ${MAX_RETRIES} ]]; do
    ATTEMPT=$((ATTEMPT + 1))
    log "Upload attempt ${ATTEMPT}/${MAX_RETRIES}..."

    UPLOAD_RESPONSE=$(curl -s -X PUT "${UPLOAD_URL}" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: ${MIME_TYPE}" \
        --data-binary "@${FILE}" 2>&1)

    VIDEO_ID=$(echo "${UPLOAD_RESPONSE}" | jq -r '.id // empty')

    if [[ -n "${VIDEO_ID}" ]]; then
        log "Upload successful!"
        break
    fi

    # Check if we need to refresh token
    ERROR_CODE=$(echo "${UPLOAD_RESPONSE}" | jq -r '.error.code // empty')
    if [[ "${ERROR_CODE}" == "401" ]]; then
        warn "Token expired, refreshing..."
        refresh_token
    fi

    if [[ ${ATTEMPT} -lt ${MAX_RETRIES} ]]; then
        WAIT=$((ATTEMPT * 5))
        warn "Upload failed. Retrying in ${WAIT}s..."
        warn "Error: ${UPLOAD_RESPONSE}"
        sleep ${WAIT}
    fi
done

if [[ -z "${VIDEO_ID}" ]]; then
    error "Upload failed after ${MAX_RETRIES} attempts"
    error "Last response: ${UPLOAD_RESPONSE}"
    exit 1
fi

VIDEO_URL="https://youtu.be/${VIDEO_ID}"
log "Video ID: ${VIDEO_ID}"
log "URL: ${VIDEO_URL}"

# Step 3: Upload thumbnail (if provided)
if [[ -n "${THUMBNAIL}" ]]; then
    if [[ ! -f "${THUMBNAIL}" ]]; then
        warn "Thumbnail file not found: ${THUMBNAIL}"
    else
        log "Uploading thumbnail..."
        THUMB_EXT="${THUMBNAIL##*.}"
        THUMB_MIME="image/jpeg"
        [[ "${THUMB_EXT,,}" == "png" ]] && THUMB_MIME="image/png"

        THUMB_RESPONSE=$(curl -s -X POST \
            "https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=${VIDEO_ID}" \
            -H "Authorization: Bearer ${ACCESS_TOKEN}" \
            -H "Content-Type: ${THUMB_MIME}" \
            --data-binary "@${THUMBNAIL}")

        if echo "${THUMB_RESPONSE}" | jq -e '.items' >/dev/null 2>&1; then
            log "Thumbnail uploaded successfully"
        else
            warn "Thumbnail upload may have failed: ${THUMB_RESPONSE}"
        fi
    fi
fi

# Step 4: Add to playlist (if provided)
if [[ -n "${PLAYLIST}" ]]; then
    log "Adding to playlist ${PLAYLIST}..."
    PL_RESPONSE=$(curl -s -X POST \
        "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"snippet\": {
                \"playlistId\": \"${PLAYLIST}\",
                \"resourceId\": {
                    \"kind\": \"youtube#video\",
                    \"videoId\": \"${VIDEO_ID}\"
                }
            }
        }")

    if echo "${PL_RESPONSE}" | jq -e '.id' >/dev/null 2>&1; then
        log "Added to playlist successfully"
    else
        warn "Playlist insertion may have failed: ${PL_RESPONSE}"
    fi
fi

# Summary
echo ""
echo "========================================"
echo "  Upload Complete"
echo "========================================"
echo "  Video ID:  ${VIDEO_ID}"
echo "  URL:       ${VIDEO_URL}"
echo "  Title:     ${TITLE}"
echo "  Privacy:   ${PRIVACY}"
if [[ -n "${PUBLISH_AT}" ]]; then
    echo "  Scheduled: ${PUBLISH_AT}"
fi
if [[ -n "${THUMBNAIL}" ]]; then
    echo "  Thumbnail: uploaded"
fi
if [[ -n "${PLAYLIST}" ]]; then
    echo "  Playlist:  ${PLAYLIST}"
fi
echo "========================================"

# Output JSON for programmatic use
jq -n \
    --arg id "${VIDEO_ID}" \
    --arg url "${VIDEO_URL}" \
    --arg title "${TITLE}" \
    --arg privacy "${PRIVACY}" \
    '{videoId: $id, url: $url, title: $title, privacy: $privacy}'
