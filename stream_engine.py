import os
import subprocess
import time
import argparse
import sys

# ==========================================================
# MITV NETWORK - 24/7 ULTIMATE STABLE ENGINE (v3.5)
# FIX: Removed all external text file dependencies for overlays
# ==========================================================

class StreamEngine:
    def __init__(self, args):
        self.video = args.video
        self.audio = args.audio
        self.key = args.key
        self.p_color = args.color
        self.do_patti = args.patti.lower() == 'yes'
        self.logo = "logon.png" 
        # Firebase text ko ab variable mein rakhenge, file mein nahi
        self.current_fb_text = "MiTV Network: Live Streaming..."

    def get_ffmpeg_inputs(self):
        # Media selection logic
        if (not self.video or self.video.strip() == "") and self.audio:
            return ["-loop", "1", "-i", self.logo, "-re", "-i", self.audio], "[0:v]", "1:a"
        elif self.video and self.audio:
            return ["-re", "-stream_loop", "-1", "-i", self.video, "-i", self.audio], "[0:v]", "1:a"
        else:
            return ["-re", "-stream_loop", "-1", "-i", self.video], "[0:v]", "0:a"

    def build_filters(self, v_map):
        # Base Visuals
        f = f"{v_map}scale=1280:720[bg];"
        
        # Logo Overlay
        f += f"movie={self.logo},scale=130:-1[logo_img];[bg][logo_img]overlay=20:20[v_logo];"
        
        # Date Display (Using FFmpeg's internal clock - NO FILE NEEDED)
        f += f"[v_logo]drawbox=y=130:x=20:w=240:h=50:color=black@0.6:t=fill[box];"
        f += f"[box]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{{localtime\\:%d-%b-%Y}}':x=40:y=145:fontsize=22:fontcolor=yellow[v_meta];"
        
        # Scrolling Patti (Direct text instead of file for stability)
        if self.do_patti:
            # Note: mod(t*...) logic for scrolling
            f += f"[v_meta]drawbox=y=ih-55:x=0:w=iw:h=55:color={self.p_color}@0.8:t=fill[p_bg];"
            f += f"[p_bg]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{self.current_fb_text}':x=w-mod(t*110\,w+tw):y=ih-40:fontsize=28:fontcolor=white[final_v]"
        else:
            f += "[v_meta]copy[final_v]"
        return f

    def start_broadcast(self):
        rtmp_target = f"rtmp://a.rtmp.youtube.com/live2/{self.key}"
        
        while True:
            inputs, v_map, a_map = self.get_ffmpeg_inputs()
            filters = self.build_filters(v_map)
            
            ffmpeg_command = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", filters,
                "-map", "[final_v]",
                "-map", a_map,
                "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3000k",
                "-bufsize", "6000k", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-f", "flv", rtmp_target
            ]
            
            print(f"--- MiTV SYSTEM ONLINE (NO-FILE MODE) ---")
            try:
                # Direct execution
                subprocess.run(ffmpeg_command, check=True)
            except Exception as e:
                print(f"[RESTART] Stream connection dropped: {e}")
            
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
        print("FATAL: Stream Key is missing!")
        sys.exit(1)
        
    engine = StreamEngine(args)
    engine.start_broadcast()
