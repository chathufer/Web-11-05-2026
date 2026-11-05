# Apply flicker fix to downloader.py and app.py
import re

# 1. Update downloader.py for clean speed and eta strings
with open("downloader.py", "r", encoding="utf-8") as f:
    dl_content = f.read()

old_speed_block = """                speed_str = d.get('_speed_str', 'Calculating...')
                eta_str = d.get('_eta_str', 'N/A')"""

new_speed_block = """                speed_raw = d.get('speed')
                if speed_raw and isinstance(speed_raw, (int, float)) and speed_raw > 0:
                    speed_str = f"{format_bytes(speed_raw)}/s"
                else:
                    speed_str = re.sub(r'\\x1b\\[[0-9;]*[a-zA-Z]', '', str(d.get('_speed_str', 'Calculating...'))).strip()

                eta_raw = d.get('eta')
                if eta_raw and isinstance(eta_raw, (int, float)) and eta_raw > 0:
                    eta_str = format_duration(int(eta_raw))
                else:
                    eta_str = re.sub(r'\\x1b\\[[0-9;]*[a-zA-Z]', '', str(d.get('_eta_str', 'N/A'))).strip()"""

if old_speed_block in dl_content:
    dl_content = dl_content.replace(old_speed_block, new_speed_block)
    with open("downloader.py", "w", encoding="utf-8") as f:
        f.write(dl_content)
    print("[OK] Updated downloader.py with sanitized speed and ETA")
else:
    print("[WARN] Could not find old_speed_block in downloader.py")

# 2. Update app.py
with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()

# Add queue_card_widgets and _queue_refresh_scheduled in __init__
old_init_state = """        self.browse_search_results = []
        self.browse_item_vars = {}
        self.browse_thumb_images = {}
        self.is_searching_browse = False"""

new_init_state = """        self.browse_search_results = []
        self.browse_item_vars = {}
        self.browse_thumb_images = {}
        self.is_searching_browse = False
        self.queue_card_widgets = {}
        self._queue_refresh_scheduled = False"""

app_content = app_content.replace(old_init_state, new_init_state)

# Update _on_queue_updated_threadsafe with debounced after
old_threadsafe = """    def _on_queue_updated_threadsafe(self):
        self.after(0, self._refresh_queue_ui)"""

new_threadsafe = """    def _on_queue_updated_threadsafe(self):
        if not getattr(self, "_queue_refresh_scheduled", False):
            self._queue_refresh_scheduled = True
            self.after(40, self._do_refresh_queue_ui)

    def _do_refresh_queue_ui(self):
        self._queue_refresh_scheduled = False
        self._refresh_queue_ui()"""

app_content = app_content.replace(old_threadsafe, new_threadsafe)

# Replace _refresh_queue_ui with flicker-free in-place widget updating
# Locate the start and end of _refresh_queue_ui
start_marker = "    def _refresh_queue_ui(self):"
end_marker = "    def _on_turbo_add_to_queue(self):"

