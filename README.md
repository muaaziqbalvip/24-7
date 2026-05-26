# 📺 MiTV 24/7 Live Stream System

## Files
| File | Purpose |
|------|---------|
| `control-panel.html` | Main control panel (Firebase connected) |
| `stream-overlay.html` | Stream preview overlay |
| `stream-engine.py` | GitHub Actions streaming engine |
| `.github/workflows/stream.yml` | 24/7 auto-restart workflow |

---

## ⚡ Setup Guide (Step by Step)

### STEP 1 — GitHub Repo
1. Create new GitHub repo (e.g. `your-name/mitv-stream`)
2. Upload ALL these files to the repo root
3. Make sure `.github/workflows/stream.yml` is in correct path

### STEP 2 — GitHub Secrets
Go to: **Repo → Settings → Secrets → Actions → New repository secret**

Add these 2 secrets:
- `YOUTUBE_STREAM_KEY` → Your YouTube stream key (e.g. `xxxx-xxxx-xxxx-xxxx`)
- `FIREBASE_KEY` → Your Firebase Database secret (optional, for private DB)

### STEP 3 — YouTube Stream Key
1. Go to YouTube Studio → Live → Stream key
2. Copy the key
3. Paste in GitHub Secret AND in control panel

### STEP 4 — Open Control Panel
- Open `control-panel.html` in browser
- It connects to Firebase automatically
- Set your video source (MP4/M3U/YouTube)
- Set logo, ticker, settings
- Click **START STREAM**

### STEP 5 — Trigger GitHub Actions
In control panel → Stream tab:
- Enter your GitHub repo name (`username/repo`)
- Enter your GitHub token (Settings → Developer Settings → Personal Access Tokens)
- Click **🚀 Trigger GitHub Actions**

---

## 🔄 How 24/7 Works
```
GitHub Actions starts → stream-engine.py reads Firebase → 
FFmpeg builds → streams to YouTube → 
if crashes → auto-restart in 5s → 
every 6 hours → GitHub cron restarts fresh
```

Your phone can be OFF. GitHub servers run it 24/7.

---

## 📺 Video Sources

### MP4
Direct video file URL. Loops forever.
```
https://example.com/video.mp4
```

### M3U
IPTV playlist. Enter URL + channel index.
```
http://server.com:8080/get.php?username=...&output=m3u
```

### YouTube
Any YouTube video/playlist URL. yt-dlp extracts stream.
```
https://youtube.com/watch?v=VIDEO_ID
https://youtube.com/playlist?list=PLAYLIST_ID
```

---

## ⚙️ Overlay Features
- **Logo**: Upload via ImgBB → 6 animations (pulse/bounce/rotate/glow/float)
- **Ticker**: Scrolling text bar → 6 animation styles
- **Transform**: Zoom, X/Y position, brightness, volume
- **Audio**: Stereo/Mono/Echo/Bass Boost
- **Branding**: Channel name, watermark, themes

---

## 🔑 GitHub Token Scopes Needed
When creating token, check: `workflow` + `repo`

---

## Firebase Structure
```
mitv_stream/
  source/       → video source config
  transform/    → zoom/position/volume
  logo/         → logo url, position, animation
  ticker/       → text, speed, colors
  streamSettings/ → key, rtmp, resolution
  branding/     → channel name, theme
  status/       → live status, loops, uptime
  logs/         → activity log entries
  images/       → uploaded ImgBB URLs
  github/       → repo info
```
