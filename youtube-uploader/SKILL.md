---
name: youtube-uploader
description: |
  Upload videos to YouTube, manage metadata, thumbnails, playlists, scheduling,
  analytics, and comments using the YouTube Data API v3 directly. No third-party
  middleware — just your Google OAuth credentials.
  Trigger with "/youtube-upload" or ask Claude to upload a video to YouTube.
user-invocable: true
allowed-tools: Read, Write, Bash, Glob, Grep, WebSearch, WebFetch, Task
---

# YouTube Uploader

Direct YouTube management skill using YouTube Data API v3. Upload videos, set metadata,
manage playlists, schedule publishing, view analytics, and moderate comments — all via
your own Google OAuth credentials.

## Prerequisites

### Required API Keys (store in `~/.claude/skills/youtube-uploader/.env`)

```bash
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token
```

### How to Get Credentials (One-Time Setup)

If the user doesn't have credentials yet, run the setup script:

```bash
python3 ~/.claude/skills/youtube-uploader/scripts/setup_oauth.py
```

This will:
1. Ask for Google Cloud project Client ID and Client Secret
2. Open browser for OAuth consent
3. Save the refresh token to `.env`

**Google Cloud Console steps** (tell user if needed):
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (type: Desktop app)
3. Enable "YouTube Data API v3" and "YouTube Analytics API" in API Library
4. Add test users in OAuth consent screen (or verify app for production)

### System Dependencies

- `curl` (pre-installed on macOS/Linux)
- `python3` (for setup script only)
- `jq` (for JSON parsing — install via `brew install jq` if missing)

## Core Operations

### 0. Refresh Access Token

**ALWAYS do this first before any API call.** Access tokens expire after ~1 hour.

```bash
source ~/.claude/skills/youtube-uploader/.env

ACCESS_TOKEN=$(curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=${YOUTUBE_CLIENT_ID}" \
  -d "client_secret=${YOUTUBE_CLIENT_SECRET}" \
  -d "refresh_token=${YOUTUBE_REFRESH_TOKEN}" \
  -d "grant_type=refresh_token" | jq -r '.access_token')

echo "Token: ${ACCESS_TOKEN:0:20}..."
```

If this returns `null`, the refresh token may be revoked. Re-run setup_oauth.py.

### 1. Upload Video

Use the resumable upload helper script for reliability:

```bash
bash ~/.claude/skills/youtube-uploader/scripts/upload.sh \
  --file "/path/to/video.mp4" \
  --title "My Video Title" \
  --description "Video description here" \
  --tags "tag1,tag2,tag3" \
  --privacy "private" \
  --category "22"
```

**Options:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--file` | Yes | — | Path to video file (mp4, mov, avi, webm) |
| `--title` | Yes | — | Video title (max 100 chars) |
| `--description` | No | "" | Video description (max 5000 chars) |
| `--tags` | No | "" | Comma-separated tags |
| `--privacy` | No | "private" | `private`, `public`, or `unlisted` |
| `--category` | No | "22" | YouTube category ID (22 = People & Blogs) |
| `--publish-at` | No | — | ISO 8601 UTC time for scheduled publish |
| `--thumbnail` | No | — | Path to thumbnail image (jpg/png, max 2MB) |
| `--playlist` | No | — | Playlist ID to add video to after upload |
| `--made-for-kids` | No | "false" | "true" or "false" |

The script handles:
- Token refresh automatically
- Resumable upload protocol (works for files up to 256GB)
- Automatic retry on network failures (3 attempts with backoff)
- Thumbnail upload after video upload
- Playlist insertion after upload
- Returns video ID and URL on success

**Manual upload via curl (for small files or custom needs):**

Step 1 — Initiate session:
```bash
UPLOAD_URL=$(curl -s -i -X POST \
  "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -H "X-Upload-Content-Length: $(stat -f%z video.mp4)" \
  -H "X-Upload-Content-Type: video/mp4" \
  -d '{
    "snippet": {
      "title": "Video Title",
      "description": "Description",
      "tags": ["tag1", "tag2"],
      "categoryId": "22"
    },
    "status": {
      "privacyStatus": "private",
      "selfDeclaredMadeForKids": false
    }
  }' 2>&1 | grep -i "^location:" | sed 's/location: //i' | tr -d '\r')
