# Update keygen.py and app.py to eliminate console popups and optimize app startup
import os

keygen_replacement = '''_CACHED_HWID = None

def get_hardware_id() -> str:
    """
    Generate a stable, tamper-resistant Hardware Identifier (HWID)
    bound to the user's physical computer motherboard & CPU.
    Completely silent without console/CMD windows and cached in memory.
    """
    global _CACHED_HWID
    if _CACHED_HWID:
        return _CACHED_HWID

    identifiers = []

    # 1. Platform architecture & node
    identifiers.append(platform.machine())
    identifiers.append(platform.processor())

    # 2. Windows-specific hardware identifiers (WMIC / PowerShell / Registry)
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = 0x08000000  # CREATE_NO_WINDOW

        # Bios / Motherboard Serial
        try:
            cmd = "Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SerialNumber"
            res = subprocess.check_output(
                ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", cmd],
                text=True,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=2.0
            )
            if res.strip():
                identifiers.append(res.strip())
        except Exception:
            pass

        # Motherboard UUID
        try:
            cmd = "Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
            res = subprocess.check_output(
                ["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", cmd],
                text=True,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=2.0
            )
            if res.strip():
                identifiers.append(res.strip())
        except Exception:
            pass

        # Windows MachineGuid (Registry)
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography")
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            if guid:
                identifiers.append(guid)
        except Exception:
            pass

    # Fallback to node name if empty
    if not identifiers:
        identifiers.append(platform.node())

    raw_string = "|".join(identifiers)
    hwid = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()[:32].upper()
    _CACHED_HWID = f"HWID-{hwid[:4]}-{hwid[4:8]}-{hwid[8:12]}-{hwid[12:16]}"
    return _CACHED_HWID'''

old_func_start = "def get_hardware_id() -> str:"
old_func_end = 'return f"HWID-{hwid[:4]}-{hwid[4:8]}-{hwid[8:12]}-{hwid[12:16]}"'

for path in ["backend/keygen.py", "deploy_vercel/backend/keygen.py"]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        p1 = c.find(old_func_start)
        p2 = c.find(old_func_end)
        if p1 != -1 and p2 != -1:
            p2 += len(old_func_end)
            c = c[:p1] + keygen_replacement + c[p2:]
            with open(path, "w", encoding="utf-8") as f:
                f.write(c)
            print(f"[OK] Updated {path}")

# Update app.py
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Add locate_in_explorer helper right before YouTubeDownloaderApp
helper_func = '''def locate_in_explorer(file_path: str):
    """Safely reveal file in Windows Explorer without flashing a CMD window."""
    if not file_path:
        return
    try:
        abs_p = os.path.abspath(file_path)
        if os.path.exists(abs_p):
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = 0x08000000
                subprocess.run(f'explorer /select,"{abs_p}"', startupinfo=startupinfo, creationflags=creationflags)
            else:
                os.startfile(os.path.dirname(abs_p))
    except Exception:
        try:
            os.startfile(os.path.dirname(os.path.abspath(file_path)))
        except Exception:
            pass

'''

if "def locate_in_explorer" not in app_code:
    target_class = "# ----------------- Main Application Window -----------------"
    app_code = app_code.replace(target_class, helper_func + target_class)

# Replace subprocess.run in locate buttons
app_code = app_code.replace(
    'command=lambda p=file_path: os.startfile(p) if is_pl else subprocess.run(f\'explorer /select,"{os.path.abspath(p)}"\'',
    'command=lambda p=file_path: os.startfile(p) if is_pl else locate_in_explorer(p'
)

old_locate = '''    def _locate_last_downloaded(self):
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            try:
                subprocess.run(f'explorer /select,"{os.path.abspath(self.last_downloaded_file)}"')
            except Exception:
                if self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
                    os.startfile(self.last_downloaded_folder)
        elif self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
            os.startfile(self.last_downloaded_folder)'''

new_locate = '''    def _locate_last_downloaded(self):
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            locate_in_explorer(self.last_downloaded_file)
        elif self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
            try:
                os.startfile(self.last_downloaded_folder)
            except Exception:
                pass'''

app_code = app_code.replace(old_locate, new_locate)

# Hide console window in app.py main()
old_main = '''def main():
    app = YouTubeDownloaderApp()
    app.mainloop()'''

new_main = '''def main():
    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
        except Exception:
            pass

    app = YouTubeDownloaderApp()
    app.mainloop()'''

app_code = app_code.replace(old_main, new_main)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("[OK] Updated app.py with silent explorer locator and main console hiding")
