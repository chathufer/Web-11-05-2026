import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add state variables in __init__
old_init_state = """        self.last_clipboard_content = ""
        self._resize_timer: Optional[str] = None
        self.active_tab = "downloader" """

# Let's find via regex or substring
match_init = re.search(r'self\.last_clipboard_content\s*=\s*""\r?\n\s*self\._resize_timer:\s*Optional\[str\]\s*=\s*None\r?\n\s*self\.active_tab\s*=\s*"downloader"', content)
if match_init:
    rep_init = """self.last_clipboard_content = ""
        self._resize_timer: Optional[str] = None
        self._last_window_w: int = 0
        self._last_window_h: int = 0
        self._rendered_thumb_w: int = 0
        self.active_tab = "downloader" """
    content = content[:match_init.start()] + rep_init + content[match_init.end():]
    print("[OK] Added window dimension tracking variables to __init__")
else:
    print("[FAIL] Could not match init state")

# 2. Update bind("<Configure>") to include add="+"
match_bind = re.search(r'self\.bind\("<Configure>",\s*self\._on_window_configure\)', content)
if match_bind:
    content = content[:match_bind.start()] + 'self.bind("<Configure>", self._on_window_configure, add="+")' + content[match_bind.end():]
    print("[OK] Updated bind('<Configure>') with add='+'")
else:
    print("[FAIL] Could not match bind('<Configure>')")

# 3. Update _setup_responsive_geometry to set initial width and height
match_geom = re.search(r'self\.geometry\(f"\{ideal_w\}x\{ideal_h\}\+\{pos_x\}\+\{pos_y\}"\)', content)
if match_geom:
    rep_geom = """self._last_window_w = ideal_w
        self._last_window_h = ideal_h
        self.geometry(f"{ideal_w}x{ideal_h}+{pos_x}+{pos_y}")"""
    content = content[:match_geom.start()] + rep_geom + content[match_geom.end():]
    print("[OK] Updated _setup_responsive_geometry with initial dimensions")
else:
    print("[FAIL] Could not match _setup_responsive_geometry")

# 4. Replace _on_window_configure and _handle_window_resize
old_config_pattern = re.compile(
    r'def _on_window_configure\(self,\s*event\):.*?def _build_app_scaffold\(self\):',
    re.DOTALL
)

new_config_block = '''def _on_window_configure(self, event):
        """Debounced resize handler to adapt text wraplength and thumbnail scaling dynamically.
        CRITICAL SMOOTH DRAGGING OPTIMIZATION:
        Tkinter fires <Configure> on every single pixel of window movement (dragging across screen).
        Window movement changes X/Y coordinates, but DOES NOT change width or height.
        Filtering out move events immediately prevents thousands of redundant timer allocations,
        widget reconfigurations, and crashes during window dragging.
        """
        if event.widget != self:
            return

        w = event.width
        h = event.height

        # Fast exit: if width and height did not change (e.g. window is being moved/dragged), IGNORE!
        if getattr(self, "_last_window_w", None) == w and getattr(self, "_last_window_h", None) == h:
            return

        self._last_window_w = w
        self._last_window_h = h

        if self._resize_timer is not None:
            try:
                self.after_cancel(self._resize_timer)
            except Exception:
                pass
        self._resize_timer = self.after(160, self._handle_window_resize, w, h)

    def _handle_window_resize(self, width: int, height: int):
        self._resize_timer = None
        try:
            content_w = max(420, width - 260)
            thumb_w = 260 if width >= 920 else 200

            # 1. Update video title wrap length
            if hasattr(self, "preview_title") and self.preview_title.winfo_exists():
                dynamic_title_wrap = max(220, content_w - thumb_w - 60)
                self.preview_title.configure(wraplength=dynamic_title_wrap)

            # 2. Update playlist title wrap length
            if hasattr(self, "playlist_title") and self.playlist_title.winfo_exists():
                self.playlist_title.configure(wraplength=max(220, content_w - thumb_w - 60))

            # 3. Update thumbnail display size ONLY if size bucket actually changed
            if self.raw_thumbnail_pil and hasattr(self, "thumb_label") and self.thumb_label.winfo_exists():
                if getattr(self, "_rendered_thumb_w", 0) != thumb_w:
                    self._rendered_thumb_w = thumb_w
                    target_h = int(thumb_w * 9 / 16)
                    self._render_thumbnail(thumb_w, target_h)

            # 4. Update status wrap length
            if hasattr(self, "status_lbl") and self.status_lbl.winfo_exists():
                self.status_lbl.configure(wraplength=max(200, int(content_w * 0.45)))
        except Exception:
            pass

    # ---------------- UI Scaffold (Sidebar + Main Workspace) ----------------

    def _build_app_scaffold(self):'''

if old_config_pattern.search(content):
    content = old_config_pattern.sub(new_config_block, content, count=1)
    print("[OK] Replaced _on_window_configure and _handle_window_resize with high-performance version")
