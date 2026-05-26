#!/usr/bin/env python3
"""
MiTV Push Endpoint
Simple webhook to trigger stream start/stop from anywhere
Can be called from:
- Telegram bot
- Webhook integrations
- IFTTT
- Custom scripts
"""

import os
import json
import time
import urllib.request
import urllib.parse
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

FIREBASE_DB = "https://ramadan-2385b-default-rtdb.firebaseio.com"
FIREBASE_KEY = os.environ.get("FIREBASE_KEY", "")
PUSH_SECRET = os.environ.get("PUSH_SECRET", "mitv-secret-key")

def fb_update(path, data):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY:
        url += f"?auth={FIREBASE_KEY}"
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False

class PushHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}
        except:
            data = {}

        # Check secret key
        secret = data.get('secret') or self.headers.get('X-Push-Secret', '')
        if secret != PUSH_SECRET:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid secret key"}).encode())
            return

        action = data.get('action', '').lower()
        
        if action == 'start':
            success = fb_update("mitv_stream/status", {
                "live": True,
                "command": "start",
                "commandAt": int(time.time() * 1000)
            })
            msg = "Stream started" if success else "Failed to start stream"
            
        elif action == 'stop':
            success = fb_update("mitv_stream/status", {
                "live": False,
                "command": "stop",
                "commandAt": int(time.time() * 1000)
            })
            msg = "Stream stopped" if success else "Failed to stop stream"
            
        elif action == 'restart':
            success = fb_update("mitv_stream/status", {
                "command": "restart",
                "commandAt": int(time.time() * 1000)
            })
            msg = "Stream restart triggered" if success else "Failed to restart"
            
        elif action == 'source':
            # Update source on the fly
            src_type = data.get('type', 'mp4')  # mp4, m3u, youtube
            src_url = data.get('url', '')
            if not src_url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "URL required"}).encode())
                return
            
            success = fb_update("mitv_stream/source", {
                "type": src_type,
                "url": src_url,
                "index": data.get('index', 0),
                "loop": data.get('loop', 'loop')
            })
            msg = f"Source updated: {src_type}" if success else "Failed to update source"
            
        elif action == 'push':
            # Generic push - just send command to start
            success = fb_update("mitv_stream/status", {
                "live": True,
                "command": "start",
                "commandAt": int(time.time() * 1000),
                "pushedAt": int(time.time() * 1000)
            })
            msg = "Push command sent" if success else "Push failed"
            
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unknown action. Use: start, stop, restart, source, push"}).encode())
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"success": success, "message": msg}).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Push-Secret')
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[Push] {args[0]}")

def start_push_server(port=8081):
    """Start push endpoint server"""
    server = HTTPServer(('0.0.0.0', port), PushHandler)
    print(f"\n{'='*50}")
    print(f"MiTV Push Endpoint Started on port {port}")
    print(f"{'='*50}")
    print(f"\n🔌 Endpoints (POST):")
    print(f"  Base:  http://localhost:{port}/")
    print(f"\n📤 Usage Examples:")
    print(f"\nStart Stream:")
    print(f'''  curl -X POST http://localhost:{port}/ \\
    -H "Content-Type: application/json" \\
    -d '{{"action":"start", "secret":"{PUSH_SECRET}"}}'
''')
    print(f"\nStop Stream:")
    print(f'''  curl -X POST http://localhost:{port}/ \\
    -H "Content-Type: application/json" \\
    -d '{{"action":"stop", "secret":"{PUSH_SECRET}"}}'
''')
    print(f"\nChange Source:")
    print(f'''  curl -X POST http://localhost:{port}/ \\
    -H "Content-Type: application/json" \\
    -d '{{"action":"source", "type":"mp4", "url":"https://...", "secret":"{PUSH_SECRET}"}}'
''')
    print(f"\n⚠️ Secret Key: {PUSH_SECRET}")
    print(f"{'='*50}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Push] Shutting down...")
        server.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    start_push_server(port)
