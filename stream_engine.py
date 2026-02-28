import os
import subprocess
import time
import datetime
import pytz
import threading
import argparse
import sys

# ==========================================================
# MITV NETWORK - 24/7 BROADCASTING SYSTEM (v3.4 - FINAL STABLE)
# FIX: 'Error parsing global options' by using Relative Paths
# REMOVED: Time Logic as per User Request
# ==========================================================

class StreamEngine:
    def __init__(self, args):
        self.video = args.video
        self.audio = args.audio
        self.key = args.key
        self.p_color = args.color
        self.do_patti = args.patti.lower() == 'yes'
        self.logo = "logon.png" 
        
        # Relative paths use kar rahe hain taake FFMPEG confuse na ho
        self.p_date = "pkt_date.txt"
        self.fb_text = "fb_live_text.txt"
        self.tz = pytz.timezone('Asia/Karachi')
        
        self.create_initial_files()

    def create_initial_files(self):
        """Files ko create karna taake FFMPEG ko mil jayein"""
        for f_name in [self.p_date, self.fb_text]:
            with open(f_name, "w") as f:
                f.write("Starting...")
            print(f"[SYSTEM] Ready: {f_name}")

    def metadata_loop(self):
        """Sirf Date update hogi"""
        while True:
            try:
                now = datetime.datetime.now(self.tz)
                with open(self.p_date, "w") as f: 
                    f.write(now.strftime("%d-%b-%Y"))
                time.sleep(60) # Date har minute baad check kafi hai
            except Exception as e:
                print(f"[WARN] Meta error: {e}")

    def get_ffmpeg_inputs(self):
        if (not self.video or self.video.strip() == "") and self.audio:
            return ["-loop", "1", "-i", self.logo, "-re", "-i", self.audio], "[0:v]", "1:a"
        elif self.video and self.audio:
            return ["-re", "-stream_loop", "-1", "-i", self.video, "-i", self.audio], "[0:v]", "1:a"
        else:
            return ["-re", "-stream_loop", "-1", "-i", self.video], "[0:v]", "0:a"

    def build_filters(self, v_map):
        # Paths ko quote mein rakha hai lekin absolute path nahi diya
        f = f"{v_map}scale=1280:720[bg];"
        f += f"movie={self.logo},scale=130:-1[logo_img];[bg][logo_img]overlay=20:20[v_logo];"
        
        # Date Display
        f += f"[v_logo]drawbox=y=130:x=20:w=240:h=50:color=black@0.6:t=fill[box];"
        f += f"[box]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile='{self.p_date}':reload=1:x=40:y=145:fontsize=22:fontcolor=yellow[v_meta];"
        
        # Scrolling Patti
        if self.do_patti:
            f += f"[v_meta]drawbox=y=ih-55:x=0:w=iw:h=55:color={self.p_color}@0.8:t=fill[p_bg];"
            f += f"[p_bg]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile='{self.fb_text}':reload=1:x=w-mod(t*110\,w+tw):y=ih-40:fontsize=28:fontcolor=white[final_v]"
        else:
            f += "[v_meta]copy[final_v]"
        return f

    def run_stream(self):
        threading.Thread(target=self.metadata_loop, daemon=True).start()
        time.sleep(2)
        
        rtmp_target = f"rtmp://a.rtmp.youtube.com/live2/{self.key}"
        
        while True:
            inputs, v_map, a_map = self.get_ffmpeg_inputs()
            filters = self.build_filters(v_map)
            
            # Pure command ko list format mein rakha hai
            ffmpeg_command = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", filters,
                "-map", "[final_v]",
                "-map", a_map,
                "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3000k",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-f", "flv", rtmp_target
            ]
            
            print(f"--- MiTV LIVE ENGINE STARTING ---")
            try:
                # stderr ko ignore nahi karenge taake logs saaf dikhein
                subprocess.run(ffmpeg_command, check=True)
            except Exception as e:
                print(f"[RESTART] Stream broke: {e}")
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
        sys.exit(1)
        
    engine = StreamEngine(args)
    engine.run_stream()
