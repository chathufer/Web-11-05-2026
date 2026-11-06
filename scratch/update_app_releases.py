import re

filepath = r"c:\Users\Chathufer\Downloads\Youtube video dowonloader\app.py"

with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update version metadata & add helper
old_meta = """# ----------------- App Metadata & Paths -----------------
APP_NAME = "Media Downloader Pro"
APP_VERSION = "v2.2 Turbo"
APP_SUBTITLE = "YouTube 4K, TikTok (No Watermark), Hi-Fi Audio & Full Playlists" """

new_meta = """# ----------------- App Metadata & Paths -----------------
APP_NAME = "Media Downloader Pro"
APP_VERSION = "v2.2.0"
APP_VERSION_DISPLAY = "v2.2 Commercial Turbo Edition"
CURRENT_VERSION_CODE = "2.2.0"
APP_SUBTITLE = "YouTube 4K, TikTok (No Watermark), Hi-Fi Audio & Full Playlists"

def parse_version_tuple(v_str: str) -> tuple:
    nums = [int(x) for x in re.findall(r'\\d+', str(v_str))]
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])

def check_for_remote_update(current_ver: str = CURRENT_VERSION_CODE) -> tuple:
    \"\"\"Checks remote endpoints for newer published releases.
    Returns: (has_newer_version: bool, latest_release_info: dict or None)
    \"\"\"
    endpoints = [
        "https://prodownloader.site/releases.json",
        "https://prodownloader.site/api/v1/releases",
        "http://127.0.0.1:5000/releases.json",
    ]
    cur_tuple = parse_version_tuple(current_ver)
    for url in endpoints:
        try:
            r = requests.get(url, timeout=3.5, headers={"User-Agent": f"MediaDownloaderPro/{current_ver}"})
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and len(data) > 0:
                    latest = next((item for item in data if item.get("is_latest")), data[0])
                    ver_str = latest.get("version", "")
                    if parse_version_tuple(ver_str) > cur_tuple:
                        return True, latest
                    return False, latest
        except Exception:
            continue
    return False, None"""

if "CURRENT_VERSION_CODE =" not in text:
    # Match more leniently
    target_meta = 'APP_VERSION = "v2.2 Turbo"'
    if target_meta in text:
        text = text.replace(target_meta, 'APP_VERSION = "v2.2.0"\nAPP_VERSION_DISPLAY = "v2.2 Commercial Turbo Edition"\nCURRENT_VERSION_CODE = "2.2.0"\n\ndef parse_version_tuple(v_str: str) -> tuple:\n    nums = [int(x) for x in re.findall(r\'\\d+\', str(v_str))]\n    while len(nums) < 3:\n        nums.append(0)\n    return tuple(nums[:3])\n\ndef check_for_remote_update(current_ver: str = CURRENT_VERSION_CODE) -> tuple:\n    endpoints = [\n        "https://prodownloader.site/releases.json",\n        "https://prodownloader.site/api/v1/releases",\n        "http://127.0.0.1:5000/releases.json",\n    ]\n    cur_tuple = parse_version_tuple(current_ver)\n    for url in endpoints:\n        try:\n            r = requests.get(url, timeout=3.5, headers={"User-Agent": f"MediaDownloaderPro/{current_ver}"})\n            if r.status_code == 200:\n                data = r.json()\n                if isinstance(data, list) and len(data) > 0:\n                    latest = next((item for item in data if item.get("is_latest")), data[0])\n                    ver_str = latest.get("version", "")\n                    if parse_version_tuple(ver_str) > cur_tuple:\n                        return True, latest\n                    return False, latest\n        except Exception:\n            continue\n    return False, None\n')
        print("[OK] Replaced APP_VERSION metadata")
    else:
        print("[WARN] target_meta not found")

# 2. Add background update check in __init__
init_target = "threading.Thread(target=self.license_mgr.verify_background, daemon=True).start()"
init_addition = """threading.Thread(target=self.license_mgr.verify_background, daemon=True).start()

        # Background silent check for newer version releases
        self.latest_available_release = None
        threading.Thread(target=self._check_for_updates_background, daemon=True).start()"""

if "self._check_for_updates_background" not in text:
    if init_target in text:
        text = text.replace(init_target, init_addition, 1)
        print("[OK] Added background update check trigger in __init__")
    else:
        print("[WARN] init_target not found")

