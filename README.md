# Media Downloader Pro - v2.2 Turbo (PC App)

A modern, ultra-cool, and fully responsive desktop application for Windows to download **YouTube videos**, **Shorts**, **TikToks (Without Watermark)**, and **Full Playlists** (download all 20+ videos in an organized folder with one click) at maximum speeds with zero ads.

---

## ✨ Features & Capabilities

### 📱 TikTok Watermark-Free Downloader
- **Pure Clean Video**: Downloads TikTok videos directly from the original CDN stream without any floating or bouncing TikTok logos or watermarks.
- **Audio Extraction**: Option to extract the pure original background sound or song as high-quality MP3.
- **All TikTok Link Formats Supported**: Works with `tiktok.com/@user/video/...`, `vm.tiktok.com`, `vt.tiktok.com`, `tiktok.com/t/...`, and mobile share links.

### 📑 Full Playlist Downloader (Batch List Download)
- **Automatic Playlist Detection**: Paste any YouTube playlist link (`playlist?list=...` or video watch link inside a playlist), and the app loads the entire list of videos in seconds!
- **Interactive Video Selector**:
  - Displays all videos in a scrollable checklist with title, duration, and track numbers.
  - Choose to download all 20+ videos, or select/deselect individual tracks with one click.
  - Quick **"☑ Select All"** and **"☐ Deselect All"** buttons.
- **Auto Subfolder Organization**: Automatically creates a dedicated subfolder named after the playlist (e.g. `Downloads/YouTube Downloads/My Playlist Name/`) and numbers files sequentially (`01 - Title.mp4`, `02 - Title.mp4`) so they stay perfectly ordered in Windows Explorer and music players!
- **Dual Telemetry HUD for Playlists**: Displays both overall playlist progress (e.g. `Video 3 of 20 (15%)`) and active video download speed, transferred bytes, and ETA.

### ⚡ Automatic Instant Fetch (No Fetch Button Needed!)
- **Zero-Click Video Loading**: Simply paste any YouTube, TikTok, or Playlist link (`Ctrl+V` or click **"📋 Paste Link"**), or copy a link in your web browser — the app validates and loads the details **automatically** without requiring a manual "Fetch" button!
- **Real-Time Clipboard Detection**: Detects supported media links copied while browsing and surfaces an instant 1-click auto-fill toast banner.

### 🖥️ Optimized for ANY Screen Resolution
- **Universal Display Compatibility**: Responsive design that looks gorgeous on standard laptops (`1366x768`), Full HD (`1920x1080`), 2K (`2560x1440`), Ultra-Wide displays (`2752x1152`), and 4K monitors.
- **Dynamic Text Wrapping & Scaling**: Title and metadata labels dynamically adapt their wrapping to the exact window width in real time without awkward overflow or truncation.
- **Responsive 16:9 Thumbnail Engine**: Maintains crisp 16:9 aspect ratio and scales smoothly as the window resizes.
- **Adjustable UI Scaling**: Includes built-in interface scaling (`85% Compact`, `100% Standard`, `115% Comfortable`, `125% Large`) in Settings for complete DPI personalization.

### 🎨 Modern Studio UI Architecture
- **Sleek Navigation Rail**: Switch effortlessly between **⚡ Downloader**, **🕒 Library & History**, and **⚙️ Settings & Tools**.
- **Dark & Light Mode**: Fluid transition between deep dark theme and crisp modern light theme.
- **Quick 1-Click Preset Pills**: Instantly select common configurations with one click:
  - `[ 🌟 Max Quality ]` (Up to 4K UHD 60fps)
  - `[ 1080p FHD ]` (Full HD 1080p)
  - `[ 720p HD ]` (Standard HD)
  - `[ 🎵 MP3 320k ]` (Extreme Studio Hi-Fi Audio)
- **Real-Time 4-Card Telemetry HUD**: Live status indicator, network speed in MB/s, transferred bytes vs. estimated total, and ETA countdown.
- **Persistent Downloads Library**: Automatically saves download records across sessions in `history.json` with live search, file size verification, and direct play/reveal buttons.

---

## 🚀 Quick Start (Running the App)

### Option 1: Standalone Executable (No Python Required!)
Double-click **`Launch_App.bat`** or launch directly:
```
dist\YouTubeDownloader\YouTubeDownloader.exe
```

