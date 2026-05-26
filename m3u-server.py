#!/usr/bin/env python3
"""
MiTV M3U Playlist Server
Serves live channel as M3U format
Anyone can grab the playlist and stream in VLC/IPTV players
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

FIREBASE_DB = "https://ramadan-2385b-default-rtdb.firebaseio.com"
FIREBASE_KEY = os.environ.get("FIREBASE_KEY", "")

def fb_get(path):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY:
        url += f"?auth={FIREBASE_KEY}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except:
        return None

class M3UHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # /playlist.m3u → return M3U format
        if self.path == '/playlist.m3u' or self.path == '/get.m3u':
            self.send_m3u_playlist()
        
        # /status → return JSON status
        elif self.path == '/status':
            self.send_json_status()
        
        # /info → channel info
        elif self.path == '/info':
            self.send_channel_info()
        
        # /push → trigger stream start
        elif self.path.startswith('/push'):
            self.trigger_stream_push()
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found. Use /playlist.m3u or /status")

    def send_m3u_playlist(self):
        """Return M3U format for IPTV players"""
        config = fb_get("mitv_stream")
        branding = config.get("branding", {}) if config else {}
        
        channel_name = branding.get("channelName", "MiTV Live Channel")
        logo_url = config.get("logo", {}).get("url", "") if config else ""
        
        # M3U Header
        m3u_content = "#EXTM3U\n"
        
        # Channel entry
        m3u_content += "#EXTINF:-1"
        if logo_url:
            m3u_content += f' tvg-logo="{logo_url}"'
        m3u_content += f' group-title="MiTV",{channel_name}\n'
        
        # Stream URL (point to this server's live endpoint)
        # In real setup, this would be the actual RTMP/HLS URL
        # For now, we'll provide the YouTube stream URL if available
        if config and config.get("source"):
            src = config["source"]
            if src.get("type") == "mp4":
                m3u_content += f"{src.get('url', '')}\n"
            elif src.get("type") == "m3u":
                m3u_content += f"{src.get('url', '')}\n"
            elif src.get("type") == "youtube":
                # YouTube live - provide direct link
                m3u_content += f"{src.get('url', '')}\n"
        else:
            m3u_content += "http://localhost:8000/live\n"
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/vnd.apple.mpegurl')
        self.send_header('Content-Disposition', f'attachment; filename="mitv-channel.m3u"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(m3u_content.encode())

    def send_json_status(self):
        """Return live status as JSON"""
        config = fb_get("mitv_stream")
        if not config:
            status = {"live": False, "error": "No config"}
        else:
            status = {
                "live": config.get("status", {}).get("live", False),
                "uptime": config.get("status", {}).get("uptime", 0),
                "loops": config.get("status", {}).get("loops", 0),
                "channel": config.get("branding", {}).get("channelName", "Unknown"),
                "source_type": config.get("source", {}).get("type", "unknown"),
                "timestamp": int(time.time() * 1000)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())

    def send_channel_info(self):
        """Return detailed channel info"""
        config = fb_get("mitv_stream")
        if not config:
            info = {"error": "No config"}
        else:
            info = {
                "name": config.get("branding", {}).get("channelName", "MiTV"),
                "watermark": config.get("branding", {}).get("watermarkText", ""),
                "theme": config.get("branding", {}).get("theme", "dark"),
                "logo": config.get("logo", {}).get("url", ""),
                "ticker": config.get("ticker", {}).get("text", ""),
                "status": config.get("status", {}),
                "source": {
                    "type": config.get("source", {}).get("type", ""),
                    "url": config.get("source", {}).get("url", "")[:60] + "..."
                }
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(info).encode())

    def trigger_stream_push(self):
        """Trigger stream to start (no params needed)"""
        try:
            # Update Firebase status to live
            url = f"{FIREBASE_DB}/mitv_stream/status.json"
            if FIREBASE_KEY:
                url += f"?auth={FIREBASE_KEY}"
            
            data = json.dumps({"live": True, "command": "start", "commandAt": int(time.time() * 1000)}).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="PATCH")
            
            with urllib.request.urlopen(req, timeout=5):
                pass
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Stream push triggered"}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        """Suppress default logging"""
        print(f"[M3U Server] {args[0]}")

def start_server(port=8080):
    """Start M3U server"""
    server = HTTPServer(('0.0.0.0', port), M3UHandler)
    print(f"\n{'='*50}")
    print(f"MiTV M3U Server Started on port {port}")
    print(f"{'='*50}")
    print(f"\n📺 Endpoints:")
    print(f"  • M3U Playlist:  http://localhost:{port}/playlist.m3u")
    print(f"  • Live Status:   http://localhost:{port}/status")
    print(f"  • Channel Info:  http://localhost:{port}/info")
    print(f"  • Push Stream:   http://localhost:{port}/push")
    print(f"\n💡 Usage:")
    print(f"  VLC: Open Network Stream → http://localhost:{port}/playlist.m3u")
    print(f"  Curl: curl http://localhost:{port}/push (to start stream)")
    print(f"\n{'='*50}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[M3U Server] Shutting down...")
        server.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(port)
