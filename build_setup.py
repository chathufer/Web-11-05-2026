"""
Automated Build Script for Single Commercial Installer File
Compiles the application into Setup/MediaDownloaderPro_Setup.exe
"""

import os
import sys
import shutil
import subprocess

def find_iscc() -> str:
    """Find the Inno Setup compiler executable."""
    # Check PATH first
    iscc = shutil.which("iscc")
    if iscc and os.path.isfile(iscc):
        return iscc

    # Known standard install locations
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "iscc.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Inno Setup 6", "iscc.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Inno Setup 6", "iscc.exe"),
        r"C:\Users\Chathufer\AppData\Local\Programs\Inno Setup 6\iscc.exe",
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c

    return ""

def build_setup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 65)
    print("      CREATING SINGLE INSTALLATION FILE FOR DISTRIBUTION")
    print("=" * 65)

    # 1. Ensure dist\YouTubeDownloader\YouTubeDownloader.exe exists
    exe_target = os.path.join(base_dir, "dist", "YouTubeDownloader", "YouTubeDownloader.exe")
    if not os.path.exists(exe_target):
        print("\n[1/4] Application binary not found. Running PyInstaller first...")
        build_exe_script = os.path.join(base_dir, "build_exe.py")
        subprocess.run([sys.executable, build_exe_script], check=True)
    else:
        print("\n[1/4] Found application executable in dist/YouTubeDownloader")

    # 2. Clean temporary/personal user data from dist before packaging
    dist_history = os.path.join(base_dir, "dist", "YouTubeDownloader", "history.json")
    if os.path.exists(dist_history):
        try:
            os.remove(dist_history)
            print("[2/4] Cleaned test history from distribution payload")
        except Exception:
            pass
    else:
        print("[2/4] Distribution payload is clean")

    # 3. Ensure Setup folder exists
    setup_dir = os.path.join(base_dir, "Setup")
    os.makedirs(setup_dir, exist_ok=True)
    print(f"[3/4] Setup directory prepared: {setup_dir}")

    # 4. Find Inno Setup compiler
    iscc_path = find_iscc()
    if not iscc_path:
        print("\nERROR: Inno Setup compiler (iscc.exe) could not be found.")
        print("Please install Inno Setup 6 using: winget install JRSoftware.InnoSetup")
        return False

    print(f"[4/4] Compiling installer using: {iscc_path} ...")
    iss_file = os.path.join(base_dir, "installer.iss")

    cmd = [iscc_path, f"/O{setup_dir}", "/FMediaDownloaderPro_Setup", iss_file]
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\nInstaller compilation failed with code:", result.returncode)
        return False

    setup_file = os.path.join(setup_dir, "MediaDownloaderPro_Setup.exe")
    generic_setup = os.path.join(setup_dir, "Setup.exe")
    if os.path.exists(setup_file):
        try:
            shutil.copyfile(setup_file, generic_setup)
        except Exception:
            pass

        size_mb = os.path.getsize(setup_file) / (1024 * 1024)
        print("\n" + "=" * 65)
        print("               INSTALLER CREATED SUCCESSFULLY!")
        print("=" * 65)
        print(f"Location: {setup_file}")
        print(f"Size:     {size_mb:.1f} MB (High-ratio solid LZMA2 compression)")
        print("\nWHAT TO GIVE TO CUSTOMERS / BUYERS:")
        print("  -> Simply send them the single file:")
        print(f"     {setup_file} (or Setup.exe)")
        print("\nWHEN THEY RUN IT ON THEIR PC:")
        print("  1. Standard professional Windows installation wizard opens.")
        print("  2. Installs the app to their computer automatically.")
        print("  3. Adds Desktop & Start Menu shortcuts with the app icon.")
        print("  4. Works on any Windows 10/11 computer with no setup required.")
        print("  5. Registers in Windows Settings -> Apps for clean 1-click uninstall.")
        print("=" * 65)
        return True
    else:
        print("\nExpected output installer not found at:", setup_file)
        return False

if __name__ == "__main__":
    success = build_setup()
    if not success:
        sys.exit(1)
