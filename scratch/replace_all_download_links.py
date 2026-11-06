import os
import glob

OLD_LINK = "https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing"
NEW_LINK = "https://drive.google.com/file/d/1Ghsj-UAtHQRpjqised3ugUjZBfdyIchS/view?usp=drive_link"

target_files = [
    "index.html",
    "public/index.html",
    "deploy_vercel/index.html",
    "deploy_vercel/public/index.html",
    "backend/website_html.py",
    "deploy_vercel/backend/website_html.py",
    "releases.json",
    "public/releases.json",
    "deploy_vercel/releases.json",
    "deploy_vercel/public/releases.json",
]

total_replaced = 0
for fpath in target_files:
    if os.path.isfile(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        cnt = content.count(OLD_LINK)
        if cnt > 0:
            content = content.replace(OLD_LINK, NEW_LINK)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            total_replaced += cnt
            print(f"[OK] Replaced {cnt} occurrence(s) in {fpath}")
        else:
            print(f"[SKIP] No occurrences in {fpath}")

print(f"\nTotal replacements: {total_replaced}")
