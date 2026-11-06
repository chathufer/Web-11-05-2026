import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add queue import if not present
if "import queue" not in content:
    content = content.replace("import threading\n", "import threading\nimport queue\n")
    print("[OK] Added import queue")

# 2. Add _gui_queue initialization in __init__ and methods
old_init_part = 'self._rendered_thumb_w: int = 0'
new_init_part = '''self._rendered_thumb_w: int = 0
        self._gui_queue = queue.Queue()
        self.after(25, self._process_gui_queue)'''

if old_init_part in content and "self._gui_queue" not in content:
    content = content.replace(old_init_part, new_init_part, 1)
    print("[OK] Added _gui_queue and poll to __init__")

# 3. Add _process_gui_queue and run_on_ui_thread methods
dispatcher_methods = '''    # ---------------- Thread-Safe GUI Dispatcher ----------------

    def _process_gui_queue(self):
        """Processes callbacks scheduled by worker threads safely on the main Tkinter thread."""
        try:
            while True:
                fn, args, kwargs = self._gui_queue.get_nowait()
                try:
                    fn(*args, **kwargs)
                except Exception as e:
                    pass
        except queue.Empty:
            pass
        self.after(25, self._process_gui_queue)

    def run_on_ui_thread(self, fn, *args, **kwargs):
        """100% thread-safe dispatcher from any background thread to the main GUI thread."""
        self._gui_queue.put((fn, args, kwargs))

    # ---------------- Resolution & Geometry ----------------'''

if "def _process_gui_queue" not in content:
    content = content.replace("    # ---------------- Resolution & Geometry ----------------", dispatcher_methods, 1)
    print("[OK] Added _process_gui_queue and run_on_ui_thread methods")

# 4. In _fetch_video_info_threaded
old_fetch_task = '''        def task():
            try:
                info = self.downloader.fetch_info(url)
                self.after(0, self._on_info_fetched_success, info)
            except Exception as e:
                err_msg = str(e)
                self.after(0, self._on_info_fetched_error, err_msg)'''

new_fetch_task = '''        def task():
            try:
                info = self.downloader.fetch_info(url)
                self.run_on_ui_thread(self._on_info_fetched_success, info)
            except Exception as e:
                err_msg = str(e)
                self.run_on_ui_thread(self._on_info_fetched_error, err_msg)'''

if old_fetch_task in content:
    content = content.replace(old_fetch_task, new_fetch_task, 1)
    print("[OK] Updated _fetch_video_info_threaded with run_on_ui_thread")
else:
    print("[WARN] Could not find old_fetch_task")

# 5. In _load_thumbnail_threaded
old_thumb_task = '''    def _load_thumbnail_threaded(self, url: str):
        def task():
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    img_data = Image.open(BytesIO(resp.content))
                    self.raw_thumbnail_pil = img_data
                    self.after(0, self._render_thumbnail_auto)
            except Exception:
                pass

        threading.Thread(target=task, daemon=True).start()'''

new_thumb_task = '''    def _load_thumbnail_threaded(self, url: str):
        def task():
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    img_data = Image.open(BytesIO(resp.content))
                    self.raw_thumbnail_pil = img_data
                    self.run_on_ui_thread(self._render_thumbnail_auto)
            except Exception:
                pass

        threading.Thread(target=task, daemon=True).start()'''

if old_thumb_task in content:
    content = content.replace(old_thumb_task, new_thumb_task, 1)
    print("[OK] Updated _load_thumbnail_threaded with run_on_ui_thread")
else:
    print("[WARN] Could not find old_thumb_task")

# 6. In _load_playlist_thumb_threaded
old_pl_thumb = '''                    def update_pl():
                        try:
                            if hasattr(self, "pl_thumb_label") and self.pl_thumb_label.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=img_data.size)
                                self.pl_thumb_label.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.after(0, update_pl)'''

new_pl_thumb = '''                    def update_pl():
                        try:
                            if hasattr(self, "pl_thumb_label") and self.pl_thumb_label.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=img_data.size)
                                self.pl_thumb_label.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.run_on_ui_thread(update_pl)'''

if old_pl_thumb in content:
    content = content.replace(old_pl_thumb, new_pl_thumb, 1)
    print("[OK] Updated _load_playlist_thumb_threaded with run_on_ui_thread")
else:
    print("[WARN] Could not find old_pl_thumb")

# 7. In _load_browse_thumb_async
old_browse_thumb = '''                    def update():
                        try:
                            if label_widget.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                                label_widget.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.after(0, update)'''

new_browse_thumb = '''                    def update():
                        try:
                            if label_widget.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                                label_widget.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.run_on_ui_thread(update)'''

if old_browse_thumb in content:
    content = content.replace(old_browse_thumb, new_browse_thumb, 1)
    print("[OK] Updated _load_browse_thumb_async with run_on_ui_thread")
else:
    print("[WARN] Could not find old_browse_thumb")

# 8. In _execute_youtube_search
old_search_task = '''        def task():
            try:
                results = self.downloader.search_youtube(query, limit=20)
                self.after(0, self._on_search_results_loaded, results)
            except Exception as e:
                err_text = str(e)
                self.after(0, self._on_search_error, err_text)'''

new_search_task = '''        def task():
            try:
                results = self.downloader.search_youtube(query, limit=20)
                self.run_on_ui_thread(self._on_search_results_loaded, results)
            except Exception as e:
                err_text = str(e)
                self.run_on_ui_thread(self._on_search_error, err_text)'''

if old_search_task in content:
    content = content.replace(old_search_task, new_search_task, 1)
    print("[OK] Updated _execute_youtube_search with run_on_ui_thread")
else:
    print("[WARN] Could not find old_search_task")

# 9. In downloads and progress
content = content.replace("self.after(0, self._update_progress_ui, data)", "self.run_on_ui_thread(self._update_progress_ui, data)")
content = content.replace("self.after(0, self._on_download_success, out_path, format_type, quality)", "self.run_on_ui_thread(self._on_download_success, out_path, format_type, quality)")
content = content.replace("self.after(0, self._on_playlist_download_success, files, format_type, quality)", "self.run_on_ui_thread(self._on_playlist_download_success, files, format_type, quality)")
content = content.replace("self.after(0, self._on_download_error, err_text)", "self.run_on_ui_thread(self._on_download_error, err_text)")

# 10. In clipboard loop
content = content.replace("self.after(0, on_valid_clip)", "self.run_on_ui_thread(on_valid_clip)")

# 11. In queue manager threadsafe methods
content = content.replace("self.after(40, self._do_refresh_queue_ui)", "self.run_on_ui_thread(self._do_refresh_queue_ui)")
content = content.replace("self.after(0, on_done)", "self.run_on_ui_thread(on_done)")

# 12. In _on_info_fetched_success: ensure preview_content is packed and lifted, and thumb_label shows initial loading state
old_success_pack = '''            self.playlist_content.pack_forget()
            self.preview_content.pack(fill="both", expand=True)'''

new_success_pack = '''            self.playlist_content.pack_forget()
            self.preview_content.pack(fill="both", expand=True)
            self.preview_content.lift()
            if hasattr(self, "thumb_label") and self.thumb_label.winfo_exists():
                self.thumb_label.configure(image=None, text="⏳ Loading...", text_color=TEXT_MUTED)'''

if old_success_pack in content:
    content = content.replace(old_success_pack, new_success_pack, 1)
    print("[OK] Updated _on_info_fetched_success with lift and placeholder")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[COMPLETE] Successfully applied queue-based UI thread dispatcher!")
