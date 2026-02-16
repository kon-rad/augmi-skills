---
name: social-media-publisher
description: |
  Uploads and schedules short videos (Reels) to Instagram and Facebook Pages using the
  Meta Graph API. Supports uploading video files, adding captions/hashtags, scheduling
  future posts, and checking publish status. Works with Instagram Business/Creator accounts
  and Facebook Pages. This skill should be used when the user wants to upload a video to
  Instagram, post a Reel, publish to Facebook, schedule a social media post, or manage
  their Instagram/Facebook content. Triggers on requests like "upload this video to Instagram",
  "post this reel", "schedule a post on Facebook", "publish to Instagram and Facebook",
  "upload short video to social media".
user_invocable:
  - name: upload
    description: "Upload a video as a Reel to Instagram and/or Facebook"
  - name: schedule
    description: "Schedule a video to publish at a future date/time"
  - name: status
    description: "Check the status of a pending or scheduled upload"
  - name: auth
    description: "Set up or verify Meta API authentication"
  - name: accounts
    description: "List connected Instagram and Facebook accounts"
---

# Social Media Publisher

Upload and schedule short videos (Reels) to Instagram and Facebook Pages via the Meta Graph API.

## Full Setup Guide (Start Here)

Follow these steps in order. The entire setup takes about 15-30 minutes (plus 1-2 weeks if you need Meta App Review for production use).

---

### Step 1: Convert Instagram to a Business or Creator Account

Personal Instagram accounts **cannot** use the Graph API. You must switch to Business or Creator.

1. Open the **Instagram app** on your phone
2. Go to your **Profile** → tap the **hamburger menu** (three lines, top-right)
3. Tap **Settings and privacy**
4. Scroll down to **Account type and tools** → tap **Switch to professional account**
5. Choose either:
   - **Creator** — best for individuals, influencers, content creators
   - **Business** — best for brands, companies, storefronts
6. Select a **category** that describes your account (e.g., "Digital Creator", "Software Company")
7. Tap **Done** to confirm

Your Instagram is now a Professional account. This is free and can be reversed anytime.

---

### Step 2: Create a Facebook Page (If You Don't Have One)

Instagram Business/Creator accounts must be linked to a Facebook Page. If you already have one, skip to Step 3.

