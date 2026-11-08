import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD_LATEST_GDRIVE = "https://drive.google.com/file/d/1WPsoALq5xDoEnGVAl0-ALGYkp_Ww3fp0/view?usp=sharing"
OLD_V100_GDRIVE = "https://drive.google.com/file/d/1qCbln3MrCcKbd_eNP3jFBlhDlpn4uhas/view?usp=sharing"

NEW_LATEST_GITHUB = "https://github.com/chathufer/Web-11-05-2026/releases/download/v1.0.1/MediaDownloaderPro_Setup.exe"
NEW_V100_GITHUB = "https://github.com/chathufer/Web-11-05-2026/releases/download/v1.0.0/MediaDownloaderPro_Setup.exe"

print(f"Base Directory: {BASE_DIR}")

# 1. Update releases.json in all target locations
updated_releases = [
    {
        "version": "v1.0.1",
        "date": "2026-11-06",
        "date_formatted": "Nov 06, 2026",
        "title": "Media Downloader Pro Turbo Update",
        "is_latest": True,
        "url": NEW_LATEST_GITHUB,
        "size": "57.8 MB",
        "notes": "Latest updated release: Streamlined 4K 60FPS video downloading, TikTok watermark-free extraction, persistent 7-day trial engine, and human-friendly error messages."
    },
    {
        "version": "v1.0.0",
        "date": "2026-11-06",
        "date_formatted": "Nov 06, 2026",
        "title": "Media Downloader Pro Official Launch",
        "is_latest": False,
        "url": NEW_V100_GITHUB,
        "size": "57.0 MB",
        "notes": "First official release of Media Downloader Pro: 4K 60FPS video downloads, TikTok watermark-free extractor, lossless MP3 conversion, playlist batching, and single-file Windows installer."
    }
]

release_files = [
    os.path.join(BASE_DIR, "releases.json"),
    os.path.join(BASE_DIR, "public", "releases.json"),
    os.path.join(BASE_DIR, "deploy_vercel", "releases.json"),
    os.path.join(BASE_DIR, "deploy_vercel", "public", "releases.json"),
]

for rf in release_files:
    if os.path.exists(rf):
        with open(rf, "w", encoding="utf-8", newline="\n") as f:
            json.dump(updated_releases, f, indent=2)
            f.write("\n")
        print(f"[OK] Updated {os.path.relpath(rf, BASE_DIR)}")

# 2. Update vercel.json in all locations
vercel_files = [
    os.path.join(BASE_DIR, "vercel.json"),
    os.path.join(BASE_DIR, "deploy_vercel", "vercel.json"),
]

for vf in vercel_files:
    if os.path.exists(vf):
        with open(vf, "r", encoding="utf-8") as f:
            v_content = f.read()
        v_content = v_content.replace(OLD_LATEST_GDRIVE, NEW_LATEST_GITHUB)
        with open(vf, "w", encoding="utf-8", newline="\n") as f:
            f.write(v_content)
        print(f"[OK] Updated {os.path.relpath(vf, BASE_DIR)}")

# 3. Update backend/server.py in all locations
server_files = [
    os.path.join(BASE_DIR, "backend", "server.py"),
    os.path.join(BASE_DIR, "deploy_vercel", "backend", "server.py"),
]

for sf in server_files:
    if os.path.exists(sf):
        with open(sf, "r", encoding="utf-8") as f:
            s_content = f.read()
        s_content = s_content.replace(OLD_LATEST_GDRIVE, NEW_LATEST_GITHUB)
        s_content = s_content.replace(OLD_V100_GDRIVE, NEW_V100_GITHUB)
        s_content = s_content.replace("Official Google Drive installer download link", "Official GitHub Release installer download link")
        with open(sf, "w", encoding="utf-8", newline="\n") as f:
            f.write(s_content)
        print(f"[OK] Updated {os.path.relpath(sf, BASE_DIR)}")

# 4. Update index.html and public copies
html_files = [
    os.path.join(BASE_DIR, "index.html"),
    os.path.join(BASE_DIR, "public", "index.html"),
    os.path.join(BASE_DIR, "deploy_vercel", "index.html"),
    os.path.join(BASE_DIR, "deploy_vercel", "public", "index.html"),
]

for hf in html_files:
    if os.path.exists(hf):
        with open(hf, "r", encoding="utf-8") as f:
            h_content = f.read()
        # Replace download URLs
        h_content = h_content.replace(OLD_LATEST_GDRIVE, NEW_LATEST_GITHUB)
        h_content = h_content.replace(OLD_V100_GDRIVE, NEW_V100_GITHUB)
        # Update selector in JS to include github.com
        h_content = h_content.replace(
            'document.querySelectorAll(\'a[href*="drive.google.com"], a[data-download-link="latest"], a.btn-download-latest\')',
            'document.querySelectorAll(\'a[href*="github.com"], a[href*="drive.google.com"], a[data-download-link="latest"], a.btn-download-latest\')'
        )
        h_content = h_content.replace(
            '// 1. Update ALL default download buttons to point to the latest Google Drive release',
            '// 1. Update ALL default download buttons to point to the latest GitHub release'
        )
        with open(hf, "w", encoding="utf-8", newline="\n") as f:
            f.write(h_content)
        print(f"[OK] Updated {os.path.relpath(hf, BASE_DIR)}")

# 5. Update backend/website_html.py in all locations
py_web_files = [
    os.path.join(BASE_DIR, "backend", "website_html.py"),
    os.path.join(BASE_DIR, "deploy_vercel", "backend", "website_html.py"),
]

for pwf in py_web_files:
    if os.path.exists(pwf):
        with open(pwf, "r", encoding="utf-8") as f:
            w_content = f.read()
        w_content = w_content.replace(OLD_LATEST_GDRIVE, NEW_LATEST_GITHUB)
        w_content = w_content.replace(OLD_V100_GDRIVE, NEW_V100_GITHUB)
        w_content = w_content.replace(
            'document.querySelectorAll(\'a[href*="drive.google.com"], a[data-download-link="latest"], a.btn-download-latest\')',
            'document.querySelectorAll(\'a[href*="github.com"], a[href*="drive.google.com"], a[data-download-link="latest"], a.btn-download-latest\')'
        )
        w_content = w_content.replace(
            '// 1. Update ALL default download buttons to point to the latest Google Drive release',
            '// 1. Update ALL default download buttons to point to the latest GitHub release'
        )
        with open(pwf, "w", encoding="utf-8", newline="\n") as f:
            f.write(w_content)
        print(f"[OK] Updated {os.path.relpath(pwf, BASE_DIR)}")

# 6. Update manage_releases.py
m_file = os.path.join(BASE_DIR, "manage_releases.py")
if os.path.exists(m_file):
    with open(m_file, "r", encoding="utf-8") as f:
        m_content = f.read()
    m_content = m_content.replace("Enables adding new Google Drive releases", "Enables adding new GitHub releases")
    m_content = m_content.replace("help=\"Google Drive shared download link\"", "help=\"GitHub release direct download link\"")
    with open(m_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(m_content)
    print(f"[OK] Updated {os.path.relpath(m_file, BASE_DIR)}")

print("\nAll project files updated to use direct GitHub Releases!")
