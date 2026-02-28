import os
import subprocess
import time
import datetime
import pytz
import threading
import argparse
import sys

# ==========================================================
# MITV NETWORK - 24/7 BROADCASTING SYSTEM (v3.3)
# MODIFICATION: Removed pkt_time.txt logic as requested.
# ==========================

class StreamEngine:
    def __init__(self, args):
        self.video = args.video
        self.audio = args.audio
        self.key = args.key
        self.p_color = args.color
        self.do_patti = args.patti.lower() == 'yes'
        self.logo = "logon.png" 
        self.p_date = os.path.abspath("pkt_date.txt")
        self.fb_text = os.path.abspath("fb_live_text.txt")
        self.tz = pytz.timezone('Asia/Karachi')
        
        # Files initialize karna (Time file ab nahi banegi)
        self.create_initial_files()

    def create_initial_files(self):
        """Date aur Firebase files ko pre-create karta hai"""
        for file_path in [self.p_date, self.fb_text]:
            with open(file_path, "w") as f:
                f.write("Loading...")
            print(f"[SYSTEM] Initialized: {file_path}")

    def metadata_loop(self):
        """Sirf Date update karega, Time nahi"""
        while True:
            try:
                now = datetime.datetime.now(self.tz)
                with open(self.p_date, "w") as f: 
                    f.write(now.strftime("%d-%b-%Y"))
                time.sleep(10) # Date har second update karne ki zaroorat nahi
            except Exception as e:
                print(f"[WARN] Metadata update error: {e}")

    def get_ffmpeg_inputs(self):
        if (not self.video or self.video.strip() == "") and self.audio:
            inputs = ["-loop", "1", "-i", self.logo, "-re", "-i", self.audio]
            v_map, a_map = "[0:v]", "1:a"
        elif self.video and self.audio:
            inputs = ["-re", "-stream_loop", "-1", "-i", self.video, "-i", self.audio]
            v_map, a_map = "[0:v]", "1:a"
        else:
            inputs = ["-re", "-stream_loop", "-1", "-i", self.video]
            v_map, a_map = "[0:v]", "0:a"
        return inputs, v_map, a_map

    def build_filters(self, v_map):
        # Paths ko escape karna taake FFMPEG error na de
        date_path = self.p_date.replace(':', '\\:').replace('\\', '/')
        fb_path = self.fb_text.replace(':', '\\:').replace('\\', '/')

        f = f"{v_map}scale=1280:720[bg];"
        f += f"movie={self.logo},scale=130:-1[logo_img];[bg][logo_img]overlay=20:20[v_logo];"
        
        # Date Box (Ab isme Time nahi dikhega)
        f += f"[v_logo]drawbox=y=130:x=20:w=240:h=50:color=black@0.6:t=fill[box];"
        f += f"[box]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile='{date_path}':reload=1:x=40:y=145:fontsize=22:fontcolor=yellow[v_meta];"
        
        if self.do_patti:
            f += f"[v_meta]drawbox=y=ih-55:x=0:w=iw:h=55:color={self.p_color}@0.8:t=fill[p_bg];"
            f += f"[p_bg]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile='{fb_path}':reload=1:x=w-mod(t*110\,w+tw):y=ih-40:fontsize=28:fontcolor=white[final_v]"
        else:
            f += "[v_meta]copy[final_v]"
        return f

    def run_stream(self):
        meta_thread = threading.Thread(target=self.metadata_loop, daemon=True)
        meta_thread.start()
        time.sleep(2)
        
        rtmp_target = f"rtmp://a.rtmp.youtube.com/live2/{self.key}"
        
        while True:
            inputs, v_map, a_map = self.get_ffmpeg_inputs()
            filters = self.build_filters(v_map)
            
            ffmpeg_command = [
                "ffmpeg", "-y", *inputs,
                "-filter_complex", filters,
                "-map", "[final_v]", "-map", a_map,
                "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3000k",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-f", "flv", rtmp_target
            ]
            
            print(f"--- MiTV LIVE FOR MUAAZ (No Time Logic) ---")
            try:
                subprocess.run(ffmpeg_command, check=True)
            except Exception as e:
                print(f"[RESTART] FFMPEG issue: {e}")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video")
    parser.add_argument("--audio")
    parser.add_argument("--key")
    parser.add_argument("--color")
    parser.add_argument("--patti")
    args = parser.parse_args()
    
    if not args.key:
        print("[ERROR] No Stream Key!")
        sys.exit(1)
        
    engine = StreamEngine(args)
    engine.run_stream()
