filepath = r"c:\Users\Chathufer\Downloads\Youtube video dowonloader\app.py"

with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

target = "    # ---------------- Clipboard & Auto-Fetch Engine ----------------"

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

"""

if "def _check_for_updates_background" not in text:
    text = text.replace(target, methods_code + target, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected methods successfully!")
else:
    print("Methods already present.")