start_idx = app_content.find(start_marker)
end_idx = app_content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_refresh_method = '''    def _refresh_queue_ui(self):
        """Render active and queued items in the queue panel with smooth in-place caching (ZERO FLICKERING)."""
        stats = self.queue_mgr.get_stats()
        active = stats["active"]
        queued = stats["queued"]
        finished = stats["finished"]
        total = stats["total"]

        if hasattr(self, "q_active_lbl") and self.q_active_lbl.winfo_exists():
            self.q_active_lbl.configure(text=f"⚡ Active: {active}")
        if hasattr(self, "q_waiting_lbl") and self.q_waiting_lbl.winfo_exists():
            self.q_waiting_lbl.configure(text=f"⏳ Queued: {queued}")
        if hasattr(self, "q_finished_lbl") and self.q_finished_lbl.winfo_exists():
            self.q_finished_lbl.configure(text=f"✔ Finished: {finished}")

        self._update_queue_badge()

        if not hasattr(self, "browse_queue_scroll") or not self.browse_queue_scroll.winfo_exists():
            return

        # 1. If queue is completely empty
        if not self.queue_mgr.items:
            for item_id, card_info in list(self.queue_card_widgets.items()):
                if "card" in card_info and card_info["card"].winfo_exists():
                    card_info["card"].destroy()
            self.queue_card_widgets.clear()

            if not hasattr(self, "queue_empty_placeholder") or not self.queue_empty_placeholder.winfo_exists():
                self.queue_empty_placeholder = ctk.CTkLabel(
                    self.browse_queue_scroll,
                    text="📥 Download Queue is currently empty.\\nAdd videos from Browse & Search or click 'Add to Queue' in Turbo Downloader!",
                    font=ctk.CTkFont(size=12),
                    text_color=TEXT_MUTED
                )
                self.queue_empty_placeholder.pack(pady=40)
            return

        # Queue has items: remove empty placeholder if present
        if hasattr(self, "queue_empty_placeholder") and self.queue_empty_placeholder.winfo_exists():
            self.queue_empty_placeholder.destroy()

        # 2. Garbage collect cards for items that were removed
        current_ids = {it.item_id for it in self.queue_mgr.items}
        for old_id in list(self.queue_card_widgets.keys()):
            if old_id not in current_ids:
                if self.queue_card_widgets[old_id]["card"].winfo_exists():
                    self.queue_card_widgets[old_id]["card"].destroy()
                del self.queue_card_widgets[old_id]

        # 3. Smooth In-Place Update or Create each queue card
        for it in self.queue_mgr.items:
            # Prepare state values
            if it.status == "downloading":
                speed_str = it.speed if it.speed else "Calculating..."
                st_text = f"⚡ {int(it.percent)}% • {speed_str}"
                st_col = COLOR_CYAN
                bar_pct = min(max(it.percent / 100.0, 0.0), 1.0)
                bar_col = COLOR_PRIMARY
                if it.downloaded and it.total:
                    info_text = f"ETA: {it.eta} • Transferred: {it.downloaded} / {it.total}"
                else:
                    info_text = f"ETA: {it.eta} • {speed_str}"
            elif it.status == "queued":
                st_text = "⏳ QUEUED (Waiting slot)"
                st_col = "#A855F7"
                bar_pct = 0.0
                bar_col = COLOR_PRIMARY
                info_text = it.uploader or "Waiting in queue for next available worker slot..."
            elif it.status == "finished":
                st_text = "✔ COMPLETED"
                st_col = COLOR_SUCCESS
                bar_pct = 1.0
                bar_col = COLOR_SUCCESS
                out_name = os.path.basename(it.output_file) if it.output_file else "Finished successfully"
                info_text = f"Saved: {out_name}"
            elif it.status == "cancelled":
                st_text = "✖ CANCELLED"
                st_col = TEXT_MUTED
                bar_pct = min(max(it.percent / 100.0, 0.0), 1.0)
                bar_col = TEXT_MUTED
                info_text = "Download cancelled by user"
            else:
                st_text = "✖ ERROR"
                st_col = COLOR_DANGER
                bar_pct = 0.0
                bar_col = COLOR_DANGER
                info_text = it.error_msg or "Failed to download"

            card_info = self.queue_card_widgets.get(it.item_id)
            if card_info and card_info["card"].winfo_exists():
                # --- IN-PLACE UPDATE WITHOUT REBUILDING (PREVENTS ALL FLICKER) ---
                if card_info["last_st_text"] != st_text or card_info["last_st_col"] != st_col:
                    card_info["status_pill"].configure(text=st_text, text_color=st_col)
                    card_info["last_st_text"] = st_text
                    card_info["last_st_col"] = st_col

                if abs(card_info["last_bar_pct"] - bar_pct) >= 0.005 or it.status != card_info["last_status"]:
                    card_info["p_bar"].set(bar_pct)
                    card_info["p_bar"].configure(progress_color=bar_col)
                    card_info["last_bar_pct"] = bar_pct

                if card_info["last_info_text"] != info_text:
                    card_info["info_lbl"].configure(text=info_text)
                    card_info["last_info_text"] = info_text

                # Status transition (e.g. active -> finished)
                if card_info["last_status"] != it.status:
                    card_info["last_status"] = it.status
                    for b in card_info["act_box"].winfo_children():
                        b.destroy()

                    if it.status == "finished" and it.output_file and os.path.exists(it.output_file):
                        ctk.CTkButton(
                            card_info["act_box"],
                            text="📂 Open File",
                            font=ctk.CTkFont(size=10, weight="bold"),
                            height=22,
                            width=78,
                            fg_color=BG_WINDOW,
                            hover_color=BG_CARD_HOVER,
                            text_color=COLOR_SUCCESS,
                            corner_radius=4,
                            command=lambda p=it.output_file: os.startfile(p)
                        ).pack(side="left", padx=2)
                    elif it.status in ("queued", "downloading"):
                        ctk.CTkButton(
                            card_info["act_box"],
                            text="✖ Cancel",
                            font=ctk.CTkFont(size=10, weight="bold"),
                            height=22,
                            width=65,
                            fg_color=BG_WINDOW,
                            hover_color=COLOR_DANGER_HOVER,
                            text_color=COLOR_DANGER,
                            corner_radius=4,
                            command=lambda i_id=it.item_id: self.queue_mgr.cancel_item(i_id)
                        ).pack(side="left", padx=2)

            else:
                # --- FIRST-TIME CARD CONSTRUCTION ---
                q_card = ctk.CTkFrame(
                    self.browse_queue_scroll,
                    fg_color=BG_CARD_SUBTLE,
                    border_width=1,
                    border_color=BORDER_COLOR,
                    corner_radius=10
                )
                q_card.pack(fill="x", pady=4, padx=4)

                # Row 1: format badge + status pill (side="right" FIRST) + title
                r1 = ctk.CTkFrame(q_card, fg_color="transparent")
                r1.pack(fill="x", padx=12, pady=(8, 2))

                fmt_badge = "🎵 MP3" if it.format_type == "audio_mp3" else ("🎧 M4A" if it.format_type == "audio_m4a" else "🎥 MP4")
                fmt_col = COLOR_GOLD if "audio" in it.format_type else COLOR_PRIMARY
                ctk.CTkLabel(
                    r1,
                    text=fmt_badge,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=fmt_col,
                    fg_color=BG_WINDOW,
                    corner_radius=4,
                    padx=6,
                    height=20
                ).pack(side="left", padx=(0, 8))

                # Pack status_pill to the right FIRST with stable width so title never jitters
                status_pill = ctk.CTkLabel(
                    r1,
                    text=st_text,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=st_col,
                    fg_color=BG_WINDOW,
                    corner_radius=4,
                    padx=6,
                    height=20,
                    width=175,
                    anchor="e"
                )
                status_pill.pack(side="right", padx=(8, 0))

                title_lbl = ctk.CTkLabel(
                    r1,
                    text=it.title,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=TEXT_PRIMARY,
                    anchor="w",
                    wraplength=480
                )
                title_lbl.pack(side="left", fill="x", expand=True)

                # Row 2: Progress Bar
                p_bar = ctk.CTkProgressBar(
                    q_card,
                    orientation="horizontal",
                    mode="determinate",
                    progress_color=bar_col,
                    fg_color=BG_WINDOW,
                    height=8,
                    corner_radius=4
                )
                p_bar.set(bar_pct)
                p_bar.pack(fill="x", padx=12, pady=4)

                # Row 3: stats info + action buttons
                r2 = ctk.CTkFrame(q_card, fg_color="transparent")
                r2.pack(fill="x", padx=12, pady=(0, 8))

                act_box = ctk.CTkFrame(r2, fg_color="transparent")
                act_box.pack(side="right")

                if it.status == "finished" and it.output_file and os.path.exists(it.output_file):
                    ctk.CTkButton(
                        act_box,
                        text="📂 Open File",
                        font=ctk.CTkFont(size=10, weight="bold"),
                        height=22,
                        width=78,
                        fg_color=BG_WINDOW,
                        hover_color=BG_CARD_HOVER,
                        text_color=COLOR_SUCCESS,
                        corner_radius=4,
                        command=lambda p=it.output_file: os.startfile(p)
                    ).pack(side="left", padx=2)
                elif it.status in ("queued", "downloading"):
                    ctk.CTkButton(
                        act_box,
                        text="✖ Cancel",
                        font=ctk.CTkFont(size=10, weight="bold"),
                        height=22,
                        width=65,
                        fg_color=BG_WINDOW,
                        hover_color=COLOR_DANGER_HOVER,
                        text_color=COLOR_DANGER,
                        corner_radius=4,
                        command=lambda i_id=it.item_id: self.queue_mgr.cancel_item(i_id)
                    ).pack(side="left", padx=2)

                info_lbl = ctk.CTkLabel(
                    r2,
                    text=info_text,
                    font=ctk.CTkFont(size=10),
                    text_color=TEXT_MUTED,
                    anchor="w"
                )
                info_lbl.pack(side="left", fill="x", expand=True)

                self.queue_card_widgets[it.item_id] = {
                    "card": q_card,
                    "status_pill": status_pill,
                    "p_bar": p_bar,
                    "info_lbl": info_lbl,
                    "act_box": act_box,
                    "last_st_text": st_text,
                    "last_st_col": st_col,
                    "last_bar_pct": bar_pct,
                    "last_info_text": info_text,
                    "last_status": it.status
                }

'''
    app_content = app_content[:start_idx] + new_refresh_method + app_content[end_idx:]
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    print("[OK] Replaced _refresh_queue_ui with smooth in-place widget caching")
else:
    print(f"[ERR] Markers not found: start={start_idx}, end={end_idx}")

print("Flicker fix successfully applied!")
