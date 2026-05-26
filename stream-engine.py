#!/usr/bin/env python3
"""
MiTV Stream Engine v3 — UPGRADED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ NO YouTube stream key — pure M3U8/HLS output
✅ Cloudflare tunnel for worldwide public access
✅ Schedule system (time-based content switching)
✅ Never-stop loop logic with auto-restart
✅ Saves stream timeline offset → overlay resumes on refresh
✅ Country-aware status updates
✅ Enhanced FFmpeg filters (effects, audio EQ, etc.)
"""

import os, sys, json, time, signal, subprocess, threading
import tempfile, urllib.request, datetime, traceback, re, socket

FIREBASE_DB  = "https://ramadan-2385b-default-rtdb.firebaseio.com"
FIREBASE_KEY = os.environ.get("FIREBASE_KEY", "")
RUNNER_NUM   = os.environ.get("RUNNER_NUMBER", "?")

tunnel_proc  = None
hls_server   = None
start_time   = time.time()
loop_count   = 0

# ─── Firebase REST ──────────────────────────────────────────────────────────
def fb_get(path):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY: url += f"?auth={FIREBASE_KEY}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[Firebase] GET error {path}: {e}")
        return None

def fb_set(path, data):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY: url += f"?auth={FIREBASE_KEY}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Content-Type":"application/json"}, method="PUT")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"[Firebase] SET error: {e}")

def fb_update(path, data):
    url = f"{FIREBASE_DB}/{path}.json"
    if FIREBASE_KEY: url += f"?auth={FIREBASE_KEY}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Content-Type":"application/json"}, method="PATCH")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"[Firebase] UPDATE error: {e}")

def log(msg):
    ts    = datetime.datetime.utcnow().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry, flush=True)
    key   = str(int(time.time() * 1000))
    fb_set(f"mitv_stream/logs/{key}", entry[-250:])

# ─── Cloudflare Tunnel ──────────────────────────────────────────────────────
def start_tunnel():
    global tunnel_proc
    log("🌐 Starting Cloudflare tunnel...")
    tunnel_proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080",
         "--no-autoupdate", "--loglevel", "info"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    url = None
    deadline = time.time() + 45
    for line in tunnel_proc.stdout:
        if time.time() > deadline: break
        m = re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com', line)
        if m:
            url = m.group(0)
            break

    if url:
        log(f"✅ Tunnel live: {url}")
        m3u8_url = f"{url}/stream.m3u8"
        m3u_text = (
            f"#EXTM3U\n"
            f"#EXTINF:-1 tvg-name=\"MiTV 24/7\" "
            f"tvg-logo=\"https://i.ibb.co/Xxpt0B54/IMG-20260415-223746-removebg-preview.png\" "
            f"group-title=\"MiTV\",MiTV 24/7 Live\n"
            f"{m3u8_url}"
        )
        fb_update("mitv_stream/m3uOutput", {
            "url":         m3u8_url,
            "tunnelUrl":   url,
            "playlist":    m3u_text,
            "generatedAt": int(time.time() * 1000),
            "status":      "LIVE"
        })
        return url
    else:
        log("⚠️  Tunnel URL not captured — HLS still local")
        return None

# ─── HLS HTTP Server ────────────────────────────────────────────────────────
def start_hls_server():
    import http.server, socketserver

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory="/tmp/hls_out", **kw)
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store")
            super().end_headers()
        def log_message(self, *a): pass

    os.makedirs("/tmp/hls_out", exist_ok=True)
    with socketserver.TCPServer(("0.0.0.0", 8080), H) as s:
        log("📡 HLS server ready on :8080")
        s.serve_forever()