# 3. Add update banner in _build_downloader_view
banner_target = "# 2. Clipboard Toast Banner (Appears dynamically if clipboard contains media link)"
banner_code = """# 1.5 Dynamic Software Update Notification Banner (Shows when a newer version is published)
        self.update_banner = ctk.CTkFrame(
            self.view_downloader,
            fg_color=COLOR_PRIMARY_SUBTLE,
            border_width=1,
            border_color=COLOR_PRIMARY,
            corner_radius=8
        )
        self.update_banner_lbl = ctk.CTkLabel(
            self.update_banner,
            text="🚀 New Version Available!",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.update_banner_lbl.pack(side="left", padx=(12, 8), pady=8)

        self.update_banner_dl_btn = ctk.CTkButton(
            self.update_banner,
            text="Download Update",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=140,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#0b0b0b",
            command=self._on_update_banner_clicked
        )
        self.update_banner_dl_btn.pack(side="left", padx=4, pady=8)

        self.update_banner_dismiss_btn = ctk.CTkButton(
            self.update_banner,
            text="✕",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=28,
            height=28,
            fg_color="transparent",
            text_color=TEXT_MUTED,
            hover_color=BG_CARD_HOVER,
            command=lambda: self.update_banner.pack_forget()
        )
        self.update_banner_dismiss_btn.pack(side="right", padx=8, pady=8)

        """ + banner_target

if "self.update_banner =" not in text:
    if banner_target in text:
        text = text.replace(banner_target, banner_code, 1)
        print("[OK] Added update_banner in _build_downloader_view")
    else:
        print("[WARN] banner_target not found")

# 4. Add software updates status & check button in Settings about_card
about_card_target = """        ctk.CTkLabel(
            about_card,
            text="Engineered for ad-free downloads across YouTube, TikTok (No Watermark), and Full Playlists.\\nOfficial Store & Updates: https://prodownloader.site",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 10))"""

about_card_addition = """        ctk.CTkLabel(
            about_card,
            text="Engineered for ad-free downloads across YouTube, TikTok (No Watermark), and Full Playlists.\\nOfficial Store & Updates: https://prodownloader.site",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 6))

        # Update Checker Row inside Settings
        update_row = ctk.CTkFrame(about_card, fg_color="transparent")
        update_row.pack(fill="x", padx=18, pady=(4, 10))

        self.settings_update_status_lbl = ctk.CTkLabel(
            update_row,
            text=f"● You are on version {APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_SUCCESS
        )
        self.settings_update_status_lbl.pack(side="left")

        self.settings_check_update_btn = ctk.CTkButton(
            update_row,
            text="⟳ Check for Updates",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=140,
            fg_color=BG_WINDOW,
            border_width=1,
            border_color=BORDER_COLOR,
            text_color=TEXT_MAIN,
            hover_color=BG_CARD_HOVER,
            command=self._on_manual_check_updates
        )
        self.settings_check_update_btn.pack(side="right")"""

if "self.settings_update_status_lbl" not in text:
    if about_card_target in text:
        text = text.replace(about_card_target, about_card_addition, 1)
        print("[OK] Added update checker in Settings about_card")
    else:
        print("[WARN] about_card_target not found")

