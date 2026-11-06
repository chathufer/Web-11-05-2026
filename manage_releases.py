#!/usr/bin/env python3
"""
Release Management Utility for Downloader Pro.
Enables adding new Google Drive releases and automatically updating:
1. releases.json across all project locations
2. index.html and public copies
3. backend/website_html.py and deploy_vercel copies
4. Making the newly added release the active 'Latest Version' for all download buttons!
"""

import os
import sys
import json
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RELEASE_FILES = [
    os.path.join(BASE_DIR, "releases.json"),
    os.path.join(BASE_DIR, "public", "releases.json"),
    os.path.join(BASE_DIR, "deploy_vercel", "releases.json"),
    os.path.join(BASE_DIR, "deploy_vercel", "public", "releases.json"),
]

HTML_FILES = [
    os.path.join(BASE_DIR, "index.html"),
    os.path.join(BASE_DIR, "public", "index.html"),
    os.path.join(BASE_DIR, "deploy_vercel", "index.html"),
    os.path.join(BASE_DIR, "deploy_vercel", "public", "index.html"),
]

PY_WEB_FILES = [
    os.path.join(BASE_DIR, "backend", "website_html.py"),
    os.path.join(BASE_DIR, "deploy_vercel", "backend", "website_html.py"),
]


def load_releases():
    p = os.path.join(BASE_DIR, "releases.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_releases(releases):
    content = json.dumps(releases, indent=2, ensure_ascii=False)
    for p in RELEASE_FILES:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(content)
        print(f"[OK] Updated {os.path.relpath(p, BASE_DIR)}")


def sync_html_releases(releases):
    """Update inline APP_RELEASES array in HTML and Python embedded files."""
    json_str = json.dumps(releases, indent=6, ensure_ascii=False)
    # Target pattern for inline APP_RELEASES
    start_tag = "// APP_RELEASES_START"
    end_tag = "// APP_RELEASES_END"

    for hf in HTML_FILES:
        if not os.path.exists(hf):
            continue
        with open(hf, "r", encoding="utf-8") as f:
            text = f.read()

        p1 = text.find(start_tag)
        p2 = text.find(end_tag)
        if p1 != -1 and p2 != -1:
            replacement = f"{start_tag}\n    const APP_RELEASES = {json_str};\n    {end_tag}"
            text = text[:p1] + replacement + text[p2 + len(end_tag):]
            with open(hf, "w", encoding="utf-8", newline="\r\n") as f:
                f.write(text)
            print(f"[OK] Synced inline APP_RELEASES in {os.path.relpath(hf, BASE_DIR)}")

    for pwf in PY_WEB_FILES:
        if not os.path.exists(pwf):
            continue
        with open(pwf, "r", encoding="utf-8") as f:
            text = f.read()

        p1 = text.find(start_tag)
        p2 = text.find(end_tag)
        if p1 != -1 and p2 != -1:
            replacement = f"{start_tag}\\n    const APP_RELEASES = {json_str};\\n    {end_tag}"
            text = text[:p1] + replacement + text[p2 + len(end_tag):]
            with open(pwf, "w", encoding="utf-8", newline="\r\n") as f:
                f.write(text)
            print(f"[OK] Synced inline APP_RELEASES in {os.path.relpath(pwf, BASE_DIR)}")


def cmd_list(args):
    releases = load_releases()
    print("\n" + "=" * 70)
    print("                    CURRENT PUBLISHED RELEASES")
    print("=" * 70)
    for idx, r in enumerate(releases):
        latest_tag = "[LATEST]" if idx == 0 or r.get("is_latest") else "[PREVIOUS]"
        print(f"{latest_tag:<11} {r.get('version'):<8} ({r.get('date')} / {r.get('date_formatted', '')})")
        print(f"             Title: {r.get('title')}")
        print(f"             Size:  {r.get('size', 'N/A')}")
        print(f"             URL:   {r.get('url')}")
        print(f"             Notes: {r.get('notes')}")
        print("-" * 70)


def cmd_add(args):
    releases = load_releases()

    version = args.version.strip()
    if not version.startswith("v"):
        version = f"v{version}"

    url = args.url.strip()
    title = args.title.strip() if args.title else f"{version} Feature & Stability Update"
    notes = args.notes.strip() if args.notes else "Performance optimizations and stability enhancements."
    size = args.size.strip() if args.size else "58.0 MB"

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    date_fmt = now.strftime("%b %d, %Y")

    # Mark all previous as not latest
    for r in releases:
        r["is_latest"] = False

    new_rel = {
        "version": version,
        "date": date_str,
        "date_formatted": date_fmt,
        "title": title,
        "is_latest": True,
        "url": url,
        "size": size,
        "notes": notes
    }

    # Insert at the beginning so it immediately becomes the Latest version
    releases.insert(0, new_rel)

    save_releases(releases)
    sync_html_releases(releases)

    print("\n" + "=" * 70)
    print(f"SUCCESS: Added {version} as the NEW LATEST RELEASE!")
    print(f"Download URL: {url}")
    print("All website download buttons now automatically point to this new release!")
    print("Previous versions have been preserved in the Updates dropdown.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Manage published Downloader Pro releases")
    subparsers = parser.add_subparsers(dest="command")

    # List command
    subparsers.add_parser("list", help="List all published releases")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new Google Drive release as the latest version")
    add_parser.add_argument("--version", "-v", required=True, help="Version string (e.g. v2.3.0)")
    add_parser.add_argument("--url", "-u", required=True, help="Google Drive shared download link")
    add_parser.add_argument("--title", "-t", default="", help="Release title / headline")
    add_parser.add_argument("--size", "-s", default="58.0 MB", help="File size (e.g. 57.7 MB)")
    add_parser.add_argument("--notes", "-n", default="", help="Changelog notes or highlights")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    else:
        cmd_list(args)


if __name__ == "__main__":
    main()