1. Go to [facebook.com/pages/create](https://www.facebook.com/pages/create)
2. Enter your **Page name** (can match your Instagram username or brand name)
3. Select a **Category** (e.g., "Software Company", "Personal Blog")
4. Add an optional **bio/description**
5. Click **Create Page**
6. Optionally add a profile picture and cover photo

---

### Step 3: Link Instagram to Your Facebook Page

1. Open the **Instagram app** → go to your **Profile**
2. Tap **Edit Profile**
3. Tap **Page** (under "Profile information" or "Public business information")
4. Tap **Connect or create** → select **Connect an existing Page**
5. Log into Facebook if prompted
6. Select the Facebook Page you created in Step 2
7. Tap **Done**

**Alternatively, from Facebook:**
1. Go to your Facebook Page
2. Click **Settings** (bottom-left) → **Linked accounts** or **Instagram**
3. Click **Connect account** → log into Instagram and authorize

---

### Step 4: Set Up Meta Business Manager (Optional but Recommended)

Business Manager gives you System User tokens (which never expire) and better permission management.

1. Go to [business.facebook.com/overview](https://business.facebook.com/overview)
2. Click **Create account** (or **Create a Business Portfolio**)
3. Enter your **business name**, **your name**, and **business email**
4. Click **Submit**
5. Once created, add your Facebook Page:
   - Go to **Business Settings** → **Accounts** → **Pages**
   - Click **Add** → **Add a Page** → search for your Page → **Add Page**
6. Add your Instagram account:
   - Go to **Business Settings** → **Accounts** → **Instagram accounts**
   - Click **Add** → log into Instagram and authorize

---

### Step 5: Create a Meta Developer App

This is the app that will make API calls on your behalf.

1. Go to [developers.facebook.com](https://developers.facebook.com) and log in
2. Click **My Apps** (top-right) → **Create App**
3. Select **Other** as the use case → click **Next**
4. Select **Business** as the app type → click **Next**
5. Enter an **App name** (e.g., "My Social Publisher") and **contact email**
6. Select your Business Portfolio if you created one in Step 4
7. Click **Create App**

After creation, note your **App ID** and **App Secret** (found under App Settings → Basic):
- `META_APP_ID` = your App ID
- `META_APP_SECRET` = your App Secret

---

### Step 6: Add Required Products and Permissions

From your app's dashboard at [developers.facebook.com](https://developers.facebook.com):

1. In the left sidebar, click **Add Product**
2. Find and add these products:
   - **Facebook Login for Business** — click **Set Up**
   - **Instagram Graph API** — click **Set Up** (if listed separately)

The permissions you need:

| Permission | Purpose |
|------------|---------|
| `instagram_basic` | Read Instagram profile info |
| `instagram_content_publish` | Publish Reels and posts to Instagram |
| `pages_show_list` | List Facebook Pages you manage |
| `pages_read_engagement` | Read Page engagement data |
| `pages_manage_posts` | Publish to Facebook Pages |

**For testing** (before App Review): Add yourself as a test user:
1. Go to **App Roles** → **Roles**
2. Your account should already be listed as Admin
3. Admin users can use all permissions without App Review

**For production** (live use): Submit for App Review:
1. Go to **App Review** → **Permissions and Features**
2. Request each permission listed above
3. Provide a screencast showing how your app uses each permission
4. Review typically takes 1-5 business days

---

### Step 7: Generate Your Access Token

#### Option A: Quick Setup (Testing — Token Expires in 60 Days)

1. Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. In the top-right dropdown, select **your app**
3. Click **Add a Permission** and add all 5 permissions listed above
4. Click **Generate Access Token**
5. A Facebook login popup will appear — authorize the app
6. You now have a **short-lived token** (expires in 1-2 hours)

Exchange it for a **long-lived token** (60 days):

```bash
python3 ~/.claude/skills/augmi-skills/social-media-publisher/scripts/auth.py exchange-token --short-lived-token "PASTE_YOUR_SHORT_LIVED_TOKEN_HERE"
```

The script will print your long-lived token. Save it as `META_ACCESS_TOKEN`.

**Important:** Set a reminder to refresh this token before it expires (every ~50 days).

#### Option B: Production Setup (System User Token — Never Expires)

System User tokens are the best choice for automation because they never expire.

1. Go to [business.facebook.com](https://business.facebook.com) → **Business Settings**
2. Click **Users** → **System Users** in the left sidebar
3. Click **Add** → enter a name (e.g., "Social Publisher Bot")
4. Set the role to **Admin**
5. Click **Create System User**
6. Now assign assets to this system user:
   - Click on the system user you just created
   - Click **Add Assets**
   - Select **Pages** tab → check your Facebook Page → set **Full Control**
   - Select **Apps** tab → check your Meta App → set **Full Control**
7. Click **Generate New Token**:
   - Select your app from the dropdown
   - Check all 5 required permissions
   - Click **Generate Token**
8. Copy and save the token — this is your `META_ACCESS_TOKEN`

---

### Step 8: Find Your Account IDs

Run the auth script to discover your connected accounts:

```bash
# Set your credentials first
export META_ACCESS_TOKEN="your_token_here"
export META_APP_ID="your_app_id"
export META_APP_SECRET="your_app_secret"

# List all connected accounts
python3 ~/.claude/skills/augmi-skills/social-media-publisher/scripts/auth.py list-accounts
```

The script will output your **Instagram Business Account ID** and **Facebook Page ID**. Example output:

```
=== Facebook Pages ===
Page: My Brand Page
  Page ID: 123456789012345
  Instagram: @mybrand
  IG Account ID: 17841400123456789
  Followers: 5,432
  Posts: 128

=== Summary ===
INSTAGRAM_BUSINESS_ACCOUNT_ID="17841400123456789"
FACEBOOK_PAGE_ID="123456789012345"
```

---

### Step 9: Set Your Environment Variables

Create a `.env` file or export these variables in your shell:

```bash
export META_APP_ID="your_app_id"
export META_APP_SECRET="your_app_secret"
export META_ACCESS_TOKEN="your_access_token"
export INSTAGRAM_BUSINESS_ACCOUNT_ID="your_ig_account_id"
export FACEBOOK_PAGE_ID="your_page_id"
```

Or add them to `~/.claude/skills/augmi-skills/social-media-publisher/assets/.env` (see `.env.example`).

---

### Step 10: Install Dependencies and Verify

```bash
# Install Python dependencies
pip install requests python-dotenv

# Verify everything works
python3 ~/.claude/skills/augmi-skills/social-media-publisher/scripts/auth.py verify
```

You should see output like:
```
=== Token Status ===
Valid: True
Type: USER (or SYSTEM)
Expires: Never (System User Token)
Permissions (5):
  - instagram_basic
  - instagram_content_publish
  - pages_show_list
  - pages_read_engagement
  - pages_manage_posts
All required permissions granted.
```

You're all set. You can now use `/social-media-publisher:upload` to post Reels.

---

### Setup Checklist

Use this to verify everything is configured:

- [ ] Instagram account converted to Business or Creator
- [ ] Facebook Page created
- [ ] Instagram linked to Facebook Page
- [ ] Meta Developer App created at developers.facebook.com
- [ ] Required permissions added to app (5 permissions)
- [ ] Access token generated (long-lived user token or system user token)
- [ ] `META_APP_ID` set
- [ ] `META_APP_SECRET` set
- [ ] `META_ACCESS_TOKEN` set
- [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID` set
- [ ] `FACEBOOK_PAGE_ID` set (if posting to Facebook)
- [ ] `python3` and `requests` installed
- [ ] `auth.py verify` shows "All required permissions granted"

## Commands

### `/social-media-publisher:upload`

Upload a video file as a Reel to Instagram and/or Facebook.

**Usage:**
```
/social-media-publisher:upload video: path/to/video.mp4 caption: "Your caption here #hashtag" platform: instagram
```

**Parameters:**
- `video` (required) - Path to the video file (MP4, 9:16 vertical recommended)
- `caption` (optional) - Caption text with hashtags
- `platform` (optional) - `instagram`, `facebook`, or `both` (default: `both`)
- `cover_url` (optional) - URL to a cover/thumbnail image

**Video Requirements:**
| Spec | Instagram Reels | Facebook Reels |
|------|----------------|----------------|
| Format | MP4 (H.264) | MP4 (H.264) |
| Aspect Ratio | 9:16 (vertical) | 9:16 (vertical) |
| Resolution | 1080x1920 recommended | 1080x1920 recommended |
| Max Duration | 90 seconds | 90 seconds |
| Max File Size | 1GB | 4GB |
| Min Duration | 3 seconds | 3 seconds |

**Workflow:**
1. Validate video file exists and check format
2. Upload video to a publicly accessible URL (or use existing URL)
3. Create media container on Instagram/Facebook
4. Poll for processing completion (may take 30s-5min)
5. Publish the reel
6. Return the published media ID and URL

### `/social-media-publisher:schedule`

Schedule a video to publish at a future date/time.

**Usage:**
```
/social-media-publisher:schedule video: path/to/video.mp4 caption: "Scheduled post" datetime: "2026-02-20 14:00" timezone: "America/Los_Angeles" platform: instagram
```

**Parameters:**
- `video` (required) - Path to the video file
- `caption` (optional) - Caption text
- `datetime` (required) - Future publish time (YYYY-MM-DD HH:MM)
- `timezone` (optional) - Timezone name (default: UTC)
- `platform` (optional) - `instagram`, `facebook`, or `both`

**How Scheduling Works:**
- For **Facebook Pages**: Uses native `scheduled_publish_time` API parameter
- For **Instagram**: Creates a local schedule job file in `OUTPUT/scheduled/` that must be published manually or via cron
- Schedule files are JSON with all upload parameters + target publish time

### `/social-media-publisher:status`

Check the processing/publish status of an upload.

**Usage:**
```
/social-media-publisher:status container_id: 12345678
```

### `/social-media-publisher:auth`

Verify authentication and token status.

**Usage:**
```
/social-media-publisher:auth
```

This will:
1. Verify your access token is valid
2. Show token expiration date
3. List available permissions
4. Show connected accounts

### `/social-media-publisher:accounts`

List all Instagram and Facebook accounts connected to your token.

**Usage:**
```
/social-media-publisher:accounts
```

## Workflow Details

### Instagram Reel Upload Flow

```
1. POST /{ig-user-id}/media
   - media_type=REELS
   - video_url={publicly accessible URL}
   - caption={text}
   → Returns container ID

2. GET /{container-id}?fields=status_code
   - Poll every 5 seconds
   - Wait for status_code=FINISHED
   - If ERROR, report and stop

3. POST /{ig-user-id}/media_publish
   - creation_id={container_id}
   → Returns published media ID
```

### Facebook Reel Upload Flow

```
1. POST /{page-id}/video_reels
   - upload_phase=start
   → Returns video_id

2. POST /{video-id}
   - upload_phase=transfer
   - video_file_chunk={binary data}

3. POST /{page-id}/video_reels
   - upload_phase=finish
   - video_id={video_id}
   - title={caption}
   → Returns success
```

### Video URL Requirement

Instagram requires a **publicly accessible URL** for the video. Options:
1. **Already hosted**: If the video is at a public URL, use it directly
2. **Local file**: The script will upload to a temporary file hosting service (transfer.sh or tmpfiles.org)
3. **Cloud storage**: Upload to S3, GCS, or similar first

## Rate Limits

| Platform | Limit | Window |
|----------|-------|--------|
| Instagram | 50 posts/day | 24 hours |
| Instagram API calls | 200 calls/hour | Per account |
| Facebook | 50 posts/day | 24 hours |

## Troubleshooting

### "Invalid OAuth access token"
- Your token may have expired. Exchange for a new long-lived token.
- System User tokens don't expire—verify the token has correct permissions.

### "The video is not eligible to be a reel"
- Video must be vertical (9:16 aspect ratio)
- Duration must be 3-90 seconds
- Format must be MP4 with H.264 codec

### "Media posted before completing processing"
- The polling phase was cut short. Increase polling timeout.
- Large videos can take 2-5 minutes to process.

### "Application does not have permission"
- Your app needs `instagram_content_publish` permission approved via App Review.
- For testing, add your account as a Tester in the Meta App dashboard.

### "Unsupported post request" for scheduling
- Instagram Reels scheduling via API is unreliable. Use the local schedule file approach.
- Facebook scheduling works for Pages only, not personal profiles.