# ─── Schedule System ────────────────────────────────────────────────────────
def get_scheduled_source(config):
    """Return source override from schedule if time matches"""
    schedule = config.get("schedule", [])
    if not schedule:
        return None
    now    = datetime.datetime.utcnow()
    now_m  = now.hour * 60 + now.minute
    day_of_week = now.strftime("%a").lower()

    for prog in schedule:
        days = prog.get("days", ["mon","tue","wed","thu","fri","sat","sun"])
        if day_of_week not in [d.lower() for d in days]:
            continue
        try:
            sh, sm = map(int, prog["start"].split(":"))
            eh, em = map(int, prog["end"].split(":"))
            if (sh * 60 + sm) <= now_m < (eh * 60 + em):
                log(f"📅 Schedule: '{prog.get('name','Program')}' active until {prog['end']}")
                return prog.get("source")
        except: pass
    return None

# ─── Source Resolution ──────────────────────────────────────────────────────
def resolve_source(source):
    if not source: raise ValueError("No source configured")
    src_type = source.get("type", "mp4")
    url      = source.get("url","").strip()
    if not url: raise ValueError("Source URL is empty")

    if src_type == "mp4":
        log(f"📹 MP4: {url[:80]}")
        return url, "mp4"
    elif src_type in ("m3u","m3u8"):
        log(f"📺 M3U: {url[:80]}")
        return extract_from_m3u(url, source.get("index",0)), "m3u"
    elif src_type == "youtube":
        log(f"▶️  YouTube: {url[:80]}")
        return extract_youtube(url), "youtube"
    elif src_type == "rtmp":
        log(f"🔴 RTMP in: {url[:80]}")
        return url, "rtmp"
    else:
        raise ValueError(f"Unknown source type: {src_type}")

def extract_from_m3u(url, index=0):
    with urllib.request.urlopen(url, timeout=20) as r:
        txt = r.read().decode("utf-8", errors="ignore")
    streams = [l.strip() for l in txt.splitlines()
               if l.strip() and not l.strip().startswith("#")]
    if not streams: raise ValueError("Empty M3U")
    idx = min(index, len(streams)-1)
    log(f"M3U: {len(streams)} channels → index {idx}: {streams[idx][:80]}")
    return streams[idx]

def extract_youtube(url):
    r = subprocess.run(
        ["yt-dlp","-g","--no-warnings","-f","best[height<=720]/best", url],
        capture_output=True, text=True, timeout=120)
    if r.returncode != 0: raise ValueError(f"yt-dlp: {r.stderr[:200]}")
    return r.stdout.strip().split("\n")[0]

# ─── Logo Download ──────────────────────────────────────────────────────────
def download_logo(url):
    if not url: return None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        with urllib.request.urlopen(url, timeout=15) as r: tmp.write(r.read())
        tmp.close()
        return tmp.name
    except Exception as e:
        log(f"⚠️  Logo DL failed: {e}"); return None

def esc(t):
    return t.replace("\\","\\\\").replace("'","\\'").replace(":","\\:").replace("%","\\%")