```

Step 2 — Upload file:
```bash
RESPONSE=$(curl -s -X PUT "${UPLOAD_URL}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: video/mp4" \
  --data-binary @video.mp4)

VIDEO_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Uploaded: https://youtu.be/${VIDEO_ID}"
```

### 2. Update Video Metadata

**IMPORTANT:** When updating `snippet`, you MUST include both `title` and `categoryId`.

```bash
curl -s -X PUT \
  "https://www.googleapis.com/youtube/v3/videos?part=snippet,status" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "VIDEO_ID",
    "snippet": {
      "title": "Updated Title",
      "description": "Updated description",
      "tags": ["new", "tags"],
      "categoryId": "22"
    },
    "status": {
      "privacyStatus": "public"
    }
  }' | jq '.id, .snippet.title'
```

### 3. Upload Thumbnail

```bash
curl -s -X POST \
  "https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=VIDEO_ID" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: image/jpeg" \
  --data-binary @thumbnail.jpg | jq '.'
```

**Requirements:** JPEG or PNG, max 2MB, recommended 1280x720 (16:9).

### 4. Schedule Video Publishing

Set `privacyStatus: "private"` with a `publishAt` timestamp. YouTube auto-publishes at that time.

```bash
curl -s -X PUT \
  "https://www.googleapis.com/youtube/v3/videos?part=status" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "VIDEO_ID",
    "status": {
      "privacyStatus": "private",
      "publishAt": "2026-03-01T15:00:00Z"
    }
  }' | jq '.status'
```

### 5. Playlist Management

**Create playlist:**
```bash
curl -s -X POST \
  "https://www.googleapis.com/youtube/v3/playlists?part=snippet,status" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "title": "My Playlist",
      "description": "Playlist description"
    },
    "status": { "privacyStatus": "public" }
  }' | jq '.id, .snippet.title'
```

**Add video to playlist:**
```bash
curl -s -X POST \
  "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "playlistId": "PLAYLIST_ID",
      "resourceId": { "kind": "youtube#video", "videoId": "VIDEO_ID" },
      "position": 0
    }
  }' | jq '.snippet.title'
```

**List playlist items:**
```bash
curl -s "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=PLAYLIST_ID&maxResults=50" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.items[] | {title: .snippet.title, videoId: .snippet.resourceId.videoId}'
```

**List my playlists:**
```bash
curl -s "https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true&maxResults=50" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.items[] | {id: .id, title: .snippet.title}'
```

**Delete playlist item:**
```bash
curl -s -X DELETE \
  "https://www.googleapis.com/youtube/v3/playlistItems?id=PLAYLIST_ITEM_ID" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### 6. Channel Analytics

**Requires scope:** `yt-analytics.readonly` (included in setup script).

**Daily views, watch time, subscribers (last 30 days):**
```bash
curl -s "https://youtubeanalytics.googleapis.com/v2/reports?ids=channel==MINE&startDate=$(date -v-30d +%Y-%m-%d)&endDate=$(date +%Y-%m-%d)&metrics=views,estimatedMinutesWatched,subscribersGained,likes,comments&dimensions=day&sort=day" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.rows[] | {date: .[0], views: .[1], watchMinutes: .[2], subs: .[3], likes: .[4], comments: .[5]}'
```

**Top 10 videos by views:**
```bash
curl -s "https://youtubeanalytics.googleapis.com/v2/reports?ids=channel==MINE&startDate=2020-01-01&endDate=$(date +%Y-%m-%d)&metrics=views,estimatedMinutesWatched,likes&dimensions=video&maxResults=10&sort=-views" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.rows'
```

**Channel statistics (quick):**
```bash
curl -s "https://www.googleapis.com/youtube/v3/channels?part=statistics&mine=true" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.items[0].statistics'
```

### 7. List My Videos

```bash
# Get uploads playlist ID first
UPLOADS_PL=$(curl -s "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq -r '.items[0].contentDetails.relatedPlaylists.uploads')

# List recent uploads
curl -s "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${UPLOADS_PL}&maxResults=25" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.items[] | {title: .snippet.title, videoId: .snippet.resourceId.videoId, published: .snippet.publishedAt}'
```

### 8. Video Details & Processing Status

