import os
import sys
import json
import ctypes
from ctypes import wintypes
import urllib.request
import urllib.error

# 1. Retrieve Token from Windows Credential Manager
class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', wintypes.DWORD),
        ('Type', wintypes.DWORD),
        ('TargetName', wintypes.LPWSTR),
        ('Comment', wintypes.LPWSTR),
        ('LastWritten', wintypes.FILETIME),
        ('CredentialBlobSize', wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', wintypes.DWORD),
        ('AttributeCount', wintypes.DWORD),
        ('Attributes', ctypes.c_void_p),
        ('TargetAlias', wintypes.LPWSTR),
        ('UserName', wintypes.LPWSTR)
    ]

Advapi32 = ctypes.windll.Advapi32
target = 'GitHub - https://api.github.com/chathufer'
cred_ptr = ctypes.POINTER(CREDENTIAL)()
token = None
if Advapi32.CredReadW(target, 1, 0, ctypes.byref(cred_ptr)):
    cred = cred_ptr.contents
    raw_bytes = bytes((cred.CredentialBlob[i] for i in range(cred.CredentialBlobSize)))
    token = raw_bytes.decode('utf-8', errors='ignore')
    Advapi32.CredFree(cred_ptr)

if not token:
    print("Error: Could not retrieve GitHub token from Windows Credential Manager")
    sys.exit(1)

print(f"Retrieved GitHub PAT successfully (length: {len(token)})")

setup_path = os.path.abspath("MediaDownloaderPro_Setup.exe")
if not os.path.exists(setup_path):
    setup_path = os.path.abspath("Setup/MediaDownloaderPro_Setup.exe")

file_size = os.path.getsize(setup_path)
print(f"Setup executable: {setup_path} ({file_size} bytes, {file_size / (1024*1024):.2f} MB)")

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'MediaDownloaderPro-Uploader'
}

repo = "chathufer/Web-11-05-2026"
tag_name = "v1.0.1"
release_title = "Media Downloader Pro v1.0.1 Turbo Update"
release_body = (
    "## 🚀 Media Downloader Pro v1.0.1 Official Release\n\n"
    "### What's New:\n"
    "- ⚡ **Ultra HD 4K 60FPS Video Engine**: High-speed multi-threaded YouTube streams.\n"
    "- 📱 **TikTok Clean Extractor**: 100% watermark-free direct MP4 downloads.\n"
    "- 🎵 **Lossless 320k Audio Converter**: Studio-grade MP3 extraction.\n"
    "- 🎁 **7-Day Full Pro Free Trial**: Built-in 1-click trial across app & PC reboots.\n"
    "- 🛡️ **Polished Error Handling & Stability**: Intelligent auto-recovery on network drops.\n\n"
    "**Install**: Download `MediaDownloaderPro_Setup.exe` below and run the installer."
)

# Step 2: Check or Create Release
print(f"\nChecking release {tag_name} on {repo}...")
release_id = None
upload_url_template = None

# Check existing releases
try:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases", headers=headers)
    with urllib.request.urlopen(req) as resp:
        releases = json.loads(resp.read().decode())
        for r in releases:
            if r.get("tag_name") == tag_name:
                release_id = r["id"]
                upload_url_template = r["upload_url"]
                print(f"Found existing release {tag_name} (ID: {release_id})")
                break
except Exception as e:
    print(f"Error checking releases: {e}")

if not release_id:
    print(f"Creating new release {tag_name} on {repo}...")
    create_payload = json.dumps({
        "tag_name": tag_name,
        "target_commitish": "main",
        "name": release_title,
        "body": release_body,
        "draft": False,
        "prerelease": False,
        "make_latest": "true"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases",
        data=create_payload,
        headers={**headers, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        rel_data = json.loads(resp.read().decode())
        release_id = rel_data["id"]
        upload_url_template = rel_data["upload_url"]
        print(f"Created release {tag_name} (ID: {release_id})")

# Step 3: Check for existing asset and delete if present
req_assets = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/{release_id}/assets", headers=headers)
with urllib.request.urlopen(req_assets) as resp:
    assets = json.loads(resp.read().decode())
    for a in assets:
        if a["name"] == "MediaDownloaderPro_Setup.exe":
            print(f"Deleting previous asset {a['name']} (ID: {a['id']})...")
            del_req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/releases/assets/{a['id']}",
                headers=headers,
                method='DELETE'
            )
            with urllib.request.urlopen(del_req) as del_resp:
                print(f"Deleted asset (Status: {del_resp.status})")

# Step 4: Upload Asset
raw_upload_url = upload_url_template.split('{')[0]
upload_url = f"{raw_upload_url}?name=MediaDownloaderPro_Setup.exe"
print(f"\nUploading {setup_path} ({file_size} bytes) to {upload_url}...")

with open(setup_path, "rb") as f:
    file_bytes = f.read()

upload_req = urllib.request.Request(
    upload_url,
    data=file_bytes,
    headers={
        **headers,
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(len(file_bytes))
    }
)

with urllib.request.urlopen(upload_req) as up_resp:
    asset_data = json.loads(up_resp.read().decode())
    browser_download_url = asset_data["browser_download_url"]
    print(f"\nSUCCESS: Asset uploaded successfully!")
    print(f"Direct Browser Download URL: {browser_download_url}")
    print(f"Size: {asset_data['size']} bytes")

# Step 5: Test public download (unauthenticated check)
print("\nTesting public unauthenticated access to download URL...")
test_req = urllib.request.Request(browser_download_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(test_req) as test_resp:
    print(f"Public Download Test: Status {test_resp.status}, Content-Length: {test_resp.headers.get('Content-Length')}")
    first_chunk = test_resp.read(1024)
    print(f"Successfully read first 1024 bytes! (MZ header: {first_chunk[:2] == b'MZ'})")