# 5. Add update methods
methods_target = "    # ---------------- Clipboard & Auto-Fetch Engine ----------------"
methods_code = """    # ---------------- Software Updates Engine ----------------

    def _check_for_updates_background(self):
        try:
            has_update, latest_rel = check_for_remote_update(CURRENT_VERSION_CODE)
            if has_update and latest_rel:
                self.after(1200, lambda: self._on_newer_version_detected(latest_rel))
        except Exception:
            pass

    def _on_newer_version_detected(self, latest_rel: dict):
        self.latest_available_release = latest_rel
        ver = latest_rel.get("version", "Newer Version")
        title = latest_rel.get("title", "")
        disp = f"🚀 New Version Available: {ver} — {title}" if title else f"🚀 New Version Available: {ver}"
        if len(disp) > 75:
            disp = disp[:75] + "..."
        self.update_banner_lbl.configure(text=disp)
        self.update_banner_dl_btn.configure(text=f"Download {ver}")

        # Show banner at the top of Downloader view
        try:
            self.update_banner.pack(fill="x", padx=18, pady=(0, 10), before=self.clipboard_banner)
        except Exception:
            self.update_banner.pack(fill="x", padx=18, pady=(0, 10))

        # Update Settings Label if exists
        if hasattr(self, "settings_update_status_lbl") and self.settings_update_status_lbl.winfo_exists():
            self.settings_update_status_lbl.configure(
                text=f"🚀 Newer Version Available: {ver}",
                text_color=COLOR_PRIMARY
            )

        # Show the friendly update popup modal
        self._show_update_modal(latest_rel)

    def _on_update_banner_clicked(self):
        if hasattr(self, "latest_available_release") and self.latest_available_release:
            url = self.latest_available_release.get("url", "https://prodownloader.site")
            webbrowser.open(url)
        else:
            webbrowser.open("https://prodownloader.site/#older-versions")

    def _on_manual_check_updates(self):
        if hasattr(self, "settings_check_update_btn"):
            self.settings_check_update_btn.configure(text="Checking...", state="disabled")
        
        def task():
            try:
                has_update, latest_rel = check_for_remote_update(CURRENT_VERSION_CODE)
                def on_done():
                    if hasattr(self, "settings_check_update_btn") and self.settings_check_update_btn.winfo_exists():
                        self.settings_check_update_btn.configure(text="⟳ Check for Updates", state="normal")
                    if has_update and latest_rel:
                        self._on_newer_version_detected(latest_rel)
                    else:
                        if hasattr(self, "settings_update_status_lbl") and self.settings_update_status_lbl.winfo_exists():
                            self.settings_update_status_lbl.configure(
                                text=f"● You are on the latest version ({APP_VERSION})",
                                text_color=COLOR_SUCCESS
                            )
                        self._show_info_dialog(
                            "Software Up to Date",
                            f"You are currently running {APP_NAME} {APP_VERSION}.\\n\\nNo newer updates are available at this time."
                        )
                self.after(0, on_done)
            except Exception as e:
                def on_err():
                    if hasattr(self, "settings_check_update_btn") and self.settings_check_update_btn.winfo_exists():
                        self.settings_check_update_btn.configure(text="⟳ Check for Updates", state="normal")
                    self._show_info_dialog("Update Check Notice", f"Unable to reach update servers right now: {str(e)}", is_error=True)
                self.after(0, on_err)

        threading.Thread(target=task, daemon=True).start()

    def _show_update_modal(self, latest_rel: dict):
        ver = latest_rel.get("version", "v2.3.0")
        title = latest_rel.get("title", "New Release")
        notes = latest_rel.get("notes", "New performance enhancements and features are available.")
        dl_url = latest_rel.get("url", "https://prodownloader.site")
        date_str = latest_rel.get("date_formatted", latest_rel.get("date", ""))
        size_str = latest_rel.get("size", "")

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Software Update Available — {ver}")
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        dialog.grab_set()

        self.update_idletasks()
        dw, dh = 520, 360
        x = self.winfo_x() + (self.winfo_width() - dw) // 2
        y = self.winfo_y() + (self.winfo_height() - dh) // 2
        dialog.geometry(f"{dw}x{dh}+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(dialog, fg_color=BG_WINDOW, corner_radius=0)
        f.pack(fill="both", expand=True, padx=24, pady=22)

        # Header Row
        top_row = ctk.CTkFrame(f, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            top_row,
            text=f"🚀 Newer Version Available: {ver}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(side="left")

        if date_str:
            ctk.CTkLabel(
                top_row,
                text=f"Released: {date_str}",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            ).pack(side="right")

        # Content Card
        card = ctk.CTkFrame(f, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR, corner_radius=12)
        card.pack(fill="both", expand=True, pady=(0, 16), padx=2, ipady=4)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MAIN,
            wraplength=460,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(12, 6))

        if size_str:
            ctk.CTkLabel(
                card,
                text=f"📦 Installer Size: {size_str} • Windows 10 & 11 64-bit",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            ).pack(anchor="w", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            card,
            text=notes,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            wraplength=460,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Button Row
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x")

        def on_download_now():
            dialog.destroy()
            webbrowser.open(dl_url)

        ctk.CTkButton(
            btn_row,
            text=f"⬇ Download & Update to {ver}",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#0b0b0b",
            command=on_download_now
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Remind Me Later",
            font=ctk.CTkFont(size=12),
            height=38,
            width=120,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            text_color=TEXT_MUTED,
            hover_color=BG_CARD_HOVER,
            command=dialog.destroy
        ).pack(side="right")

    """ + methods_target

if "_check_for_updates_background" not in text:
    if methods_target in text:
        text = text.replace(methods_target, methods_code, 1)
        print("[OK] Added update methods before clipboard engine")
    else:
        print("[WARN] methods_target not found")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("Finished updating app.py")
