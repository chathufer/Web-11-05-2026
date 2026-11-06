"""
PyInstaller build script to package the YouTube Downloader into a standalone Windows .exe
"""

import os
import sys
import subprocess
import shutil

def build():
    print("=" * 60)
    print("Building YouTube Video Downloader Standalone Executable (.exe)")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # Ensure ffmpeg is present
    ffmpeg_exe = os.path.join(base_dir, "bin", "ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        print("ERROR: bin/ffmpeg.exe not found! Please ensure FFmpeg is in the bin directory.")
        return False

    qjs_exe = os.path.join(base_dir, "bin", "qjs.exe")
    icon_file = os.path.join(base_dir, "icon.ico")

    # PyInstaller arguments with bloat exclusions
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=YouTubeDownloader",
        f"--icon={icon_file}",
        "--collect-all=customtkinter",
        "--collect-all=yt_dlp",
        "--exclude-module=imageio_ffmpeg",
        "--exclude-module=imageio",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        "--exclude-module=matplotlib",
        "--exclude-module=unittest",
        "--exclude-module=pytest",
        "--exclude-module=tkinter.test",
        "--exclude-module=pydoc",
        "--exclude-module=sqlite3.test",
        "--hidden-import=bs4",
        "--hidden-import=requests",
        "--hidden-import=licensing",
        "--hidden-import=queue_manager",
        "--hidden-import=backend",
        "--hidden-import=backend.keygen",
        "--hidden-import=backend.database",
        f"--add-data={ffmpeg_exe};bin",
        f"--add-data={icon_file};.",
        f"--add-data={os.path.join(base_dir, 'backend')};backend",
    ]

    if os.path.exists(qjs_exe):
        cmd.append(f"--add-data={qjs_exe};bin")

    cmd.append("main.py")

    print(f"Running command:\n{' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        dist_dir = os.path.join(base_dir, "dist", "YouTubeDownloader")
        exe_path = os.path.join(dist_dir, "YouTubeDownloader.exe")
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print(f"Executable location: {exe_path}")
        print("=" * 60)
        return True
    else:
        print("\nBUILD FAILED with return code:", result.returncode)
        return False

if __name__ == "__main__":
    success = build()
    if not success:
        sys.exit(1)
