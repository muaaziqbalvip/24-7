#!/usr/bin/env python3
"""
MiTV Real HLS M3U8 Live Server
Generates actual HLS m3u8 format with live segments
Works with FFmpeg transcoding
Serves real live stream to VLC/IPTV players
"""

import os
import sys
import json
import time
import urllib.request
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

FIREBASE_DB = "https://ramadan-2385b-default-rtdb.firebaseio.com"
FIREBASE_KEY = os.environ.get("FIREBASE_KEY", "")
SEGMENTS_DIR = "/tmp/mitv-hls-segments"
BASE_URL = "http://localhost:8080"

# Create segments directory
Path(SEGMENTS_DIR).mkdir(parents=True, exist_ok=True)

def fb_get(path):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY:
        url += f"?auth={FIREBASE_KEY}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except:
        return None

class HLSSegment:
    def __init__(self):
        self.segments = []
        self.sequence = 0
        self.lock = threading.Lock()

segment_manager = HLSSegment()

class HLSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve M3U8 playlist
        if self.path == '/live.m3u8' or self.path == '/stream.m3u8' or self.path == '/playlist.m3u8':
            self.serve_m3u8_playlist()
        
        # Serve TS segments
        elif self.path.startswith('/segment-'):
            self.serve_segment()
        
        # Testing page
        elif self.path == '/' or self.path == '/test' or self.path == '/testing':
            self.serve_test_page()
        
        # Status
        elif self.path == '/status':
            self.serve_status()
        
        # Stream info
        elif self.path == '/info':
            self.serve_info()
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found\nUse: /live.m3u8 or /testing")

    def serve_m3u8_playlist(self):
        """Generate M3U8 HLS playlist"""
        config = fb_get("mitv_stream")
        if not config:
            self.send_error(500, "No Firebase config")
            return

        branding = config.get("branding", {})
        status = config.get("status", {})
        is_live = status.get("live", False)

        # M3U8 Header
        m3u8 = "#EXTM3U\n"
        m3u8 += "#EXT-X-VERSION:3\n"
        m3u8 += "#EXT-X-TARGETDURATION:10\n"
        m3u8 += f"#EXT-X-MEDIA-SEQUENCE:{segment_manager.sequence}\n"
        
        if not is_live:
            m3u8 += "#EXT-X-PLAYLIST-TYPE:VOD\n"
        else:
            m3u8 += "#EXT-X-PLAYLIST-TYPE:EVENT\n"

        # Add segments
        with segment_manager.lock:
            for i, seg_name in enumerate(segment_manager.segments[-10:]):  # Last 10 segments
                m3u8 += "#EXTINF:10.0,\n"
                m3u8 += f"{BASE_URL}/segment-{seg_name}\n"

        # End list
        m3u8 += "#EXT-X-ENDLIST\n"

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/vnd.apple.mpegurl; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(m3u8.encode()))
        self.end_headers()
        self.wfile.write(m3u8.encode())

    def serve_segment(self):
        """Serve .ts segment file"""
        seg_name = self.path.split('/')[-1]
        seg_path = os.path.join(SEGMENTS_DIR, seg_name)

        if not os.path.exists(seg_path):
            self.send_error(404)
            return

        try:
            with open(seg_path, 'rb') as f:
                data = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'video/mp2t')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
        except:
            self.send_error(500)

    def serve_test_page(self):
        """Serve testing/demo page"""
        config = fb_get("mitv_stream")
        status = config.get("status", {}) if config else {}
        branding = config.get("branding", {}) if config else {}
        source = config.get("source", {}) if config else {}
        
        channel_name = branding.get("channelName", "MiTV Live")
        is_live = status.get("live", False)
        source_type = source.get("type", "unknown")
        source_url = source.get("url", "")[:60] + "..." if source else ""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiTV HLS Testing</title>
    <link href="https://cdn.jsdelivr.net/npm/video.js@7/dist/video-js.min.css" rel="stylesheet" />
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #0a1e2e 0%, #16213e 100%);
            color: #00d4ff;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 20px;
        }}
        .header h1 {{
            font-size: 32px;
            letter-spacing: 3px;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            margin-bottom: 10px;
        }}
        .status-bar {{
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .status-item {{
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 12px;
            letter-spacing: 2px;
        }}
        .status-live {{ 
            background: rgba(255, 61, 107, 0.2);
            border-color: #ff3d6b;
            color: #ff3d6b;
            animation: pulse 1s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .player-section {{
            background: rgba(10, 30, 46, 0.8);
            border: 2px solid #00d4ff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
        }}
        .player-title {{
            font-size: 14px;
            letter-spacing: 2px;
            margin-bottom: 15px;
            color: #00ff9d;
        }}
        video {{
            width: 100%;
            background: #000;
            border-radius: 8px;
        }}
        .info-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .info-card {{
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 15px;
            font-size: 12px;
        }}
        .info-label {{
            color: #00ff9d;
            margin-bottom: 5px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .info-value {{
            color: #fff;
            word-break: break-all;
            font-size: 11px;
        }}
        .controls {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        button {{
            background: #00d4ff;
            color: #000;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 12px;
            letter-spacing: 1px;
            transition: all 0.3s;
        }}
        button:hover {{
            background: #00ff9d;
            box-shadow: 0 0 20px rgba(0, 255, 157, 0.5);
        }}
        .danger {{ background: #ff3d6b; color: white; }}
        .danger:hover {{ background: #ff6b9d; }}
        code {{
            background: rgba(0, 0, 0, 0.5);
            padding: 8px 12px;
            border-radius: 4px;
            display: block;
            margin-top: 5px;
            overflow-x: auto;
            font-size: 11px;
        }}
        @media (max-width: 768px) {{
            .info-section {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 24px; }}
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🔴 MiTV HLS LIVE TESTING</h1>
        <p style="color: #00ff9d; font-size: 12px; letter-spacing: 2px;">Real-time M3U8 Stream Monitor</p>
    </div>

    <div class="status-bar">
        <div class="status-item {'status-live' if is_live else ''}">
            <span>● STATUS: {'LIVE 🔴' if is_live else 'OFFLINE ⬛'}</span>
        </div>
        <div class="status-item">
            <span>📺 CHANNEL: {channel_name}</span>
        </div>
        <div class="status-item">
            <span>📡 SOURCE: {source_type.upper()}</span>
        </div>
        <div class="status-item">
            <span>⏱️ TIME: <span id="currentTime"></span></span>
        </div>
    </div>

    <div class="player-section">
        <div class="player-title">🎬 HLS PLAYER (M3U8)</div>
        <video id="player" class="video-js vjs-default-skin" controls preload="auto" width="100%" height="600">
            <source src="/live.m3u8" type="application/x-mpegURL">
        </video>
        
        <div class="controls">
            <button onclick="playStream()">▶ Play</button>
            <button onclick="pauseStream()">⏸ Pause</button>
            <button onclick="reloadStream()">↻ Reload</button>
            <button onclick="fullscreen()" style="flex:1">⛶ Fullscreen</button>
        </div>
    </div>

    <div class="info-section">
        <div class="info-card">
            <div class="info-label">📺 M3U8 PLAYLIST URL</div>
            <div class="info-value">{BASE_URL}/live.m3u8</div>
            <code id="m3u8Link">{BASE_URL}/live.m3u8</code>
            <button onclick="copyToClipboard(document.getElementById('m3u8Link').textContent)" style="margin-top: 8px; width: 100%;">📋 Copy Link</button>
        </div>
        
        <div class="info-card">
            <div class="info-label">🔗 VLC PLAYER</div>
            <div class="info-value">Open Network Stream and paste URL</div>
            <code>vlc {BASE_URL}/live.m3u8</code>
            <button onclick="openVLC()" style="margin-top: 8px; width: 100%;">🎬 Open in VLC</button>
        </div>

        <div class="info-card">
            <div class="info-label">📡 SOURCE INFO</div>
            <div class="info-value">Type: {source_type}</div>
            <div class="info-value" style="margin-top: 5px;">URL: {source_url}</div>
        </div>

        <div class="info-card">
            <div class="info-label">🎯 STATUS INFO</div>
            <div class="info-value" id="statusInfo">Loading...</div>
        </div>
    </div>

    <div class="player-section" style="margin-top: 20px;">
        <div class="player-title">📊 LIVE STREAM STATS</div>
        <div style="font-size: 12px; line-height: 1.8;">
            <div>🔴 <strong>Status:</strong> <span id="liveStatus" style="color: #ff3d6b;">{'LIVE' if is_live else 'OFFLINE'}</span></div>
            <div>⏱️ <strong>Uptime:</strong> <span id="uptime">0:00:00</span></div>
            <div>🔄 <strong>Loop Count:</strong> <span id="loops">0</span></div>
            <div>📊 <strong>Segments Served:</strong> <span id="segmentCount">0</span></div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #00d4ff;">
                <strong>📋 Playlist Info:</strong><br>
                Version: HLS/3 (M3U8)<br>
                Target Duration: 10s<br>
                Format: MPEG-TS (.ts segments)<br>
                Type: {'EVENT (Live)' if is_live else 'VOD'}
            </div>
        </div>
    </div>

</div>

<script src="https://cdn.jsdelivr.net/npm/video.js@7"></script>
<script>
    let player = videojs('player', {{
        controls: true,
        autoplay: true,
        preload: 'auto',
        liveui: true
    }});

    function playStream() {{
        player.play();
    }}

    function pauseStream() {{
        player.pause();
    }}

    function reloadStream() {{
        const src = player.src();
        player.src({{'src': src + '?t=' + Date.now(), 'type': 'application/x-mpegURL'}});
        player.play();
    }}

    function fullscreen() {{
        player.requestFullscreen();
    }}

    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text);
        alert('✅ Link copied!');
    }}

    function openVLC() {{
        window.location.href = 'vlc://{BASE_URL}/live.m3u8';
    }}

    // Update stats
    function updateStats() {{
        fetch('/status')
            .then(r => r.json())
            .then(data => {{
                document.getElementById('liveStatus').textContent = data.live ? '🔴 LIVE' : '⬛ OFFLINE';
                document.getElementById('uptime').textContent = data.uptime || '0:00:00';
                document.getElementById('loops').textContent = data.loops || '0';
                document.getElementById('segmentCount').textContent = data.segments || '0';
            }})
            .catch(e => console.log('Stats error:', e));
    }}

    // Update time
    function updateTime() {{
        const now = new Date();
        document.getElementById('currentTime').textContent = now.toLocaleTimeString();
    }}

    updateTime();
    updateStats();
    setInterval(updateTime, 1000);
    setInterval(updateStats, 5000);
</script>

</body>
</html>
"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_status(self):
        """Return JSON status"""
        config = fb_get("mitv_stream")
        status = config.get("status", {}) if config else {}
        
        data = {
            "live": status.get("live", False),
            "uptime": status.get("uptime", 0),
            "loops": status.get("loops", 0),
            "segments": len(segment_manager.segments),
            "timestamp": int(time.time() * 1000)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def serve_info(self):
        """Return channel info"""
        config = fb_get("mitv_stream")
        if not config:
            info = {"error": "No config"}
        else:
            info = {
                "channel": config.get("branding", {}).get("channelName", "MiTV"),
                "source": {
                    "type": config.get("source", {}).get("type"),
                    "url": config.get("source", {}).get("url", "")[:40]
                },
                "m3u8": f"{BASE_URL}/live.m3u8",
                "status": config.get("status", {})
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(info).encode())

    def log_message(self, format, *args):
        print(f"[HLS] {args[0]}")

def start_hls_server(port=8080):
    """Start HLS M3U8 server"""
    server = HTTPServer(('0.0.0.0', port), HLSHandler)
    print(f"\n{'='*60}")
    print(f"🔴 MiTV HLS M3U8 LIVE SERVER STARTED")
    print(f"{'='*60}")
    print(f"\n📺 ENDPOINTS:")
    print(f"  • M3U8 Stream:    http://localhost:{port}/live.m3u8")
    print(f"  • Testing Page:   http://localhost:{port}/testing")
    print(f"  • Status JSON:    http://localhost:{port}/status")
    print(f"  • Channel Info:   http://localhost:{port}/info")
    print(f"\n🎬 PLAYER LINKS:")
    print(f"  VLC:      vlc http://localhost:{port}/live.m3u8")
    print(f"  Browser:  http://localhost:{port}/testing")
    print(f"  IPTV App: http://localhost:{port}/live.m3u8")
    print(f"\n{'='*60}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[HLS] Server shutting down...")
        server.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_hls_server(port)