else:
    print("[FAIL] Could not match _on_window_configure block")

# 5. Optimize _render_thumbnail
old_render_thumb = re.compile(
    r'def _render_thumbnail\(self,\s*width:\s*int,\s*height:\s*int\):.*?def _on_format_changed',
    re.DOTALL
)

new_render_thumb = '''def _render_thumbnail(self, width: int, height: int):
        if not self.raw_thumbnail_pil:
            return
        try:
            self._rendered_thumb_w = width
            copy_img = self.raw_thumbnail_pil.copy()
            copy_img.thumbnail((width, height), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=copy_img, dark_image=copy_img, size=copy_img.size)
            self.cached_thumbnail_ctk = ctk_img
            if hasattr(self, "thumb_box") and self.thumb_box.winfo_exists():
                self.thumb_box.configure(width=width, height=height)
            if hasattr(self, "thumb_label") and self.thumb_label.winfo_exists():
                self.thumb_label.configure(image=ctk_img, text="")
        except Exception:
            pass

    # ---------------- Format & Options Handlers ----------------

    def _on_format_changed'''

if old_render_thumb.search(content):
    content = old_render_thumb.sub(new_render_thumb, content, count=1)
    print("[OK] Updated _render_thumbnail with guarded widget existence checks")
else:
    print("[FAIL] Could not match _render_thumbnail block")

# 6. Optimize _check_clipboard_loop to never block UI thread
old_clip_loop = re.compile(
    r'def _check_clipboard_loop\(self\):.*?def _show_clipboard_banner',
    re.DOTALL
)

new_clip_loop = '''def _check_clipboard_loop(self):
        if not self.config.get("auto_clipboard", True):
            return

        def bg_check():
            try:
                clip = pyperclip.paste()
                if clip:
                    clip = clip.strip()
                    if clip and clip != getattr(self, "last_clipboard_content", "") and is_valid_media_url(clip):
                        def on_valid_clip():
                            self.last_clipboard_content = clip
                            current_entry = self.url_var.get().strip()
                            if clip != current_entry:
                                self._show_clipboard_banner(clip)
                        self.after(0, on_valid_clip)
            except Exception:
                pass

        threading.Thread(target=bg_check, daemon=True).start()
        self.after(2000, self._check_clipboard_loop)

    def _show_clipboard_banner'''

if old_clip_loop.search(content):
    content = old_clip_loop.sub(new_clip_loop, content, count=1)
    print("[OK] Offloaded _check_clipboard_loop to background thread")
else:
    print("[FAIL] Could not match _check_clipboard_loop block")

# 7. Make CTkImage creation thread-safe in _load_browse_thumb_async
old_browse_thumb = re.compile(
    r'def _load_browse_thumb_async\(self,\s*thumb_url:\s*str,\s*label_widget:\s*ctk\.CTkLabel\):.*?threading\.Thread\(target=task,\s*daemon=True\)\.start\(\)',
    re.DOTALL
)

new_browse_thumb = '''def _load_browse_thumb_async(self, thumb_url: str, label_widget: ctk.CTkLabel):
        def task():
            try:
                resp = requests.get(thumb_url, timeout=6)
                if resp.status_code == 200:
                    img = Image.open(BytesIO(resp.content))
                    img.thumbnail((120, 68), Image.Resampling.LANCZOS)
                    def update():
                        try:
                            if label_widget.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                                label_widget.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.after(0, update)
            except Exception:
                pass
        threading.Thread(target=task, daemon=True).start()'''

if old_browse_thumb.search(content):
    content = old_browse_thumb.sub(new_browse_thumb, content, count=1)
    print("[OK] Made _load_browse_thumb_async thread-safe")
else:
    print("[FAIL] Could not match _load_browse_thumb_async block")

# 8. Make CTkImage creation thread-safe in pl_thumb_label
old_pl_thumb = re.compile(
    r'img_data\.thumbnail\(\(180,\s*100\),\s*Image\.Resampling\.LANCZOS\)\s*\r?\n\s*ctk_img\s*=\s*ctk\.CTkImage\(light_image=img_data,\s*dark_image=img_data,\s*size=img_data\.size\)\s*\r?\n\s*self\.after\(0,\s*lambda:\s*self\.pl_thumb_label\.configure\(image=ctk_img,\s*text=""\)\)'
)

new_pl_thumb = '''img_data.thumbnail((180, 100), Image.Resampling.LANCZOS)
                    def update_pl():
                        try:
                            if hasattr(self, "pl_thumb_label") and self.pl_thumb_label.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=img_data.size)
                                self.pl_thumb_label.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.after(0, update_pl)'''

if old_pl_thumb.search(content):
    content = old_pl_thumb.sub(new_pl_thumb, content, count=1)
    print("[OK] Made playlist thumbnail CTkImage instantiation thread-safe")
else:
    print("[FAIL] Could not match playlist thumbnail block")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[COMPLETE] app.py successfully optimized for smooth, non-crashing window movement!")
