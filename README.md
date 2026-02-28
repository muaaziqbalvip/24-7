# 24-7
THIS REPOSTRI AS A SOFTWER LIVE YOUTUBE STREAM.
# 📺 MiTV Network - 24/7 Professional Live Stream Engine
### 🚀 Developed by: Muaaz Iqbal | ICS Computer Science 
#### 🏛️ Institution: Govt Islamia Graduate College

---

## 🌟 Project Overview
**MiTV Network** ek advance, cloud-based broadcasting system hai jo **GitHub Actions** ki taqat ko istemal karte hue YouTube par **24/7 Live Streaming** faraham karta hai. Yeh system sirf video nahi chalata, balkay ye real-time data overlays aur automated management ke sath aata hai.

> **Note:** Yeh project khas tor par ICS level ke advanced logic aur Python-FFMPEG integration ko mad-de-nazar rakh kar banaya gaya hai.

---

## 🔥 Key Features

* **⚡ 24/7 Persistent Stream:** GitHub Actions ki 6-hour limit ko bypass karne ke liye automatic re-triggering logic.
* **🖼️ Dynamic Visual Overlays:**
    * **Fixed Logo:** Stream ke top-left corner par professional branding.
    * **Live PKT Clock:** Pakistan Time Zone ke mutabiq digital clock.
    * **Live Date:** Animated date box jo har roz auto-update hota hai.
* **📡 Real-Time Firebase Integration:** Database project `ramadan-2385b` se live text fetch kar ke bottom patti par display karna.
* **🎨 Customizable UI:** GitHub Workflow se hi patti ka color aur visibility control karne ki saholat.
* **🔄 Smart Looping & Fallback:** * Video links (mp4, m3u8, mkv, mpd) ka infinite loop.
    * Agar video link na ho, to Logo ko hi background bana kar audio stream karna.
    * Audio priority logic (External audio vs Video audio).

---

## 🛠️ Technical Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Core Engine** | FFMPEG (High Performance) |
| **Automation** | GitHub Actions (CI/CD) |
| **Real-time DB** | Firebase (Google Cloud) |
| **Timezone** | Pytz (Asia/Karachi) |

---

## 🚀 How to Setup

### 1. Repository Preparation
Is repository mein niche di gayi files ka hona zaroori hai:
* `stream_engine.py` (Main Python Logic)
* `logo.png` (Aapka Channel Logo)
* `requirements.txt` (Dependencies)

### 2. GitHub Secrets Setup
Apni repository ki **Settings > Secrets and Variables > Actions** mein jayein aur naya secret add karein:
* **Name:** `FIREBASE_CONFIG`
* **Value:** Aapka Firebase Admin JSON ya config data.

### 3. Launching the Stream
1.  GitHub ke **Actions** tab par jayein.
2.  **"MiTV 24/7 Stream Engine"** select karein.
3.  **"Run workflow"** par click karein.
4.  Apna `Stream Key`, `Video Link`, aur `Audio Link` enter karein aur **Run** kar dein!

---

## 📊 Error Handling & Stability
Yeh system **"Zero-Downtime"** logic par chalta hai. 
* **Buffer Logic:** FFMPEG logs ko musalsal monitor karta hai.
* **Atomic File Writes:** Firebase se data fetch karte waqt temporary files use hoti hain taake stream mein jhatka (glitch) na aaye.
* **Auto-Reconnect:** Internet ya link break hone par 5 seconds mein auto-reconnect.

---

## 👨‍💻 About the Developer
**Muaaz Iqbal** ek pur-azm computer science student hain jo technology aur automation ke zariye naye solutions nikalne mein maharat rakhte hain.
* **Born:** 28th Nov 2009
* **Father:** Zafar Iqbal
* **Current Project:** MiTV Network Infrastructure

---
© 2026 MiTV Network | All Rights Reserved.

