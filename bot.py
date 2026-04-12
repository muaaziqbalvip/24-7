#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║        MI AI — THE COMPLETE INTELLIGENCE SYSTEM                                ║
# ║        BY: MUAAZ IQBAL | MUSLIM ISLAM ORGANIZATION                            ║
# ║        GOVT ISLAMIA GRADUATE COLLEGE KASUR — ICS (Statistics)                 ║
# ║        WALID: ZAFAR IQBAL | MITV NETWORK                                      ║
# ║        FEATURES: PDF BOOKS · IMAGE GEN · DOWNLOADS · GROUP/CHANNEL POSTING    ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

import telebot
from telebot import types
import requests, os, time, json, threading, sqlite3, logging, random, re, io, zipfile, math
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import A4, letter, A5
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, Image as RLImage)
from reportlab.pdfgen import canvas as rl_canvas
from duckduckgo_search import DDGS

# ── LOGGING ──────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] MI_AI: %(message)s",
    handlers=[logging.FileHandler("mi_ai.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# ── CONFIG ───────────────────────────────────────────────────────────────────────
BOT_TOKEN      = os.environ.get("BOT_TOKEN",      "YOUR_BOT_TOKEN")
GEMINI_KEY     = os.environ.get("GEMINI_API_KEY", "")
GROQ_KEY       = os.environ.get("GROQ_API_KEY",   "")
OR_KEY         = os.environ.get("OPENROUTER_KEY", "")
ADMIN_ID       = int(os.environ.get("ADMIN_ID",   "0"))
BOT_NAME       = "MI AI"
CREATOR        = "Muaaz Iqbal"
ORG            = "Muslim Islam Organization"
COLLEGE        = "Govt Islamia Graduate College Kasur"
COURSE         = "ICS with Statistics"
WALID          = "Zafar Iqbal"
VERSION        = "V20 — The Singularity"
WEBSITE        = "muslimislam.vercel.app"
BOT_START      = datetime.now()
LOADING_FRAMES = ["⏳ MI AI thinking...","🧠 Neural nodes...","⚡ Processing...","✨ Almost ready..."]
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=100)

# ══════════════════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════════════════
class MiAiDB:
    def __init__(self):
        self.conn = sqlite3.connect("mi_ai.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self._lk = threading.Lock()
        self._init()

    def _init(self):
        with self._lk:
            self.c.executescript("""
            CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY,name TEXT,username TEXT,
                password TEXT,registered INTEGER DEFAULT 0,engine TEXT DEFAULT 'auto',
                mode TEXT DEFAULT 'chat',deep INTEGER DEFAULT 0,queries INTEGER DEFAULT 0,
                joined TEXT DEFAULT CURRENT_TIMESTAMP,last_seen TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,prompt TEXT,response TEXT,engine TEXT,ts TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS chats(chat_id INTEGER PRIMARY KEY,chat_type TEXT,title TEXT,
                msg_count INTEGER DEFAULT 0,auto_post INTEGER DEFAULT 0,
                post_interval INTEGER DEFAULT 3600,last_post TEXT,topic TEXT DEFAULT 'Islamic wisdom');
            CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,title TEXT,path TEXT,pages INTEGER,ts TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS images(id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,prompt TEXT,path TEXT,style TEXT,ts TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS downloads(id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,url TEXT,filename TEXT,size_kb INTEGER,ts TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS training(id INTEGER PRIMARY KEY AUTOINCREMENT,
                input TEXT,output TEXT,category TEXT,ts TEXT DEFAULT CURRENT_TIMESTAMP);
            """)
            self.conn.commit()

    def sync(self, uid, name, uname):
        with self._lk:
            self.c.execute("INSERT OR IGNORE INTO users(uid,name,username) VALUES(?,?,?)",(uid,name,uname))
            self.c.execute("UPDATE users SET name=?,username=?,last_seen=CURRENT_TIMESTAMP WHERE uid=?",(name,uname,uid))
            self.conn.commit()

    def get(self, uid):
        self.c.execute("SELECT * FROM users WHERE uid=?",(uid,))
        r = self.c.fetchone()
        return dict(r) if r else {"engine":"auto","mode":"chat","deep":0,"queries":0}

    def upd(self, uid, key, val):
        with self._lk:
            self.c.execute(f"UPDATE users SET {key}=? WHERE uid=?",(val,uid))
            self.conn.commit()

    def save_mem(self, uid, p, r, eng=""):
        with self._lk:
            self.c.execute("INSERT INTO memory(uid,prompt,response,engine) VALUES(?,?,?,?)",(uid,p,r,eng))
            self.c.execute("UPDATE users SET queries=queries+1 WHERE uid=?",(uid,))
            self.conn.commit()

    def get_mem(self, uid, n=5):
        self.c.execute("SELECT prompt,response FROM memory WHERE uid=? ORDER BY id DESC LIMIT ?",(uid,n))
        return list(reversed(self.c.fetchall()))

    def clear_mem(self, uid):
        with self._lk:
            self.c.execute("DELETE FROM memory WHERE uid=?",(uid,))
            self.conn.commit()

    def reg_chat(self, cid, ctype, title=""):
        with self._lk:
            self.c.execute("INSERT OR IGNORE INTO chats(chat_id,chat_type,title) VALUES(?,?,?)",(cid,ctype,title))
            self.c.execute("UPDATE chats SET msg_count=msg_count+1 WHERE chat_id=?",(cid,))
            self.conn.commit()

    def get_chat(self, cid):
        self.c.execute("SELECT * FROM chats WHERE chat_id=?",(cid,))
        r = self.c.fetchone()
        return dict(r) if r else {"auto_post":0,"topic":"Islamic wisdom","post_interval":3600}

    def set_chat(self, cid, key, val):
        with self._lk:
            self.c.execute(f"UPDATE chats SET {key}=? WHERE chat_id=?",(val,cid))
            self.conn.commit()

    def all_auto(self):
        self.c.execute("SELECT * FROM chats WHERE auto_post=1")
        return [dict(r) for r in self.c.fetchall()]

    def save_book(self, uid, title, path, pages):
        with self._lk:
            self.c.execute("INSERT INTO books(uid,title,path,pages) VALUES(?,?,?,?)",(uid,title,path,pages))
            self.conn.commit()

    def save_img(self, uid, prompt, path, style):
        with self._lk:
            self.c.execute("INSERT INTO images(uid,prompt,path,style) VALUES(?,?,?,?)",(uid,prompt,path,style))
            self.conn.commit()

    def save_dl(self, uid, url, fname, size_kb=0):
        with self._lk:
            self.c.execute("INSERT INTO downloads(uid,url,filename,size_kb) VALUES(?,?,?,?)",(uid,url,fname,size_kb))
            self.conn.commit()

    def add_train(self, inp, out, cat="general"):
        with self._lk:
            self.c.execute("INSERT INTO training(input,output,category) VALUES(?,?,?)",(inp,out,cat))
            self.conn.commit()

    def get_train(self, limit=100):
        self.c.execute("SELECT * FROM training ORDER BY id DESC LIMIT ?",(limit,))
        return [dict(r) for r in self.c.fetchall()]

    def stats(self):
        res = {}
        for tbl,key in [("users","users"),("memory","msgs"),("chats","chats"),
                        ("books","books"),("images","images"),("downloads","dls")]:
            self.c.execute(f"SELECT COUNT(*) as n FROM {tbl}")
            res[key] = self.c.fetchone()["n"]
        return res

db = MiAiDB()

# ══════════════════════════════════════════════════════════════════════════════════
# NEURAL ENGINE
# ══════════════════════════════════════════════════════════════════════════════════
class NE:
    SYS = (f"You are {BOT_NAME} by {CREATOR} ({ORG}, {COLLEGE}).\n"
           f"Walid: {WALID}. Website: {WEBSITE}.\n"
           f"Reply in Roman Urdu + English mix with emojis. Be helpful and detailed.\n"
           f"Current UTC time: {{dt}}. Mode: {{mode}}.\n")

    @staticmethod
    def sys(mode="chat"):
        return NE.SYS.format(dt=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), mode=mode)

    @staticmethod
    def gemini(p, s):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":f"{s}\n\nUser: {p}"}]}],
                          "generationConfig":{"temperature":0.75,"maxOutputTokens":2048}}, timeout=20)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    @staticmethod
    def groq(p, s):
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"system","content":s},{"role":"user","content":p}],
                  "temperature":0.75,"max_tokens":2048}, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    @staticmethod
    def openrouter(p, s):
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization":f"Bearer {OR_KEY}","Content-Type":"application/json"},
            json={"model":"mistralai/mistral-7b-instruct:free",
                  "messages":[{"role":"system","content":s},{"role":"user","content":p}]}, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    @classmethod
    def ask(cls, uid, prompt, eng_ov=None, custom_sys=None):
        u   = db.get(uid)
        mode= u.get("mode","chat")
        eng = eng_ov or u.get("engine","auto")
        sys_= custom_sys or cls.sys(mode)
        order = {"auto":["gemini","groq","openrouter"],"gemini":["gemini","groq","openrouter"],
                 "groq":["groq","gemini","openrouter"],"openrouter":["openrouter","gemini","groq"]
                 }.get(eng, ["gemini","groq","openrouter"])
        labels = {"gemini":"Gemini-1.5-Flash 💎","groq":"Groq-LLaMA-3.3 ⚡","openrouter":"OpenRouter 🌐"}
        fns    = {"gemini":cls.gemini,"groq":cls.groq,"openrouter":cls.openrouter}
        for e in order:
            try:
                resp = fns[e](prompt, sys_)
                db.save_mem(uid, prompt, resp, e)
                return resp, labels[e]
            except Exception as ex:
                logger.warning(f"Engine {e} failed: {ex}")
        return "⚠️ Sab AI nodes busy hain. Thodi der baad try karein.", "Error"