```bash
curl -s "https://www.googleapis.com/youtube/v3/videos?part=snippet,status,statistics,processingDetails&id=VIDEO_ID" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '{
    title: .items[0].snippet.title,
    privacy: .items[0].status.privacyStatus,
    processing: .items[0].processingDetails.processingStatus,
    views: .items[0].statistics.viewCount,
    likes: .items[0].statistics.likeCount
  }'
```

### 9. Comment Management

**List comments on video:**
```bash
curl -s "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=VIDEO_ID&maxResults=50&order=time" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.items[] | {
    id: .id,
    author: .snippet.topLevelComment.snippet.authorDisplayName,
    text: .snippet.topLevelComment.snippet.textDisplay,
    likes: .snippet.topLevelComment.snippet.likeCount,
    published: .snippet.topLevelComment.snippet.publishedAt
  }'
```

**Post comment:**
```bash
curl -s -X POST \
  "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "videoId": "VIDEO_ID",
      "topLevelComment": {
        "snippet": { "textOriginal": "Great video!" }
      }
    }
  }' | jq '.id'
```

**Reply to comment:**
```bash
curl -s -X POST \
  "https://www.googleapis.com/youtube/v3/comments?part=snippet" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "parentId": "COMMENT_THREAD_ID",
      "textOriginal": "Thanks for watching!"
    }
  }' | jq '.id'
```

**Delete comment:**
```bash
curl -s -X DELETE \
  "https://www.googleapis.com/youtube/v3/comments?id=COMMENT_ID" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### 10. Search YouTube

```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=SEARCH_QUERY&type=video&maxResults=10" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.items[] | {title: .snippet.title, videoId: .id.videoId, channel: .snippet.channelTitle}'
```

**Warning:** Search costs 100 quota units per call. Use sparingly.

### 11. Delete Video

```bash
curl -s -X DELETE \
  "https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**WARNING:** This is irreversible. Always confirm with user before deleting.

## Category IDs Reference

| ID | Category |
|----|----------|
| 1 | Film & Animation |
| 2 | Autos & Vehicles |
| 10 | Music |
| 15 | Pets & Animals |
| 17 | Sports |
| 19 | Travel & Events |
| 20 | Gaming |
| 22 | People & Blogs |
| 23 | Comedy |
| 24 | Entertainment |
| 25 | News & Politics |
| 26 | Howto & Style |
| 27 | Education |
| 28 | Science & Technology |

## Quota Budget

Daily limit: **10,000 units** (resets midnight Pacific Time).

| Operation | Cost | Max/Day |
|-----------|------|---------|
| Upload video | 1,600 | ~6 |
| Update metadata | 50 | 200 |
| Set thumbnail | 50 | 200 |
| Create playlist | 50 | 200 |
| Add to playlist | 50 | 200 |
| List anything | 1 | 10,000 |
| Search | 100 | 100 |
| Post comment | 50 | 200 |

## Important Gotchas

1. **Unverified apps force private uploads** — Videos uploaded from unverified Google Cloud projects are locked to `private`. User must manually publish in YouTube Studio OR verify their app in Google Cloud Console.

2. **Snippet updates need title + categoryId** — Omitting either causes `invalidVideoMetadata` error.

3. **Service accounts don't work** — YouTube API requires OAuth user flow. No workaround.

4. **Processing takes time** — After upload returns 201, video still processes. Poll `processingDetails` to confirm.

5. **Quota resets at midnight Pacific** — Not UTC or local time.

6. **Upload session URIs expire** — If a resumable upload pauses too long, start over.

7. **YouTube Shorts** — Vertical (9:16) videos under 60 seconds auto-categorize as Shorts. No special API flag needed.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `unauthorized (401)` | Token expired | Re-run token refresh |
| `forbidden (403)` | Wrong scopes or quota exceeded | Check scopes; wait for quota reset |
| `quotaExceeded (403)` | Daily limit hit | Wait until midnight PT |
| `invalidVideoMetadata` | Missing title or categoryId in snippet update | Include both fields |
| `uploadLimitExceeded` | Too many uploads | Wait or request quota increase |
| `null` access token | Revoked refresh token | Re-run `setup_oauth.py` |
| `notFound (404)` on upload PUT | Session URI expired | Start new upload session |
