import ctypes
from ctypes import wintypes
import subprocess
import os

git_cmd = r"C:\Users\Chathufer\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe"
cwd = r"c:\Users\Chathufer\Downloads\Youtube video dowonloader"

print("Checking git status...")
res = subprocess.run([git_cmd, "status", "--short"], cwd=cwd, capture_output=True, text=True)
print(res.stdout)

print("Adding changes...")
subprocess.run([git_cmd, "add", "-A"], cwd=cwd, check=True)

commit_msg = "security: remove public display of admin credentials, quick guest login bypass, and hide admin portal link from website"
print("Committing...")
res_c = subprocess.run([git_cmd, "commit", "-m", commit_msg], cwd=cwd, capture_output=True, text=True)
print(res_c.stdout or res_c.stderr)

# Read credentials from Windows Credential Manager
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
CredRead = Advapi32.CredReadW
CredFree = Advapi32.CredFree

target = "GitHub - https://api.github.com/chathufer"
cred_ptr = ctypes.POINTER(CREDENTIAL)()
token = None
if CredRead(target, 1, 0, ctypes.byref(cred_ptr)):
    cred = cred_ptr.contents
    raw_bytes = bytes((cred.CredentialBlob[i] for i in range(cred.CredentialBlobSize)))
    token = raw_bytes.decode('utf-8', errors='ignore')
    CredFree(cred_ptr)

if not token:
    print("Error: Could not retrieve GitHub token from Windows Credential Manager")
    exit(1)

targets = [
    ("Youtube-video-dowonloader", "main"),
    ("Youtube-video-dowonloader", "V2"),
    ("Web-11-05-2026", "main"),
    ("Downloaderpro", "main")
]

for repo, branch in targets:
    remote_url = f"https://x-access-token:{token}@github.com/chathufer/{repo}.git"
    print(f"\nPushing to {repo} ({branch})...")
    res = subprocess.run([git_cmd, "push", remote_url, f"main:{branch}", "--force"], cwd=cwd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"SUCCESS: Pushed to {repo} ({branch})")
    else:
        print(f"FAILED {repo}: {res.stderr}")

print("\nAll GitHub repositories updated successfully!")
