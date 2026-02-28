import os
import subprocess
import time
import datetime
import pytz
import threading
import argparse
import sys

# ==========================================================
# MITV NETWORK - 24/7 BROADCASTING SYSTEM (v3.1 - STABLE)
# DEVELOPED BY: MUAAZ IQBAL (ICS STUDENT)
# ==========================================================

class StreamEngine:
    def __init__(self, args):
        # Initializing Arguments
        self.video = args.video
        self.audio = args.audio
        self.key = args.key
        self.p_color = args.color
        self.do_patti = args.patti.lower() == 'yes'
        self.logo = "logon.png" # As per your uploaded file name
        self.p_time = "pkt_time.txt"
        self.p_date = "pkt_date.txt"
        self.fb_text = "fb_live_text.txt"
        self.tz = pytz.timezone('Asia/Karachi')
        
        # Initializing Display Files
        self.initialize_files()

    def initialize_files(self):
        """Creates initial files to prevent FFMPEG read errors"""
        with open(self.fb_text, "w") as f: f.write("MiTV Network: Connecting to Firebase...")
        with open(self.p_time, "w") as f: f.write("00:00:00")
        with open(self.p_date, "w") as f: f.write("01-01-2026")

    def metadata_loop(self):
        """Updates PKT Time and Date every second in background"""
        print("[INFO] Metadata thread started.")
        while True:
            try:
                now = datetime.datetime.now(self.tz)
                with open(self.p_time, "w") as f: f.write(now.strftime("%I:%M:%S %p"))
                with open(self.p_date, "w") as f: f.write(now.strftime("%d-%b-%Y"))
                time.sleep(1)
            except Exception as e:
                print(f"[WARN] Metadata update failed: {e}")

    def get_ffmpeg_inputs(self):
        """Determines input mapping based on user provide links"""
        # Scenario 1: Only Audio (Use Logo as Background)
        if (not self.video or self.video.strip() == "") and self.audio:
            print("[LOGIC] Video missing. Using logo as background with user audio.")
            inputs = ["-loop", "1", "-i", self.logo, "-re", "-i", self.audio]
            v_map, a_map = "[0:v]", "1:a"
        
        # Scenario 2: Both Video and Audio (Custom audio priority)
        elif self.video and self.audio:
            print("[LOGIC] Both links provided. Video loop enabled, audio mapped from audio link.")
            inputs = ["-re", "-stream_loop", "-1", "-i", self.video, "-i", self.audio]
            v_map, a_map = "[0:v]", "1:a"
            
        # Scenario 3: Only Video (Use original audio)
        else:
            print("[LOGIC] Streaming video with original audio in loop.")
            inputs = ["-re", "-stream_loop", "-1", "-i", self.video]
            v_map, a_map = "[0:v]", "0:a"
            
        return inputs, v_map, a_map

    def build_filters(self, v_map):
        """Massive FFMPEG Filter Complex for Overlays"""
        # Base Scale
        f = f"{v_map}scale=1280:720[bg];"
        
        # Logo Positioning (Top Left)
        f += f"movie={self.logo},scale=130:-1[logo_img];[bg][logo_img]overlay=20:20[v_logo];"
        
        # Time & Date Boxes (With Background Box)
        f += f"[v_logo]drawbox=y=130:x=20:w=240:h=90:color=black@0.6:t=fill[box];"
        f += f"[box]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile={self.p_time}:reload=1:x=40:y=150:fontsize=30:fontcolor=white[t1];"
        f += f"[t1]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile={self.p_date}:reload=1:x=40:y=185:fontsize=20:fontcolor=yellow[v_meta];"
        
        # Bottom Patti (Conditional)
        if self.do_patti:
            f += f"[v_meta]drawbox=y=ih-55:x=0:w=iw:h=55:color={self.p_color}@0.8:t=fill[p_bg];"
            f += f"[p_bg]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:textfile={self.fb_text}:reload=1:x=w-mod(t*110\,w+tw):y=ih-40:fontsize=28:fontcolor=white[final_v]"
        else:
            f += "[v_meta]copy[final_v]"
            
        return f

    def run_stream(self):
        """Main loop that executes FFMPEG and handles restarts"""
        threading.Thread(target=self.metadata_loop, daemon=True).start()
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
            
            print("--- MiTV BROADCAST STARTING ---")
            print(f"Target: {rtmp_target[:15]}...")
            
            try:
                subprocess.run(ffmpeg_command, check=True)
            except Exception as e:
                print(f"[CRITICAL] FFMPEG Exit: {e}")
            
            print("[RESTART] Connection lost or loop ended. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video")
    parser.add_argument("--audio")
    parser.add_argument("--key")
    parser.add_argument("--color")
    parser.add_argument("--patti")
    args = parser.parse_args()
    
    # DEBUG INFO
    print("--- INPUT DEBUG INFO ---")
    print(f"Video Link: {args.video}")
    print(f"Audio Link: {args.audio}")
    print(f"Patti Color: {args.color}")
    print(f"Show Patti: {args.patti}")
    print("------------------------")
    
    if not args.key:
        print("[ERROR] Stream Key missing from Inputs!")
        sys.exit(1)
        
    engine = StreamEngine(args)
    engine.run_stream()