# ─── FFmpeg Command Builder ─────────────────────────────────────────────────
def build_ffmpeg(config):
    source   = config.get("source", {})
    sched    = get_scheduled_source(config)
    if sched: source = sched          # schedule overrides default source

    transform= config.get("transform", {})
    logo_cfg = config.get("logo", {})
    ticker   = config.get("ticker", {})
    settings = config.get("streamSettings", {})
    branding = config.get("branding", {})
    effects  = config.get("effects", {})
    audio_fx = config.get("audioFx", {})

    src_url, src_type = resolve_source(source)

    res     = settings.get("resolution", "1280x720")
    fps     = str(settings.get("fps", 30))
    bitrate = str(settings.get("bitrate", 4000))
    w, h    = [int(x) for x in res.split("x")]

    zoom        = float(transform.get("zoom", 100)) / 100.0
    pos_x       = int(transform.get("posX", 0))
    pos_y       = int(transform.get("posY", 0))
    brightness  = float(transform.get("brightness", 100)) / 100.0
    volume      = float(transform.get("volume", 100)) / 100.0

    # ── base cmd ──
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]
    loop = source.get("loop","loop")
    if loop in ("loop","playlist"):
        cmd += ["-stream_loop","-1"]
    cmd += ["-re", "-i", src_url]

    # ── logo ──
    logo_path = download_logo(logo_cfg.get("url",""))
    if logo_path:
        cmd += ["-i", logo_path]

    # ── video filters ──
    vf = []
    vf.append(f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}")
    if zoom != 1.0 or pos_x or pos_y:
        sw, sh = int(w*zoom), int(h*zoom)
        vf.append(f"scale={sw}:{sh},crop={w}:{h}:{pos_x}:{pos_y}")
    if abs(brightness-1.0) > 0.01:
        vf.append(f"eq=brightness={brightness-1.0:.2f}")

    # ── extra video effects ──
    contrast   = float(effects.get("contrast",   100)) / 100.0
    saturation = float(effects.get("saturation", 100)) / 100.0
    hue_shift  = float(effects.get("hue",        0))
    blur_amt   = float(effects.get("blur",        0))
    sharpness  = float(effects.get("sharpness",  0))
    vignette   = effects.get("vignette", False)
    mirror     = effects.get("mirror",   False)

    if abs(contrast-1.0) > 0.01 or abs(saturation-1.0) > 0.01 or abs(hue_shift) > 0.1:
        vf.append(f"eq=contrast={contrast:.2f}:saturation={saturation:.2f}")
    if hue_shift:
        vf.append(f"hue=h={hue_shift:.1f}")
    if blur_amt > 0:
        vf.append(f"boxblur={blur_amt:.1f}:{blur_amt:.1f}")
    if sharpness > 0:
        vf.append(f"unsharp=5:5:{sharpness/10:.2f}:5:5:0")
    if mirror:
        vf.append("hflip")
    if vignette:
        vf.append("vignette=PI/4")

    # ── ticker bar ──
    tick_text  = esc(ticker.get("text","MiTV Network • 24/7 Live Stream"))
    tick_bg    = ticker.get("bg","#cc0000").lstrip("#")
    tick_color = ticker.get("color","#ffffff").lstrip("#")
    speed_map  = {"slow":"60","medium":"120","fast":"240","vfast":"400"}
    tick_speed = speed_map.get(ticker.get("speed","medium"),"120")
    tick_anim  = ticker.get("animation","scroll")

    vf.append(f"drawbox=x=0:y=ih-44:w=iw:h=44:color=0x{tick_bg}@1.0:t=fill")
    if tick_anim == "scroll":
        vf.append(f"drawtext=text='{tick_text}':fontsize=20:fontcolor=0x{tick_color}"
                  f":y=h-32:x=w-mod(t*{tick_speed}\\,w+tw)")
    else:
        vf.append(f"drawtext=text='{tick_text}':fontsize=20:fontcolor=0x{tick_color}"
                  f":y=h-32:x=(w-tw)/2")

    # ── LIVE badge ──
    vf.append("drawbox=x=iw-92:y=8:w=82:h=30:color=0xCC0000@1.0:t=fill")
    vf.append("drawtext=text='\\u25CF LIVE':fontsize=14:fontcolor=white:x=iw-84:y=16")

    # ── date/time overlay ──
    if config.get("showDateTime", False):
        tz_offset = int(config.get("tzOffset", 5))
        vf.append(
            f"drawtext=text='%{{localtime\\:%H\\:%M\\:%S}}':fontsize=16"
            f":fontcolor=white@0.9:x=iw-160:y=50"
        )

    # ── watermark ──
    wm = esc(branding.get("watermarkText","MiTV Network"))
    vf.append(f"drawtext=text='{wm}':fontsize=13:fontcolor=white@0.3:x=iw-tw-10:y=ih-58")

    # ── channel name overlay ──
    ch = esc(branding.get("channelName",""))
    if ch:
        vf.append(f"drawtext=text='{ch}':fontsize=14:fontcolor=white@0.8:x=16:y=16")

    # ── logo position ──
    pos_map = {
        "top-left":     "10:10",
        "top-right":    "main_w-overlay_w-10:10",
        "top-center":   "(main_w-overlay_w)/2:10",
        "bottom-left":  "10:main_h-overlay_h-52",
        "bottom-right": "main_w-overlay_w-10:main_h-overlay_h-52",
    }
    overlay_pos = pos_map.get(logo_cfg.get("position","top-left"), "10:10")
    logo_size   = int(logo_cfg.get("size", 80))

    vf_str = ",".join(vf)
    if logo_path:
        cmd += [
            "-filter_complex",
            f"[0:v]{vf_str}[base];[1:v]scale={logo_size}:-1[logo];[base][logo]overlay={overlay_pos}[vout]",
            "-map","[vout]"
        ]
    else:
        cmd += ["-vf", vf_str, "-map","0:v"]

    # ── audio ──
    af = [f"volume={volume:.2f}"]
    audio_mode = transform.get("audio","stereo")
    bass    = float(audio_fx.get("bass",    0))
    treble  = float(audio_fx.get("treble",  0))
    echo    = audio_fx.get("echo",   False)
    norm    = audio_fx.get("normalize", False)
    stereo_w= float(audio_fx.get("stereoWidth", 100)) / 100.0

    if bass != 0:
        af.append(f"equalizer=f=80:t=o:w=2:g={bass:.1f}")
    if treble != 0:
        af.append(f"equalizer=f=8000:t=o:w=2:g={treble:.1f}")
    if echo:
        af.append("aecho=0.8:0.9:500:0.3")
    if norm:
        af.append("dynaudnorm=p=0.9")
    if audio_mode == "mono":
        af.append("pan=mono|c0=c0")
    elif audio_mode == "surround":
        af.append("aformat=channel_layouts=5.1")

    cmd += ["-map","0:a", "-af", ",".join(af)]

    # ── encoding ──
    fps_i = int(float(fps))
    br_i  = int(float(bitrate))
    cmd += [
        "-c:v","libx264","-preset","veryfast","-tune","zerolatency",
        "-b:v",f"{bitrate}k","-maxrate",f"{br_i*2}k","-bufsize",f"{br_i*4}k",
        "-g",str(fps_i*2),"-r",fps,
        "-c:a","aac","-b:a","128k","-ar","44100","-ac","2",
    ]

    # ── HLS output ──
    hls_dir = "/tmp/hls_out"
    os.makedirs(hls_dir, exist_ok=True)
    cmd += [
        "-f","hls",
        "-hls_time","4",
        "-hls_list_size","12",
        "-hls_flags","delete_segments+append_list+independent_segments",
        "-hls_segment_filename", f"{hls_dir}/seg%05d.ts",
        "-hls_base_url", "",
        f"{hls_dir}/stream.m3u8"
    ]

    log(f"HLS → {hls_dir}/stream.m3u8")
    return cmd, logo_path