### Option 2: Run via Python
Double-click **`run_app.bat`** or execute in terminal:
```bash
python main.py
```

---

## 🛠 Project Structure

```
Youtube video dowonloader/
│
├── bin/
│   └── ffmpeg.exe         # High-performance FFmpeg binary for audio/video merging
├── app.py                 # Modern CustomTkinter GUI (v2.2 Turbo)
├── downloader.py          # Backend engine supporting YouTube, TikTok & Playlists
├── main.py                # Main launcher
├── run_app.bat            # Windows Python launcher
├── Launch_App.bat         # Direct executable launcher
├── build_exe.py           # Standalone executable compiler script
├── build_exe.bat          # Double-click PyInstaller build script
├── requirements.txt       # Dependencies (customtkinter, yt-dlp, pillow, etc.)
├── icon.ico               # Windows desktop icon
├── settings.json          # Persistent user preferences & scaling
├── history.json           # Persistent download library records
└── README.md              # Complete documentation
```

---

## 🔑 Subscription & Licensing System (Commercial Distribution)

Media Downloader Pro comes with a complete **Subscription & Licensing Backend** built to sell the product to customers safely with Hardware-ID (HWID) binding, cryptographic tamper protection, and subscription expiration.

### 💼 How to Generate Keys (For Seller / Admin)

You can generate license keys using either the **Interactive Desktop GUI**, the **Web Admin Dashboard**, or the **Command Line**.

#### 1. Instant Desktop Key Manager (Recommended):
Double-click:
```
License_Manager.bat
```
- **Generate Keys**: Select plan (**Monthly**, **Annual**, or **Lifetime**), enter customer name, and click **"⚡ Generate Pro License Key"**.
- **📋 Copy Key**: Instantly copy any issued license key to your clipboard.
- **🚫 Terminate License**: Click **"Terminate"** on any customer's license to immediately revoke access, unbind all their machines, and disable their Pro features!
- **↺ Restore License**: Un-revoke and restore access if an issue is resolved.
- **🗑️ Delete Key**: Permanently delete any key record from the database.

#### 2. Web Admin Dashboard:
1. Double-click **`backend\run_server.bat`** (or run `python backend/server.py`).
2. Open browser: **`http://localhost:5000/admin`**
3. View active subscribers, devices bound, expiration dates, generate new keys, and revoke keys with 1 click.

#### 3. Command Line Generator:
```bash
# Generate a Lifetime Key:
python license_admin.py --generate --plan pro_lifetime --customer "Customer Name"

# Generate an Annual Key:
python license_admin.py --generate --plan pro_yearly --customer "Customer Name"

# Generate a Monthly Key:
python license_admin.py --generate --plan pro_monthly --customer "Customer Name"

# List all active licenses and device activations:
python license_admin.py --list
```

---

## 🛒 What to Give to Customers When You Sell:

1. **Send the Installer**:
   Give them the single installation file from the `Setup\` folder:
   ```
   Setup\MediaDownloaderPro_Setup.exe  (or Setup\Setup.exe)
   ```
2. **Send Their Pro Key**:
   Provide the generated license key (e.g. `MDP-LFT-72C8-DLMH-FWZF`).

### 📱 How Customers Activate Their Pro Key:
1. The customer runs the installer and opens **Media Downloader Pro**.
2. Click **"⭐ Activate Pro"** in the top header, sidebar, or Settings tab.
3. Paste their Pro License Key into the box and click **"⚡ Activate Pro License"**.
4. The app verifies the key, locks it to their physical PC (HWID), and immediately unlocks **4K Ultra HD**, **Unlimited Playlist Downloads**, and **Multi-Thread Acceleration**!
5. **PC Transfer**: If the customer buys a new PC, they can open *Settings -> Subscription & License* and click **"🔌 Deactivate / Transfer PC"** to safely migrate their key to their new machine.

---

## 📦 How to Re-compile the Standalone Executable & Installer

### Step 1: Compile Executable (.exe)
```bash
python build_exe.py
# or double-click: build_exe.bat
```

### Step 2: Compile Single Setup Installer
```bash
python build_setup.py
# or double-click: Build_Setup_Installer.bat
```
Output single installer: **`Setup\MediaDownloaderPro_Setup.exe`**.
