# -*- coding: utf-8 -*-
"""
Systematic update of the latest installer download link:
New URL: https://drive.google.com/file/d/1Ghsj-UAtHQRpjqised3ugUjZBfdyIchS/view?usp=drive_link
Old latest URL: https://drive.google.com/file/d/1oDrWH2SAtZK_gET-T9O9Ts0KX3Gcrsnc/view?usp=drive_link
"""
import os
import json
import shutil

NEW_LINK = "https://drive.google.com/file/d/1Ghsj-UAtHQRpjqised3ugUjZBfdyIchS/view?usp=drive_link"
OLD_LATEST_LINK = "https://drive.google.com/file/d/1oDrWH2SAtZK_gET-T9O9Ts0KX3Gcrsnc/view?usp=drive_link"

print(f"Updating latest installer link to:\n  {NEW_LINK}\n")

# 1. Update releases.json files
releases_files = [
    "releases.json",
    "public/releases.json",
    "deploy_vercel/releases.json",
    "deploy_vercel/public/releases.json"
]

for rf in releases_files:
    if os.path.isfile(rf):
        with open(rf, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            data[0]["url"] = NEW_LINK
            with open(rf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"[OK] Updated {rf} (version {data[0].get('version')})")

# 2. Update vercel.json files
vercel_files = [
    "vercel.json",
    "deploy_vercel/vercel.json"
]

for vf in vercel_files:
    if os.path.isfile(vf):
        with open(vf, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        if "redirects" in v_data:
            for r in v_data["redirects"]:
                if r.get("source") in ["/download", "/Setup.exe", "/MediaDownloaderPro_Setup.exe"]:
                    r["destination"] = NEW_LINK
        with open(vf, "w", encoding="utf-8") as f:
            json.dump(v_data, f, indent=2)
        print(f"[OK] Updated {vf}")

# 3. Update backend/server.py and deploy_vercel/backend/server.py
server_files = [
    "backend/server.py",
    "deploy_vercel/backend/server.py"
]

for sf in server_files:
    if os.path.isfile(sf):
        with open(sf, "r", encoding="utf-8") as f:
            code = f.read()
        code = code.replace(OLD_LATEST_LINK, NEW_LINK)
        with open(sf, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[OK] Updated {sf}")

# 4. Update index.html, public/index.html, deploy_vercel/index.html, deploy_vercel/public/index.html
html_files = [
    "index.html",
    "public/index.html",
    "deploy_vercel/index.html",
    "deploy_vercel/public/index.html"
]

for hf in html_files:
    if os.path.isfile(hf):
        with open(hf, "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace(OLD_LATEST_LINK, NEW_LINK)
        with open(hf, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] Updated {hf}")

# 5. Update backend/website_html.py and deploy_vercel/backend/website_html.py
web_py_files = [
    "backend/website_html.py",
    "deploy_vercel/backend/website_html.py"
]

for wpf in web_py_files:
    if os.path.isfile(wpf):
        with open(wpf, "r", encoding="utf-8") as f:
            py_code = f.read()
        py_code = py_code.replace(OLD_LATEST_LINK, NEW_LINK)
        with open(wpf, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"[OK] Updated {wpf}")

print("\nALL FILES SYSTEMATICALLY UPDATED!")