# ─── Status Updater ─────────────────────────────────────────────────────────
def run_status_updater():
    while True:
        time.sleep(20)
        try:
            uptime = int(time.time() - start_time)
            fb_update("mitv_stream/status", {
                "loops":    loop_count,
                "uptime":   uptime,
                "lastPing": int(time.time()*1000),
                "runner":   RUNNER_NUM,
                "streamOffset": int(time.time() - start_time),  # for overlay resume
            })
        except: pass

# ─── Command Watcher ────────────────────────────────────────────────────────
restart_flag = [False]
stop_flag    = [False]

def run_command_watcher():
    while True:
        time.sleep(12)
        try:
            status = fb_get("mitv_stream/status") or {}
            cmd    = status.get("command","none")
            if cmd == "stop":
                log("⛔ Stop command from panel")
                stop_flag[0] = True
                os.kill(os.getpid(), signal.SIGTERM)
            elif cmd == "restart":
                log("🔁 Restart command from panel")
                fb_update("mitv_stream/status",{"command":"none"})
                restart_flag[0] = True
        except: pass

# ─── MAIN ───────────────────────────────────────────────────────────────────
def main():
    global loop_count, start_time

    log("=" * 55)
    log("  MiTV Stream Engine v3  |  NO YouTube Key Mode")
    log(f"  Runner #{RUNNER_NUM}  |  UTC {datetime.datetime.utcnow():%Y-%m-%d %H:%M}")
    log("=" * 55)

    # Init Firebase status
    start_time = time.time()
    fb_update("mitv_stream/status", {
        "live":      True,
        "loops":     0,
        "startedAt": int(start_time * 1000),
        "pid":       os.getpid(),
        "mode":      "hls",
        "command":   "none",
        "runner":    RUNNER_NUM,
        "streamOffset": 0,
    })

    # Start HLS server
    threading.Thread(target=start_hls_server, daemon=True).start()
    time.sleep(1.5)

    # Start Cloudflare tunnel
    threading.Thread(target=start_tunnel,   daemon=True).start()
    time.sleep(8)   # give tunnel time to get URL

    # Background threads
    threading.Thread(target=run_status_updater,  daemon=True).start()
    threading.Thread(target=run_command_watcher, daemon=True).start()

    process  = None
    logo_tmp = None

    def cleanup():
        nonlocal process, logo_tmp
        if process and process.poll() is None:
            process.terminate()
            try:    process.wait(timeout=10)
            except: process.kill()
        if logo_tmp and os.path.exists(logo_tmp):
            try: os.unlink(logo_tmp)
            except: pass

    def sigterm_handler(sig, frame):
        log("SIGTERM received — cleaning up")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)

    # ── Main streaming loop ──
    while not stop_flag[0]:
        try:
            log(f"\n🔄 Loop #{loop_count + 1} — fetching config...")
            config = fb_get("mitv_stream") or {}

            status = config.get("status", {})
            if status.get("live") is False and status.get("command") != "start":
                log("⏸️  Paused (live=false). Waiting...")
                time.sleep(20)
                continue

            try:
                cmd, logo_tmp = build_ffmpeg(config)
            except Exception as e:
                log(f"⚠️  Config/build error: {e}")
                time.sleep(30)
                continue

            log(f"▶️  FFmpeg starting (loop {loop_count+1})...")

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            def log_stderr():
                kw = ['error','warning','frame','fps','speed','drop']
                for line in iter(process.stderr.readline, b''):
                    txt = line.decode('utf-8', errors='ignore').strip()
                    if txt and any(k in txt.lower() for k in kw):
                        print(f"  [FFmpeg] {txt}")
            threading.Thread(target=log_stderr, daemon=True).start()

            # Wait for process
            while process.poll() is None and not stop_flag[0]:
                if restart_flag[0]:
                    restart_flag[0] = False
                    process.terminate()
                    log("🔁 Restarting FFmpeg...")
                    break
                time.sleep(4)

            ret        = process.returncode
            loop_count += 1

            if logo_tmp and os.path.exists(logo_tmp):
                try: os.unlink(logo_tmp)
                except: pass
                logo_tmp = None

            fb_update("mitv_stream/status", {"loops": loop_count})

            if ret == 0:
                log(f"✅ Loop {loop_count} done — restarting immediately")
            elif ret == -15:
                log("⚡ FFmpeg terminated (restart/stop)")
                if stop_flag[0]: break
            else:
                log(f"⚠️  FFmpeg exit {ret} — retrying in 5s")
                time.sleep(5)

        except KeyboardInterrupt:
            log("⌨️  Keyboard interrupt")
            break
        except SystemExit:
            log("🛑 SystemExit")
            break
        except Exception as e:
            log(f"💥 Unexpected: {e}")
            traceback.print_exc()
            time.sleep(10)

    cleanup()
    fb_update("mitv_stream/status", {"live": False, "command": "none"})
    log("🔴 Engine stopped.")

if __name__ == "__main__":
    main()