# ══════════════════════════════════════════════════════════════════════════════════
# IMAGE ENGINE (PIL-based digital art)
# ══════════════════════════════════════════════════════════════════════════════════
class ImgEng:
    FBold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    FReg  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    @staticmethod
    def fnt(size, bold=True):
        try: return ImageFont.truetype(ImgEng.FBold if bold else ImgEng.FReg, size)
        except: return ImageFont.load_default()

    @staticmethod
    def center_text(draw, text, y, font, fill, W):
        try:
            bb = draw.textbbox((0,0), text, font=font)
            tw = bb[2]-bb[0]
        except: tw = len(text)*10
        x = (W-tw)//2
        draw.text((x+2,y+2), text, font=font, fill=(0,0,0,100))
        draw.text((x,y), text, font=font, fill=fill)

    @staticmethod
    def wrap(draw, text, font, max_w):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            t = cur+(" " if cur else "")+w
            try: tw = draw.textbbox((0,0),t,font=font)[2]
            except: tw = len(t)*10
            if tw <= max_w: cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines

    @staticmethod
    def islamic(text="MI AI", sub="Muslim Islam", size=(1024,576)):
        W,H = size
        img = Image.new("RGB",(W,H),(5,6,15))
        draw = ImageDraw.Draw(img,"RGBA")
        # Radial glow
        for r in range(min(W,H)//2,0,-5):
            a = int(50*(1-r/(min(W,H)//2)))
            draw.ellipse([(W//2-r,H//2-r),(W//2+r,H//2+r)],fill=(240,192,64,a))
        # 8-pointed star
        cx,cy = W//2, H//2
        for scale in [0.45,0.32,0.19]:
            R2 = int(min(W,H)*scale)
            pts=[]
            for i in range(16):
                angle = math.pi/8*i - math.pi/2
                r2 = R2 if i%2==0 else R2//2
                pts.extend([cx+r2*math.cos(angle), cy+r2*math.sin(angle)])
            draw.polygon(pts, outline=(240,192,64,70))
        # Corner arcs
        for (px,py) in [(0,0),(W,0),(0,H),(W,H)]:
            for rad in [90,65,42]:
                draw.ellipse([(px-rad,py-rad),(px+rad,py+rad)], outline=(240,192,64,45))
        # Horizontal dividers
        draw.line([(40,H//4),(W-40,H//4)],fill=(240,192,64,50),width=1)
        draw.line([(40,3*H//4),(W-40,3*H//4)],fill=(240,192,64,50),width=1)
        # Diagonal lines
        for i in range(0,W+H,90):
            draw.line([(i,0),(i-H,H)],fill=(240,192,64,8),width=1)
        # Text
        ImgEng.center_text(draw,text,H//2-55,ImgEng.fnt(72),(240,192,64),W)
        ImgEng.center_text(draw,sub, H//2+30, ImgEng.fnt(30,False),(220,220,220),W)
        ImgEng.center_text(draw,f"By {CREATOR} | {ORG}",H-48,ImgEng.fnt(18,False),(150,150,150),W)
        img = img.filter(ImageFilter.SMOOTH)
        return img

    @staticmethod
    def digital(text="MI AI", sub="", style="gold_dark", size=(1024,576)):
        W,H = size
        img = Image.new("RGB",(W,H))
        draw = ImageDraw.Draw(img,"RGBA")
        palettes = {
            "gold_dark":  [(5,6,15),(15,20,50),(240,192,64)],
            "ocean":      [(2,10,30),(5,50,80),(64,200,240)],
            "forest":     [(5,15,5),(10,40,10),(64,240,100)],
            "sunset":     [(30,5,5),(80,20,5),(240,120,40)],
            "purple":     [(10,5,25),(25,10,50),(160,64,240)],
            "green":      [(5,20,10),(5,40,20),(64,240,120)],
        }
        c1,c2,acc = palettes.get(style,palettes["gold_dark"])
        for y in range(H):
            t=y/H
            draw.line([(0,y),(W,y)],fill=(int(c1[0]*(1-t)+c2[0]*t),int(c1[1]*(1-t)+c2[1]*t),int(c1[2]*(1-t)+c2[2]*t)))
        for i in range(0,W+H,80):
            draw.line([(i,0),(i-H,H)],fill=(*acc,12),width=1)
        for (gx,gy,gr) in [(W//4,H//3,150),(3*W//4,2*H//3,120),(W//2,H//2,200)]:
            for rad in range(gr,0,-8):
                draw.ellipse([(gx-rad,gy-rad),(gx+rad,gy+rad)],fill=(*acc,int(38*(1-rad/gr))))
        draw.rectangle([(10,10),(W-10,H-10)],outline=(*acc,110),width=2)
        draw.rectangle([(18,18),(W-18,H-18)],outline=(*acc,55),width=1)
        ImgEng.center_text(draw,text,    H//2-55,ImgEng.fnt(80),acc,W)
        if sub: ImgEng.center_text(draw,sub,H//2+40,ImgEng.fnt(30,False),(255,255,255),W)
        ImgEng.center_text(draw,f"MI AI | {ORG}",H-40,ImgEng.fnt(18,False),(180,180,180),W)
        return img

    @staticmethod
    def cover(title, author, org=ORG, theme=(10,14,39), size=(794,1123)):
        W,H = size
        img = Image.new("RGB",(W,H),theme)
        draw = ImageDraw.Draw(img,"RGBA")
        for y in range(H):
            t=y/H
            r,g,b = [min(255,int(theme[i]*(1+0.5*t))) for i in range(3)]
            draw.line([(0,y),(W,y)],fill=(r,g,b))
        for ring in [280,210,140,70]:
            draw.ellipse([(W//2-ring,H//3-ring),(W//2+ring,H//3+ring)],outline=(240,192,64,28),width=2)
        for i in range(0,W+H,70):
            draw.line([(i,0),(i-H,H)],fill=(240,192,64,6),width=1)
        draw.rectangle([(0,0),(W,12)],fill=(240,192,64))
        draw.rectangle([(0,H-12),(W,H)],fill=(240,192,64))
        draw.rectangle([(0,0),(12,H)],fill=(240,192,64))
        draw.rectangle([(W-12,0),(W,H)],fill=(240,192,64))
        draw.rectangle([(25,H//2-50),(W-25,H//2+320)],fill=(0,0,0,75))
        # ORG
        f_org = ImgEng.fnt(22)
        try:
            ow = draw.textbbox((0,0),org,font=f_org)[2]
        except: ow = len(org)*14
        ox = (W-ow)//2
        draw.rectangle([(ox-12,58),(ox+ow+12,96)],fill=(240,192,64))
        draw.text((ox,62),org,font=f_org,fill=(0,0,0))
        # Title
        f_t = ImgEng.fnt(48 if len(title)<=22 else 34)
        lines = ImgEng.wrap(draw, title, f_t, W-80)
        ty = H//2-30
        for ln in lines[:4]:
            ImgEng.center_text(draw, ln, ty, f_t, (240,192,64), W)
            ty += 65
        draw.line([(70,ty+8),(W-70,ty+8)],fill=(240,192,64),width=2)
        ImgEng.center_text(draw,f"By {author}",ty+28,ImgEng.fnt(30),(220,220,220),W)
        ImgEng.center_text(draw,f"MI AI | {WEBSITE}",H-38,ImgEng.fnt(18,False),(200,200,200),W)
        return img

    @staticmethod
    def banner(title, sub="", style="gold_dark", size=(1280,380)):
        img = ImgEng.digital(title, sub, style, size)
        draw = ImageDraw.Draw(img,"RGBA")
        W,H = size
        draw.line([(0,H//3),(W,H//3)],fill=(240,192,64,28),width=1)
        draw.line([(0,2*H//3),(W,2*H//3)],fill=(240,192,64,28),width=1)
        return img

    @staticmethod
    def poster(text, sub="", bg="islamic"):
        if bg == "islamic": return ImgEng.islamic(text, sub)
        return ImgEng.digital(text, sub, bg)

    @staticmethod
    def save(img, fname):
        os.makedirs("mi_images",exist_ok=True)
        path = f"mi_images/{fname}"
        img.save(path,"PNG",optimize=True)
        return path

# ══════════════════════════════════════════════════════════════════════════════════
# PDF ENGINE
# ══════════════════════════════════════════════════════════════════════════════════
THEMES = {
    "islamic_gold":  {"bg":(10,14,39), "title":"#f0c040","heading":"#f0c040","body":"#e8eaf6","accent":"#a07820"},
    "ocean_blue":    {"bg":(2,10,30),  "title":"#40c0f0","heading":"#40c0f0","body":"#ddeeff","accent":"#1060a0"},
    "forest_green":  {"bg":(5,20,5),   "title":"#40f064","heading":"#40f064","body":"#ddfde0","accent":"#205030"},
    "royal_purple":  {"bg":(10,5,26),  "title":"#a040f0","heading":"#a040f0","body":"#eeddff","accent":"#501090"},
    "white_classic": {"bg":(250,250,250),"title":"#1a237e","heading":"#1a237e","body":"#212121","accent":"#c0a020"},
}

class PDFEngine:
    def __init__(self, cfg):
        self.title    = cfg.get("title","MI AI Book")
        self.author   = cfg.get("author",CREATOR)
        self.org      = cfg.get("org",ORG)
        self.year     = cfg.get("year",str(datetime.now().year))
        self.desc     = cfg.get("desc","")
        self.chapters = cfg.get("chapters",[])
        self.tn       = cfg.get("theme","islamic_gold")
        self.psize    = {"A4":A4,"LETTER":letter,"A5":A5}.get(cfg.get("page_size","A4"),A4)
        self.cimg     = cfg.get("cover_img",None)
        self.toc      = cfg.get("add_toc",True)
        self.pn       = cfg.get("add_pn",True)
        self.th       = THEMES.get(self.tn, THEMES["islamic_gold"])
        self.W,self.H = self.psize
        self._pn      = [0]

    def _bg_cb(self, c, doc):
        bg = self.th["bg"]
        c.saveState()
        c.setFillColorRGB(bg[0]/255,bg[1]/255,bg[2]/255)
        c.rect(0,0,self.W,self.H,fill=1,stroke=0)
        # Diagonal lines
        r,g,b = [int(x[1:3],16)/255 for x in [self.th["title"][:3]+"0000",self.th["title"][:3]+"0000",self.th["title"][:3]+"0000"]]
        gold = (240/255,192/255,64/255)
        c.setStrokeColorRGB(*gold)
        c.setStrokeAlpha(0.04)
        for i in range(-200,int(self.W+self.H),70):
            c.line(i,0,i+self.H,self.H)
        # Geometric circles
        c.setStrokeAlpha(0.07)
        for rad in [290,220,150,80]:
            c.circle(self.W/2,self.H*0.38,rad,fill=0,stroke=1)
        c.setFillColorRGB(*gold); c.setFillAlpha(1)
        c.rect(0,self.H-8,self.W,8,fill=1,stroke=0)
        c.rect(0,0,self.W,8,fill=1,stroke=0)
        c.rect(0,0,8,self.H,fill=1,stroke=0)
        c.rect(self.W-8,0,8,self.H,fill=1,stroke=0)
        c.restoreState()

    def _page_cb(self, c, doc):
        bg = self.th["bg"]
        self._pn[0] += 1
        c.saveState()
        c.setFillColorRGB(bg[0]/255,bg[1]/255,bg[2]/255)
        c.rect(0,0,self.W,self.H,fill=1,stroke=0)
        gold = (240/255,192/255,64/255)
        c.setStrokeColorRGB(*gold)
        c.setStrokeAlpha(0.03)
        for i in range(-100,int(self.W+self.H),80):
            c.line(i,0,i+self.H,self.H)
        c.setFillColorRGB(*gold); c.setFillAlpha(0.9)
        c.rect(0,self.H-28,self.W,28,fill=1,stroke=0)
        c.rect(0,0,self.W,22,fill=1,stroke=0)
        c.setFillColorRGB(0,0,0); c.setFillAlpha(1)
        c.setFont("Helvetica-Bold",8)
        c.drawString(14,self.H-18,self.title[:55])
        c.drawRightString(self.W-14,self.H-18,f"{ORG} | {WEBSITE}")
        c.setFont("Helvetica",8)
        c.drawString(14,7,f"MI AI | By {self.author}")
        if self.pn: c.drawCentredString(self.W/2,7,f"— {self._pn[0]} —")
        c.drawRightString(self.W-14,7,self.year)
        c.restoreState()

    def _st(self):
        tc = colors.HexColor(self.th["title"])
        bc = colors.HexColor(self.th["body"])
        hc = colors.HexColor(self.th["heading"])
        ac = colors.HexColor(self.th["accent"])
        return {
            "title":    ParagraphStyle("t",fontName="Helvetica-Bold",fontSize=34,leading=42,textColor=tc,alignment=TA_CENTER,spaceAfter=10,spaceBefore=18),
            "sub":      ParagraphStyle("s",fontName="Helvetica",fontSize=16,leading=24,textColor=bc,alignment=TA_CENTER,spaceAfter=6),
            "author":   ParagraphStyle("a",fontName="Helvetica-Bold",fontSize=15,leading=22,textColor=hc,alignment=TA_CENTER,spaceAfter=5),
            "org":      ParagraphStyle("o",fontName="Helvetica",fontSize=12,leading=18,textColor=bc,alignment=TA_CENTER,spaceAfter=4),
            "desc":     ParagraphStyle("d",fontName="Helvetica-Oblique",fontSize=11,leading=17,textColor=bc,alignment=TA_CENTER,spaceAfter=10,leftIndent=20,rightIndent=20),
            "chnum":    ParagraphStyle("cn",fontName="Helvetica-Bold",fontSize=11,leading=16,textColor=hc,alignment=TA_LEFT,spaceAfter=2),
            "chtitle":  ParagraphStyle("ct",fontName="Helvetica-Bold",fontSize=24,leading=32,textColor=tc,alignment=TA_LEFT,spaceAfter=8,spaceBefore=4),
            "h2":       ParagraphStyle("h2",fontName="Helvetica-Bold",fontSize=17,leading=24,textColor=hc,alignment=TA_LEFT,spaceAfter=5,spaceBefore=9),
            "h3":       ParagraphStyle("h3",fontName="Helvetica-Bold",fontSize=13,leading=19,textColor=hc,alignment=TA_LEFT,spaceAfter=4,spaceBefore=7),
            "body":     ParagraphStyle("b",fontName="Helvetica",fontSize=11,leading=19,textColor=bc,alignment=TA_JUSTIFY,spaceAfter=5,spaceBefore=1,firstLineIndent=18),
            "bullet":   ParagraphStyle("bl",fontName="Helvetica",fontSize=10,leading=17,textColor=bc,alignment=TA_LEFT,spaceAfter=3,leftIndent=18,bulletIndent=8),
            "quote":    ParagraphStyle("q",fontName="Helvetica-Oblique",fontSize=11,leading=19,textColor=hc,alignment=TA_CENTER,spaceAfter=7,spaceBefore=7,leftIndent=28,rightIndent=28),
            "toc_h":    ParagraphStyle("th",fontName="Helvetica-Bold",fontSize=20,leading=28,textColor=tc,alignment=TA_CENTER,spaceAfter=14,spaceBefore=6),
            "toc_e":    ParagraphStyle("te",fontName="Helvetica",fontSize=11,leading=19,textColor=bc,alignment=TA_LEFT,spaceAfter=3),
            "toc_eb":   ParagraphStyle("teb",fontName="Helvetica-Bold",fontSize=11,leading=19,textColor=hc,alignment=TA_LEFT,spaceAfter=3),
            "fnote":    ParagraphStyle("fn",fontName="Helvetica",fontSize=8,leading=12,textColor=colors.HexColor("#888888"),alignment=TA_CENTER,spaceAfter=3),
        }

    def _cover(self, story, st):
        story.append(Spacer(1,1.0*cm))
        if self.cimg and os.path.exists(self.cimg):
            try:
                img = RLImage(self.cimg,width=11*cm,height=7.5*cm)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1,0.5*cm))
            except: pass
        story.append(Spacer(1,0.6*cm))
        story.append(Paragraph(self.org.upper(), st["org"]))
        story.append(HRFlowable(width="65%",thickness=1,color=colors.HexColor(self.th["heading"]),hAlign="CENTER"))
        story.append(Spacer(1,0.4*cm))
        story.append(Paragraph(self.title, st["title"]))
        story.append(Spacer(1,0.25*cm))
        story.append(HRFlowable(width="45%",thickness=2,color=colors.HexColor(self.th["accent"]),hAlign="CENTER"))
        story.append(Spacer(1,0.4*cm))
        story.append(Paragraph(f"By {self.author}", st["author"]))
        story.append(Paragraph(f"{COLLEGE} | {COURSE}", st["org"]))
        story.append(Spacer(1,0.25*cm))
        if self.desc:
            story.append(Paragraph(f'"{self.desc}"', st["desc"]))
        story.append(Spacer(1,0.6*cm))
        story.append(Paragraph(f"{self.year}  |  {WEBSITE}", st["fnote"]))
        story.append(Spacer(1,0.3*cm))
        data = [[f"  MI AI — {VERSION}  "]]
        tbl  = Table(data, colWidths=[8*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor(self.th["heading"])),
            ("TEXTCOLOR",(0,0),(-1,-1),colors.black),
            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),10),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ]))
        tbl.hAlign = "CENTER"
        story.append(tbl)
        story.append(PageBreak())

    def _toc(self, story, st):
        story.append(Spacer(1,0.5*cm))
        story.append(Paragraph("TABLE OF CONTENTS", st["toc_h"]))
        story.append(HRFlowable(width="75%",thickness=2,color=colors.HexColor(self.th["heading"]),hAlign="CENTER"))
        story.append(Spacer(1,0.5*cm))
        bg1 = colors.HexColor("#0d1030") if "dark" in self.tn or "gold" in self.tn else colors.HexColor("#f5f5f5")
        bg2 = colors.HexColor("#0a0e27") if "dark" in self.tn or "gold" in self.tn else colors.HexColor("#eeeeee")
        rows = []
        pg = 3
        for i,ch in enumerate(self.chapters,1):
            rows.append([Paragraph(f"Ch {i}",st["toc_eb"]),
                         Paragraph(ch.get("title",""),st["toc_e"]),
                         Paragraph(str(pg),st["toc_e"])])
            pg += max(1, len(ch.get("content",""))//2500+1)
        if rows:
            tbl = Table(rows, colWidths=[2.2*cm,11.5*cm,1.8*cm])
            tbl.setStyle(TableStyle([
                ("ROWBACKGROUNDS",(0,0),(-1,-1),[bg1,bg2]),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),7),
                ("LINEBELOW",(0,0),(-1,-1),0.3,colors.HexColor(self.th["accent"])),
            ]))
            story.append(tbl)
        story.append(PageBreak())

    def _chapter(self, story, st, ch, num):
        story.append(Spacer(1,0.5*cm))
        tbl = Table([[f"  CHAPTER {num}  "]], colWidths=[3.8*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor(self.th["heading"])),
            ("TEXTCOLOR",(0,0),(-1,-1),colors.black),
            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        story.append(tbl)
        story.append(Spacer(1,0.25*cm))
        story.append(Paragraph(ch.get("title",""), st["chtitle"]))
        story.append(HRFlowable(width="100%",thickness=1.5,color=colors.HexColor(self.th["accent"]),hAlign="LEFT"))
        story.append(Spacer(1,0.35*cm))
        for line in ch.get("content","").split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1,0.12*cm)); continue
            if line.startswith("## "):   story.append(Paragraph(line[3:],st["h2"]))
            elif line.startswith("### "): story.append(Paragraph(line[4:],st["h3"]))
            elif line.startswith(("- ","• ")): story.append(Paragraph(f"• {line[2:]}",st["bullet"]))
            elif line.startswith("> "): story.append(Paragraph(line[2:],st["quote"]))
            else: story.append(Paragraph(line,st["body"]))
        story.append(PageBreak())

    def build(self, out):
        os.makedirs(os.path.dirname(out) if os.path.dirname(out) else ".",exist_ok=True)
        doc = SimpleDocTemplate(out, pagesize=self.psize,
            leftMargin=1.8*cm,rightMargin=1.8*cm,topMargin=1.8*cm,bottomMargin=1.8*cm,
            title=self.title, author=self.author, creator=f"MI AI | {ORG}")
        st = self._st()
        story = []
        self._pn[0] = 0
        self._cover(story,st)
        if self.toc and self.chapters: self._toc(story,st)
        for i,ch in enumerate(self.chapters,1): self._chapter(story,st,ch,i)
        doc.build(story, onFirstPage=self._bg_cb, onLaterPages=self._page_cb)
        return len(story)//3+3

# ══════════════════════════════════════════════════════════════════════════════════
# DOWNLOAD ENGINE
# ══════════════════════════════════════════════════════════════════════════════════
class DLEngine:
    HDR = {"User-Agent":f"MI-AI-Bot/20 (+{WEBSITE})"}

    @staticmethod
    def fetch(url, fname=None):
        os.makedirs("mi_downloads",exist_ok=True)
        if not fname:
            fname = url.split("/")[-1].split("?")[0] or "file"
            if "." not in fname: fname += ".bin"
        fname = re.sub(r'[^\w.\-]','_',fname)[:80]
        path  = f"mi_downloads/{fname}"
        r = requests.get(url,headers=DLEngine.HDR,stream=True,timeout=30,allow_redirects=True)
        r.raise_for_status()
        cl = int(r.headers.get("content-length",0))
        if cl > 50*1024*1024: raise ValueError(f"File too large: {cl//1024//1024}MB (max 50MB)")
        size=0
        with open(path,"wb") as f:
            for chunk in r.iter_content(65536):
                if chunk: f.write(chunk); size+=len(chunk)
        return path, size//1024, fname

# ══════════════════════════════════════════════════════════════════════════════════
# AUTO-POST ENGINE
# ══════════════════════════════════════════════════════════════════════════════════
TOPICS = ["Islamic wisdom quote","Hadith of the day","Quran verse with reflection",
          "Dajjali system awareness","Technology in Islam","MI AI tip of the day",
          "Islamic history fact","Spiritual reminder","Imam Mahdi info","Du'a of the day"]

def auto_post_worker():
    while True:
        try:
            for chat in db.all_auto():
                cid      = chat["chat_id"]
                interval = chat.get("post_interval",3600)
                last     = chat.get("last_post","")
                topic    = chat.get("topic",random.choice(TOPICS))
                now      = datetime.now(timezone.utc)
                should   = True
                if last:
                    try:
                        ld = datetime.fromisoformat(last.replace("Z",""))
                        if (now - ld.replace(tzinfo=timezone.utc)).total_seconds() < interval:
                            should = False
                    except: pass
                if should:
                    try:
                        _do_auto_post(cid, topic)
                        db.set_chat(cid,"last_post",now.isoformat())
                        db.set_chat(cid,"topic",random.choice(TOPICS))
                    except Exception as e:
                        logger.warning(f"Auto-post {cid}: {e}")
        except Exception as e:
            logger.error(f"Auto-post worker: {e}")
        time.sleep(60)

def _do_auto_post(cid, topic):
    prompt  = (f"Write a short inspiring {topic} in Roman Urdu+English. "
               f"Max 180 words. Beautiful emojis. End with: — MI AI | Muslim Islam")
    resp, _ = NE.ask(ADMIN_ID or 1, prompt,
                     custom_sys=f"You are {BOT_NAME}. Write beautiful Islamic content.")
    styles  = ["gold_dark","ocean","green","purple","forest"]
    img_obj = ImgEng.poster(topic.upper()[:28], "MI AI | Muslim Islam", random.choice(styles))
    path    = ImgEng.save(img_obj, f"ap_{cid}_{int(time.time())}.png")
    cap     = (f"🌟 *{topic}*\n\n{resp[:750]}\n\n"
               f"━━━━━━━━━━━━\n🤖 _MI AI | {ORG}_\n🌐 _{WEBSITE}_")
    with open(path,"rb") as f:
        bot.send_photo(cid, f, caption=cap, parse_mode="Markdown")
    try: os.remove(path)
    except: pass

# ══════════════════════════════════════════════════════════════════════════════════
# TRAINING SYSTEM
# ══════════════════════════════════════════════════════════════════════════════════
INIT_TRAINING = [
    ("Tum kaun ho?",f"Main {BOT_NAME} hoon — {CREATOR} ka banaya hua advanced AI! {ORG} ki taraf se ek tohfa 🎁","identity"),
    ("Tumhara naam kya hai?",f"Mera naam {BOT_NAME} hai! M-I yani Muslim Islam. {CREATOR} ne banaya jo {COLLEGE} mein {COURSE} kar rahe hain 🌟","identity"),
    ("Tumhe kisne banaya?",f"Mujhe {CREATOR} ne banaya — {COLLEGE} | {COURSE}. Unke walid {WALID} hain. Ye {ORG} ki taraf se tohfa hai 👑","identity"),
    ("Muslim Islam kya hai?",f"Muslim Islam Organization ek Islamic educational & tech platform hai. Website: {WEBSITE}. {CREATOR} ne {BOT_NAME} banaya 🕌","identity"),
    ("PDF kaise banaun?",f"/pdf [topic] type karo — main cover image ke saath complete book generate karunga! 📚","features"),
    ("Image kaise banaun?",f"/img [topic] type karo — main Islamic art, digital art, covers sab bana sakta hoon! 🎨","features"),
    ("Download kaise karun?",f"/dl [URL] bhejo — main file download karke tumhe send karunga! Direct links support karta hoon ⬇️","features"),
    ("Kya tum group mein kaam karte ho?",f"Haan! Group mein mujhe mention karo ya reply karo — main full jawab dunga. Har message par bhi respond karta hoon 💬","features"),
]

def load_training():
    if not db.get_train(1):
        for i,o,c in INIT_TRAINING:
            db.add_train(i,o,c)
        logger.info(f"✅ {len(INIT_TRAINING)} training examples loaded.")

def trained_resp(text):
    tl = text.lower().strip()
    for t in db.get_train(150):
        if t["input"].lower().strip() in tl or tl in t["input"].lower():
            return t["output"]
    return None

# ══════════════════════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════════════════════
def main_kb(uid):
    u=db.get(uid); d=u.get("deep",0)
    kb=types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🧠 Ask AI",callback_data="ask_ai"),
           types.InlineKeyboardButton("📚 PDF Book",callback_data="menu_pdf"))
    kb.add(types.InlineKeyboardButton("🎨 Make Image",callback_data="menu_img"),
           types.InlineKeyboardButton("⬇️ Download",callback_data="menu_dl"))
    kb.add(types.InlineKeyboardButton("🔍 Web Search",callback_data="menu_search"),
           types.InlineKeyboardButton("📊 Dashboard",callback_data="view_dash"))
    kb.add(types.InlineKeyboardButton("⚙️ AI Engine",callback_data="menu_eng"),
           types.InlineKeyboardButton("🎯 Mode",callback_data="menu_mode"))
    kb.add(types.InlineKeyboardButton("🔵 Deep ON" if d else "⚪ Deep Think",callback_data="tog_deep"),
           types.InlineKeyboardButton("🗑️ Clear Memory",callback_data="clr_mem"))
    kb.add(types.InlineKeyboardButton("📢 Channel/Group",callback_data="menu_ch"),
           types.InlineKeyboardButton("🎓 Training",callback_data="menu_train"))
    kb.add(types.InlineKeyboardButton("👤 Profile",callback_data="my_prof"),
           types.InlineKeyboardButton("ℹ️ About MI AI",callback_data="about"))
    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("🛡️ Admin",callback_data="admin"))
    return kb

def eng_kb(uid):
    u=db.get(uid); e=u.get("engine","auto")
    m = lambda x: f"✅ {x}" if e==x else x
    kb=types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(f"🤖 {m('auto')} (Auto-Switch)",callback_data="se_auto"),
           types.InlineKeyboardButton(f"💎 {m('gemini')} Flash",callback_data="se_gemini"),
           types.InlineKeyboardButton(f"⚡ {m('groq')} LLaMA-3.3",callback_data="se_groq"),
           types.InlineKeyboardButton(f"🌐 {m('openrouter')} Mistral",callback_data="se_or"),
           types.InlineKeyboardButton("🔙 Back",callback_data="go_home"))
    return kb

def mode_kb():
    kb=types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("💬 Chat",callback_data="sm_chat"),
           types.InlineKeyboardButton("📚 Study",callback_data="sm_study"),
           types.InlineKeyboardButton("💻 Code",callback_data="sm_code"),
           types.InlineKeyboardButton("🔍 Search",callback_data="sm_search"),
           types.InlineKeyboardButton("🎨 Creative",callback_data="sm_creative"),
           types.InlineKeyboardButton("🕌 Islamic",callback_data="sm_islamic"),
           types.InlineKeyboardButton("🔙 Back",callback_data="go_home"))
    return kb

def pdf_kb():
    kb=types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📖 Quick PDF (Auto topic+content)",callback_data="pdf_quick"),
           types.InlineKeyboardButton("📝 Custom Book (You give topic)",callback_data="pdf_custom"),
           types.InlineKeyboardButton("🕌 Islamic Book",callback_data="pdf_islamic"),
           types.InlineKeyboardButton("📊 ICS Study Notes",callback_data="pdf_ics"),
           types.InlineKeyboardButton("🎓 Dajjali Matrix Book",callback_data="pdf_dajjal"),
           types.InlineKeyboardButton("🔙 Back",callback_data="go_home"))
    return kb

def img_kb():
    kb=types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🕌 Islamic Geometric",callback_data="img_islamic"),
           types.InlineKeyboardButton("✨ Digital Art",callback_data="img_digital"),
           types.InlineKeyboardButton("📚 Book Cover",callback_data="img_cover"),
           types.InlineKeyboardButton("📢 Channel Banner",callback_data="img_banner"),
           types.InlineKeyboardButton("🌌 Space Art",callback_data="img_space"),
           types.InlineKeyboardButton("🌿 Nature Art",callback_data="img_nature"),
           types.InlineKeyboardButton("✏️ Custom Text",callback_data="img_custom"),
           types.InlineKeyboardButton("🔙 Back",callback_data="go_home"))
    return kb

def ch_kb(cid):
    c=db.get_chat(cid); a=c.get("auto_post",0)
    kb=types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🔴 Stop Auto-Post" if a else "🟢 Start Auto-Post",callback_data=f"ch_tog_{cid}"),
           types.InlineKeyboardButton("📢 Post Text Now",callback_data=f"ch_post_{cid}"),
           types.InlineKeyboardButton("🎨 Send Image Now",callback_data=f"ch_img_{cid}"),
           types.InlineKeyboardButton("📚 Send PDF Now",callback_data=f"ch_pdf_{cid}"),
           types.InlineKeyboardButton("🏠 Main Menu",callback_data="go_home"))
    return kb

def back_kb():
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🏠 Main Menu",callback_data="go_home"))
    return kb

# ══════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════════
def uptime():
    d=datetime.now()-BOT_START; h,r=divmod(int(d.total_seconds()),3600); m,s=divmod(r,60)
    return f"{h}h {m}m {s}s"

def anim(cid, n=3):
    fs = random.sample(LOADING_FRAMES, min(n,len(LOADING_FRAMES)))
    msg = bot.send_message(cid, fs[0])
    for f in fs[1:]:
        time.sleep(0.55)
        try: bot.edit_message_text(f, cid, msg.message_id)
        except: pass
    return msg.message_id

def chunked(cid, text, pm="Markdown", reply=None):
    for i in range(0,len(text),4000):
        p=text[i:i+4000]
        try:
            if reply and i==0: bot.send_message(cid,p,parse_mode=pm,reply_to_message_id=reply)
            else: bot.send_message(cid,p,parse_mode=pm)
        except:
            try: bot.send_message(cid,p)
            except: pass

# ══════════════════════════════════════════════════════════════════════════════════
# PDF GENERATION HELPER
# ══════════════════════════════════════════════════════════════════════════════════
def gen_pdf(cid, uid, topic, theme="islamic_gold"):
    mid = anim(cid)
    try:
        bot.edit_message_text(f"📚 *AI se content generate ho raha hai...*\n_{topic}_", cid, mid, parse_mode="Markdown")
        prompt = (f"Write a complete educational book about '{topic}' in Roman Urdu+English.\n"
                  f"Include exactly 4 chapters. Format:\n"
                  f"CHAPTER: [Chapter Title]\n[3-4 detailed paragraphs]\n\n"
                  f"Make it informative, educational, use ## for sub-headings, - for bullet points.")
        resp, engine = NE.ask(uid, prompt, custom_sys=f"Expert author. Write detailed book content.")
        # Parse
        chapters=[]
        parts = re.split(r'CHAPTER:\s*', resp, flags=re.IGNORECASE)
        for pt in parts[1:]:
            lns = pt.strip().split("\n",1)
            chapters.append({"title":lns[0].strip(),"content":lns[1].strip() if len(lns)>1 else pt.strip()})
        if not chapters:
            chapters = [{"title":"Introduction","content":resp}]

        bot.edit_message_text("🎨 *Cover image ban rahi hai...*", cid, mid, parse_mode="Markdown")
        cv_img = ImgEng.cover(topic, CREATOR, ORG)
        cv_path= ImgEng.save(cv_img, f"cv_{uid}_{int(time.time())}.png")

        bot.edit_message_text("📄 *PDF format ho rahi hai...*", cid, mid, parse_mode="Markdown")
        os.makedirs("mi_books",exist_ok=True)
        pdf_path = f"mi_books/book_{uid}_{int(time.time())}.pdf"
        pe = PDFEngine({"title":topic,"author":CREATOR,"org":ORG,"year":str(datetime.now().year),
                        "desc":f"A comprehensive guide about {topic}",
                        "chapters":chapters,"theme":theme,"page_size":"A4",
                        "cover_img":cv_path,"add_toc":True,"add_pn":True})
        pages = pe.build(pdf_path)
        try: bot.delete_message(cid,mid)
        except: pass
        cap = (f"📚 *{topic}*\n\n✅ PDF ready!\n📄 ~{pages} pages\n"
               f"📚 {len(chapters)} chapters\n🧠 {engine}\n👨‍💻 _{CREATOR} | {ORG}_")
        with open(pdf_path,"rb") as f:
            bot.send_document(cid,f,caption=cap,parse_mode="Markdown",
                              visible_file_name=f"{topic.replace(' ','_')}.pdf")
        db.save_book(uid,topic,pdf_path,pages)
        try: os.remove(cv_path)
        except: pass
    except Exception as e:
        logger.error(f"gen_pdf: {e}")
        try: bot.edit_message_text(f"❌ PDF Error: {e}",cid,mid)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATION HELPER
# ══════════════════════════════════════════════════════════════════════════════════
def gen_img(cid, uid, prompt, style="digital"):
    mid = anim(cid,2)
    try:
        bot.edit_message_text(f"🎨 *Image ban rahi hai...*\n_{prompt[:40]}_", cid, mid, parse_mode="Markdown")
        if style in ["islamic","islamic_geometric"]:
            img = ImgEng.islamic(prompt[:30].upper(), BOT_NAME)
        elif style == "cover":
            img = ImgEng.cover(prompt, CREATOR)
        elif style == "banner":
            img = ImgEng.banner(prompt, BOT_NAME)
        elif style == "space":
            img = ImgEng.digital(prompt[:25].upper(), BOT_NAME, "purple")
        elif style == "nature":
            img = ImgEng.digital(prompt[:25].upper(), BOT_NAME, "forest")
        else:
            styles=["gold_dark","ocean","forest","sunset","purple","green"]
            img = ImgEng.digital(prompt[:25].upper(), BOT_NAME, random.choice(styles))
        path = ImgEng.save(img, f"img_{uid}_{int(time.time())}.png")
        try: bot.delete_message(cid,mid)
        except: pass
        with open(path,"rb") as f:
            bot.send_photo(cid,f,
                caption=f"🎨 *{prompt[:50]}*\nStyle: `{style}`\n_By {CREATOR} | {ORG}_",
                parse_mode="Markdown")
        db.save_img(uid,prompt,path,style)
        try: os.remove(path)
        except: pass
    except Exception as e:
        logger.error(f"gen_img: {e}")
        try: bot.edit_message_text(f"❌ Image error: {e}",cid,mid)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════════
# COMMANDS
# ══════════════════════════════════════════════════════════════════════════════════
@bot.message_handler(commands=["start"])
def cmd_start(m):
    uid=m.from_user.id
    db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    db.reg_chat(m.chat.id,m.chat.type,getattr(m.chat,"title","") or "")
    if m.chat.type=="private":
        bot.send_message(m.chat.id,
            f"🌟 *AS-SALAM-O-ALAIKUM {m.from_user.first_name}!* 🌟\n\n"
            f"Main *{BOT_NAME}* hoon — *{VERSION}*\n"
            f"Mujhe *{CREATOR}* ne banaya\n"
            f"🎓 *{COLLEGE}* | {COURSE}\n"
            f"👴 Walid: *{WALID}*\n"
            f"🏢 *{ORG}* | 🌐 {WEBSITE}\n\n"
            f"🎁 *Ye Muslim Islam Organization ki taraf se ek tohfa hai!*\n\n"
            f"*Features:*\n"
            f"📚 PDF books with cover images\n"
            f"🎨 Digital art & Islamic geometric art\n"
            f"⬇️ File downloads (direct links)\n"
            f"🔍 Smart web search\n"
            f"🧠 Auto-switch AI (Gemini/Groq/OpenRouter)\n"
            f"📢 Group & channel auto-posting\n"
            f"🎓 Training system\n"
            f"💾 Persistent memory & real-time data\n\n"
            f"👇 *Main menu se shuru karein:*",
            parse_mode="Markdown",reply_markup=main_kb(uid))
    else:
        bot.send_message(m.chat.id,
            f"🤖 *{BOT_NAME} ACTIVATED* in `{m.chat.type}`!\n"
            f"Mujhe mention karo ya /channel se auto-posting setup karein.",
            parse_mode="Markdown")

@bot.message_handler(commands=["menu","help"])
def cmd_menu(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    bot.send_message(m.chat.id,"🎛️ *MI AI CONTROL PANEL*\n\nOption chunein 👇",
                     parse_mode="Markdown",reply_markup=main_kb(uid))

@bot.message_handler(commands=["pdf"])
def cmd_pdf(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    args=m.text.split(None,1)
    if len(args)>1:
        threading.Thread(target=gen_pdf,args=(m.chat.id,uid,args[1].strip()),daemon=True).start()
    else:
        bot.send_message(m.chat.id,"📚 *PDF BOOK GENERATOR*\nTemplate chunein:",
                         parse_mode="Markdown",reply_markup=pdf_kb())

@bot.message_handler(commands=["img","image"])
def cmd_img(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    args=m.text.split(None,1)
    if len(args)>1:
        threading.Thread(target=gen_img,args=(m.chat.id,uid,args[1].strip()),daemon=True).start()
    else:
        bot.send_message(m.chat.id,"🎨 *IMAGE GENERATOR*\nStyle chunein:",
                         parse_mode="Markdown",reply_markup=img_kb())

@bot.message_handler(commands=["dl","download"])
def cmd_dl(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    args=m.text.split(None,1)
    if len(args)<2:
        bot.send_message(m.chat.id,"⬇️ */dl [URL]* — koi bhi direct file link bhejo!",parse_mode="Markdown"); return
    url=args[1].strip()
    mid=anim(m.chat.id,2)
    def do_dl():
        try:
            bot.edit_message_text("⬇️ Downloading...",m.chat.id,mid)
            path,size,fname=DLEngine.fetch(url)
            try: bot.delete_message(m.chat.id,mid)
            except: pass
            cap=(f"✅ *Download Complete!*\n📄 `{fname}`\n📦 `{size} KB`\n_MI AI | {ORG}_")
            ext=fname.rsplit(".",1)[-1].lower() if "." in fname else ""
            with open(path,"rb") as f:
                if ext in ["jpg","jpeg","png","gif","webp"]: bot.send_photo(m.chat.id,f,caption=cap,parse_mode="Markdown")
                elif ext in ["mp4","mov","avi"]: bot.send_video(m.chat.id,f,caption=cap,parse_mode="Markdown")
                elif ext in ["mp3","ogg","wav"]: bot.send_audio(m.chat.id,f,caption=cap,parse_mode="Markdown")
                else: bot.send_document(m.chat.id,f,caption=cap,parse_mode="Markdown",visible_file_name=fname)
            db.save_dl(uid,url,fname,size)
            try: os.remove(path)
            except: pass
        except Exception as e:
            try: bot.edit_message_text(f"❌ Download failed: {e}",m.chat.id,mid)
            except: pass
    threading.Thread(target=do_dl,daemon=True).start()

@bot.message_handler(commands=["search","s"])
def cmd_search(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    q=" ".join(m.text.split()[1:]).strip()
    if not q: bot.send_message(m.chat.id,"🔍 `/search [query]`",parse_mode="Markdown"); return
    mid=anim(m.chat.id,2)
    def do_search():
        try:
            bot.edit_message_text(f"🔍 *Searching: {q}*...",m.chat.id,mid,parse_mode="Markdown")
            with DDGS() as ddgs: results=list(ddgs.text(q,max_results=5))
            if not results: bot.edit_message_text("❌ No results.",m.chat.id,mid); return
            ctx="\n".join([f"- {r['title']}: {r['body'][:200]}" for r in results])
            ans,node=NE.ask(uid,f"Query: {q}\nData:\n{ctx}\nBest Roman Urdu+English summary.")
            src="\n".join([f"🔗 {r['title'][:45]}" for r in results[:3]])
            final=(f"🌐 *{q}*\n━━━━━━━━━━━━\n\n{ans}\n\n━━━━━━━━━━━━\n📎 *Sources:*\n{src}\n⚡ _{node}_")
            try: bot.delete_message(m.chat.id,mid)
            except: pass
            chunked(m.chat.id,final)
        except Exception as e:
            try: bot.edit_message_text(f"❌ Search error: {e}",m.chat.id,mid)
            except: pass
    threading.Thread(target=do_search,daemon=True).start()

@bot.message_handler(commands=["channel"])
def cmd_channel(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    cid=m.chat.id; db.reg_chat(cid,m.chat.type,getattr(m.chat,"title","") or "")
    c=db.get_chat(cid)
    bot.send_message(m.chat.id,
        f"📢 *CHANNEL/GROUP SETTINGS*\n\n"
        f"Chat: `{getattr(m.chat,'title','This Chat')}`\n"
        f"Auto-Post: {'🟢 ON' if c.get('auto_post') else '🔴 OFF'}\n"
        f"Topic: _{c.get('topic','Islamic wisdom')}_\n"
        f"Interval: {c.get('post_interval',3600)//60} min\n\n"
        f"Niche se manage karein 👇",
        parse_mode="Markdown",reply_markup=ch_kb(cid))

@bot.message_handler(commands=["zip"])
def cmd_zip(m):
    uid=m.from_user.id; mid=anim(m.chat.id,2)
    try:
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("bot.py",f"# {BOT_NAME} by {CREATOR} | {ORG}\n# GitHub: Run workflow for 24/7\nimport telebot,os\nbot=telebot.TeleBot(os.environ.get('BOT_TOKEN',''))\n@bot.message_handler(commands=['start'])\ndef s(m): bot.send_message(m.chat.id,f'🤖 {BOT_NAME} Active! By {CREATOR}')\nif __name__=='__main__': bot.infinity_polling()\n")
            zf.writestr("requirements.txt","pyTelegramBotAPI==4.20.0\nrequests==2.31.0\nPillow>=10.0\nreportlab>=4.0\nduckduckgo-search>=6.0\n")
            zf.writestr(".github/workflows/main.yml",f"name: \"{BOT_NAME} Bot\"\non:\n  schedule:\n    - cron: '0 */6 * * *'\n  workflow_dispatch:\njobs:\n  run:\n    runs-on: ubuntu-latest\n    timeout-minutes: 350\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.11'\n      - run: pip install -r requirements.txt\n      - run: python bot.py\n        env:\n          BOT_TOKEN: ${{{{ secrets.BOT_TOKEN }}}}\n          GEMINI_API_KEY: ${{{{ secrets.GEMINI_API_KEY }}}}\n          GROQ_API_KEY: ${{{{ secrets.GROQ_API_KEY }}}}\n")
            zf.writestr("README.md",f"# {BOT_NAME}\nBy **{CREATOR}** | {ORG}\n\n## Deploy on GitHub Actions\n1. Fork this repo\n2. Add secrets: BOT_TOKEN, GEMINI_API_KEY, GROQ_API_KEY\n3. Actions → Run workflow\n4. Bot runs 24/7!\n")
        buf.seek(0)
        try: bot.delete_message(m.chat.id,mid)
        except: pass
        bot.send_document(m.chat.id,buf,
                          caption=f"📦 *{BOT_NAME} Project ZIP*\n\n• bot.py\n• requirements.txt\n• .github/workflows/main.yml\n• README.md\n\n_By {CREATOR} | {ORG}_",
                          visible_file_name="MI_AI_Project.zip",parse_mode="Markdown")
    except Exception as e:
        try: bot.edit_message_text(f"❌ ZIP error: {e}",m.chat.id,mid)
        except: pass

@bot.message_handler(commands=["dashboard","stats"])
def cmd_dash(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    msg=bot.send_message(m.chat.id,"⏳ Loading live dashboard...")
    def run():
        for tick in range(72):
            try:
                s=db.stats(); u=db.get(uid)
                text=(f"╔═════════════════════════╗\n"
                      f"║  📊 MI AI LIVE DASHBOARD  ║\n"
                      f"╚═════════════════════════╝\n\n"
                      f"🕐 `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}`\n"
                      f"⏱️ Uptime: `{uptime()}`\n\n"
                      f"👥 Users: `{s['users']}`\n"
                      f"💬 Messages: `{s['msgs']}`\n"
                      f"📡 Chats: `{s['chats']}`\n"
                      f"📚 Books: `{s['books']}`\n"
                      f"🎨 Images: `{s['images']}`\n"
                      f"⬇️ Downloads: `{s['dls']}`\n\n"
                      f"─────────────────────────\n"
                      f"👤 *Your Stats:*\n"
                      f"🔑 Engine: `{u.get('engine','auto').upper()}`\n"
                      f"🎯 Mode: `{u.get('mode','chat').upper()}`\n"
                      f"📊 Queries: `{u.get('queries',0)}`\n\n"
                      f"🏢 _{ORG}_\n👨‍💻 _{CREATOR}_\n_Tick #{tick+1}_")
                bot.edit_message_text(text,m.chat.id,msg.message_id,parse_mode="Markdown",reply_markup=back_kb())
            except: pass
            time.sleep(5)
    threading.Thread(target=run,daemon=True).start()

@bot.message_handler(commands=["train"])
def cmd_train(m):
    if m.from_user.id!=ADMIN_ID: bot.send_message(m.chat.id,"🚫 Admin only!"); return
    bot.send_message(m.chat.id,
        "🎓 *TRAINING MODE*\n\nFormat:\n`INPUT|||OUTPUT|||CATEGORY`\n\n"
        "Example:\n`Tum kaun ho?|||Main MI AI hoon!|||identity`",
        parse_mode="Markdown")
    bot.register_next_step_handler(m, lambda msg: _proc_train(msg))

def _proc_train(m):
    try:
        p=m.text.split("|||")
        if len(p)<2: bot.send_message(m.chat.id,"❌ Format galat!"); return
        db.add_train(p[0].strip(), p[1].strip(), p[2].strip() if len(p)>2 else "general")
        bot.send_message(m.chat.id,f"✅ *Trained!*\n📥 `{p[0][:40]}`\n📤 `{p[1][:40]}`",parse_mode="Markdown")
    except Exception as e:
        bot.send_message(m.chat.id,f"❌ {e}")

@bot.message_handler(commands=["clear"])
def cmd_clear(m):
    uid=m.from_user.id; db.clear_mem(uid)
    bot.send_message(m.chat.id,"🗑️ *Memory cleared! Fresh start* 🚀",parse_mode="Markdown",reply_markup=main_kb(uid))

@bot.message_handler(commands=["profile"])
def cmd_profile(m):
    uid=m.from_user.id; db.sync(uid,m.from_user.first_name,m.from_user.username or ""); u=db.get(uid)
    bot.send_message(m.chat.id,
        f"👤 *PROFILE — MI AI*\n\n🆔 `{uid}`\n👤 {u.get('name','?')}\n"
        f"🔑 Engine: `{u.get('engine','auto')}`\n🎯 Mode: `{u.get('mode','chat')}`\n"
        f"🧠 Deep: `{'ON' if u.get('deep') else 'OFF'}`\n📊 Queries: `{u.get('queries',0)}`",
        parse_mode="Markdown",reply_markup=back_kb())

# ══════════════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid=c.from_user.id; d=c.data; cid=c.message.chat.id; mid=c.message.message_id
    db.sync(uid,c.from_user.first_name,c.from_user.username or "")
    try:
        if d=="go_home":
            bot.edit_message_text("🎛️ *MI AI CONTROL PANEL*\nOption chunein 👇",cid,mid,parse_mode="Markdown",reply_markup=main_kb(uid))
        elif d=="ask_ai":
            bot.answer_callback_query(c.id,"Apna sawal type karein!")
            bot.send_message(cid,"🧠 *Apna sawal likhein:*",parse_mode="Markdown",reply_markup=back_kb())
        elif d=="menu_pdf":
            bot.edit_message_text("📚 *PDF BOOK GENERATOR*\nTemplate chunein:",cid,mid,parse_mode="Markdown",reply_markup=pdf_kb())
        elif d in ["pdf_quick","pdf_islamic","pdf_ics","pdf_dajjal"]:
            topics={"pdf_quick":"MI AI Complete Guide","pdf_islamic":"Dajjali Matrix Roman Urdu",
                    "pdf_ics":"ICS Statistics Study Notes","pdf_dajjal":"Dajjal aur Aakhiri Zamana"}
            t=topics[d]
            bot.answer_callback_query(c.id,f"Generating: {t}...")
            threading.Thread(target=gen_pdf,args=(cid,uid,t),daemon=True).start()
        elif d=="pdf_custom":
            bot.answer_callback_query(c.id)
            bot.send_message(cid,"📝 *Book title likhein:*",parse_mode="Markdown")
            bot.register_next_step_handler(c.message,lambda m: threading.Thread(target=gen_pdf,args=(m.chat.id,uid,m.text.strip()),daemon=True).start())
        elif d=="menu_img":
            bot.edit_message_text("🎨 *IMAGE GENERATOR*\nStyle chunein:",cid,mid,parse_mode="Markdown",reply_markup=img_kb())
        elif d.startswith("img_"):
            style=d[4:]
            labels={"islamic":"Islamic Geometric Art","digital":"Digital Art","cover":"Book Cover",
                    "banner":"Channel Banner","space":"Space Art","nature":"Nature Art"}
            if style=="custom":
                bot.send_message(cid,"✏️ *Image topic likhein:*",parse_mode="Markdown")
                bot.register_next_step_handler(c.message,lambda m: threading.Thread(target=gen_img,args=(m.chat.id,uid,m.text.strip()),daemon=True).start())
            else:
                p=labels.get(style,"MI AI Art")
                threading.Thread(target=gen_img,args=(cid,uid,p,style),daemon=True).start()
            bot.answer_callback_query(c.id,"Image ban rahi hai...")
        elif d=="menu_dl":
            bot.answer_callback_query(c.id)
            bot.send_message(cid,"⬇️ *URL bhejo:*\n`/dl [URL]`",parse_mode="Markdown",reply_markup=back_kb())
        elif d=="menu_search":
            bot.answer_callback_query(c.id)
            bot.send_message(cid,"🔍 *Search query likhein:*",parse_mode="Markdown",reply_markup=back_kb())
            bot.register_next_step_handler(c.message,lambda m: setattr(m,"text",f"/search {m.text}") or cmd_search(m))
        elif d=="view_dash":
            bot.answer_callback_query(c.id,"Dashboard loading...")
            msg=bot.edit_message_text("⏳ Loading...",cid,mid)
            def run():
                for tick in range(72):
                    try:
                        s=db.stats(); u2=db.get(uid)
                        text=(f"╔═════════════════════╗\n║  📊 MI AI DASHBOARD  ║\n╚═════════════════════╝\n\n"
                              f"🕐 `{datetime.now(timezone.utc).strftime('%H:%M UTC')}`\n⏱️ `{uptime()}`\n\n"
                              f"👥 `{s['users']}` users  |  💬 `{s['msgs']}` msgs\n"
                              f"📚 `{s['books']}` books  |  🎨 `{s['images']}` imgs\n"
                              f"⬇️ `{s['dls']}` downloads\n\n"
                              f"🔑 Engine: `{u2.get('engine','auto')}`\n📊 Queries: `{u2.get('queries',0)}`\n"
                              f"_Tick #{tick+1}_")
                        bot.edit_message_text(text,cid,mid,parse_mode="Markdown",reply_markup=back_kb())
                    except: pass
                    time.sleep(5)
            threading.Thread(target=run,daemon=True).start()
        elif d=="menu_eng":
            bot.edit_message_text("⚙️ *AI ENGINE SELECT*",cid,mid,parse_mode="Markdown",reply_markup=eng_kb(uid))
        elif d.startswith("se_"):
            eng={"se_auto":"auto","se_gemini":"gemini","se_groq":"groq","se_or":"openrouter"}.get(d,"auto")
            db.upd(uid,"engine",eng); bot.answer_callback_query(c.id,f"✅ {eng.upper()}!")
            bot.edit_message_reply_markup(cid,mid,reply_markup=eng_kb(uid))
        elif d=="menu_mode":
            bot.edit_message_text("🎯 *MODE SELECT*",cid,mid,parse_mode="Markdown",reply_markup=mode_kb())
        elif d.startswith("sm_"):
            mode=d[3:]; db.upd(uid,"mode",mode)
            bot.answer_callback_query(c.id,f"✅ {mode.upper()} mode!")
            bot.edit_message_text(f"✅ *Mode: {mode.upper()}*\n\nMain menu 👇",cid,mid,parse_mode="Markdown",reply_markup=main_kb(uid))
        elif d=="tog_deep":
            u=db.get(uid); nv=0 if u.get("deep") else 1; db.upd(uid,"deep",nv)
            bot.answer_callback_query(c.id,f"Deep Think: {'ON' if nv else 'OFF'}")
            bot.edit_message_reply_markup(cid,mid,reply_markup=main_kb(uid))
        elif d=="clr_mem":
            db.clear_mem(uid); bot.answer_callback_query(c.id,"🗑️ Cleared!")
            bot.edit_message_text("✅ *Memory cleared!* 🚀",cid,mid,parse_mode="Markdown",reply_markup=main_kb(uid))
        elif d=="menu_ch":
            bot.answer_callback_query(c.id)
            c2=db.get_chat(cid)
            bot.edit_message_text(
                f"📢 *CHANNEL/GROUP*\nAuto-Post: {'🟢 ON' if c2.get('auto_post') else '🔴 OFF'}\nTopic: _{c2.get('topic','?')}_",
                cid,mid,parse_mode="Markdown",reply_markup=ch_kb(cid))
        elif d.startswith("ch_tog_"):
            tcid=int(d.split("_")[-1]); c2=db.get_chat(tcid)
            nv=0 if c2.get("auto_post") else 1; db.set_chat(tcid,"auto_post",nv)
            bot.answer_callback_query(c.id,f"Auto-post: {'ON' if nv else 'OFF'}")
            bot.edit_message_reply_markup(cid,mid,reply_markup=ch_kb(tcid))
        elif d.startswith("ch_post_"):
            tcid=int(d.split("_")[-1]); bot.answer_callback_query(c.id,"Posting...")
            topic=db.get_chat(tcid).get("topic",random.choice(TOPICS))
            threading.Thread(target=_do_auto_post,args=(tcid,topic),daemon=True).start()
        elif d.startswith("ch_img_"):
            tcid=int(d.split("_")[-1]); bot.answer_callback_query(c.id,"Image sending...")
            def si():
                img=ImgEng.islamic("MI AI",ORG); path=ImgEng.save(img,f"ch_{int(time.time())}.png")
                try:
                    with open(path,"rb") as f:
                        bot.send_photo(tcid,f,caption=f"🌟 *{BOT_NAME}*\n_{ORG}_\n🌐 {WEBSITE}",parse_mode="Markdown")
                finally:
                    try: os.remove(path)
                    except: pass
            threading.Thread(target=si,daemon=True).start()
        elif d.startswith("ch_pdf_"):
            tcid=int(d.split("_")[-1]); bot.answer_callback_query(c.id,"PDF sending...")
            threading.Thread(target=gen_pdf,args=(tcid,uid,"Islamic Wisdom Guide"),daemon=True).start()
        elif d=="menu_train":
            data=db.get_train(5)
            txt="🎓 *TRAINING DATA*\n\n"
            if data:
                for t in data[:5]: txt+=f"📥 _{t['input'][:40]}_\n📤 {t['output'][:40]}\n\n"
            else: txt+="Koi data nahi. /train se add karein."
            bot.edit_message_text(txt,cid,mid,parse_mode="Markdown",reply_markup=back_kb())
        elif d=="my_prof":
            u=db.get(uid)
            bot.edit_message_text(
                f"👤 *PROFILE*\n\n🆔 `{uid}`\n👤 {u.get('name','?')}\n"
                f"🔑 `{u.get('engine','auto')}`  🎯 `{u.get('mode','chat')}`\n📊 `{u.get('queries',0)}` queries",
                cid,mid,parse_mode="Markdown",reply_markup=back_kb())
        elif d=="about":
            bot.edit_message_text(
                f"ℹ️ *ABOUT {BOT_NAME}*\n\n"
                f"📌 Version: `{VERSION}`\n"
                f"👨‍💻 Creator: *{CREATOR}*\n"
                f"🎓 *{COLLEGE}*\n"
                f"📚 {COURSE}\n"
                f"👴 Walid: *{WALID}*\n"
                f"🏢 *{ORG}*\n"
                f"🌐 `{WEBSITE}`\n\n"
                f"🎁 _Muslim Islam ki taraf se ek tohfa!_\n"
                f"🤖 AI: Gemini + Groq + OpenRouter\n"
                f"📚 PDF: ReportLab + PIL\n"
                f"🎨 Images: PIL Digital Art",
                cid,mid,parse_mode="Markdown",reply_markup=back_kb())
        elif d=="admin" and uid==ADMIN_ID:
            s=db.stats()
            bot.edit_message_text(
                f"🛡️ *ADMIN*\n\n👥 `{s['users']}` users\n💬 `{s['msgs']}` msgs\n"
                f"📚 `{s['books']}` books\n🎨 `{s['images']}` imgs\n⬇️ `{s['dls']}` dls\n⏱️ `{uptime()}`",
                cid,mid,parse_mode="Markdown",reply_markup=back_kb())
        else:
            bot.answer_callback_query(c.id,"⚙️ Processing...")
    except Exception as e:
        logger.error(f"CB [{d}]: {e}")
        try: bot.answer_callback_query(c.id,"❌ Error, retry karein.")
        except: pass

# ══════════════════════════════════════════════════════════════════════════════════
# UNIVERSAL MESSAGE HANDLER
# ══════════════════════════════════════════════════════════════════════════════════
@bot.message_handler(content_types=["text","photo","video","document","audio","voice"])
def universal(m):
    uid=m.from_user.id if m.from_user else 0
    cid=m.chat.id; ctype=m.chat.type
    text=m.text or m.caption or "[Media]"
    if m.from_user: db.sync(uid,m.from_user.first_name,m.from_user.username or "")
    db.reg_chat(cid,ctype,getattr(m.chat,"title","") or "")
    if text.startswith("/"): return
    u=db.get(uid)

    if ctype=="channel": return

    if ctype in ["group","supergroup"]:
        try:
            bi=bot.get_me()
            is_reply = m.reply_to_message and m.reply_to_message.from_user and m.reply_to_message.from_user.id==bi.id
            is_mention = (bi.username or "").lower() in text.lower() or "mi ai" in text.lower()
            if is_reply or is_mention:
                bot.send_chat_action(cid,"typing")
                ans,node=NE.ask(uid,text,custom_sys=f"You are {BOT_NAME}. Brief helpful Roman Urdu reply.")
                chunked(cid,f"🤖 {ans}\n\n⚡ _{node}_",reply=m.message_id)
            else:
                bot.send_chat_action(cid,"typing")
                ans,_=NE.ask(uid,text,custom_sys=f"You are {BOT_NAME}. 1-2 line witty Roman Urdu reaction.")
                try: bot.reply_to(m,ans)
                except: pass
        except Exception as e: logger.error(f"Group: {e}")
        return

    if ctype=="private":
        tr=trained_resp(text)
        if tr: bot.send_message(cid,tr,reply_markup=main_kb(uid)); return
        mode=u.get("mode","chat")
        bot.send_chat_action(cid,"typing")
        mid=anim(cid,3)
        try:
            if mode=="search":
                with DDGS() as ddgs: res=list(ddgs.text(text,max_results=4))
                ctx="\n".join([f"- {r['title']}: {r['body'][:200]}" for r in res]) if res else ""
                ans,node=NE.ask(uid,f"Query:{text}\nData:\n{ctx}")
                final=f"🌐 *SEARCH*\n\n{ans}\n\n⚡ _{node}_"
            elif mode=="study":
                ans,node=NE.ask(uid,text,custom_sys=f"Expert tutor. Detailed step-by-step Roman Urdu+English with examples.")
                final=f"📚 *STUDY*\n\n{ans}\n\n⚡ _{node}_"
            elif mode=="code":
                ans,node=NE.ask(uid,text,custom_sys=f"Expert developer. Code with Roman Urdu comments.")
                final=f"💻 *CODE*\n\n{ans}\n\n⚡ _{node}_"
            elif mode=="creative":
                ans,node=NE.ask(uid,text,custom_sys=f"Creative writer. Poetic Roman Urdu response.")
                final=f"🎨 *CREATIVE*\n\n{ans}\n\n⚡ _{node}_"
            elif mode=="islamic":
                ans,node=NE.ask(uid,text,custom_sys=f"Islamic scholar. Answer with Quran/Hadith in Roman Urdu.")
                final=f"🕌 *ISLAMIC*\n\n{ans}\n\n⚡ _{node}_"
            else:
                ans,node=NE.ask(uid,text)
                final=f"{ans}\n\n━━━━━━━━━━━━\n🧠 _{node}_ | 🏢 _{ORG}_"
            try: bot.delete_message(cid,mid)
            except: pass
            chunked(cid,final)
        except Exception as e:
            logger.error(f"Private: {e}")
            try: bot.edit_message_text(f"❌ Error: {e}",cid,mid)
            except: pass

# ══════════════════════════════════════════════════════════════════════════════════
# BOOT
# ══════════════════════════════════════════════════════════════════════════════════
def boot():
    print("\n"+"═"*65)
    print(f"  🤖  {BOT_NAME} — {VERSION}")
    print(f"  👨‍💻  {CREATOR}  |  {COLLEGE}")
    print(f"  📚  {COURSE}  |  Walid: {WALID}")
    print(f"  🏢  {ORG}  |  🌐 {WEBSITE}")
    print(f"  🕒  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("─"*65)
    print("  ✅  PDF Engine   : ReportLab + PIL Cover")
    print("  ✅  Image Engine : PIL Digital Art + Islamic")
    print("  ✅  AI Engine    : Auto-Switch Gemini→Groq→OpenRouter")
    print("  ✅  Download     : Direct file fetcher")
    print("  ✅  Auto-Post    : Groups & Channels")
    print("  ✅  Training     : Custom response system")
    print("  ✅  Dashboard    : Live real-time")
    print("═"*65+"\n")
    load_training()
    threading.Thread(target=auto_post_worker,daemon=True).start()
    logger.info("🚀 Auto-post worker started.")

if __name__=="__main__":
    boot()
    while True:
        try:
            logger.info("🚀 Starting infinity_polling...")
            bot.infinity_polling(timeout=90,long_polling_timeout=90,logger_level=logging.WARNING)
        except Exception as e:
            logger.critical(f"CRASH: {e}")
            time.sleep(5)

# END — MI AI | By Muaaz Iqbal | Muslim Islam Organization | MiTV Network
