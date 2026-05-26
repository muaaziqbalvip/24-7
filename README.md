# 🎬 StreamX - 24/7 Live Stream System

## Files Structure
```
/
├── .github/workflows/stream.yml    ← GitHub Actions (auto-run 24/7)
├── stream_engine.sh                ← FFmpeg stream engine
├── public/
│   ├── index.html                  ← Public viewer page
│   └── control-room.html           ← Control Room (admin panel)
├── firebase-init.json              ← Firebase DB initial data
└── README.md
```

## Setup Steps

### 1. GitHub Repository
- Upload all files to: `https://github.com/muaaziqbalvip/24-7`
- Enable GitHub Pages → Source: `public/` folder
- Your stream page: `https://muaaziqbalvip.github.io/24-7/`
- Control room: `https://muaaziqbalvip.github.io/24-7/control-room.html`

### 2. Firebase Setup
- Go to Firebase Console → Realtime Database
- Import `firebase-init.json` as initial data
- Set Database Rules to public read/write (for testing):
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### 3. GitHub Actions
- Go to your repo → Settings → Actions → General
- Enable: "Allow all actions and reusable workflows"
- The workflow auto-starts on push and restarts every 25 minutes

### 4. How It Works
1. GitHub Actions runs `stream_engine.sh` 24/7
2. FFmpeg reads your source URL (YouTube/M3U8/MP4/etc)
3. Adds overlays: ticker, clock, logo, text
4. Outputs to HLS format
5. Control Room sends config to Firebase in realtime
6. Stream engine reads Firebase config every loop

## Control Room Features
- 📡 **Source**: M3U8, MP4, MKV, YouTube, any URL
- 🎨 **Overlays**: Ticker, Clock, Date, Logo, Custom Text
- 🎵 **Audio**: Volume, Pitch, EQ, Background Music
- 📅 **Schedule**: Time-based show switching
- 🖼 **Images**: ImgBB upload and manage
- ✨ **Templates**: Pre-built overlay styles
- 📤 **Output**: Stream links and embed codes

## Supported Source Types
- ✅ M3U8 / HLS streams
- ✅ MP4 video files  
- ✅ MKV video files
- ✅ MP3 audio files
- ✅ M3U playlists
- ✅ YouTube URLs (via yt-dlp)
- ✅ Any direct video URL

## Copyright Protection Features
- Audio pitch shifting (avoids audio fingerprinting)
- Visual overlays (changes video fingerprint)
- Custom logos and branding
- Custom color grading via FFmpeg filters

## 24/7 Logic
- GitHub Actions runs for up to 6 hours max per job
- Cron schedule restarts every 25 minutes as safety
- Stream engine loops 50 times before GitHub auto-restarts
- Firebase stores status so control room shows real-time state
- If stream source fails, auto-retries after 5 seconds
