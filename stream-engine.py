#!/usr/bin/env python3
"""
MiTV 24/7 Stream Engine - FIXED VERSION
- Reads config from Firebase Realtime Database
- Builds FFmpeg command with all overlays
- Streams to YouTube RTMP OR generates HLS/M3U for non-YouTube mode
- Auto-restart 24/7
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import tempfile
import urllib.request
import urllib.parse
import datetime
import traceback

FIREBASE_DB = "https://ramadan-2385b-default-rtdb.firebaseio.com"
FIREBASE_KEY = os.environ.get("FIREBASE_KEY", "")
STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY", "")

# ─── Firebase REST ─────────────────────────────────────────────────────────────
def fb_get(path):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY:
        url += f"?auth={FIREBASE_KEY}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[Firebase] GET error {path}: {e}")
        return None

def fb_set(path, data):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY:
        url += f"?auth={FIREBASE_KEY}"
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[Firebase] SET error {path}: {e}")

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
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[Firebase] UPDATE error {path}: {e}")

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    key = str(int(time.time() * 1000))
    fb_set(f"mitv_stream/logs/{key}", entry)

# ─── Source resolution ─────────────────────────────────────────────────────────
def resolve_source(source):
    if not source:
        raise ValueError("No source configured in Firebase")
    src_type = source.get("type", "mp4")
    url = source.get("url", "")
    if not url:
        raise ValueError("Source URL is empty")

    if src_type == "mp4":
        log(f"Source: MP4 — {url[:60]}")
        return url, "mp4"
    elif src_type == "m3u":
        log(f"Source: M3U — {url[:60]}")
        stream_url = extract_from_m3u(url, source.get("index", 0))
        return stream_url, "m3u"
    elif src_type == "youtube":
        log(f"Source: YouTube — {url[:60]}")
        stream_url = extract_youtube(url)
        return stream_url, "youtube"
    else:
        raise ValueError(f"Unknown source type: {src_type}")

def extract_from_m3u(url, index=0):
    log("Parsing M3U playlist...")
    with urllib.request.urlopen(url, timeout=20) as r:
        content = r.read().decode("utf-8", errors="ignore")
    lines = [l.strip() for l in content.splitlines()]
    streams = [l for l in lines if l and not l.startswith("#")]
    if not streams:
        raise ValueError("No streams found in M3U")
    idx = min(index, len(streams) - 1)
    chosen = streams[idx]
    log(f"M3U: {len(streams)} channels, using index {idx}: {chosen[:60]}")
    return chosen

def extract_youtube(url):
    log("Extracting YouTube stream URL with yt-dlp...")
    result = subprocess.run(
        ["yt-dlp", "-g", "--no-warnings", "-f", "best[height<=720]/best", url],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise ValueError(f"yt-dlp failed: {result.stderr[:200]}")
    stream_url = result.stdout.strip().split("\n")[0]
    log(f"YouTube stream extracted: {stream_url[:60]}...")
    return stream_url

# ─── Logo download ─────────────────────────────────────────────────────────────
def download_logo(url):
    if not url:
        return None
    try:
        log(f"Downloading logo: {url[:60]}")
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        with urllib.request.urlopen(url, timeout=15) as r:
            tmp.write(r.read())
        tmp.close()
        return tmp.name
    except Exception as e:
        log(f"Logo download failed: {e}")
        return None

# ─── FFmpeg filter text escape ─────────────────────────────────────────────────
def esc(text):
    """Escape text for FFmpeg drawtext filter"""
    return text.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:").replace("%", "\\%")

# ─── Build FFmpeg command ──────────────────────────────────────────────────────
def build_ffmpeg_cmd(config, stream_key, mode="youtube"):
    source = config.get("source", {})
    transform = config.get("transform", {})
    logo_cfg = config.get("logo", {})
    ticker_cfg = config.get("ticker", {})
    stream_settings = config.get("streamSettings", {})
    branding = config.get("branding", {})

    src_url, src_type = resolve_source(source)

    resolution = stream_settings.get("resolution", "1280x720")
    fps = str(stream_settings.get("fps", "30"))
    bitrate = str(stream_settings.get("bitrate", "4000"))
    rtmp = stream_settings.get("rtmp", "rtmp://a.rtmp.youtube.com/live2")

    zoom = float(transform.get("zoom", 100)) / 100.0
    pos_x = int(transform.get("posX", 0))
    pos_y = int(transform.get("posY", 0))
    brightness = float(transform.get("brightness", 100)) / 100.0
    volume = float(transform.get("volume", 100)) / 100.0
    audio_mode = transform.get("audio", "stereo")

    w, h = [int(x) for x in resolution.split("x")]

    # ── Build FFmpeg base ──
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]
    loop_flag = source.get("loop", "loop")
    if loop_flag in ["loop", "playlist"]:
        cmd += ["-stream_loop", "-1"]
    cmd += ["-re", "-i", src_url]

    # Logo input
    logo_path = None
    logo_url = logo_cfg.get("url", "")
    if logo_url:
        logo_path = download_logo(logo_url)
        if logo_path:
            cmd += ["-i", logo_path]

    # ── Video filter chain ──
    vf_parts = []

    # Scale to resolution
    vf_parts.append(f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}")

    # Zoom/pan
    if zoom != 1.0 or pos_x != 0 or pos_y != 0:
        scaled_w = int(w * zoom)
        scaled_h = int(h * zoom)
        vf_parts.append(f"scale={scaled_w}:{scaled_h},crop={w}:{h}:{pos_x}:{pos_y}")

    # Brightness
    if abs(brightness - 1.0) > 0.01:
        vf_parts.append(f"eq=brightness={brightness - 1.0:.2f}")

    # ── Ticker bottom bar ──
    ticker_text = ticker_cfg.get("text", "MiTV Network • 24/7 Live Stream")
    ticker_text_esc = esc(ticker_text)
    ticker_bg = ticker_cfg.get("bg", "#cc0000").lstrip("#")
    ticker_color = ticker_cfg.get("color", "#ffffff").lstrip("#")
    ticker_speed_map = {"slow": "60", "medium": "120", "fast": "240", "vfast": "400"}
    ticker_speed = ticker_speed_map.get(ticker_cfg.get("speed", "medium"), "120")

    # Bottom bar background — FIXED: separate drawbox and drawtext (no comma join between them)
    vf_parts.append(f"drawbox=x=0:y=ih-44:w=iw:h=44:color=0x{ticker_bg}@1.0:t=fill")

    # Scrolling ticker text
    vf_parts.append(
        f"drawtext=text='{ticker_text_esc}'"
        f":fontsize=20:fontcolor=0x{ticker_color}"
        f":y=h-32"
        f":x=w-mod(t*{ticker_speed}\\,w+tw)"
    )

    # LIVE badge — FIXED: separate drawbox and drawtext properly
    vf_parts.append("drawbox=x=iw-92:y=8:w=82:h=30:color=0xCC0000@1.0:t=fill")
    vf_parts.append("drawtext=text='\\u25CF LIVE':fontsize=15:fontcolor=white:x=iw-85:y=16")

    # Watermark
    watermark = branding.get("watermarkText", "MiTV Network")
    watermark_esc = esc(watermark)
    vf_parts.append(
        f"drawtext=text='{watermark_esc}':fontsize=13"
        f":fontcolor=white@0.35:x=iw-tw-10:y=ih-58"
    )

    # Logo overlay position
    logo_pos = logo_cfg.get("position", "top-left")
    logo_size = int(logo_cfg.get("size", 80))
    pos_map = {
        "top-left":     "10:10",
        "top-right":    "main_w-overlay_w-10:10",
        "top-center":   "(main_w-overlay_w)/2:10",
        "bottom-left":  "10:main_h-overlay_h-50",
        "bottom-right": "main_w-overlay_w-10:main_h-overlay_h-50",
    }
    overlay_pos = pos_map.get(logo_pos, "10:10")

    vf_str = ",".join(vf_parts)

    if logo_path:
        logo_vf = f"scale={logo_size}:-1"
        cmd += [
            "-filter_complex",
            f"[0:v]{vf_str}[base];[1:v]{logo_vf}[logo];[base][logo]overlay={overlay_pos}[vout]",
            "-map", "[vout]"
        ]
    else:
        cmd += ["-vf", vf_str, "-map", "0:v"]

    # ── Audio filter ──
    af_parts = [f"volume={volume:.2f}"]
    if audio_mode == "mono":
        af_parts.append("pan=mono|c0=c0")
    elif audio_mode == "echo":
        af_parts.append("aecho=0.8:0.9:1000:0.3")
    elif audio_mode == "bass":
        af_parts.append("equalizer=f=60:t=o:w=2:g=8")

    cmd += ["-map", "0:a", "-af", ",".join(af_parts)]

    # ── Encoding ──
    cmd += [
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "zerolatency",
        "-b:v", f"{bitrate}k",
        "-maxrate", f"{int(float(bitrate)) * 2}k",
        "-bufsize", f"{int(float(bitrate)) * 4}k",
        "-g", str(int(float(fps)) * 2),
        "-r", fps,
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
    ]

    if mode == "m3u":
        # HLS output for M3U mode — no stream key needed
        hls_dir = "/tmp/hls_out"
        os.makedirs(hls_dir, exist_ok=True)
        cmd += [
            "-f", "hls",
            "-hls_time", "4",
            "-hls_list_size", "10",
            "-hls_flags", "delete_segments+append_list",
            "-hls_segment_filename", f"{hls_dir}/seg%03d.ts",
            f"{hls_dir}/stream.m3u8"
        ]
        log(f"HLS output -> {hls_dir}/stream.m3u8")
    else:
        # RTMP/YouTube mode
        cmd += [
            "-flvflags", "no_duration_filesize",
            "-f", "flv",
            f"{rtmp}/{stream_key}"
        ]

    return cmd, logo_path


# ─── M3U generation ────────────────────────────────────────────────────────────
def generate_m3u_link(config):
    """Generate a virtual M3U playlist that points to our HLS stream"""
    branding = config.get("branding", {})
    channel_name = branding.get("channelName", "MiTV Network 24/7")
    hls_url = "http://localhost:8080/stream.m3u8"

    # Save M3U info to Firebase so control panel can display it
    fb_update("mitv_stream/m3uOutput", {
        "url": hls_url,
        "playlist": f"#EXTM3U\n#EXTINF:-1 tvg-name=\"{channel_name}\" tvg-logo=\"https://i.ibb.co/Xxpt0B54/IMG-20260415-223746-removebg-preview.png\" group-title=\"MiTV\",{channel_name}\n{hls_url}",
        "generatedAt": int(time.time() * 1000)
    })
    log(f"M3U link generated: {hls_url}")
    return hls_url


# ─── HLS HTTP Server (for M3U mode) ───────────────────────────────────────────
def start_hls_server():
    """Start a simple HTTP server to serve HLS files"""
    import http.server
    import socketserver

    class HLSHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="/tmp/hls_out", **kwargs)
        def log_message(self, format, *args):
            pass  # suppress logs

    with socketserver.TCPServer(("0.0.0.0", 8080), HLSHandler) as httpd:
        log("HLS server started on port 8080")
        httpd.serve_forever()


# ─── MAIN LOOP ─────────────────────────────────────────────────────────────────
def main():
    global STREAM_KEY

    log("=" * 50)
    log("MiTV Stream Engine v2 Starting...")
    log("=" * 50)

    config = fb_get("mitv_stream")
    stream_settings = (config or {}).get("streamSettings", {})
    mode = stream_settings.get("outputMode", "youtube")  # "youtube" or "m3u"

    if mode == "youtube":
        if not STREAM_KEY:
            cfg = fb_get("mitv_stream/streamSettings")
            if cfg and cfg.get("key"):
                STREAM_KEY = cfg["key"]
                log("Stream key loaded from Firebase")
            else:
                log("ERROR: No stream key! Set YOUTUBE_STREAM_KEY secret or save in panel")
                sys.exit(1)
    else:
        log("Output mode: M3U/HLS — no YouTube key needed")
        hls_thread = threading.Thread(target=start_hls_server, daemon=True)
        hls_thread.start()
        time.sleep(1)

    loop_count = 0
    start_time = time.time()

    fb_update("mitv_stream/status", {
        "live": True,
        "loops": 0,
        "startedAt": int(start_time * 1000),
        "pid": os.getpid(),
        "mode": mode
    })

    # Status updater thread
    def status_updater():
        while True:
            time.sleep(30)
            uptime = int(time.time() - start_time)
            fb_update("mitv_stream/status", {
                "loops": loop_count,
                "uptime": uptime,
                "lastPing": int(time.time() * 1000)
            })

    threading.Thread(target=status_updater, daemon=True).start()

    # Command watcher thread
    restart_flag = [False]
    def command_watcher():
        while True:
            time.sleep(15)
            status = fb_get("mitv_stream/status")
            if status:
                cmd = status.get("command")
                if cmd == "stop":
                    log("Stop command received from panel")
                    os.kill(os.getpid(), signal.SIGTERM)
                elif cmd == "restart":
                    log("Restart command received")
                    fb_update("mitv_stream/status", {"command": "none"})
                    restart_flag[0] = True

    threading.Thread(target=command_watcher, daemon=True).start()

    process = None
    logo_tmp = None

    def cleanup():
        nonlocal process, logo_tmp
        if process and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=10)
            except: process.kill()
        if logo_tmp and os.path.exists(logo_tmp):
            os.unlink(logo_tmp)

    # Main streaming loop
    while True:
        try:
            log(f"Loop #{loop_count + 1} — Loading config from Firebase...")
            config = fb_get("mitv_stream")
            if not config:
                log("No config in Firebase, retrying in 30s...")
                time.sleep(30)
                continue

            status = config.get("status", {})
            if status.get("live") is False and status.get("command") != "start":
                log("Stream paused (live=false). Waiting for start command...")
                time.sleep(20)
                continue

            # Generate M3U if needed
            if mode == "m3u":
                generate_m3u_link(config)

            log("Building FFmpeg command...")
            try:
                cmd, logo_tmp = build_ffmpeg_cmd(config, STREAM_KEY, mode=mode)
            except Exception as e:
                log(f"Config error: {e}")
                time.sleep(30)
                continue

            log(f"FFmpeg: {' '.join(cmd[:10])}...")
            log(f"Streaming... (loop {loop_count + 1}, mode={mode})")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            def log_ffmpeg_stderr():
                for line in iter(process.stderr.readline, b''):
                    txt = line.decode('utf-8', errors='ignore').strip()
                    if txt and any(k in txt.lower() for k in ['error', 'warning', 'frame', 'fps', 'speed']):
                        print(f"[FFmpeg] {txt}")

            threading.Thread(target=log_ffmpeg_stderr, daemon=True).start()

            while process.poll() is None:
                if restart_flag[0]:
                    restart_flag[0] = False
                    process.terminate()
                    log("Restarting stream...")
                    break
                time.sleep(5)

            ret = process.returncode
            loop_count += 1

            if logo_tmp and os.path.exists(logo_tmp):
                os.unlink(logo_tmp)
                logo_tmp = None

            fb_update("mitv_stream/status", {"loops": loop_count})

            if ret == 0:
                log(f"Loop {loop_count} complete, restarting...")
            elif ret == -15:
                log("Process terminated by signal")
            else:
                log(f"FFmpeg exit code {ret}, restarting in 5s...")
                time.sleep(5)

        except KeyboardInterrupt:
            log("Keyboard interrupt — stopping")
            break
        except SystemExit:
            log("Stop command — exiting")
            break
        except Exception as e:
            log(f"Unexpected error: {e}")
            traceback.print_exc()
            time.sleep(10)

    cleanup()
    fb_update("mitv_stream/status", {"live": False, "command": "none"})
    log("Stream engine stopped.")


if __name__ == "__main__":
    main()
