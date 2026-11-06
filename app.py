"""
YouTube & TikTok Video Downloader PC App - v1.0 Turbo
Supports YouTube Videos, Shorts, TikTok (Without Watermark), and Full Playlists
Optimized for any screen resolution (720p, 1080p, 2K, 4K, Ultra-Wide)
"""

import os
import re
import sys
import json
import time
import shutil
import threading
import queue
import subprocess
import webbrowser
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any, List

import requests
from PIL import Image, ImageTk
import customtkinter as ctk
import pyperclip

from downloader import (
    YouTubeDownloader,
    CancelToken,
    is_valid_youtube_url,
    is_valid_youtube_playlist_url,
    is_valid_tiktok_url,
    is_valid_media_url,
    detect_url_type,
    get_ffmpeg_dir
)
from licensing import LicenseManager, get_hardware_id
from queue_manager import DownloadQueueManager, QueueItem

# ----------------- App Metadata & Paths -----------------
APP_NAME = "Media Downloader Pro"
APP_VERSION = "v1.0.0"
APP_VERSION_DISPLAY = "v1.0 Commercial Launch Edition"
CURRENT_VERSION_CODE = "1.0.0"

def parse_version_tuple(v_str: str) -> tuple:
    nums = [int(x) for x in re.findall(r'\d+', str(v_str))]
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])

def check_for_remote_update(current_ver: str = CURRENT_VERSION_CODE) -> tuple:
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
    return False, None

APP_SUBTITLE = "YouTube 4K, TikTok (No Watermark), Hi-Fi Audio & Full Playlists"

DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube Downloads")


def get_app_dir() -> str:
    """Return the base directory for app files."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir() -> str:
    """Return directory for persistent configs and history."""
    app_dir = get_app_dir()
    try:
        test_path = os.path.join(app_dir, ".write_test")
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        return app_dir
    except Exception:
        fallback = os.path.join(os.path.expanduser("~"), ".youtube_downloader")
        os.makedirs(fallback, exist_ok=True)
        return fallback


# ----------------- Design System Colors & Calm Palettes -----------------
# 6 Soothing, Eye-Friendly Color Themes for Prolonged Comfort
CALM_PALETTES = {
    "Ocean": {
        "name": "Calm Ocean",
        "primary": "#0EA5E9",
        "primary_hover": "#0284C7",
        "primary_subtle": ("#E0F2FE", "#0C2D48"),
        "accent": "#38BDF8",
        "accent_hover": "#0284C7",
        "accent_subtle": ("#E0F2FE", "#0C4A6E"),
        "bg_window": ("#F8FAFC", "#0B0F19"),
        "bg_sidebar": ("#FFFFFF", "#0F172A"),
        "bg_card": ("#FFFFFF", "#131C2E"),
        "bg_card_subtle": ("#F1F5F9", "#1B273D"),
        "bg_card_hover": ("#E2E8F0", "#24355A"),
        "border": ("#E2E8F0", "#1E2C4A"),
        "swatch": "#0EA5E9"
    },
    "Sage": {
        "name": "Nordic Sage",
        "primary": "#10B981",
        "primary_hover": "#059669",
        "primary_subtle": ("#D1FAE5", "#063D2B"),
        "accent": "#34D399",
        "accent_hover": "#059669",
        "accent_subtle": ("#ECFDF5", "#064E3B"),
        "bg_window": ("#F8FAFC", "#0A130F"),
        "bg_sidebar": ("#FFFFFF", "#0F1F19"),
        "bg_card": ("#FFFFFF", "#142A22"),
        "bg_card_subtle": ("#F0FDF4", "#1B372D"),
        "bg_card_hover": ("#DCFCE7", "#23473A"),
        "border": ("#E2E8F0", "#1D3F33"),
        "swatch": "#10B981"
    },
    "Lavender": {
        "name": "Twilight Lavender",
        "primary": "#8B5CF6",
        "primary_hover": "#7C3AED",
        "primary_subtle": ("#EDE9FE", "#25124D"),
        "accent": "#A78BFA",
        "accent_hover": "#7C3AED",
        "accent_subtle": ("#F5F3FF", "#2E1065"),
        "bg_window": ("#FAF5FF", "#0E0C1B"),
        "bg_sidebar": ("#FFFFFF", "#15122B"),
        "bg_card": ("#FFFFFF", "#1E1A3D"),
        "bg_card_subtle": ("#F3E8FF", "#282352"),
        "bg_card_hover": ("#E9D5FF", "#342E69"),
        "border": ("#E2E8F0", "#2E2757"),
        "swatch": "#8B5CF6"
    },
    "Amber": {
        "name": "Warm Sunset",
        "primary": "#F59E0B",
        "primary_hover": "#D97706",
        "primary_subtle": ("#FEF3C7", "#3B2205"),
        "accent": "#FBBF24",
        "accent_hover": "#D97706",
        "accent_subtle": ("#FFFBEB", "#451A03"),
        "bg_window": ("#FFFBEB", "#120F09"),
        "bg_sidebar": ("#FFFFFF", "#1A160D"),
        "bg_card": ("#FFFFFF", "#241F13"),
        "bg_card_subtle": ("#FEF3C7", "#332B1A"),
        "bg_card_hover": ("#FDE68A", "#423822"),
        "border": ("#E2E8F0", "#3B311B"),
        "swatch": "#F59E0B"
    },
    "Slate": {
        "name": "Minimal Slate",
        "primary": "#64748B",
        "primary_hover": "#475569",
        "primary_subtle": ("#F1F5F9", "#1E293B"),
        "accent": "#94A3B8",
        "accent_hover": "#475569",
        "accent_subtle": ("#F8FAFC", "#0F172A"),
        "bg_window": ("#F8FAFC", "#0B0F17"),
        "bg_sidebar": ("#FFFFFF", "#111827"),
        "bg_card": ("#FFFFFF", "#182234"),
        "bg_card_subtle": ("#F1F5F9", "#1F2D44"),
        "bg_card_hover": ("#E2E8F0", "#283956"),
        "border": ("#E2E8F0", "#22314B"),
        "swatch": "#64748B"
    },
    "Rose": {
        "name": "Soft Rose",
        "primary": "#FB7185",
        "primary_hover": "#E11D48",
        "primary_subtle": ("#FFE4E6", "#3D0D17"),
        "accent": "#FDA4AF",
        "accent_hover": "#E11D48",
        "accent_subtle": ("#FFF1F2", "#4C0519"),
        "bg_window": ("#FFF1F2", "#130A0D"),
        "bg_sidebar": ("#FFFFFF", "#1C0F14"),
        "bg_card": ("#FFFFFF", "#27151D"),
        "bg_card_subtle": ("#FFE4E6", "#351C27"),
        "bg_card_hover": ("#FECDD3", "#452533"),
        "border": ("#E2E8F0", "#3B1F2C"),
        "swatch": "#FB7185"
    }
}

# Tuple format: (Light Mode Color, Dark Mode Color) - Default Calm Ocean
BG_WINDOW = ("#F8FAFC", "#0B0F19")          # Soft obsidian navy
BG_SIDEBAR = ("#FFFFFF", "#0F172A")         # Deep slate navy sidebar
BG_CARD = ("#FFFFFF", "#131C2E")            # Frosted obsidian card surface
BG_CARD_SUBTLE = ("#F1F5F9", "#1B273D")     # Elevated calm panel
BG_CARD_HOVER = ("#E2E8F0", "#24355A")      # Soft interactive hover
BORDER_COLOR = ("#E2E8F0", "#1E2C4A")       # Modern calm slate border
BORDER_ACTIVE = ("#38BDF8", "#38BDF8")      # Radiant Sky Cyan active border
BORDER_CYAN = ("#00F2FE", "#00F2FE")        # Electric Cyan active border

COLOR_PRIMARY = "#0EA5E9"                   # Soothing Sky Blue / Cyan (Calm Ocean)
COLOR_PRIMARY_HOVER = "#0284C7"
COLOR_PRIMARY_SUBTLE = ("#E0F2FE", "#0C2D48")

COLOR_CYAN = "#00F2FE"                      # Electric Cyan
COLOR_TIKTOK = "#00F2FE"                    # Electric Neon Cyan
COLOR_TIKTOK_SUBTLE = ("#E0F2FE", "#052E3D")

COLOR_ACCENT = "#38BDF8"                    # Radiant Sky Blue
COLOR_ACCENT_HOVER = "#0284C7"
COLOR_ACCENT_SUBTLE = ("#E0F2FE", "#0C4A6E")

COLOR_GOLD = "#F59E0B"                      # Warm Amber Gold
COLOR_GOLD_HOVER = "#D97706"
COLOR_GOLD_SUBTLE = ("#FEF3C7", "#3B2205")

COLOR_SUCCESS = "#10B981"                   # Emerald Green
COLOR_SUCCESS_BG = ("#D1FAE5", "#063D2B")

COLOR_WARNING = "#F59E0B"                   # Amber Warning
COLOR_WARNING_BG = ("#FEF3C7", "#451A03")

COLOR_DANGER = "#EF4444"                    # Crimson Alert
COLOR_DANGER_HOVER = "#DC2626"

COLOR_PURPLE = "#8B5CF6"                    # Soft Violet
COLOR_PURPLE_SUBTLE = ("#EDE9FE", "#25124D")

TEXT_PRIMARY = ("#0F172A", "#F8FAFC")
TEXT_SECONDARY = ("#475569", "#94A3B8")
TEXT_MUTED = ("#94A3B8", "#64748B")
TEXT_MAIN = TEXT_PRIMARY



# ----------------- Persistent Storage -----------------
class ConfigManager:
    """Manages application settings persisted as JSON."""
    def __init__(self):
        self.file_path = os.path.join(get_data_dir(), "settings.json")
        self.data = {
            "download_dir": DEFAULT_DOWNLOAD_DIR,
            "theme": "Dark",
            "theme_palette": "Ocean",
            "ui_scale": "100%",
            "auto_clipboard": True,
            "default_format": "video"
        }
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()


class HistoryManager:
    """Manages session & persistent download history."""
    def __init__(self):
        self.file_path = os.path.join(get_data_dir(), "history.json")
        self.history: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass

    def add(self, title: str, file_path: str, format_type: str, quality: str = "", is_playlist: bool = False, count: int = 1):
        item = {
            "title": title,
            "file_path": file_path,
            "format_type": format_type,
            "quality": quality,
            "is_playlist": is_playlist,
            "item_count": count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.history.insert(0, item)
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.save()

    def remove(self, index: int):
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save()

    def clear(self):
        self.history = []
        self.save()


def clean_error_message(err_msg: str) -> str:
    """Format technical raw download/fetch error strings into polished human-readable messages."""
    if not err_msg:
        return "Download error occurred"
    text = str(err_msg).strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        for l in lines:
            if "error:" in l.lower() or "exception:" in l.lower():
                text = l
                break
        else:
            text = lines[0]

    import re
    text = re.sub(r'^[a-zA-Z0-9_.]*Error:\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(?:ERROR|Error):\s*', '', text)
    text = re.sub(r'^\[[a-zA-Z0-9_:-]+\]\s*', '', text)
    text = re.sub(r'^(?:ERROR|Error):\s*', '', text)

    low = text.lower()
    if '1008 bytes read' in low or 'incomplete read' in low or 'connection reset' in low:
        text = 'Network connection interrupted by host. Please retry download.'
    elif 'video unavailable' in low:
        text = 'Video is unavailable or has been removed.'
    elif 'private video' in low:
        text = 'This video is private and cannot be downloaded.'
    elif 'sign in' in low or 'age-restricted' in low:
        text = 'Video requires YouTube login or is age-restricted.'
    elif 'ffmpeg' in low and 'not found' in low:
        text = 'FFmpeg media converter was not found.'
    elif 'no space' in low or 'disk full' in low:
        text = 'Not enough disk space on target drive.'
    elif 'permission denied' in low:
        text = 'Permission denied saving to destination folder.'

    text = text.strip()
    if len(text) > 75:
        text = text[:72] + '...'
    return text


def locate_in_explorer(file_path: str):
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

# ----------------- Main Application Window -----------------
class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Managers & State
        self.config = ConfigManager()
        self.history_mgr = HistoryManager()
        self.downloader = YouTubeDownloader()
        self.license_mgr = LicenseManager()

        self.current_video_info: Optional[Dict[str, Any]] = None
        self.active_cancel_token: Optional[CancelToken] = None
        self.is_downloading = False
        self.is_fetching = False
        self.last_fetched_url: str = ""
        self.last_downloaded_file: Optional[str] = None
        self.last_downloaded_folder: Optional[str] = None

        self.raw_thumbnail_pil: Optional[Image.Image] = None
        self.cached_thumbnail_ctk: Optional[ctk.CTkImage] = None

        # Playlist Selection State
        self.playlist_item_vars: Dict[int, ctk.BooleanVar] = {}

        self.download_dir = self.config.get("download_dir", DEFAULT_DOWNLOAD_DIR)
        os.makedirs(self.download_dir, exist_ok=True)

        self.last_clipboard_content = ""
        self._resize_timer: Optional[str] = None
        self._last_window_w: int = 0
        self._last_window_h: int = 0
        self._rendered_thumb_w: int = 0
        self._gui_queue = queue.Queue()
        self.after(25, self._process_gui_queue)
        self.active_tab = "downloader" 

        # Queue Manager & Browse Search State
        self.queue_mgr = DownloadQueueManager(
            downloader=self.downloader,
            on_queue_updated=self._on_queue_updated_threadsafe,
            on_item_finished=self._on_queue_item_finished_threadsafe,
            max_concurrent=3
        )
        self.browse_search_results = []
        self.browse_item_vars = {}
        self.browse_thumb_images = {}
        self.is_searching_browse = False
        self.queue_card_widgets = {}
        self._queue_refresh_scheduled = False

        # Apply Appearance & Scaling
        initial_theme = self.config.get("theme", "Dark")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")

        self.current_palette_key = self.config.get("theme_palette", "Ocean")
        self._load_palette_constants(self.current_palette_key)

        self._apply_ui_scaling(self.config.get("ui_scale", "100%"))

        # Setup Window Title & Adaptive Responsive Geometry
        self.title(f"{APP_NAME} {APP_VERSION}")
        self._setup_responsive_geometry()

        # Window Icon
        self._setup_window_icon()

        # Build Main UI Components
        self._build_app_scaffold()

        # Update License UI Badges & Status
        self._update_license_ui()

        # Background silent license validation & website backend trial synchronization
        def bg_verify():
            self.license_mgr.verify_background()
            self.run_on_ui_thread(self._update_license_ui)
        threading.Thread(target=bg_verify, daemon=True).start()

        # Background silent check for newer version releases
        self.latest_available_release = None
        threading.Thread(target=self._check_for_updates_background, daemon=True).start()

        # Bind Resize Listener for Dynamic Wrap and Layout Adaptation
        self.bind("<Configure>", self._on_window_configure, add="+")

        # Start Clipboard Monitor (if enabled)
        if self.config.get("auto_clipboard", True):
            self.after(600, self._check_clipboard_loop)

        # Switch to Downloader Tab by Default
        self._switch_tab("downloader")

    # ---------------- Thread-Safe GUI Dispatcher ----------------

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

    # ---------------- Resolution & Geometry ----------------

    def _setup_responsive_geometry(self):
        """Calculates optimal window size for any screen resolution (720p, 1080p, 1440p, 4K, Ultra-Wide)."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        ideal_w = min(1140, max(760, int(screen_w * 0.70)))
        ideal_h = min(840, max(560, int(screen_h * 0.82)))

        pos_x = max(0, (screen_w // 2) - (ideal_w // 2))
        pos_y = max(0, (screen_h // 2) - (ideal_h // 2) - 20)

        self._last_window_w = ideal_w
        self._last_window_h = ideal_h
        self.geometry(f"{ideal_w}x{ideal_h}+{pos_x}+{pos_y}")
        self.minsize(700, 520)

    def _setup_window_icon(self):
        icon_path = os.path.join(get_app_dir(), "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _apply_ui_scaling(self, scale_str: str):
        """Sets CustomTkinter global widget scaling for high-DPI or low-DPI displays."""
        scale_map = {
            "85% (Compact)": 0.85,
            "85%": 0.85,
            "100% (Standard)": 1.0,
            "100%": 1.0,
            "115% (Comfortable)": 1.15,
            "115%": 1.15,
            "125% (Large)": 1.25,
            "125%": 1.25,
        }
        factor = scale_map.get(scale_str, 1.0)
        try:
            ctk.set_widget_scaling(factor)
        except Exception:
            pass

    def _on_window_configure(self, event):
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

    def _build_app_scaffold(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed
        self.grid_columnconfigure(1, weight=1)  # Content expands

        # 1. Left Navigation Sidebar
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=210,
            corner_radius=0,
            fg_color=BG_SIDEBAR,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self._build_sidebar_content(self.sidebar_frame)

        # 2. Right Main Content Workspace
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_WINDOW)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Build Views
        self._build_downloader_view()
        self._build_browse_view()
        self._build_history_view()
        self._build_settings_view()

    def _build_sidebar_content(self, parent):
        # Brand Logo & Title Header
        brand_frame = ctk.CTkFrame(parent, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(18, 12))

        logo_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_box.pack(side="left")

        self.logo_icon = ctk.CTkLabel(
            logo_box,
            text=" 👑 ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF",
            fg_color=COLOR_PRIMARY,
            corner_radius=10,
            width=38,
            height=38
        )
        self.logo_icon.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left")

        title_row = ctk.CTkFrame(title_box, fg_color="transparent")
        title_row.pack(anchor="w")

        title_lbl = ctk.CTkLabel(
            title_row,
            text="DOWNLOADER",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_lbl.pack(side="left")

        title_pro = ctk.CTkLabel(
            title_row,
            text=" PRO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_GOLD
        )
        title_pro.pack(side="left")

        sub_lbl = ctk.CTkLabel(
            title_box,
            text="TURBO STUDIO EDITION",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLOR_CYAN
        )
        sub_lbl.pack(anchor="w")

        # Supported Platforms Chips Pill
        platforms_pill = ctk.CTkLabel(
            parent,
            text="▶ YouTube 4K  •  📱 TikTok Clean  •  📑 Playlists",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=COLOR_ACCENT,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=8,
            height=28
        )
        platforms_pill.pack(fill="x", padx=12, pady=(0, 16))

        # Nav Buttons Container
        self.nav_btns_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.nav_btns_frame.pack(fill="x", padx=10, expand=True, anchor="n")

        self.nav_btn_downloader = self._create_nav_button(
            self.nav_btns_frame,
            text="  ⚡  Turbo Downloader",
            command=lambda: self._switch_tab("downloader")
        )
        self.nav_btn_downloader.pack(fill="x", pady=4)

        self.nav_btn_browse = self._create_nav_button(
            self.nav_btns_frame,
            text="  🌐  Browse & Search",
            command=lambda: self._switch_tab("browse")
        )
        self.nav_btn_browse.pack(fill="x", pady=4)

        self.nav_btn_history = self._create_nav_button(
            self.nav_btns_frame,
            text="  🕒  Media Library & Vault",
            command=lambda: self._switch_tab("history")
        )
        self.nav_btn_history.pack(fill="x", pady=4)

        self.nav_btn_settings = self._create_nav_button(
            self.nav_btns_frame,
            text="  ⚙️  Studio Preferences",
            command=lambda: self._switch_tab("settings")
        )
        self.nav_btn_settings.pack(fill="x", pady=4)

        # Bottom System Info & Theme Toggle
        bottom_frame = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=14)

        # Pro Subscription Card in Sidebar (packed above bottom_frame)
        self.sidebar_pro_card = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_GOLD
        )
        self.sidebar_pro_card.pack(fill="x", side="bottom", padx=10, pady=(0, 10))

        sp_head = ctk.CTkFrame(self.sidebar_pro_card, fg_color="transparent")
        sp_head.pack(fill="x", padx=10, pady=(8, 2))

        self.sidebar_pro_badge = ctk.CTkLabel(
            sp_head,
            text="⭐ FREE EDITION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_GOLD
        )
        self.sidebar_pro_badge.pack(side="left")

        self.sidebar_pro_desc = ctk.CTkLabel(
            self.sidebar_pro_card,
            text="Unlock 4K 60fps, Playlists & Multi-thread Boost",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
            wraplength=170,
            justify="left"
        )
        self.sidebar_pro_desc.pack(anchor="w", padx=10, pady=(0, 8))

        self.sidebar_pro_btn = ctk.CTkButton(
            self.sidebar_pro_card,
            text="⚡ Activate Pro Key",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=30,
            fg_color=COLOR_GOLD_HOVER,
            hover_color=COLOR_GOLD,
            text_color="#FFFFFF",
            corner_radius=8,
            command=self._open_activation_dialog
        )
        self.sidebar_pro_btn.pack(fill="x", padx=10, pady=(0, 10))

        ffmpeg_ok = bool(get_ffmpeg_dir())
        ff_color = COLOR_SUCCESS if ffmpeg_ok else COLOR_WARNING
        ff_text = "🟢 FFmpeg Hardware Accel Active" if ffmpeg_ok else "🟡 FFmpeg Portable Active"
        self.ffmpeg_badge = ctk.CTkLabel(
            bottom_frame,
            text=ff_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=ff_color
        )
        self.ffmpeg_badge.pack(anchor="w", padx=12, pady=(10, 4))

        self.theme_switch = ctk.CTkSwitch(
            bottom_frame,
            text="Dark Obsidian",
            font=ctk.CTkFont(size=11),
            command=self._on_theme_switched,
            onvalue="Dark",
            offvalue="Light"
        )
        current_theme = self.config.get("theme", "Dark")
        if current_theme == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
            self.theme_switch.configure(text="Light Mode")
        self.theme_switch.pack(anchor="w", padx=12, pady=(4, 6))

        # Sidebar Palette Customizer
        ctk.CTkLabel(
            bottom_frame,
            text="🎨 Theme Color Palette:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(4, 2))

        palette_options = [
            "🌊 Calm Ocean",
            "🌿 Nordic Sage",
            "🔮 Twilight Lavender",
            "🌅 Warm Sunset",
            "🩶 Minimal Slate",
            "🌸 Soft Rose"
        ]
        self.sidebar_palette_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=palette_options,
            font=ctk.CTkFont(size=11),
            height=28,
            corner_radius=6,
            fg_color=BG_CARD,
            button_color=COLOR_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._on_palette_menu_selected
        )
        disp_map = {
            "Ocean": "🌊 Calm Ocean",
            "Sage": "🌿 Nordic Sage",
            "Lavender": "🔮 Twilight Lavender",
            "Amber": "🌅 Warm Sunset",
            "Slate": "🩶 Minimal Slate",
            "Rose": "🌸 Soft Rose"
        }
        self.sidebar_palette_menu.set(disp_map.get(self.current_palette_key, "🌊 Calm Ocean"))
        self.sidebar_palette_menu.pack(fill="x", padx=12, pady=(0, 10))

    def _create_nav_button(self, parent, text: str, command):
        return ctk.CTkButton(
            parent,
            text=text,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            corner_radius=10,
            height=40,
            command=command
        )

    def _switch_tab(self, tab_name: str):
        self.active_tab = tab_name

        nav_map = {
            "downloader": self.nav_btn_downloader,
            "browse": self.nav_btn_browse,
            "history": self.nav_btn_history,
            "settings": self.nav_btn_settings
        }
        for name, btn in nav_map.items():
            if name == tab_name:
                btn.configure(
                    fg_color=COLOR_PRIMARY_SUBTLE,
                    text_color=COLOR_PRIMARY,
                    border_width=1,
                    border_color=COLOR_PRIMARY
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=TEXT_SECONDARY,
                    border_width=0
                )

        self.view_downloader.grid_forget()
        if hasattr(self, "view_browse") and self.view_browse.winfo_exists():
            self.view_browse.grid_forget()
        self.view_history.grid_forget()
        self.view_settings.grid_forget()

        if tab_name == "downloader":
            self.view_downloader.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "browse":
            if hasattr(self, "view_browse"):
                self.view_browse.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "history":
            self._refresh_history_ui()
            self.view_history.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "settings":
            self.view_settings.grid(row=0, column=0, sticky="nsew")

    # ---------------- 1. Downloader Tab View ----------------

    def _build_downloader_view(self):
        self.view_downloader = ctk.CTkScrollableFrame(
            self.content_container,
            corner_radius=0,
            fg_color="transparent"
        )

        content_pad = 18

        # 1. Top Header Banner
        header_card = ctk.CTkFrame(self.view_downloader, fg_color="transparent")
        header_card.pack(fill="x", padx=content_pad, pady=(16, 12))

        header_left = ctk.CTkFrame(header_card, fg_color="transparent")
        header_left.pack(side="left", fill="both", expand=True)

        head_title_row = ctk.CTkFrame(header_left, fg_color="transparent")
        head_title_row.pack(anchor="w")

        head_icon = ctk.CTkLabel(
            head_title_row,
            text="⚡",
            font=ctk.CTkFont(size=20),
            text_color=COLOR_GOLD
        )
        head_icon.pack(side="left", padx=(0, 6))

        head_title = ctk.CTkLabel(
            head_title_row,
            text="High-Speed Media Downloader",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        head_title.pack(side="left")

        head_sub = ctk.CTkLabel(
            header_left,
            text=APP_SUBTITLE,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        head_sub.pack(anchor="w", pady=(2, 0))

        # Pro Status / Upgrade CTA in Header
        header_right = ctk.CTkFrame(header_card, fg_color="transparent")
        header_right.pack(side="right", padx=(10, 0))

        self.header_pro_btn = ctk.CTkButton(
            header_right,
            text="⭐ Activate Pro Key",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_GOLD_HOVER,
            hover_color=COLOR_GOLD,
            text_color="#FFFFFF",
            corner_radius=10,
            height=36,
            command=self._open_activation_dialog
        )
        self.header_pro_btn.pack(side="right")

        # 1.5 Dynamic Software Update Notification Banner (Shows when a newer version is published)
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

        # 2. Clipboard Toast Banner (Appears dynamically if clipboard contains media link)
        self.clipboard_banner = ctk.CTkFrame(
            self.view_downloader,
            fg_color=COLOR_ACCENT_SUBTLE,
            border_width=1,
            border_color=COLOR_ACCENT,
            corner_radius=8
        )
        self.clipboard_label = ctk.CTkLabel(
            self.clipboard_banner,
            text="📋 Media link detected on clipboard!",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.clipboard_label.pack(side="left", padx=(12, 8), pady=8)

        self.clipboard_auto_btn = ctk.CTkButton(
            self.clipboard_banner,
            text="Auto-Paste & Fetch",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=130,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self._on_clipboard_banner_clicked
        )
        self.clipboard_auto_btn.pack(side="left", padx=4, pady=8)

        self.clipboard_dismiss_btn = ctk.CTkButton(
            self.clipboard_banner,
            text="✕",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=28,
            height=28,
            fg_color="transparent",
            text_color=COLOR_ACCENT,
            hover_color=BG_CARD_HOVER,
            command=self._dismiss_clipboard_banner
        )
        self.clipboard_dismiss_btn.pack(side="right", padx=8, pady=8)

        # 2.5 Promotional 7-Day Free Trial Banner
        self._build_promo_banner(self.view_downloader, padx=content_pad)

        # 3. Streamlined URL Input Section
        self._build_input_section(self.view_downloader, padx=content_pad)

        # 4. Dynamic Media Preview Section (Single Video or Full Playlist Hub)
        self._build_preview_section(self.view_downloader, padx=content_pad)

        # 5. Format & Quality Configuration Card
        self._build_options_section(self.view_downloader, padx=content_pad)

        # 6. Action, Telemetry HUD & Progress Section
        self._build_progress_section(self.view_downloader, padx=content_pad)

    def _build_promo_banner(self, parent, padx: int):
        """Promotional banner highlighting the 7-Day Free Trial for 1 PC."""
        self.promo_trial_banner = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color="#00F2FE",
            corner_radius=12
        )
        self.promo_trial_padx = padx

        left_box = ctk.CTkFrame(self.promo_trial_banner, fg_color="transparent")
        left_box.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        self.promo_banner_title = ctk.CTkLabel(
            left_box,
            text="🎁 SPECIAL PROMOTION: Try Pro 100% Free for 7 Days!",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00F2FE"
        )
        self.promo_banner_title.pack(anchor="w")

        self.promo_banner_sub = ctk.CTkLabel(
            left_box,
            text="Unlock 4K 60FPS video, unlimited playlists & 320kbps MP3s on this PC (No credit card required).",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.promo_banner_sub.pack(anchor="w", pady=(2, 0))

        self.promo_banner_btn = ctk.CTkButton(
            self.promo_trial_banner,
            text="⚡ Start 7-Day Free Trial",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
            fg_color="#0284C7",
            hover_color="#0369A1",
            corner_radius=8,
            command=self._on_start_trial_promo_clicked
        )
        self.promo_banner_btn.pack(side="right", padx=(10, 14), pady=10)

    def _on_start_trial_promo_clicked(self):
        """1-Click Start 7-Day Free Trial handler."""
        if hasattr(self, "promo_banner_btn") and self.promo_banner_btn.winfo_exists():
            self.promo_banner_btn.configure(state="disabled", text="Activating Trial...")

        def worker():
            ok, msg = self.license_mgr.start_trial()
            def on_done():
                self._update_license_ui()
                self._on_format_changed(self.format_seg.get())
                if ok:
                    self._show_info_dialog("7-Day Free Trial Activated", msg)
                else:
                    self._show_info_dialog("Free Trial Notice", msg, is_error=True)
            self.after(100, on_done)

        threading.Thread(target=worker, daemon=True).start()

    def _show_info_dialog(self, title: str, message: str, is_error: bool = False):
        """Show clean modal dialog with informative message."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("460x220")
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 460) // 2
        y = self.winfo_y() + (self.winfo_height() - 220) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(dialog, fg_color=BG_WINDOW, corner_radius=0)
        f.pack(fill="both", expand=True, padx=20, pady=20)

        icon_color = COLOR_DANGER if is_error else COLOR_SUCCESS
        header_text = f"✖ {title}" if is_error else f"✔ {title}"

        ctk.CTkLabel(
            f,
            text=header_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=icon_color
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            f,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_PRIMARY if not is_error else COLOR_DANGER,
            justify="left",
            wraplength=410
        ).pack(anchor="w", pady=(0, 20))

        btn = ctk.CTkButton(
            f,
            text="OK",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_PRIMARY if not is_error else BG_CARD_SUBTLE,
            hover_color=COLOR_PRIMARY_HOVER if not is_error else BG_CARD_HOVER,
            width=100,
            height=36,
            corner_radius=8,
            command=dialog.destroy
        )
        btn.pack(side="right")

    def _build_input_section(self, parent, padx: int):
        self.input_card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.input_card.pack(fill="x", padx=padx, pady=(0, 14), ipady=6)
        input_card = self.input_card

        lbl_row = ctk.CTkFrame(self.input_card, fg_color="transparent")
        lbl_row.pack(fill="x", padx=16, pady=(12, 6))

        lbl = ctk.CTkLabel(
            lbl_row,
            text="Media Stream URL (YouTube, TikTok Clean, Shorts, or Playlist):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl.pack(side="left")

        self.auto_badge = ctk.CTkLabel(
            lbl_row,
            text="● SMART AUTO-CAPTURE ACTIVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLOR_SUCCESS,
            fg_color=COLOR_SUCCESS_BG,
            corner_radius=8,
            height=22,
            padx=10
        )
        self.auto_badge.pack(side="right")

        # Input Row
        row = ctk.CTkFrame(self.input_card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 8))

        self.url_var = ctk.StringVar()
        self.url_var.trace_add("write", self._on_url_entry_changed)

        self.url_entry = ctk.CTkEntry(
            row,
            textvariable=self.url_var,
            placeholder_text="🔗 Paste YouTube, TikTok (No Watermark), or Playlist link here...",
            font=ctk.CTkFont(size=13),
            height=44,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_CARD_SUBTLE
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.paste_btn = ctk.CTkButton(
            row,
            text="📋 Paste Link",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=130,
            height=44,
            corner_radius=10,
            command=self._on_paste_button_clicked
        )
        self.paste_btn.pack(side="left", padx=(0, 6))

        self.clear_btn = ctk.CTkButton(
            row,
            text="✕",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=44,
            height=44,
            corner_radius=10,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            command=self._on_clear_clicked
        )
        self.clear_btn.pack(side="left")

        # Quick Format Indicator Pills underneath input
        pills_row = ctk.CTkFrame(self.input_card, fg_color="transparent")
        pills_row.pack(fill="x", padx=16, pady=(2, 8))

        pills = [
            ("▶ 4K 60FPS Video", COLOR_PRIMARY),
            ("📱 TikTok 100% Clean", COLOR_TIKTOK),
            ("🎵 Studio 320k MP3", COLOR_GOLD),
            ("📑 Batch Playlist Grabber", COLOR_PURPLE)
        ]
        for p_text, p_col in pills:
            p_badge = ctk.CTkLabel(
                pills_row,
                text=p_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=p_col,
                fg_color=BG_CARD_SUBTLE,
                corner_radius=6,
                padx=8,
                pady=2
            )
            p_badge.pack(side="left", padx=(0, 6))

        # Feedback/status message below entry
        self.input_msg_lbl = ctk.CTkLabel(
            self.input_card,
            text="✨ Pro Tip: Simply copy any link — it auto-detects, extracts metadata, and unlocks maximum bitrate streams!",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.input_msg_lbl.pack(anchor="w", padx=16, pady=(0, 6))

    def _build_preview_section(self, parent, padx: int):
        self.preview_card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.preview_card.pack(fill="x", padx=padx, pady=(0, 14), ipady=4)

        # 1. Idle Placeholder State
        self.preview_placeholder = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        self.preview_placeholder.pack(fill="x", pady=24)

        ph_icon = ctk.CTkLabel(
            self.preview_placeholder,
            text="🎬",
            font=ctk.CTkFont(size=36)
        )
        ph_icon.pack(pady=(0, 6))

        ph_title = ctk.CTkLabel(
            self.preview_placeholder,
            text="MEDIA STUDIO DECK READY",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        ph_title.pack()

        ph_desc = ctk.CTkLabel(
            self.preview_placeholder,
            text="Paste any YouTube video, TikTok (No Watermark), Shorts, or full Playlist link above to extract high-bitrate streams",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        ph_desc.pack(pady=(3, 14))

        # Supported Feature Badges Pill Row
        pills_row = ctk.CTkFrame(self.preview_placeholder, fg_color="transparent")
        pills_row.pack()

        for tag, tag_col in [
            ("📱 TikTok 100% Clean", COLOR_TIKTOK),
            ("📑 Full Playlist Batch", COLOR_PURPLE),
            ("👑 4K UHD 60FPS", COLOR_GOLD),
            ("⚡ Multi-Thread Turbo", COLOR_PRIMARY),
            ("🎵 Studio MP3 320k", COLOR_SUCCESS)
        ]:
            tag_lbl = ctk.CTkLabel(
                pills_row,
                text=tag,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=tag_col,
                fg_color=BG_CARD_SUBTLE,
                corner_radius=8,
                padx=10,
                pady=4
            )
            tag_lbl.pack(side="left", padx=4)

        # 2. Loaded Single Video Preview Content
        self.preview_content = ctk.CTkFrame(self.preview_card, fg_color="transparent")

        # Left: Thumbnail Box
        self.thumb_box = ctk.CTkFrame(
            self.preview_content,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
            width=260,
            height=146
        )
        self.thumb_box.pack(side="left", padx=(14, 14), pady=12)
        self.thumb_box.pack_propagate(False)

        self.thumb_label = ctk.CTkLabel(self.thumb_box, text="")
        self.thumb_label.place(relx=0.5, rely=0.5, anchor="center")

        # Right: Video Details Info
        self.details_box = ctk.CTkFrame(self.preview_content, fg_color="transparent")
        self.details_box.pack(side="left", fill="both", expand=True, padx=(0, 14), pady=10)

        self.preview_title = ctk.CTkLabel(
            self.details_box,
            text="Video Title",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_PRIMARY,
            wraplength=460,
            justify="left"
        )
        self.preview_title.pack(anchor="w", pady=(0, 6))

        # Channel & Quality Badges Row
        channel_row = ctk.CTkFrame(self.details_box, fg_color="transparent")
        channel_row.pack(anchor="w", pady=(0, 6))

        self.preview_channel = ctk.CTkLabel(
            channel_row,
            text="✔ Creator Name",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.preview_channel.pack(side="left", padx=(0, 10))

        self.max_res_badge = ctk.CTkLabel(
            channel_row,
            text="👑 4K UHD 60FPS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=COLOR_PRIMARY,
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.max_res_badge.pack(side="left")

        # Metadata Row
        meta_row = ctk.CTkFrame(self.details_box, fg_color="transparent")
        meta_row.pack(anchor="w", pady=(0, 8))

        self.preview_duration = ctk.CTkLabel(
            meta_row,
            text="⏱ 00:00",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        )
        self.preview_duration.pack(side="left", padx=(0, 14))

        self.preview_views = ctk.CTkLabel(
            meta_row,
            text="👁 0 views",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        )
        self.preview_views.pack(side="left", padx=(0, 14))

        self.preview_date = ctk.CTkLabel(
            meta_row,
            text="📅 Date",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        )
        self.preview_date.pack(side="left")

        # Action Buttons Row
        action_btn_row = ctk.CTkFrame(self.details_box, fg_color="transparent")
        action_btn_row.pack(anchor="w")

        self.open_web_btn = ctk.CTkButton(
            action_btn_row,
            text="🌐 Watch Online",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=130,
            height=30,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_CARD_HOVER,
            command=self._open_in_browser
        )
        self.open_web_btn.pack(side="left", padx=(0, 8))

        self.copy_link_btn = ctk.CTkButton(
            action_btn_row,
            text="📋 Copy Link",
            font=ctk.CTkFont(size=11),
            width=90,
            height=30,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            command=self._copy_video_link
        )
        self.copy_link_btn.pack(side="left")
        self.copy_link_btn.pack(side="left")

        # 3. Loaded Playlist Hub Content (Displayed when URL is a playlist)
        self.playlist_content = ctk.CTkFrame(self.preview_card, fg_color="transparent")

        # Top Playlist Header Row
        pl_head_row = ctk.CTkFrame(self.playlist_content, fg_color="transparent")
        pl_head_row.pack(fill="x", padx=14, pady=(12, 10))

        # Left: Playlist Thumbnail
        self.pl_thumb_box = ctk.CTkFrame(
            pl_head_row,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR,
            width=180,
            height=100
        )
        self.pl_thumb_box.pack(side="left", padx=(0, 14))
        self.pl_thumb_box.pack_propagate(False)

        self.pl_thumb_label = ctk.CTkLabel(self.pl_thumb_box, text="📑 Playlist")
        self.pl_thumb_label.place(relx=0.5, rely=0.5, anchor="center")

        # Right: Playlist Title & Stats
        pl_info_box = ctk.CTkFrame(pl_head_row, fg_color="transparent")
        pl_info_box.pack(side="left", fill="both", expand=True)

        self.playlist_badge = ctk.CTkLabel(
            pl_info_box,
            text="📑 FULL PLAYLIST DETECTED",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLOR_PRIMARY,
            fg_color=COLOR_PRIMARY_SUBTLE,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.playlist_badge.pack(anchor="w", pady=(0, 4))

        self.playlist_title = ctk.CTkLabel(
            pl_info_box,
            text="Playlist Title",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_PRIMARY,
            wraplength=460,
            justify="left"
        )
        self.playlist_title.pack(anchor="w", pady=(0, 4))

        self.playlist_meta = ctk.CTkLabel(
            pl_info_box,
            text="👤 Creator Name • 20 Videos",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.playlist_meta.pack(anchor="w")

        # Interactive Video Selection List inside Playlist
        self.pl_list_card = ctk.CTkFrame(
            self.playlist_content,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.pl_list_card.pack(fill="x", padx=14, pady=(0, 10))

        # Selection bar controls
        ctrl_bar = ctk.CTkFrame(self.pl_list_card, fg_color="transparent")
        ctrl_bar.pack(fill="x", padx=10, pady=(8, 4))

        self.pl_select_count_lbl = ctk.CTkLabel(
            ctrl_bar,
            text="Videos to Download: 20 of 20 selected",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.pl_select_count_lbl.pack(side="left")

        select_all_btn = ctk.CTkButton(
            ctrl_bar,
            text="☑ Select All",
            font=ctk.CTkFont(size=11),
            width=80,
            height=26,
            fg_color=BG_CARD,
            text_color=TEXT_PRIMARY,
            hover_color=BG_CARD_HOVER,
            command=self._select_all_playlist_items
        )
        select_all_btn.pack(side="right", padx=(4, 0))

        deselect_all_btn = ctk.CTkButton(
            ctrl_bar,
            text="☐ Deselect All",
            font=ctk.CTkFont(size=11),
            width=90,
            height=26,
            fg_color=BG_CARD,
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            command=self._deselect_all_playlist_items
        )
        deselect_all_btn.pack(side="right")

        # Scrollable list of items
        self.pl_items_scroll = ctk.CTkScrollableFrame(
            self.pl_list_card,
            height=130,
            fg_color="transparent"
        )
        self.pl_items_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_options_section(self, parent, padx: int):
        self.options_card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.options_card.pack(fill="x", padx=padx, pady=(0, 14), ipady=6)

        card_title_row = ctk.CTkFrame(self.options_card, fg_color="transparent")
        card_title_row.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            card_title_row,
            text="⚡ Output Format & Audio-Visual Quality Engine",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkLabel(
            card_title_row,
            text="PRO PRESETS ACTIVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLOR_GOLD,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=6,
            padx=8,
            pady=2
        ).pack(side="right")

        # Format & Quality Matrix Row
        grid_frame = ctk.CTkFrame(self.options_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=16, pady=(0, 10))

        # Col 1: Format Selector
        col1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))

        f_lbl = ctk.CTkLabel(
            col1,
            text="Media Format:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        f_lbl.pack(anchor="w", pady=(0, 4))

        self.format_seg = ctk.CTkSegmentedButton(
            col1,
            values=["🎥 Video (MP4)", "🎵 Music (MP3)", "🎧 Audio (M4A)"],
            command=self._on_format_changed,
            height=38,
            selected_color=COLOR_PRIMARY,
            selected_hover_color=COLOR_PRIMARY_HOVER,
            unselected_color=BG_CARD_SUBTLE,
            unselected_hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=10
        )
        self.format_seg.set("🎥 Video (MP4)")
        self.format_seg.pack(fill="x")

        # Col 2: Quality Dropdown
        col2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(10, 0))

        q_lbl = ctk.CTkLabel(
            col2,
            text="Resolution & Bitrate:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        q_lbl.pack(anchor="w", pady=(0, 4))

        self.quality_menu = ctk.CTkOptionMenu(
            col2,
            values=["🌟 Best Available Quality", "1080p (Full HD)", "720p (HD)", "480p (SD)", "360p"],
            height=38,
            fg_color=BG_CARD_SUBTLE,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_CARD_HOVER,
            corner_radius=10
        )
        self.quality_menu.set("🌟 Best Available Quality")
        self.quality_menu.pack(fill="x")

        # Quick Preset Buttons Row
        self.presets_row = ctk.CTkFrame(self.options_card, fg_color="transparent")
        self.presets_row.pack(fill="x", padx=16, pady=(0, 10))

        presets_lbl = ctk.CTkLabel(
            self.presets_row,
            text="Studio Presets:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        presets_lbl.pack(side="left", padx=(0, 8))

        p1 = ctk.CTkButton(
            self.presets_row,
            text="👑 Max 4K Pro",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=95,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=COLOR_GOLD,
            corner_radius=8,
            command=lambda: self._apply_quick_preset("video", "best")
        )
        p1.pack(side="left", padx=3)

        p2 = ctk.CTkButton(
            self.presets_row,
            text="⚡ 1080p FHD",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=88,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            command=lambda: self._apply_quick_preset("video", "1080p")
        )
        p2.pack(side="left", padx=3)

        p3 = ctk.CTkButton(
            self.presets_row,
            text="📱 720p Fast",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=80,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=COLOR_ACCENT,
            corner_radius=8,
            command=lambda: self._apply_quick_preset("video", "720p")
        )
        p3.pack(side="left", padx=3)

        p4 = ctk.CTkButton(
            self.presets_row,
            text="🎵 MP3 320k",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=90,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=COLOR_SUCCESS,
            corner_radius=8,
            command=lambda: self._apply_quick_preset("audio_mp3", "320")
        )
        p4.pack(side="left", padx=3)

        # Destination Folder Selector Row
        folder_row = ctk.CTkFrame(self.options_card, fg_color="transparent")
        folder_row.pack(fill="x", padx=16, pady=(4, 10))

        folder_lbl = ctk.CTkLabel(
            folder_row,
            text="Save To Vault:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        folder_lbl.pack(side="left", padx=(0, 10))

        self.folder_display = ctk.CTkEntry(
            folder_row,
            font=ctk.CTkFont(size=12),
            height=36,
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8
        )
        self.folder_display.insert(0, self.download_dir)
        self.folder_display.configure(state="readonly")
        self.folder_display.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            folder_row,
            text="📁 Browse...",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=95,
            height=36,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            command=self._on_browse_folder
        )
        browse_btn.pack(side="left", padx=(0, 6))

        open_folder_btn = ctk.CTkButton(
            folder_row,
            text="📂 Open Folder",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=105,
            height=36,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            command=lambda: os.startfile(self.download_dir)
        )
        open_folder_btn.pack(side="left")

    def _build_progress_section(self, parent, padx: int):
        self.progress_card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.progress_card.pack(fill="x", padx=padx, pady=(0, 16), ipady=8)

        # Primary Action CTA Button Row
        action_row = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        action_row.pack(fill="x", padx=16, pady=(12, 14))

        self.download_btn = ctk.CTkButton(
            action_row,
            text="⬇   START TURBO DOWNLOAD",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=12,
            height=50,
            command=self._on_download_clicked
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.turbo_queue_btn = ctk.CTkButton(
            action_row,
            text="➕ Add to Queue",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            border_width=1,
            border_color="#00F2FE",
            text_color="#00F2FE",
            corner_radius=12,
            width=135,
            height=50,
            command=self._on_turbo_add_to_queue
        )
        self.turbo_queue_btn.pack(side="left", padx=(0, 8))

        self.cancel_btn = ctk.CTkButton(
            action_row,
            text="✖ Cancel",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            hover_color=COLOR_DANGER_HOVER,
            corner_radius=12,
            state="disabled",
            width=110,
            height=50,
            command=self._on_cancel_clicked
        )
        self.cancel_btn.pack(side="left")

        # Smooth Determinate Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_card,
            orientation="horizontal",
            mode="determinate",
            progress_color=COLOR_PRIMARY,
            fg_color=BG_CARD_SUBTLE,
            height=14,
            corner_radius=7
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))

        # 4-Card Real-Time Telemetry HUD
        hud_frame = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        hud_frame.pack(fill="x", padx=16, pady=(0, 4))
        hud_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # HUD 1: Status
        card_status = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=10, height=48, border_width=1, border_color=BORDER_COLOR)
        card_status.grid(row=0, column=0, sticky="nsew", padx=3)
        card_status.grid_propagate(False)
        self.status_title = ctk.CTkLabel(card_status, text="STREAM ENGINE", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.status_title.pack(anchor="w", padx=10, pady=(4, 0))
        self.status_lbl = ctk.CTkLabel(card_status, text="Ready", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_SUCCESS)
        self.status_lbl.pack(anchor="w", padx=10)

        # HUD 2: Speed / Item
        card_speed = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=10, height=48, border_width=1, border_color=BORDER_COLOR)
        card_speed.grid(row=0, column=1, sticky="nsew", padx=3)
        card_speed.grid_propagate(False)
        self.lbl_sp_t = ctk.CTkLabel(card_speed, text="TURBO SPEED", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_sp_t.pack(anchor="w", padx=10, pady=(4, 0))
        self.speed_lbl = ctk.CTkLabel(card_speed, text="-- MB/s", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_CYAN)
        self.speed_lbl.pack(anchor="w", padx=10)

        # HUD 3: Size
        card_size = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=10, height=48, border_width=1, border_color=BORDER_COLOR)
        card_size.grid(row=0, column=2, sticky="nsew", padx=3)
        card_size.grid_propagate(False)
        self.lbl_sz_t = ctk.CTkLabel(card_size, text="DATA TRANSFERRED", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_sz_t.pack(anchor="w", padx=10, pady=(4, 0))
        self.size_lbl = ctk.CTkLabel(card_size, text="-- / --", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        self.size_lbl.pack(anchor="w", padx=10)

        # HUD 4: ETA
        card_eta = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=10, height=48, border_width=1, border_color=BORDER_COLOR)
        card_eta.grid(row=0, column=3, sticky="nsew", padx=3)
        card_eta.grid_propagate(False)
        self.lbl_et_t = ctk.CTkLabel(card_eta, text="ESTIMATED REMAINING", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_et_t.pack(anchor="w", padx=10, pady=(4, 0))
        self.eta_lbl = ctk.CTkLabel(card_eta, text="--:--", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_GOLD)
        self.eta_lbl.pack(anchor="w", padx=10)

        # Download Success Banner (Hidden until finished)
        self.complete_bar = ctk.CTkFrame(
            self.progress_card,
            fg_color=COLOR_SUCCESS_BG,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_SUCCESS
        )

        self.complete_msg = ctk.CTkLabel(
            self.complete_bar,
            text="🎉 Download Complete! High-speed stream captured.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        self.complete_msg.pack(side="left", padx=14, pady=10)

        self.play_file_btn = ctk.CTkButton(
            self.complete_bar,
            text="▶ Play File",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=95,
            height=32,
            corner_radius=8,
            fg_color=COLOR_SUCCESS,
            hover_color="#0D9467",
            command=self._play_last_downloaded
        )
        self.play_file_btn.pack(side="right", padx=(4, 12), pady=8)

        self.show_file_btn = ctk.CTkButton(
            self.complete_bar,
            text="📂 Locate in Folder",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=125,
            height=32,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_CARD_HOVER,
            command=self._locate_last_downloaded
        )
        self.show_file_btn.pack(side="right", padx=4, pady=8)
        self.show_file_btn.pack(side="right", padx=4, pady=8)


    # ---------------- 1.5 Browse & Direct Stream Search View ----------------

    def _build_browse_view(self):
        """Construct the YouTube Browse, Search & Concurrent Queue Workspace."""
        self.view_browse = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="transparent")

        # Top Header
        header = ctk.CTkFrame(self.view_browse, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 10))

        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x")

        title_box = ctk.CTkFrame(top_row, fg_color="transparent")
        title_box.pack(side="left")

        title_badge_row = ctk.CTkFrame(title_box, fg_color="transparent")
        title_badge_row.pack(anchor="w")

        ctk.CTkLabel(
            title_badge_row,
            text="🌐 YOUTUBE BROWSE & QUEUE",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            title_badge_row,
            text="● MULTI-STREAM ACTIVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#00F2FE",
            fg_color=BG_CARD_SUBTLE,
            corner_radius=6,
            height=20,
            padx=8
        ).pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Search YouTube in real-time, select multiple videos (2-3 simultaneously), and queue parallel downloads",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Top Right Actions: Concurrency selector & Queue switch button
        right_box = ctk.CTkFrame(top_row, fg_color="transparent")
        right_box.pack(side="right")

        self.concurrency_seg = ctk.CTkSegmentedButton(
            right_box,
            values=["⚡ 2 Parallel", "⚡ 3 Parallel"],
            command=self._on_concurrency_changed,
            height=32,
            selected_color="#0284C7",
            selected_hover_color="#0369A1",
            unselected_color=BG_CARD_SUBTLE,
            text_color=TEXT_PRIMARY
        )
        self.concurrency_seg.set("⚡ 3 Parallel")
        self.concurrency_seg.pack(side="left", padx=(0, 8))

        self.browse_queue_pill = ctk.CTkButton(
            right_box,
            text="📥 Queue: 0 Active",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color="#00F2FE",
            text_color="#00F2FE",
            hover_color=BG_CARD_HOVER,
            command=lambda: self._set_browse_subtab("queue")
        )
        self.browse_queue_pill.pack(side="left")

        # 2. Search & Category Card
        search_card = ctk.CTkFrame(
            self.view_browse,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        search_card.pack(fill="x", padx=20, pady=(0, 10), ipady=2)

        search_input_row = ctk.CTkFrame(search_card, fg_color="transparent")
        search_input_row.pack(fill="x", padx=14, pady=(10, 6))

        self.browse_search_var = ctk.StringVar()
        self.browse_search_entry = ctk.CTkEntry(
            search_input_row,
            textvariable=self.browse_search_var,
            placeholder_text="🔍 Search YouTube for videos, music, tutorials, shorts (e.g. 'lofi chill', '4k nature', 'python tutorial')...",
            font=ctk.CTkFont(size=13),
            height=40,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_CARD_SUBTLE
        )
        self.browse_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.browse_search_entry.bind("<Return>", lambda e: self._execute_youtube_search())

        self.browse_search_btn = ctk.CTkButton(
            search_input_row,
            text="🔍 Search YouTube",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            width=140,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self._execute_youtube_search
        )
        self.browse_search_btn.pack(side="left")

        # Tags Row (Quick Search Categories)
        tags_row = ctk.CTkFrame(search_card, fg_color="transparent")
        tags_row.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            tags_row,
            text="Quick Categories:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        ).pack(side="left", padx=(0, 6))

        quick_tags = [
            ("🎵 Trending Music", "top music hits 2026"),
            ("🌟 4K HDR Nature", "4k hdr nature relaxation"),
            ("🎧 Lo-Fi Chill", "chill lofi hip hop beats"),
            ("🎮 Gaming", "top gaming highlights"),
            ("💻 Coding & AI", "python programming tutorial"),
            ("🎙 Podcasts", "popular podcasts")
        ]
        for tag_label, tag_query in quick_tags:
            t_btn = ctk.CTkButton(
                tags_row,
                text=tag_label,
                font=ctk.CTkFont(size=10, weight="bold"),
                height=24,
                fg_color=BG_CARD_SUBTLE,
                hover_color=BG_CARD_HOVER,
                text_color=TEXT_SECONDARY,
                corner_radius=6,
                command=lambda q=tag_query: self._quick_search_tag(q)
            )
            t_btn.pack(side="left", padx=3)

        # 3. Subtab Segmented Switcher (Search Results vs Download Queue)
        mode_row = ctk.CTkFrame(self.view_browse, fg_color="transparent")
        mode_row.pack(fill="x", padx=20, pady=(2, 6))

        self.browse_subtab_seg = ctk.CTkSegmentedButton(
            mode_row,
            values=["🌐 Search Results", "📥 Download Queue (0)"],
            command=self._on_browse_subtab_changed,
            height=34,
            selected_color=COLOR_PRIMARY,
            selected_hover_color=COLOR_PRIMARY_HOVER,
            unselected_color=BG_CARD_SUBTLE,
            text_color=TEXT_PRIMARY,
            corner_radius=10
        )
        self.browse_subtab_seg.set("🌐 Search Results")
        self.browse_subtab_seg.pack(side="left")

        # 4. Containers
        self.browse_search_container = ctk.CTkFrame(self.view_browse, fg_color="transparent")
        self.browse_search_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.browse_queue_container = ctk.CTkFrame(self.view_browse, fg_color="transparent")

        # Build Sub-Sections
        self._build_browse_search_results_section()
        self._build_browse_queue_section()

    def _build_browse_search_results_section(self):
        """Construct the search results list with batch multi-selection."""
        # Batch Action Toolbar
        toolbar = ctk.CTkFrame(self.browse_search_container, fg_color=BG_CARD_SUBTLE, corner_radius=10, height=44)
        toolbar.pack(fill="x", pady=(0, 8))

        tb_left = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_left.pack(side="left", padx=10, pady=6)

        ctk.CTkButton(
            tb_left,
            text="✓ Select All",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=85,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=6,
            command=self._select_all_browse_results
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            tb_left,
            text="✕ Deselect",
            font=ctk.CTkFont(size=11),
            height=28,
            width=75,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            corner_radius=6,
            command=self._deselect_all_browse_results
        ).pack(side="left", padx=(0, 8))

        self.browse_sel_count_lbl = ctk.CTkLabel(
            tb_left,
            text="0 videos selected",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.browse_sel_count_lbl.pack(side="left")

        tb_right = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_right.pack(side="right", padx=10, pady=6)

        self.browse_batch_format_seg = ctk.CTkSegmentedButton(
            tb_right,
            values=["🎥 MP4 Video", "🎵 MP3 Audio"],
            height=28,
            selected_color=COLOR_PRIMARY,
            selected_hover_color=COLOR_PRIMARY_HOVER,
            unselected_color=BG_CARD,
            text_color=TEXT_PRIMARY,
            corner_radius=6
        )
        self.browse_batch_format_seg.set("🎥 MP4 Video")
        self.browse_batch_format_seg.pack(side="left", padx=(0, 8))

        self.browse_batch_quality_menu = ctk.CTkOptionMenu(
            tb_right,
            values=["🌟 Best (Free: 720p)", "720p (HD)", "480p", "360p"],
            height=28,
            width=140,
            fg_color=BG_CARD,
            button_color=COLOR_PRIMARY,
            text_color=TEXT_PRIMARY,
            corner_radius=6
        )
        self.browse_batch_quality_menu.set("🌟 Best (Free: 720p)")
        self.browse_batch_quality_menu.pack(side="left", padx=(0, 8))

        self.browse_batch_dl_btn = ctk.CTkButton(
            tb_right,
            text="⚡ Download Selected to Queue",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            corner_radius=6,
            command=self._on_download_selected_browse_clicked
        )
        self.browse_batch_dl_btn.pack(side="left")

        # Scrollable Results Frame
        self.browse_results_scroll = ctk.CTkScrollableFrame(
            self.browse_search_container,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.browse_results_scroll.pack(fill="both", expand=True)

        self.browse_placeholder_lbl = ctk.CTkLabel(
            self.browse_results_scroll,
            text="🔍 Enter a search topic above or click any Quick Category to browse & download YouTube videos!",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        self.browse_placeholder_lbl.pack(pady=40)

    def _build_browse_queue_section(self):
        """Construct the Download Queue panel with parallel progress and controls."""
        # Queue Controls Bar
        q_bar = ctk.CTkFrame(self.browse_queue_container, fg_color=BG_CARD_SUBTLE, corner_radius=10, height=44)
        q_bar.pack(fill="x", pady=(0, 8))

        q_left = ctk.CTkFrame(q_bar, fg_color="transparent")
        q_left.pack(side="left", padx=10, pady=6)

        self.q_active_lbl = ctk.CTkLabel(
            q_left,
            text="⚡ Active: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00F2FE",
            fg_color=BG_CARD,
            corner_radius=6,
            height=24,
            padx=8
        )
        self.q_active_lbl.pack(side="left", padx=(0, 6))

        self.q_waiting_lbl = ctk.CTkLabel(
            q_left,
            text="⏳ Queued: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#A855F7",
            fg_color=BG_CARD,
            corner_radius=6,
            height=24,
            padx=8
        )
        self.q_waiting_lbl.pack(side="left", padx=(0, 6))

        self.q_finished_lbl = ctk.CTkLabel(
            q_left,
            text="✔ Finished: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10B981",
            fg_color=BG_CARD,
            corner_radius=6,
            height=24,
            padx=8
        )
        self.q_finished_lbl.pack(side="left")

        q_right = ctk.CTkFrame(q_bar, fg_color="transparent")
        q_right.pack(side="right", padx=10, pady=6)

        self.q_pause_btn = ctk.CTkButton(
            q_right,
            text="⏸ Pause Queue",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=95,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            text_color=COLOR_WARNING,
            corner_radius=6,
            command=self._on_toggle_queue_pause
        )
        self.q_pause_btn.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            q_right,
            text="🗑 Clear Finished",
            font=ctk.CTkFont(size=11),
            height=28,
            width=95,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            corner_radius=6,
            command=self._on_clear_finished_queue
        ).pack(side="left")

        # Scrollable Queue Items Frame
        self.browse_queue_scroll = ctk.CTkScrollableFrame(
            self.browse_queue_container,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.browse_queue_scroll.pack(fill="both", expand=True)

        self.queue_empty_lbl = ctk.CTkLabel(
            self.browse_queue_scroll,
            text="📥 Download Queue is currently empty.\nSelect videos from Browse & Search or click 'Add to Queue' in Turbo Downloader!",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.queue_empty_lbl.pack(pady=40)

    # ---------------- Browse & Queue Event Handlers ----------------

    def _execute_youtube_search(self):
        """Execute real-time YouTube search across ydl backend."""
        query = self.browse_search_var.get().strip()
        if not query or self.is_searching_browse:
            return

        self.is_searching_browse = True
        self.browse_search_btn.configure(state="disabled", text="Searching...")

        # Switch to Search Results tab if in queue
        self._set_browse_subtab("search")

        # Show searching placeholder
        for w in self.browse_results_scroll.winfo_children():
            w.destroy()
        loading_lbl = ctk.CTkLabel(
            self.browse_results_scroll,
            text=f"⏳ Searching YouTube for '{query}' with high-speed parser...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_ACCENT
        )
        loading_lbl.pack(pady=40)

        def task():
            try:
                results = self.downloader.search_youtube(query, limit=20)
                self.run_on_ui_thread(self._on_search_results_loaded, results)
            except Exception as e:
                err_text = str(e)
                self.run_on_ui_thread(self._on_search_error, err_text)

        threading.Thread(target=task, daemon=True).start()

    def _quick_search_tag(self, query: str):
        self.browse_search_var.set(query)
        self._execute_youtube_search()

    def _on_search_error(self, err: str):
        self.is_searching_browse = False
        self.browse_search_btn.configure(state="normal", text="🔍 Search YouTube")
        for w in self.browse_results_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.browse_results_scroll,
            text=f"⚠ Search failed: {err}",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_DANGER
        ).pack(pady=40)

    def _on_search_results_loaded(self, results: List[Dict[str, Any]]):
        self.is_searching_browse = False
        self.browse_search_btn.configure(state="normal", text="🔍 Search YouTube")
        self.browse_search_results = results
        self.browse_item_vars.clear()

        for w in self.browse_results_scroll.winfo_children():
            w.destroy()

        if not results:
            ctk.CTkLabel(
                self.browse_results_scroll,
                text="No video results found. Try searching with different keywords.",
                font=ctk.CTkFont(size=13),
                text_color=TEXT_MUTED
            ).pack(pady=40)
            return

        self._update_browse_selection_counter()

        # Populate Results Cards
        for item in results:
            v_id = item["id"]
            var = ctk.BooleanVar(value=False)
            self.browse_item_vars[v_id] = var

            card = ctk.CTkFrame(
                self.browse_results_scroll,
                fg_color=BG_CARD_SUBTLE,
                border_width=1,
                border_color=BORDER_COLOR,
                corner_radius=10
            )
            card.pack(fill="x", pady=4, padx=4)

            # Left: Checkbox
            cb = ctk.CTkCheckBox(
                card,
                text="",
                variable=var,
                width=24,
                checkmark_color="#FFFFFF",
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                command=self._update_browse_selection_counter
            )
            cb.pack(side="left", padx=(10, 6), pady=8)

            # Thumbnail box
            thumb_box = ctk.CTkFrame(card, fg_color=BG_WINDOW, width=120, height=68, corner_radius=8)
            thumb_box.pack(side="left", padx=4, pady=8)
            thumb_box.pack_propagate(False)

            thumb_lbl = ctk.CTkLabel(thumb_box, text="▶", font=ctk.CTkFont(size=18), text_color=TEXT_MUTED)
            thumb_lbl.pack(expand=True)

            # Load thumbnail async
            thumb_url = item.get("thumbnail")
            if thumb_url:
                self._load_browse_thumb_async(thumb_url, thumb_lbl)

            # Middle: Metadata
            mid = ctk.CTkFrame(card, fg_color="transparent")
            mid.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            title_lbl = ctk.CTkLabel(
                mid,
                text=item["title"],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=480
            )
            title_lbl.pack(anchor="w")

            meta_row = ctk.CTkFrame(mid, fg_color="transparent")
            meta_row.pack(anchor="w", pady=(2, 0))

            ctk.CTkLabel(
                meta_row,
                text=f"👤 {item.get('uploader', 'YouTube')}",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                meta_row,
                text=f"⏱ {item.get('duration_str', 'N/A')}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLOR_GOLD,
                fg_color=BG_WINDOW,
                corner_radius=4,
                padx=6
            ).pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                meta_row,
                text=f"👁 {item.get('views_str', '')}",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            ).pack(side="left")

            # Right: Action Buttons
            right_btns = ctk.CTkFrame(card, fg_color="transparent")
            right_btns.pack(side="right", padx=10, pady=8)

            # Quality Selection MP4 Download
            ctk.CTkButton(
                right_btns,
                text="⚡ MP4",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=65,
                height=30,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                corner_radius=6,
                command=lambda it=item: self._open_browse_quality_dialog([it], default_format="video")
            ).pack(side="left", padx=2)

            # Quality Selection MP3 Download
            ctk.CTkButton(
                right_btns,
                text="🎵 MP3",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=65,
                height=30,
                fg_color="#0284C7",
                hover_color="#0369A1",
                corner_radius=6,
                command=lambda it=item: self._open_browse_quality_dialog([it], default_format="audio_mp3")
            ).pack(side="left", padx=2)

            # Copy link button
            ctk.CTkButton(
                right_btns,
                text="📋",
                font=ctk.CTkFont(size=11),
                width=32,
                height=30,
                fg_color=BG_CARD,
                hover_color=BG_CARD_HOVER,
                text_color=TEXT_SECONDARY,
                corner_radius=6,
                command=lambda u=item["url"]: self._copy_text(u, "Video URL copied!")
            ).pack(side="left", padx=2)

    def _load_browse_thumb_async(self, thumb_url: str, label_widget: ctk.CTkLabel):
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
                    self.run_on_ui_thread(update)
            except Exception:
                pass
        threading.Thread(target=task, daemon=True).start()

    def _update_browse_selection_counter(self):
        selected_count = sum(1 for v in self.browse_item_vars.values() if v.get())
        total = len(self.browse_item_vars)
        self.browse_sel_count_lbl.configure(text=f"{selected_count} of {total} selected")
        if selected_count > 0:
            self.browse_batch_dl_btn.configure(text=f"⚡ Download {selected_count} Selected (Queue Parallel)")
        else:
            self.browse_batch_dl_btn.configure(text="⚡ Download Selected to Queue")

    def _select_all_browse_results(self):
        for v in self.browse_item_vars.values():
            v.set(True)
        self._update_browse_selection_counter()

    def _deselect_all_browse_results(self):
        for v in self.browse_item_vars.values():
            v.set(False)
        self._update_browse_selection_counter()

    def _open_browse_quality_dialog(self, items: List[Dict[str, Any]], default_format: str = "video"):
        """
        Prompt user to select download format and quality before adding to concurrent queue.
        Supports single or multiple selected videos with Free/Pro tier enforcement.
        """
        if not items:
            return

        is_batch = len(items) > 1
        dialog = ctk.CTkToplevel(self)
        dialog.title("Select Download Quality & Format" if not is_batch else f"Batch Queue ({len(items)} Videos)")
        dialog.geometry("540x630" if not is_batch else "560x680")
        dialog.minsize(500, 560)
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        dw = 560 if is_batch else 540
        dh = 680 if is_batch else 630
        x = self.winfo_x() + (self.winfo_width() - dw) // 2
        y = self.winfo_y() + (self.winfo_height() - dh) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        container = ctk.CTkFrame(dialog, fg_color=BG_WINDOW, corner_radius=0)
        container.pack(fill="both", expand=True, padx=20, pady=18)

        # 1. Header Box
        head_box = ctk.CTkFrame(container, fg_color="transparent")
        head_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            head_box,
            text="⚡ CONCURRENT QUEUE SETUP",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLOR_PRIMARY,
            fg_color=COLOR_PRIMARY_SUBTLE,
            corner_radius=6,
            height=22,
            padx=8
        ).pack(anchor="w", pady=(0, 4))

        title_text = "Select Download Quality" if not is_batch else f"Queue {len(items)} Selected Videos"
        ctk.CTkLabel(
            head_box,
            text=title_text,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            head_box,
            text="Choose your preferred media format, quality resolution, and target folder.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w")

        # 2. Preview Card
        preview_card = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        preview_card.pack(fill="x", pady=(0, 12), ipady=4)

        if not is_batch:
            item = items[0]
            p_row = ctk.CTkFrame(preview_card, fg_color="transparent")
            p_row.pack(fill="x", padx=12, pady=8)

            # Thumbnail label
            thumb_lbl = ctk.CTkLabel(
                p_row,
                text="🎬",
                font=ctk.CTkFont(size=22),
                width=90,
                height=52,
                fg_color=BG_CARD_SUBTLE,
                corner_radius=8
            )
            thumb_lbl.pack(side="left", padx=(0, 12))
            if item.get("thumbnail"):
                self._load_browse_thumb_async(item["thumbnail"], thumb_lbl)

            p_info = ctk.CTkFrame(p_row, fg_color="transparent")
            p_info.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                p_info,
                text=item.get("title", "Video"),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=340
            ).pack(anchor="w")

            meta_line = f"👤 {item.get('uploader', 'YouTube')}   •   ⏱ {item.get('duration_str', 'N/A')}"
            ctk.CTkLabel(
                p_info,
                text=meta_line,
                font=ctk.CTkFont(size=10),
                text_color=TEXT_MUTED
            ).pack(anchor="w", pady=(2, 0))
        else:
            ctk.CTkLabel(
                preview_card,
                text=f"📋 Selected for Concurrent Queue ({len(items)} items):",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_PRIMARY
            ).pack(anchor="w", padx=14, pady=(8, 4))

            list_scroll = ctk.CTkScrollableFrame(preview_card, fg_color=BG_CARD_SUBTLE, corner_radius=8, height=75)
            list_scroll.pack(fill="x", padx=14, pady=(0, 8))

            for idx, it in enumerate(items, 1):
                ctk.CTkLabel(
                    list_scroll,
                    text=f"{idx}. {it.get('title', 'Video')[:52]} ({it.get('duration_str', 'N/A')})",
                    font=ctk.CTkFont(size=10),
                    text_color=TEXT_SECONDARY,
                    anchor="w"
                ).pack(anchor="w", padx=6, pady=1)

        # 3. Settings Box (Format + Quality)
        config_card = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        config_card.pack(fill="x", pady=(0, 12), ipady=6)

        # Format Segmented Row
        ctk.CTkLabel(
            config_card,
            text="Select Media Format:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=14, pady=(8, 4))

        format_seg = ctk.CTkSegmentedButton(
            config_card,
            values=["🎥 MP4 Video", "🎵 MP3 Audio", "🎧 M4A Audio"],
            height=32,
            selected_color=COLOR_PRIMARY,
            selected_hover_color=COLOR_PRIMARY_HOVER,
            unselected_color=BG_CARD_SUBTLE,
            text_color=TEXT_PRIMARY
        )
        format_seg.pack(fill="x", padx=14, pady=(0, 10))

        if default_format == "audio_mp3":
            format_seg.set("🎵 MP3 Audio")
        elif default_format == "audio_m4a":
            format_seg.set("🎧 M4A Audio")
        else:
            format_seg.set("🎥 MP4 Video")

        # Quality Row
        q_label = ctk.CTkLabel(
            config_card,
            text="Select Video Resolution:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        q_label.pack(anchor="w", padx=14, pady=(0, 4))

        quality_menu = ctk.CTkOptionMenu(
            config_card,
            height=34,
            fg_color=BG_CARD_SUBTLE,
            button_color=COLOR_PRIMARY,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            corner_radius=8
        )
        quality_menu.pack(fill="x", padx=14, pady=(0, 8))

        video_qualities = [
            "🌟 Ultra HD 4K (2160p 60fps) ⭐ PRO",
            "✨ Quad HD 2K (1440p 60fps) ⭐ PRO",
            "⚡ Full HD 1080p (60fps) ⭐ PRO",
            "🎬 HD 720p (30fps Standard)",
            "📺 Standard 480p",
            "📱 Compact 360p"
        ]
        audio_qualities = [
            "🌟 Hi-Fi Studio (320 kbps)",
            "✨ High Quality (256 kbps)",
            "⚡ Standard Quality (192 kbps)",
            "📱 Fast Compact (128 kbps)"
        ]

        # Free Tier Notice Frame
        is_pro = self.license_mgr.is_pro()
        free_notice_frame = ctk.CTkFrame(config_card, fg_color=BG_CARD_SUBTLE, corner_radius=8)

        fn_label = ctk.CTkLabel(
            free_notice_frame,
            text="ℹ️ Free Plan is limited to 720p 30fps max. Upgrade or start 7-Day Free Trial for 4K 60fps & 320k Hi-Fi.",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_GOLD,
            wraplength=360,
            justify="left"
        )
        fn_label.pack(side="left", padx=10, pady=6, fill="x", expand=True)

        if not is_pro and self.license_mgr.can_start_trial():
            def on_trial_click():
                dialog.destroy()
                self._open_trial_dialog()

            ctk.CTkButton(
                free_notice_frame,
                text="⚡ Start Trial",
                font=ctk.CTkFont(size=10, weight="bold"),
                width=80,
                height=26,
                fg_color="#D97706",
                hover_color="#B45309",
                corner_radius=6,
                command=on_trial_click
            ).pack(side="right", padx=(0, 8), pady=4)

        def update_quality_options(fmt_val: str):
            if "Video" in fmt_val:
                quality_menu.configure(values=video_qualities)
                q_label.configure(text="Select Video Resolution:")
                if is_pro:
                    quality_menu.set("🌟 Ultra HD 4K (2160p 60fps) ⭐ PRO")
                else:
                    quality_menu.set("🎬 HD 720p (30fps Standard)")
                if not is_pro:
                    free_notice_frame.pack(fill="x", padx=14, pady=(0, 8))
                else:
                    free_notice_frame.pack_forget()
            else:
                quality_menu.configure(values=audio_qualities)
                q_label.configure(text="Select Audio Bitrate:")
                quality_menu.set("🌟 Hi-Fi Studio (320 kbps)")
                free_notice_frame.pack_forget()

        format_seg.configure(command=update_quality_options)
        update_quality_options(format_seg.get())

        # 4. Target Directory Row
        folder_card = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        folder_card.pack(fill="x", pady=(0, 12))

        f_row = ctk.CTkFrame(folder_card, fg_color="transparent")
        f_row.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(f_row, text="📁 Save to:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        folder_var = ctk.StringVar(value=self.download_dir)
        folder_entry = ctk.CTkEntry(f_row, textvariable=folder_var, height=28, font=ctk.CTkFont(size=10), fg_color=BG_CARD_SUBTLE, border_width=0)
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def choose_folder():
            chosen = ctk.filedialog.askdirectory(initialdir=folder_var.get())
            if chosen:
                folder_var.set(chosen)

        ctk.CTkButton(
            f_row,
            text="Browse...",
            font=ctk.CTkFont(size=10, weight="bold"),
            width=70,
            height=28,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=6,
            command=choose_folder
        ).pack(side="right")

        # 5. Buttons Row
        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(4, 0))

        def on_confirm():
            fmt_val = format_seg.get()
            if "MP3" in fmt_val:
                fmt_type = "audio_mp3"
            elif "M4A" in fmt_val:
                fmt_type = "audio_m4a"
            else:
                fmt_type = "video"

            q_val = quality_menu.get()
            if "4K" in q_val:
                quality = "2160p"
            elif "2K" in q_val:
                quality = "1440p"
            elif "1080p" in q_val:
                quality = "1080p"
            elif "720p" in q_val:
                quality = "720p"
            elif "480p" in q_val:
                quality = "480p"
            elif "360p" in q_val:
                quality = "360p"
            elif "320" in q_val:
                quality = "320"
            elif "256" in q_val:
                quality = "256"
            elif "192" in q_val:
                quality = "192"
            elif "128" in q_val:
                quality = "128"
            else:
                quality = "best"

            # Check Free tier quality clamp
            if not self.license_mgr.is_pro() and fmt_type == "video":
                if quality in ("2160p", "1440p", "1080p", "best"):
                    quality = "720p"

            dest_dir = folder_var.get().strip() or self.download_dir

            # Batch add to queue
            items_payload = []
            for it in items:
                items_payload.append({
                    "url": it["url"],
                    "title": it["title"],
                    "uploader": it.get("uploader", ""),
                    "thumbnail": it.get("thumbnail", ""),
                    "duration_str": it.get("duration_str", ""),
                    "format_type": fmt_type,
                    "quality": quality
                })

            self.queue_mgr.add_batch(items_payload, download_dir=dest_dir)
            self._deselect_all_browse_results()
            self._update_queue_badge()
            dialog.destroy()

            # Switch to queue subtab immediately so user sees their 2 or 3 parallel downloads
            self._set_browse_subtab("queue")

        start_btn = ctk.CTkButton(
            btn_row,
            text="⚡ Add to Queue & Start" if not is_batch else f"⚡ Add {len(items)} to Queue & Start",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=38,
            corner_radius=8,
            command=on_confirm
        )
        start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_MUTED,
            height=38,
            width=85,
            corner_radius=8,
            command=dialog.destroy
        ).pack(side="right")

    def _queue_single_browse_video(self, video_data: Dict[str, Any], format_type: str = "video"):
        """Queue a single video directly from browse results."""
        # Quality check for Free users
        quality = "best"
        if not self.license_mgr.is_pro() and format_type == "video":
            quality = "720p"

        self.queue_mgr.add_to_queue(
            url=video_data["url"],
            title=video_data["title"],
            uploader=video_data.get("uploader", ""),
            thumbnail=video_data.get("thumbnail", ""),
            duration_str=video_data.get("duration_str", ""),
            format_type=format_type,
            quality=quality,
            download_dir=self.download_dir
        )
        self._update_queue_badge()
        # Switch to queue tab to show downloading item
        self._set_browse_subtab("queue")

    def _on_download_selected_browse_clicked(self):
        """Batch queue all checked search result videos with quality selection dialog."""
        selected_ids = [vid for vid, v in self.browse_item_vars.items() if v.get()]
        if not selected_ids:
            self.browse_sel_count_lbl.configure(text="⚠️ Please check at least 1 video first!", text_color=COLOR_WARNING)
            return

        fmt_choice = self.browse_batch_format_seg.get()
        default_format = "audio_mp3" if "MP3" in fmt_choice else "video"
        items_to_add = [it for it in self.browse_search_results if it["id"] in selected_ids]
        self._open_browse_quality_dialog(items_to_add, default_format=default_format)

    def _on_concurrency_changed(self, value: str):
        if "2" in value:
            self.queue_mgr.set_concurrency(2)
        elif "3" in value:
            self.queue_mgr.set_concurrency(3)

    def _on_browse_subtab_changed(self, value: str):
        if "Queue" in value:
            self._set_browse_subtab("queue")
        else:
            self._set_browse_subtab("search")

    def _set_browse_subtab(self, subtab: str):
        if subtab == "queue":
            self.browse_search_container.pack_forget()
            self.browse_queue_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            self.browse_subtab_seg.set(f"📥 Download Queue ({len(self.queue_mgr.items)})")
            self._refresh_queue_ui()
        else:
            self.browse_queue_container.pack_forget()
            self.browse_search_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            self.browse_subtab_seg.set("🌐 Search Results")

    def _on_toggle_queue_pause(self):
        if self.queue_mgr.is_paused:
            self.queue_mgr.resume_queue()
            self.q_pause_btn.configure(text="⏸ Pause Queue", text_color=COLOR_WARNING)
        else:
            self.queue_mgr.pause_queue()
            self.q_pause_btn.configure(text="▶ Resume Queue", text_color=COLOR_SUCCESS)

    def _on_clear_finished_queue(self):
        self.queue_mgr.clear_completed()
        self._refresh_queue_ui()

    def _on_queue_updated_threadsafe(self):
        if not getattr(self, "_queue_refresh_scheduled", False):
            self._queue_refresh_scheduled = True
            self.run_on_ui_thread(self._do_refresh_queue_ui)

    def _do_refresh_queue_ui(self):
        self._queue_refresh_scheduled = False
        self._refresh_queue_ui()

    def _on_queue_item_finished_threadsafe(self, item: QueueItem):
        def on_done():
            self.history_mgr.add(
                title=item.title,
                file_path=item.output_file,
                format_type=item.format_type,
                quality=item.quality
            )
            self._update_telemetry_ui()
            self._update_queue_badge()
        self.run_on_ui_thread(on_done)

    def _update_queue_badge(self):
        stats = self.queue_mgr.get_stats()
        active = stats["active"]
        queued = stats["queued"]
        total = stats["total"]

        if hasattr(self, "browse_queue_pill") and self.browse_queue_pill.winfo_exists():
            self.browse_queue_pill.configure(text=f"📥 Queue: {active} Active, {queued} Queued")

        if hasattr(self, "browse_subtab_seg") and self.browse_subtab_seg.winfo_exists():
            # Only update label text while preserving active tab
            pass

    def _refresh_queue_ui(self):
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
                    text="📥 Download Queue is currently empty.\nAdd videos from Browse & Search or click 'Add to Queue' in Turbo Downloader!",
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

    def _on_turbo_add_to_queue(self):
        """Add media from Turbo Downloader URL input into Download Queue."""
        url = self.url_var.get().strip()
        if not url:
            self.input_msg_lbl.configure(text="Please enter a valid video or media link first.", text_color=COLOR_WARNING)
            return

        fmt_choice = self.format_seg.get()
        format_type = "audio_mp3" if "MP3" in fmt_choice else ("audio_m4a" if "M4A" in fmt_choice else "video")
        quality = "best"
        q_val = self.quality_menu.get()
        for q_tag in ["2160p", "1440p", "1080p", "720p", "480p", "360p", "320"]:
            if q_tag in q_val:
                quality = q_tag
                break

        title = self.current_video_info.get("title", "Video") if self.current_video_info else "Queued Stream"
        uploader = self.current_video_info.get("uploader", "") if self.current_video_info else ""
        thumb = self.current_video_info.get("thumbnail", "") if self.current_video_info else ""
        dur = self.current_video_info.get("duration_str", "") if self.current_video_info else ""

        self.queue_mgr.add_to_queue(
            url=url,
            title=title,
            uploader=uploader,
            thumbnail=thumb,
            duration_str=dur,
            format_type=format_type,
            quality=quality,
            download_dir=self.download_dir
        )
        self.input_msg_lbl.configure(text="✔ Video added to Download Queue!", text_color=COLOR_SUCCESS)
        self._update_queue_badge()

    # ---------------- 2. History & Library View ----------------

    def _build_history_view(self):
        self.view_history = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="transparent")

        header = ctk.CTkFrame(self.view_history, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 14))

        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x")

        title_box = ctk.CTkFrame(top_row, fg_color="transparent")
        title_box.pack(side="left")

        title_badge_row = ctk.CTkFrame(title_box, fg_color="transparent")
        title_badge_row.pack(anchor="w")

        ctk.CTkLabel(
            title_badge_row,
            text="🕒 MEDIA VAULT & LIBRARY",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            title_badge_row,
            text="● VAULT ENCRYPTED",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#10B981",
            fg_color=BG_CARD_SUBTLE,
            corner_radius=6,
            height=20,
            padx=8
        ).pack(side="left")

        self.history_count_lbl = ctk.CTkLabel(
            title_box,
            text="All captured video streams, audio tracks & playlist batches",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.history_count_lbl.pack(anchor="w", pady=(2, 0))

        actions_box = ctk.CTkFrame(top_row, fg_color="transparent")
        actions_box.pack(side="right")

        open_folder_btn = ctk.CTkButton(
            actions_box,
            text="📂 Open Vault Folder",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=135,
            height=34,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY,
            hover_color=BG_CARD_HOVER,
            command=lambda: os.startfile(self.download_dir)
        )
        open_folder_btn.pack(side="left", padx=(0, 8))

        clear_btn = ctk.CTkButton(
            actions_box,
            text="🗑 Clear History",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=110,
            height=34,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color=BORDER_COLOR,
            text_color=COLOR_DANGER,
            hover_color=BG_CARD_HOVER,
            command=self._clear_all_history
        )
        clear_btn.pack(side="left")

        search_card = ctk.CTkFrame(
            self.view_history,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        search_card.pack(fill="x", padx=20, pady=(0, 14))

        self.history_search_var = ctk.StringVar()
        self.history_search_var.trace_add("write", lambda *a: self._refresh_history_ui())

        search_entry = ctk.CTkEntry(
            search_card,
            textvariable=self.history_search_var,
            placeholder_text="🔍 Filter media vault by title, resolution, platform or filename...",
            font=ctk.CTkFont(size=12),
            height=40,
            border_width=0,
            fg_color="transparent"
        )
        search_entry.pack(fill="x", padx=14, pady=4)

        self.history_scroll = ctk.CTkScrollableFrame(
            self.view_history,
            fg_color="transparent",
            corner_radius=0
        )
        self.history_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _refresh_history_ui(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        query = self.history_search_var.get().strip().lower()
        all_items = self.history_mgr.history

        if query:
            filtered = [
                (idx, item) for idx, item in enumerate(all_items)
                if query in item.get("title", "").lower()
                or query in item.get("format_type", "").lower()
                or query in os.path.basename(item.get("file_path", "")).lower()
            ]
        else:
            filtered = [(idx, item) for idx, item in enumerate(all_items)]

        self.history_count_lbl.configure(text=f"{len(all_items)} total media items recorded in local vault")

        if not filtered:
            empty_box = ctk.CTkFrame(self.history_scroll, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
            empty_box.pack(pady=40, padx=40, fill="x", ipady=24)

            ctk.CTkLabel(
                empty_box,
                text="🎬",
                font=ctk.CTkFont(size=36)
            ).pack(pady=(0, 6))

            empty_lbl = ctk.CTkLabel(
                empty_box,
                text="No downloads found matching query." if query else "Your Media Vault is currently empty.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_PRIMARY
            )
            empty_lbl.pack()

            ctk.CTkLabel(
                empty_box,
                text="Captured video streams, MP3 audio, and TikTok clips will be cataloged here automatically.",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            ).pack(pady=(4, 0))
            return

        for orig_idx, item in filtered:
            self._create_history_card(self.history_scroll, orig_idx, item)

    def _create_history_card(self, parent, orig_idx: int, item: Dict[str, Any]):
        card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.pack(fill="x", pady=5)

        is_pl = item.get("is_playlist", False)
        format_type = item.get("format_type", "video").lower()
        is_video = "video" in format_type
        is_tiktok = "tiktok" in item.get("title", "").lower() or "tiktok" in item.get("url", "").lower()

        if is_pl:
            pill_text = "📑 PLAYLIST BATCH"
            pill_color = "#A855F7"
        elif is_tiktok:
            pill_text = "📱 TIKTOK CLEAN"
            pill_color = "#00F2FE"
        elif is_video:
            pill_text = "🎬 4K/HD VIDEO"
            pill_color = "#FF2A5F"
        else:
            pill_text = "🎵 STUDIO AUDIO"
            pill_color = "#10B981"

        left_col = ctk.CTkFrame(card, fg_color="transparent")
        left_col.pack(side="left", padx=12, pady=10)

        pill_badge = ctk.CTkLabel(
            left_col,
            text=pill_text,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=pill_color,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=6,
            height=22,
            padx=8
        )
        pill_badge.pack(anchor="w")

        info_box = ctk.CTkFrame(card, fg_color="transparent")
        info_box.pack(side="left", fill="x", expand=True, pady=8)

        title = item.get("title", "Untitled Media")
        title_lbl = ctk.CTkLabel(
            info_box,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.pack(anchor="w")

        file_path = item.get("file_path", "")
        exists = os.path.exists(file_path)

        if is_pl:
            count = item.get("item_count", 0)
            meta_text = f"⏱ {item.get('timestamp', '')}  •  Batch Collection ({count} items)"
        else:
            size_str = ""
            if exists:
                try:
                    mb = os.path.getsize(file_path) / (1024 * 1024)
                    size_str = f"  •  💾 {mb:.1f} MB"
                except Exception:
                    pass
            else:
                size_str = "  •  ⚠️ (File moved or deleted)"
            meta_text = f"⏱ {item.get('timestamp', '')}{size_str}"

        meta_lbl = ctk.CTkLabel(
            info_box,
            text=meta_text,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED if exists else COLOR_WARNING,
            anchor="w"
        )
        meta_lbl.pack(anchor="w", pady=(2, 0))

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(side="right", padx=12, pady=10)

        if exists:
            if not is_pl:
                play_btn = ctk.CTkButton(
                    btn_box,
                    text="▶ Play Stream",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    width=90,
                    height=32,
                    corner_radius=8,
                    fg_color=COLOR_SUCCESS,
                    hover_color="#059669",
                    command=lambda p=file_path: os.startfile(p)
                )
                play_btn.pack(side="left", padx=3)

            locate_btn = ctk.CTkButton(
                btn_box,
                text="📂 Folder" if is_pl else "📂 Show File",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=80,
                height=32,
                corner_radius=8,
                fg_color=BG_CARD_SUBTLE,
                text_color=TEXT_PRIMARY,
                hover_color=BG_CARD_HOVER,
                command=lambda p=file_path: os.startfile(p) if is_pl else locate_in_explorer(p)
            )
            locate_btn.pack(side="left", padx=3)

        del_btn = ctk.CTkButton(
            btn_box,
            text="✕",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=32,
            height=32,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_MUTED,
            hover_color=COLOR_DANGER_HOVER,
            command=lambda idx=orig_idx: self._remove_history_item(idx)
        )
        del_btn.pack(side="left", padx=(3, 0))

    def _remove_history_item(self, index: int):
        self.history_mgr.remove(index)
        self._refresh_history_ui()

    def _clear_all_history(self):
        self.history_mgr.clear()
        self._refresh_history_ui()

    # ---------------- 3. Settings & Diagnostics View ----------------

    def _build_settings_view(self):
        self.view_settings = ctk.CTkScrollableFrame(self.content_container, corner_radius=0, fg_color="transparent")

        head = ctk.CTkFrame(self.view_settings, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(18, 14))

        ctk.CTkLabel(
            head,
            text="⚙️ STUDIO PREFERENCES & ENGINE CONFIG",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            head,
            text="Configure rendering pipeline, monitor DPI scaling, and hardware acceleration parameters",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Card 0: Subscription & Pro License Management
        self.license_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        self.license_card.pack(fill="x", padx=20, pady=(0, 14), ipady=10)

        lic_header_row = ctk.CTkFrame(self.license_card, fg_color="transparent")
        lic_header_row.pack(fill="x", padx=18, pady=(12, 4))

        ctk.CTkLabel(
            lic_header_row,
            text="👑 PRO MEMBERSHIP & MACHINE LICENSING",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        self.lic_badge_pill = ctk.CTkLabel(
            lic_header_row,
            text="FREE EDITION",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            text_color=COLOR_WARNING,
            corner_radius=6,
            height=24,
            padx=10
        )
        self.lic_badge_pill.pack(side="right")

        self.lic_desc_lbl = ctk.CTkLabel(
            self.license_card,
            text="Unlock 4K Ultra HD 60FPS, full playlist batch downloads, and high-speed multi-threaded acceleration.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.lic_desc_lbl.pack(anchor="w", padx=18, pady=(0, 10))

        # License Details Box
        self.lic_details_frame = ctk.CTkFrame(self.license_card, fg_color=BG_CARD_SUBTLE, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        self.lic_details_frame.pack(fill="x", padx=18, pady=(0, 12))

        # Plan Row
        row1 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(row1, text="Active Subscription:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        self.lic_plan_lbl = ctk.CTkLabel(row1, text="Free Edition", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_GOLD)
        self.lic_plan_lbl.pack(side="right")

        # Expiry Row
        row2 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(row2, text="License Expiration:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        self.lic_exp_lbl = ctk.CTkLabel(row2, text="N/A", font=ctk.CTkFont(size=11), text_color=TEXT_PRIMARY)
        self.lic_exp_lbl.pack(side="right")

        # Key Row
        row3 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row3.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(row3, text="Bound License Key:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        self.lic_key_lbl = ctk.CTkLabel(row3, text="None", font=ctk.CTkFont(size=11, family="Consolas"), text_color=TEXT_PRIMARY)
        self.lic_key_lbl.pack(side="right")

        # HWID Row
        row4 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row4.pack(fill="x", padx=14, pady=(4, 10))
        ctk.CTkLabel(row4, text="Machine Hardware ID (HWID):", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        hwid_right = ctk.CTkFrame(row4, fg_color="transparent")
        hwid_right.pack(side="right")
        self.lic_hwid_lbl = ctk.CTkLabel(hwid_right, text=self.license_mgr.hwid, font=ctk.CTkFont(size=10, family="Consolas"), text_color=TEXT_MUTED)
        self.lic_hwid_lbl.pack(side="left", padx=(0, 6))
        copy_hwid_btn = ctk.CTkButton(
            hwid_right,
            text="📋 Copy HWID",
            font=ctk.CTkFont(size=10, weight="bold"),
            width=85,
            height=24,
            corner_radius=6,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            command=lambda: self._copy_text(self.license_mgr.hwid, "HWID copied to clipboard!")
        )
        copy_hwid_btn.pack(side="left")

        # Button Row
        self.lic_actions_frame = ctk.CTkFrame(self.license_card, fg_color="transparent")
        self.lic_actions_frame.pack(fill="x", padx=18, pady=(0, 8))

        self.lic_activate_btn = ctk.CTkButton(
            self.lic_actions_frame,
            text="⚡ Activate Pro License Key",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#D97706",
            hover_color="#B45309",
            height=38,
            corner_radius=8,
            command=self._open_activation_dialog
        )
        self.lic_activate_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.lic_deactivate_btn = ctk.CTkButton(
            self.lic_actions_frame,
            text="🔌 Deactivate / Transfer PC",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=38,
            corner_radius=8,
            command=self._deactivate_license_confirmed
        )

        # Card: Theme Palette & Visual Customization
        palette_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        palette_card.pack(fill="x", padx=20, pady=(0, 14), ipady=10)

        ctk.CTkLabel(
            palette_card,
            text="🎨 THEME PALETTES & VISUAL CUSTOMIZATION",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(12, 4))

        ctk.CTkLabel(
            palette_card,
            text="Select from tranquil, calm palettes designed for long sessions without eye fatigue.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=18, pady=(0, 12))

        pal_select_row = ctk.CTkFrame(palette_card, fg_color="transparent")
        pal_select_row.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkLabel(
            pal_select_row,
            text="Accent Color Palette:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        ).pack(side="left")

        self.settings_palette_menu = ctk.CTkOptionMenu(
            pal_select_row,
            values=[
                "🌊 Calm Ocean",
                "🌿 Nordic Sage",
                "🔮 Twilight Lavender",
                "🌅 Warm Sunset",
                "🩶 Minimal Slate",
                "🌸 Soft Rose"
            ],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            width=200,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            button_color=COLOR_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self._on_palette_menu_selected
        )
        disp_map = {
            "Ocean": "🌊 Calm Ocean",
            "Sage": "🌿 Nordic Sage",
            "Lavender": "🔮 Twilight Lavender",
            "Amber": "🌅 Warm Sunset",
            "Slate": "🩶 Minimal Slate",
            "Rose": "🌸 Soft Rose"
        }
        self.settings_palette_menu.set(disp_map.get(self.current_palette_key, "🌊 Calm Ocean"))
        self.settings_palette_menu.pack(side="right")

        # Swatches row
        swatches_row = ctk.CTkFrame(palette_card, fg_color="transparent")
        swatches_row.pack(fill="x", padx=18, pady=(0, 8))

        ctk.CTkLabel(
            swatches_row,
            text="Quick Swatches:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        ).pack(side="left", padx=(0, 8))

        swatch_items = [
            ("🌊 Ocean", "Ocean", "#0EA5E9"),
            ("🌿 Sage", "Sage", "#10B981"),
            ("🔮 Lavender", "Lavender", "#8B5CF6"),
            ("🌅 Amber", "Amber", "#F59E0B"),
            ("🩶 Slate", "Slate", "#64748B"),
            ("🌸 Rose", "Rose", "#FB7185")
        ]
        for s_lbl, s_key, s_col in swatch_items:
            ctk.CTkButton(
                swatches_row,
                text=s_lbl,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=s_col,
                hover_color=s_col,
                text_color="#FFFFFF",
                width=72,
                height=26,
                corner_radius=6,
                command=lambda k=s_key: self._apply_theme_palette(k)
            ).pack(side="left", padx=3)

        # Card 1: Display & Resolution Scaling
        display_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        display_card.pack(fill="x", padx=20, pady=(0, 14), ipady=8)

        ctk.CTkLabel(
            display_card,
            text="🖥 DISPLAY & RESOLUTION SCALING ENGINE",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(12, 4))

        ctk.CTkLabel(
            display_card,
            text="Adjust UI zoom scaling for 4K UHD, high-DPI retina monitors, or compact laptop displays.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=18, pady=(0, 12))

        scale_row = ctk.CTkFrame(display_card, fg_color="transparent")
        scale_row.pack(fill="x", padx=18, pady=(0, 12))

        ctk.CTkLabel(scale_row, text="Interface Display Scaling:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")

        self.scale_menu = ctk.CTkOptionMenu(
            scale_row,
            values=["85% (Compact)", "100% (Standard)", "115% (Comfortable)", "125% (Large 4K)"],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            width=180,
            corner_radius=8,
            command=self._on_scale_selected,
            fg_color=BG_CARD_SUBTLE,
            button_color=COLOR_PRIMARY,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD
        )
        current_scale = self.config.get("ui_scale", "100%")
        for v in self.scale_menu._values:
            if current_scale in v:
                self.scale_menu.set(v)
                break
        self.scale_menu.pack(side="right")

        # Card 2: Download Automation Preferences
        auto_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        auto_card.pack(fill="x", padx=20, pady=(0, 14), ipady=8)

        ctk.CTkLabel(
            auto_card,
            text="⚡ REAL-TIME SMART CLIPBOARD MONITOR",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(12, 4))

        clip_row = ctk.CTkFrame(auto_card, fg_color="transparent")
        clip_row.pack(fill="x", padx=18, pady=(6, 12))

        clip_info = ctk.CTkFrame(clip_row, fg_color="transparent")
        clip_info.pack(side="left")

        ctk.CTkLabel(clip_info, text="Clipboard Auto-Detection Hook", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(clip_info, text="Instantly capture YouTube & TikTok links copied from web browsers in real time.", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w")

        self.clip_switch = ctk.CTkSwitch(
            clip_row,
            text="",
            command=self._on_toggle_auto_clipboard,
            progress_color=COLOR_PRIMARY
        )
        if self.config.get("auto_clipboard", True):
            self.clip_switch.select()
        else:
            self.clip_switch.deselect()
        self.clip_switch.pack(side="right")

        # Card 3: Engine Diagnostics & Capabilities
        diag_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        diag_card.pack(fill="x", padx=20, pady=(0, 14), ipady=10)

        ctk.CTkLabel(
            diag_card,
            text="🚀 CORE HARDWARE & STREAMING ENGINE TELEMETRY",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=18, pady=(12, 6))

        ffmpeg_dir = get_ffmpeg_dir() or "Internal Binary Pack"
        telemetry_items = [
            ("🟢 ONLINE", "YouTube Video Engine", "Ultra HD 4K 60fps, 1080p, Shorts & Playlists", "#10B981"),
            ("🟢 ACTIVE", "TikTok Clean Extractor", "Watermark-Free Direct Stream Engine Enabled", "#00F2FE"),
            ("🟢 ACTIVE", "FFmpeg Transcoder", f"Hardware Acceleration Active ({ffmpeg_dir})", "#10B981"),
            ("🔒 LOCKED", "License Security Enclave", f"HMAC-SHA256 Machine Identity Engine ({sys.platform})", "#F59E0B"),
        ]
        for tag, name, desc, col in telemetry_items:
            row = ctk.CTkFrame(diag_card, fg_color=BG_CARD_SUBTLE, corner_radius=8, height=36)
            row.pack(fill="x", padx=18, pady=3)

            pill = ctk.CTkLabel(
                row,
                text=tag,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=col,
                fg_color=BG_CARD,
                corner_radius=4,
                width=65,
                height=22
            )
            pill.pack(side="left", padx=8, pady=6)

            ctk.CTkLabel(
                row,
                text=f"{name}: ",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_PRIMARY
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=desc,
                font=ctk.CTkFont(size=10),
                text_color=TEXT_MUTED
            ).pack(side="left")

        # Card 4: About
        about_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        about_card.pack(fill="x", padx=20, pady=(0, 20), ipady=8)

        ctk.CTkLabel(
            about_card,
            text=f"{APP_NAME} {APP_VERSION}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=18, pady=(12, 2))

        ctk.CTkLabel(
            about_card,
            text="Engineered for ad-free downloads across YouTube, TikTok (No Watermark), and Full Playlists.\nOfficial Store & Updates: https://prodownloader.site",
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
            text_color=TEXT_PRIMARY,
            hover_color=BG_CARD_HOVER,
            command=self._on_manual_check_updates
        )
        self.settings_check_update_btn.pack(side="right")

    def _on_scale_selected(self, choice: str):
        self.config.set("ui_scale", choice)
        self._apply_ui_scaling(choice)

    def _on_toggle_auto_clipboard(self):
        val = bool(self.clip_switch.get())
        self.config.set("auto_clipboard", val)
        if val:
            self._check_clipboard_loop()

    # ---------------- Software Updates Engine ----------------

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
                            f"You are currently running {APP_NAME} {APP_VERSION}.\n\nNo newer updates are available at this time."
                        )
                self.run_on_ui_thread(on_done)
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
            text_color=TEXT_PRIMARY,
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

    # ---------------- Clipboard & Auto-Fetch Engine ----------------

    def _check_clipboard_loop(self):
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
                        self.run_on_ui_thread(on_valid_clip)
            except Exception:
                pass

        threading.Thread(target=bg_check, daemon=True).start()
        self.after(2000, self._check_clipboard_loop)

    def _show_clipboard_banner(self, url: str):
        display_url = url if len(url) <= 45 else url[:45] + "..."
        url_type = detect_url_type(url)
        type_str = "TikTok link" if url_type == "tiktok" else ("Playlist link" if url_type == "playlist" else "YouTube link")
        self.clipboard_label.configure(text=f"📋 Detected {type_str}: {display_url}")
        self.pending_clipboard_url = url
        self.clipboard_banner.pack(fill="x", padx=18, pady=(0, 10), before=self.preview_card)

    def _dismiss_clipboard_banner(self):
        self.clipboard_banner.pack_forget()

    def _on_clipboard_banner_clicked(self):
        if hasattr(self, "pending_clipboard_url") and self.pending_clipboard_url:
            self.url_var.set(self.pending_clipboard_url)
            self._dismiss_clipboard_banner()
            self._auto_fetch_if_new(self.pending_clipboard_url)

    def _on_paste_button_clicked(self):
        try:
            clip_text = pyperclip.paste()
            if not clip_text:
                self.input_msg_lbl.configure(text="Clipboard is empty.", text_color=COLOR_WARNING)
                return

            clip_text = clip_text.strip()
            self.url_var.set(clip_text)
            self.last_clipboard_content = clip_text

            if is_valid_media_url(clip_text):
                self._dismiss_clipboard_banner()
                self._auto_fetch_if_new(clip_text)
            else:
                self.input_msg_lbl.configure(
                    text="⚠ Pasted text does not appear to be a supported YouTube, TikTok, or Playlist URL.",
                    text_color=COLOR_WARNING
                )
        except Exception as e:
            self.input_msg_lbl.configure(text=f"Paste error: {str(e)}", text_color=COLOR_DANGER)

    def _on_url_entry_changed(self, *args):
        url = self.url_var.get().strip()
        if not url:
            return

        if is_valid_media_url(url):
            self._auto_fetch_if_new(url)

    def _on_clear_clicked(self):
        self.url_var.set("")
        self.last_fetched_url = ""
        self.current_video_info = None
        self.raw_thumbnail_pil = None
        self.cached_thumbnail_ctk = None
        self.playlist_item_vars.clear()

        # Reset Preview Sections
        self.preview_content.pack_forget()
        self.playlist_content.pack_forget()
        self.preview_placeholder.pack(fill="x", pady=25)

        # Reset Controls
        self.download_btn.configure(text="⬇   START DOWNLOAD")
        self.input_msg_lbl.configure(
            text="✨ Tip: Simply paste or press Ctrl+V — videos, TikToks without watermark, and playlists load automatically!",
            text_color=TEXT_MUTED
        )
        self.auto_badge.configure(text="⚡ Auto-Fetch Active", text_color=COLOR_SUCCESS, fg_color=COLOR_SUCCESS_BG)

    def _auto_fetch_if_new(self, url: str):
        if url == self.last_fetched_url:
            return

        if self.is_fetching or self.is_downloading:
            return

        self.last_fetched_url = url
        self._dismiss_clipboard_banner()
        self._fetch_video_info_threaded(url)

    # ---------------- Asynchronous Video/Playlist Fetching ----------------

    def _fetch_video_info_threaded(self, url: str):
        self.is_fetching = True
        url_type = detect_url_type(url)

        if url_type == "tiktok":
            fetch_text = "⏳ Fetching TikTok (No Watermark)..."
        elif url_type == "playlist":
            fetch_text = "⏳ Fetching Playlist Videos..."
        else:
            fetch_text = "⏳ Fetching Video Info..."

        self.auto_badge.configure(text=fetch_text, text_color=COLOR_ACCENT, fg_color=COLOR_ACCENT_SUBTLE)
        self.input_msg_lbl.configure(text=fetch_text, text_color=COLOR_ACCENT)

        def task():
            try:
                info = self.downloader.fetch_info(url)
                self.run_on_ui_thread(self._on_info_fetched_success, info)
            except Exception as e:
                err_msg = str(e)
                self.run_on_ui_thread(self._on_info_fetched_error, err_msg)

        threading.Thread(target=task, daemon=True).start()

    def _on_info_fetched_success(self, info: Dict[str, Any]):
        self.is_fetching = False
        self.current_video_info = info
        try:
            self._populate_video_preview(info)
        except Exception as e:
            self._on_info_fetched_error(f"Render error: {str(e)}")

    def _populate_video_preview(self, info: Dict[str, Any]):
        self.preview_placeholder.pack_forget()

        is_pl = info.get("is_playlist", False)
        is_tiktok = info.get("is_tiktok", False)

        if is_pl:
            # ---------------- PLAYLIST MODE ----------------
            self.preview_content.pack_forget()
            self.playlist_content.pack(fill="both", expand=True)

            self.auto_badge.configure(text=f"✓ Playlist Loaded ({info.get('total_items', 0)} Videos)", text_color=COLOR_SUCCESS, fg_color=COLOR_SUCCESS_BG)
            self.input_msg_lbl.configure(text=f"✓ Playlist loaded: {info.get('title')} ({info.get('total_items')} videos ready)", text_color=COLOR_SUCCESS)

            self.playlist_title.configure(text=info.get("title", "Untitled Playlist"))
            self.playlist_meta.configure(text=f"👤 {info.get('uploader', 'Unknown Channel')}  •  {info.get('total_items', 0)} Videos total")

            # Recalculate title wrap
            content_w = max(420, self.winfo_width() - 260)
            self.playlist_title.configure(wraplength=max(220, content_w - 240))

            # Build Checkbox List of Playlist Items
            self._populate_playlist_items(info.get("entries", []))

            # Update Format Choices for Playlist
            self.format_seg.configure(values=["🎥 All as Video (MP4)", "🎵 All as Music (MP3)"])
            self.format_seg.set("🎥 All as Video (MP4)")

            # Update Download Button
            total_selected = len(info.get("entries", []))
            self.download_btn.configure(text=f"⬇   DOWNLOAD PLAYLIST ({total_selected} VIDEOS)")

            # Load Thumbnail if available
            thumb_url = info.get("thumbnail")
            if thumb_url:
                self._load_playlist_thumb_threaded(thumb_url)

        else:
            # ---------------- SINGLE VIDEO MODE (YouTube or TikTok) ----------------
            self.playlist_content.pack_forget()
            self.preview_content.pack(fill="both", expand=True)
            self.preview_content.lift()
            if hasattr(self, "thumb_label") and self.thumb_label.winfo_exists():
                self.thumb_label.configure(image=None, text="⏳ Loading...", text_color=TEXT_MUTED)

            badge_text = "✓ TikTok Loaded (No Watermark)" if is_tiktok else "✓ Video Loaded"
            self.auto_badge.configure(text=badge_text, text_color=COLOR_SUCCESS, fg_color=COLOR_SUCCESS_BG)
            self.input_msg_lbl.configure(text=f"✓ Ready: {info.get('title')}", text_color=COLOR_SUCCESS)

            self.preview_title.configure(text=info.get("title", "No Title"))

            # Recalculate title wrap
            content_w = max(420, self.winfo_width() - 260)
            thumb_w = 260 if self.winfo_width() >= 920 else 200
            self.preview_title.configure(wraplength=max(220, content_w - thumb_w - 60))

            uploader = info.get("uploader", "Unknown Creator")
            self.preview_channel.configure(text=f"👤 {uploader}")

            # Badge pill
            if is_tiktok:
                self.max_res_badge.configure(
                    text="📱 NO WATERMARK",
                    fg_color=COLOR_TIKTOK,
                    text_color="#000000"
                )
                self.format_seg.configure(values=["🎥 Video (MP4 - No Watermark)", "🎵 Audio (MP3)"])
                self.format_seg.set("🎥 Video (MP4 - No Watermark)")
                self.download_btn.configure(text="⬇   DOWNLOAD TIKTOK VIDEO")
            else:
                max_h = info.get("max_height")
                max_fps = info.get("max_fps")
                fps_text = f" {max_fps}fps" if max_fps and max_fps > 30 else ""
                if max_h and max_h >= 2160:
                    res_label = f"🌟 4K UHD{fps_text}"
                elif max_h and max_h >= 1440:
                    res_label = f"2K QHD{fps_text}"
                elif max_h and max_h >= 1080:
                    res_label = f"1080p FHD{fps_text}"
                elif max_h and max_h >= 720:
                    res_label = f"720p HD{fps_text}"
                else:
                    res_label = "HD"

                self.max_res_badge.configure(text=res_label, fg_color=COLOR_PRIMARY, text_color="#FFFFFF")
                self.format_seg.configure(values=["🎥 Video (MP4)", "🎵 Music (MP3)", "🎧 Audio (M4A)"])
                self.format_seg.set("🎥 Video (MP4)")
                self.download_btn.configure(text="⬇   START DOWNLOAD")

            # Metadata
            self.preview_duration.configure(text=f"⏱ {info.get('duration_str', 'N/A')}")
            self.preview_views.configure(text=f"👁 {info.get('views_str', 'N/A')}")

            upload_date = info.get("upload_date", "")
            if len(upload_date) == 8:
                formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            else:
                formatted_date = upload_date or "N/A"
            self.preview_date.configure(text=f"📅 {formatted_date}")

            # Quality dropdown
            self._on_format_changed(self.format_seg.get())

            # Load Thumbnail
            thumb_url = info.get("thumbnail")
            fallbacks = info.get("thumbnail_fallbacks", [])
            if thumb_url:
                self._load_thumbnail_threaded(thumb_url, fallbacks)

    def _populate_playlist_items(self, entries: List[Dict[str, Any]]):
        for widget in self.pl_items_scroll.winfo_children():
            widget.destroy()
        self.playlist_item_vars.clear()

        for e in entries:
            idx = e.get("index", 1)
            var = ctk.BooleanVar(value=True)
            self.playlist_item_vars[idx] = var

            row = ctk.CTkFrame(self.pl_items_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)

            cb = ctk.CTkCheckBox(
                row,
                text=f"{idx:02d}. {e.get('title')} ({e.get('duration_str')})",
                variable=var,
                font=ctk.CTkFont(size=12),
                checkmark_color="#FFFFFF",
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                command=self._on_playlist_item_check_toggled
            )
            cb.pack(side="left", padx=4)

        self._update_playlist_selection_counter()

    def _on_playlist_item_check_toggled(self):
        self._update_playlist_selection_counter()

    def _update_playlist_selection_counter(self):
        total = len(self.playlist_item_vars)
        selected = sum(1 for v in self.playlist_item_vars.values() if v.get())
        self.pl_select_count_lbl.configure(text=f"Videos to Download: {selected} of {total} selected")
        self.download_btn.configure(text=f"⬇   DOWNLOAD PLAYLIST ({selected} VIDEOS)")

    def _select_all_playlist_items(self):
        for v in self.playlist_item_vars.values():
            v.set(True)
        self._update_playlist_selection_counter()

    def _deselect_all_playlist_items(self):
        for v in self.playlist_item_vars.values():
            v.set(False)
        self._update_playlist_selection_counter()

    def _load_playlist_thumb_threaded(self, url: str):
        def task():
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'image/*,*/*;q=0.8'
            }
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200 and len(resp.content) > 500:
                    img_data = Image.open(BytesIO(resp.content))
                    if img_data.mode not in ("RGB", "RGBA"):
                        img_data = img_data.convert("RGB")
                    img_data.thumbnail((180, 100), Image.Resampling.LANCZOS)
                    def update_pl():
                        try:
                            if hasattr(self, "pl_thumb_label") and self.pl_thumb_label.winfo_exists():
                                ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=img_data.size)
                                self.pl_thumb_label.configure(image=ctk_img, text="")
                        except Exception:
                            pass
                    self.run_on_ui_thread(update_pl)
                else:
                    def fallback_pl():
                        try:
                            if hasattr(self, "pl_thumb_label") and self.pl_thumb_label.winfo_exists():
                                self.pl_thumb_label.configure(image=None, text="📑\nPlaylist", text_color=TEXT_MUTED)
                        except Exception:
                            pass
                    self.run_on_ui_thread(fallback_pl)
            except Exception:
                def fallback_pl_err():
                    try:
                        if hasattr(self, "pl_thumb_label") and self.pl_thumb_label.winfo_exists():
                            self.pl_thumb_label.configure(image=None, text="📑\nPlaylist", text_color=TEXT_MUTED)
                    except Exception:
                        pass
                self.run_on_ui_thread(fallback_pl_err)

        threading.Thread(target=task, daemon=True).start()

    def _on_info_fetched_error(self, err_msg: str):
        self.is_fetching = False
        self.auto_badge.configure(text="⚠ Fetch Failed", text_color=COLOR_DANGER, fg_color=COLOR_PRIMARY_SUBTLE)

        cleaned = clean_error_message(err_msg)
        self.input_msg_lbl.configure(text=f"⚠ Error: {cleaned}", text_color=COLOR_DANGER)

    def _load_thumbnail_threaded(self, primary_url: str, fallbacks: Optional[List[str]] = None):
        def task():
            urls_to_try = [primary_url]
            if fallbacks:
                for f_url in fallbacks:
                    if f_url and f_url not in urls_to_try:
                        urls_to_try.append(f_url)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            }

            loaded_image = None
            for u in urls_to_try:
                try:
                    resp = requests.get(u, headers=headers, timeout=4)
                    if resp.status_code == 200 and len(resp.content) > 500:
                        img = Image.open(BytesIO(resp.content))
                        if img.mode not in ("RGB", "RGBA"):
                            img = img.convert("RGB")
                        loaded_image = img
                        break
                except Exception:
                    continue

            if loaded_image is not None:
                self.raw_thumbnail_pil = loaded_image
                self.run_on_ui_thread(self._render_thumbnail_auto)
            else:
                def set_fallback_badge():
                    try:
                        if hasattr(self, "thumb_label") and self.thumb_label.winfo_exists():
                            self.thumb_label.configure(image=None, text="🎬\nMedia Preview", text_color=TEXT_MUTED)
                    except Exception:
                        pass
                self.run_on_ui_thread(set_fallback_badge)

        threading.Thread(target=task, daemon=True).start()

    def _render_thumbnail_auto(self):
        target_w = 260 if self.winfo_width() >= 920 else 200
        target_h = int(target_w * 9 / 16)
        self._render_thumbnail(target_w, target_h)

    def _render_thumbnail(self, width: int, height: int):
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

    def _on_format_changed(self, value: str):
        is_pro = self.license_mgr.is_pro()
        if "Video" in value:
            if not is_pro:
                # FREE TIER OPTIONS: strictly max 720p and max 30fps
                options = [
                    "🌟 Best (Max 720p 30fps - Free)",
                    "🔒 2160p (4K UHD 60fps) [PRO]",
                    "🔒 1440p (2K QHD 60fps) [PRO]",
                    "🔒 1080p (Full HD 60fps) [PRO]",
                    "720p (HD 30fps)",
                    "480p (SD 30fps)",
                    "360p"
                ]
            else:
                # PRO / 7-DAY TRIAL OPTIONS: full 4K, 1440p, 1080p, 60fps
                options = ["🌟 Best Available Quality", "2160p (4K UHD 60fps)", "1440p (2K QHD 60fps)", "1080p (Full HD 60fps)", "720p (HD)", "480p (SD)", "360p"]
                if self.current_video_info and self.current_video_info.get("available_heights"):
                    heights = self.current_video_info["available_heights"]
                    custom_opts = ["🌟 Best Available Quality"]
                    if 2160 in heights:
                        custom_opts.append("2160p (4K UHD 60fps)")
                    if 1440 in heights:
                        custom_opts.append("1440p (2K QHD 60fps)")
                    if 1080 in heights:
                        custom_opts.append("1080p (Full HD 60fps)")
                    if 720 in heights:
                        custom_opts.append("720p (HD)")
                    if 480 in heights:
                        custom_opts.append("480p (SD)")
                    if 360 in heights:
                        custom_opts.append("360p")
                    options = custom_opts
            self.quality_menu.configure(values=options)
            self.quality_menu.set(options[0])

        elif "MP3" in value:
            options = ["💎 320 kbps (Studio Quality)", "256 kbps (High)", "192 kbps (Standard)", "128 kbps (Compact)"]
            self.quality_menu.configure(values=options)
            self.quality_menu.set("💎 320 kbps (Studio Quality)")

        elif "M4A" in value:
            options = ["Best Audio (Original AAC/M4A)"]
            self.quality_menu.configure(values=options)
            self.quality_menu.set("Best Audio (Original AAC/M4A)")

    def _apply_quick_preset(self, format_type: str, quality_key: str):
        is_pro = self.license_mgr.is_pro()
        if format_type == "video" and not is_pro and quality_key in ["best", "1080p", "1440p", "2160p"]:
            self._show_pro_upsell_dialog(
                feature_title="1080p, 4K & 60FPS Video Streams",
                feature_desc="Downloading in 1080p Full HD, 4K Ultra HD or 60FPS requires Media Downloader Pro.\n\nThe Free edition is limited to 720p 30fps.\n\nStart your 7-Day Free Trial (100% Free on this PC) or activate a license key to unlock 4K 60FPS!"
            )
            return

        if format_type == "video":
            if self.current_video_info and self.current_video_info.get("is_playlist"):
                self.format_seg.set("🎥 All as Video (MP4)")
            elif self.current_video_info and self.current_video_info.get("is_tiktok"):
                self.format_seg.set("🎥 Video (MP4 - No Watermark)")
            else:
                self.format_seg.set("🎥 Video (MP4)")
            self._on_format_changed("Video")
            for opt in self.quality_menu._values:
                if quality_key == "best" and "Best" in opt:
                    self.quality_menu.set(opt)
                    break
                elif quality_key in opt:
                    self.quality_menu.set(opt)
                    break
        elif format_type == "audio_mp3":
            if self.current_video_info and self.current_video_info.get("is_playlist"):
                self.format_seg.set("🎵 All as Music (MP3)")
            elif self.current_video_info and self.current_video_info.get("is_tiktok"):
                self.format_seg.set("🎵 Audio (MP3)")
            else:
                self.format_seg.set("🎵 Music (MP3)")
            self._on_format_changed("MP3")
            for opt in self.quality_menu._values:
                if quality_key in opt:
                    self.quality_menu.set(opt)
                    break

    def _on_browse_folder(self):
        selected = ctk.filedialog.askdirectory(initialdir=self.download_dir)
        if selected:
            self.download_dir = selected
            self.config.set("download_dir", self.download_dir)
            self.folder_display.configure(state="normal")
            self.folder_display.delete(0, "end")
            self.folder_display.insert(0, self.download_dir)
            self.folder_display.configure(state="readonly")

    def _open_in_browser(self):
        if self.current_video_info and self.current_video_info.get("webpage_url"):
            webbrowser.open(self.current_video_info["webpage_url"])

    def _copy_video_link(self):
        url = self.url_var.get().strip()
        if url:
            pyperclip.copy(url)
            self.copy_link_btn.configure(text="✓ Copied!")
            self.after(2000, lambda: self.copy_link_btn.configure(text="📋 Copy Link"))

    def _load_palette_constants(self, palette_key: str):
        """Set module colors based on the requested calm palette."""
        global COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_SUBTLE
        global BG_WINDOW, BG_SIDEBAR, BG_CARD, BG_CARD_SUBTLE, BG_CARD_HOVER, BORDER_COLOR
        if palette_key not in CALM_PALETTES:
            palette_key = "Ocean"
        pal = CALM_PALETTES[palette_key]
        COLOR_PRIMARY = pal["primary"]
        COLOR_PRIMARY_HOVER = pal["primary_hover"]
        COLOR_PRIMARY_SUBTLE = pal["primary_subtle"]
        BG_WINDOW = pal["bg_window"]
        BG_SIDEBAR = pal["bg_sidebar"]
        BG_CARD = pal["bg_card"]
        BG_CARD_SUBTLE = pal["bg_card_subtle"]
        BG_CARD_HOVER = pal["bg_card_hover"]
        BORDER_COLOR = pal["border"]

    def _apply_theme_palette(self, palette_key: str, save_config: bool = True):
        """Dynamically re-skin active widgets with the selected calm color palette."""
        global COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_SUBTLE
        if palette_key not in CALM_PALETTES:
            palette_key = "Ocean"
        pal = CALM_PALETTES[palette_key]
        self.current_palette_key = palette_key
        self._load_palette_constants(palette_key)

        if save_config:
            self.config.set("theme_palette", palette_key)

        # 1. Update Logo & Branding
        if hasattr(self, "logo_icon") and self.logo_icon.winfo_exists():
            self.logo_icon.configure(fg_color=COLOR_PRIMARY)

        # 2. Update Nav Buttons
        if hasattr(self, "active_tab"):
            self._switch_tab(self.active_tab)

        # 3. Update Downloader View Widgets
        if hasattr(self, "download_btn") and self.download_btn.winfo_exists():
            self.download_btn.configure(fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "paste_btn") and self.paste_btn.winfo_exists():
            self.paste_btn.configure(fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "format_seg") and self.format_seg.winfo_exists():
            self.format_seg.configure(selected_color=COLOR_PRIMARY, selected_hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "quality_menu") and self.quality_menu.winfo_exists():
            self.quality_menu.configure(button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "download_progress") and self.download_progress.winfo_exists():
            self.download_progress.configure(progress_color=COLOR_PRIMARY)
        if hasattr(self, "batch_download_btn") and self.batch_download_btn.winfo_exists():
            self.batch_download_btn.configure(fg_color=COLOR_PRIMARY)

        # 4. Update Browse View Widgets
        if hasattr(self, "browse_search_btn") and self.browse_search_btn.winfo_exists():
            self.browse_search_btn.configure(fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "browse_subtab_seg") and self.browse_subtab_seg.winfo_exists():
            self.browse_subtab_seg.configure(selected_color=COLOR_PRIMARY, selected_hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "browse_batch_format_seg") and self.browse_batch_format_seg.winfo_exists():
            self.browse_batch_format_seg.configure(selected_color=COLOR_PRIMARY, selected_hover_color=COLOR_PRIMARY_HOVER)
        if hasattr(self, "browse_batch_quality_menu") and self.browse_batch_quality_menu.winfo_exists():
            self.browse_batch_quality_menu.configure(button_color=COLOR_PRIMARY)
        if hasattr(self, "browse_batch_dl_btn") and self.browse_batch_dl_btn.winfo_exists():
            self.browse_batch_dl_btn.configure(fg_color=COLOR_PRIMARY_HOVER, hover_color=COLOR_PRIMARY)

        # 5. Update Settings View Widgets
        if hasattr(self, "scale_menu") and self.scale_menu.winfo_exists():
            self.scale_menu.configure(button_color=COLOR_PRIMARY)
        if hasattr(self, "clip_switch") and self.clip_switch.winfo_exists():
            self.clip_switch.configure(progress_color=COLOR_PRIMARY)

        # 6. Synchronize dropdowns
        disp_map = {
            "Ocean": "🌊 Calm Ocean",
            "Sage": "🌿 Nordic Sage",
            "Lavender": "🔮 Twilight Lavender",
            "Amber": "🌅 Warm Sunset",
            "Slate": "🩶 Minimal Slate",
            "Rose": "🌸 Soft Rose"
        }
        disp_val = disp_map.get(palette_key, "🌊 Calm Ocean")
        if hasattr(self, "sidebar_palette_menu") and self.sidebar_palette_menu.winfo_exists():
            self.sidebar_palette_menu.set(disp_val)
            self.sidebar_palette_menu.configure(button_color=COLOR_PRIMARY)
        if hasattr(self, "settings_palette_menu") and self.settings_palette_menu.winfo_exists():
            self.settings_palette_menu.set(disp_val)
            self.settings_palette_menu.configure(button_color=COLOR_PRIMARY)

    def _on_palette_menu_selected(self, choice_text: str):
        """Handler for palette dropdown selection."""
        if "Ocean" in choice_text:
            key = "Ocean"
        elif "Sage" in choice_text:
            key = "Sage"
        elif "Lavender" in choice_text:
            key = "Lavender"
        elif "Amber" in choice_text or "Sunset" in choice_text:
            key = "Amber"
        elif "Slate" in choice_text:
            key = "Slate"
        elif "Rose" in choice_text:
            key = "Rose"
        else:
            key = "Ocean"
        self._apply_theme_palette(key)

    def _on_theme_switched(self):
        mode = self.theme_switch.get()
        ctk.set_appearance_mode(mode)
        self.config.set("theme", mode)
        self.theme_switch.configure(text=f"{mode} Mode")

    def _copy_text(self, text: str, msg: str = "Copied!"):
        try:
            pyperclip.copy(text)
            if hasattr(self, "input_msg_lbl") and self.input_msg_lbl.winfo_exists():
                self.input_msg_lbl.configure(text=f"✔ {msg}", text_color=COLOR_SUCCESS)
        except Exception:
            pass

    def _update_license_ui(self):
        """Update all badges, labels, and buttons reflecting current Pro status, 7-Day Free Trial, or Free tier."""
        status = self.license_mgr.get_status()
        is_pro = status.get("is_pro", False)
        is_trial = status.get("is_trial", False)
        can_trial = status.get("can_start_trial", False)
        days_rem = status.get("days_remaining", 0)

        # 1. Update Header Button
        if hasattr(self, "header_pro_btn") and self.header_pro_btn.winfo_exists():
            if is_pro and not is_trial:
                self.header_pro_btn.configure(
                    text="👑 PRO ACTIVATED",
                    fg_color="#10B981",
                    hover_color="#059669",
                    command=self._open_activation_dialog
                )
            elif is_trial:
                self.header_pro_btn.configure(
                    text=f"👑 TRIAL: {days_rem}d LEFT",
                    fg_color="#0284C7",
                    hover_color="#0369A1",
                    command=self._open_activation_dialog
                )
            elif can_trial:
                self.header_pro_btn.configure(
                    text="🎁 Free 7-Day Trial",
                    fg_color="#D97706",
                    hover_color="#B45309",
                    command=self._on_start_trial_promo_clicked
                )
            else:
                self.header_pro_btn.configure(
                    text="⭐ Activate Pro Key",
                    fg_color="#D97706",
                    hover_color="#B45309",
                    command=self._open_activation_dialog
                )

        # 2. Update Sidebar Card
        if hasattr(self, "sidebar_pro_card") and self.sidebar_pro_card.winfo_exists():
            if is_pro and not is_trial:
                self.sidebar_pro_card.configure(border_color="#10B981")
                self.sidebar_pro_badge.configure(text="👑 PRO MEMBER", text_color="#10B981")
                plan_t = status.get("plan_title", "Pro Plan")
                exp_t = status.get("expires_at", "Lifetime")
                self.sidebar_pro_desc.configure(text=f"{plan_t}\nExpires: {exp_t}")
                self.sidebar_pro_btn.configure(
                    text="Manage License",
                    fg_color="#10B981",
                    hover_color="#059669",
                    command=self._open_activation_dialog
                )
            elif is_trial:
                self.sidebar_pro_card.configure(border_color="#00F2FE")
                self.sidebar_pro_badge.configure(text="👑 PRO 7-DAY TRIAL", text_color="#00F2FE")
                self.sidebar_pro_desc.configure(text=f"Active on this PC\n{days_rem} Days Remaining")
                self.sidebar_pro_btn.configure(
                    text="💎 Upgrade to Lifetime",
                    fg_color="#D97706",
                    hover_color="#B45309",
                    command=self._open_activation_dialog
                )
            elif can_trial:
                self.sidebar_pro_card.configure(border_color="#F59E0B")
                self.sidebar_pro_badge.configure(text="🎁 7-DAY FREE TRIAL", text_color="#F59E0B")
                self.sidebar_pro_desc.configure(text="Unlock 4K 60fps & Playlists free on this PC")
                self.sidebar_pro_btn.configure(
                    text="⚡ Start Free Trial",
                    fg_color="#0284C7",
                    hover_color="#0369A1",
                    command=self._on_start_trial_promo_clicked
                )
            else:
                self.sidebar_pro_card.configure(border_color="#D97706")
                self.sidebar_pro_badge.configure(text="⭐ FREE EDITION", text_color="#F59E0B")
                self.sidebar_pro_desc.configure(text="Trial expired (Max 720p 30fps). Upgrade for 4K 60fps.")
                self.sidebar_pro_btn.configure(
                    text="⚡ Activate Pro Key",
                    fg_color="#D97706",
                    hover_color="#B45309",
                    command=self._open_activation_dialog
                )

        # 2.5 Update Top Promotional Banner
        if hasattr(self, "promo_trial_banner") and self.promo_trial_banner.winfo_exists():
            if is_pro and not is_trial:
                self.promo_trial_banner.pack_forget()
            elif is_trial:
                padx = getattr(self, "promo_trial_padx", 16)
                if hasattr(self, "input_card") and self.input_card.winfo_exists():
                    self.promo_trial_banner.pack(fill="x", padx=padx, pady=(0, 14), before=self.input_card)
                else:
                    self.promo_trial_banner.pack(fill="x", padx=padx, pady=(0, 14))
                self.promo_trial_banner.configure(border_color="#00F2FE")
                self.promo_banner_title.configure(text=f"👑 PRO 7-DAY TRIAL: {days_rem} Days Remaining", text_color="#00F2FE")
                self.promo_banner_sub.configure(text="All Pro features active on this PC (4K 60fps, Batch Playlists, Lossless 320k MP3).")
                self.promo_banner_btn.configure(text="💎 Upgrade to Lifetime Pro", fg_color="#D97706", hover_color="#B45309", command=self._open_activation_dialog)
            elif can_trial:
                padx = getattr(self, "promo_trial_padx", 16)
                if hasattr(self, "input_card") and self.input_card.winfo_exists():
                    self.promo_trial_banner.pack(fill="x", padx=padx, pady=(0, 14), before=self.input_card)
                else:
                    self.promo_trial_banner.pack(fill="x", padx=padx, pady=(0, 14))
                self.promo_trial_banner.configure(border_color="#F59E0B")
                self.promo_banner_title.configure(text="🎁 SPECIAL PROMOTION: Try Pro 100% Free for 7 Days!", text_color="#F59E0B")
                self.promo_banner_sub.configure(text="Free Edition is limited to 720p 30fps. Start your 7-Day Free Trial to unlock 4K 60fps!")
                self.promo_banner_btn.configure(text="⚡ Start 7-Day Free Trial (0$)", fg_color="#0284C7", hover_color="#0369A1", command=self._on_start_trial_promo_clicked)
            else:
                padx = getattr(self, "promo_trial_padx", 16)
                if hasattr(self, "input_card") and self.input_card.winfo_exists():
                    self.promo_trial_banner.pack(fill="x", padx=padx, pady=(0, 14), before=self.input_card)
                else:
                    self.promo_trial_banner.pack(fill="x", padx=padx, pady=(0, 14))
                self.promo_trial_banner.configure(border_color=BORDER_COLOR)
                self.promo_banner_title.configure(text="⭐ 7-Day Free Trial Expired — Free Edition Active (Max 720p 30fps)", text_color=COLOR_WARNING)
                self.promo_banner_sub.configure(text="Upgrade to Pro Lifetime to restore 4K 60fps, unlimited playlists & high-speed acceleration.")
                self.promo_banner_btn.configure(text="🛒 Buy Pro License Key", fg_color="#F59E0B", hover_color="#D97706", command=lambda: webbrowser.open("https://prodownloader.site#pricing"))

        # 3. Update Settings Card
        if hasattr(self, "lic_badge_pill") and self.lic_badge_pill.winfo_exists():
            if is_pro and not is_trial:
                self.lic_badge_pill.configure(
                    text="👑 PRO ACTIVE",
                    fg_color="#D1FAE5",
                    text_color="#065F46"
                )
                self.lic_plan_lbl.configure(text=status.get("plan_title", "Pro Plan"))
                self.lic_exp_lbl.configure(text=status.get("expires_at", "Lifetime"))
                full_key = status.get("license_key", "")
                masked_key = (full_key[:8] + "••••" + full_key[-5:]) if len(full_key) >= 14 else full_key
                self.lic_key_lbl.configure(text=masked_key)
                self.lic_desc_lbl.configure(text=f"Licensed to: {status.get('customer_name', 'Customer')} | Unlimited Pro Features Active")
                self.lic_activate_btn.configure(text="🔑 Change License Key", fg_color=BG_CARD_SUBTLE, hover_color=BG_CARD_HOVER, text_color=TEXT_PRIMARY)
                self.lic_deactivate_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))
            elif is_trial:
                self.lic_badge_pill.configure(
                    text="👑 PRO TRIAL ACTIVE",
                    fg_color="#E0F2FE",
                    text_color="#0369A1"
                )
                self.lic_plan_lbl.configure(text="Pro 7-Day Free Trial")
                self.lic_exp_lbl.configure(text=f"{status.get('expires_at', '7 Days')} ({days_rem} days left)")
                self.lic_key_lbl.configure(text=status.get("license_key", "TRIAL"))
                self.lic_desc_lbl.configure(text="Trial active on this PC. Unlimited 4K 60fps and playlists active.")
                self.lic_activate_btn.configure(text="💎 Upgrade to Pro Lifetime", fg_color="#D97706", hover_color="#B45309", text_color="#FFFFFF")
                self.lic_deactivate_btn.pack_forget()
            else:
                self.lic_badge_pill.configure(
                    text="FREE EDITION",
                    fg_color=BG_CARD_SUBTLE,
                    text_color=COLOR_WARNING
                )
                self.lic_plan_lbl.configure(text="Free Edition (Max 720p 30fps)")
                self.lic_exp_lbl.configure(text="N/A")
                self.lic_key_lbl.configure(text="None")
                self.lic_desc_lbl.configure(text="Free edition limited to 720p 30fps. Start 7-Day Free Trial or activate Pro Key for 4K 60fps.")
                if can_trial:
                    self.lic_activate_btn.configure(text="⚡ Start 7-Day Free Trial (0$)", fg_color="#0284C7", hover_color="#0369A1", text_color="#FFFFFF")
                else:
                    self.lic_activate_btn.configure(text="⚡ Activate Pro License Key", fg_color="#D97706", hover_color="#B45309", text_color="#FFFFFF")
                self.lic_deactivate_btn.pack_forget()

    def _open_activation_dialog(self):
        """Open modern modal dialog for activating license key with cyber-luxury aesthetic and error protection."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Activate Media Downloader Pro")
        dialog.geometry("560x700")
        dialog.minsize(520, 650)
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 560) // 2
        y = self.winfo_y() + (self.winfo_height() - 700) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        frame = ctk.CTkFrame(dialog, fg_color=BG_WINDOW, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=22, pady=20)

        # Header Box
        head_box = ctk.CTkFrame(frame, fg_color="transparent")
        head_box.pack(fill="x", pady=(0, 12))

        head_title_row = ctk.CTkFrame(head_box, fg_color="transparent")
        head_title_row.pack(anchor="w")

        ctk.CTkLabel(
            head_title_row,
            text="👑 DOWNLOADER PRO",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F59E0B"
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            head_title_row,
            text="TURBO VIP ENCLAVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#00F2FE",
            fg_color=BG_CARD_SUBTLE,
            corner_radius=6,
            height=20,
            padx=8
        ).pack(side="left")

        ctk.CTkLabel(
            head_box,
            text="Unlock unlimited 4K 60FPS video, audio extractions & batch playlist grabbers.\nPackages: Monthly $1.99 · Annual $14.99 · Lifetime $24.99 (or 7-Day Free Trial for $0)",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Pro Perks Box
        perks_card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        perks_card.pack(fill="x", pady=(0, 14), ipady=6)

        ctk.CTkLabel(
            perks_card,
            text="⚡ PRO STUDIO PRIVILEGES UNLOCKED:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#F59E0B"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        perks = [
            ("🚀", "Unlimited Playlist Batch Downloads", "Download 1,000+ videos in one click"),
            ("🌟", "Ultra HD 4K & 2K 60FPS", "Highest possible YouTube AV1/VP9 fidelity"),
            ("⚡", "Multi-Threaded Turbo Engine", "Up to 5x higher network throughput"),
            ("🎵", "Studio 320kbps MP3 / Hi-Fi M4A", "Lossless audio extraction with full ID3 tags"),
            ("📱", "TikTok Clean Stream Engine", "100% watermark-free direct MP4 capture")
        ]
        for icon, title, desc in perks:
            p_row = ctk.CTkFrame(perks_card, fg_color="transparent")
            p_row.pack(fill="x", padx=14, pady=2)
            ctk.CTkLabel(p_row, text=icon, font=ctk.CTkFont(size=12), width=20).pack(side="left")
            ctk.CTkLabel(p_row, text=f" {title} ", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(p_row, text=f"— {desc}", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(side="left")

        if self.license_mgr.can_start_trial():
            trial_promo_card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color="#00F2FE")
            trial_promo_card.pack(fill="x", pady=(0, 12), ipady=4)

            tp_head = ctk.CTkFrame(trial_promo_card, fg_color="transparent")
            tp_head.pack(fill="x", padx=14, pady=(6, 2))
            ctk.CTkLabel(tp_head, text="🎁 SPECIAL PROMO: 7-DAY FREE TRIAL (1 PC)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00F2FE").pack(side="left")
            ctk.CTkLabel(tp_head, text="No Card Required", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(side="right")

            ctk.CTkLabel(
                trial_promo_card,
                text="Try full Pro abilities free on this PC for 7 days: 4K 60fps, unlimited playlists & turbo speed.",
                font=ctk.CTkFont(size=10),
                text_color=TEXT_MUTED
            ).pack(anchor="w", padx=14, pady=(0, 6))

            def start_trial_action():
                trial_act_btn.configure(state="disabled", text="Activating Trial...")
                def worker():
                    ok, msg = self.license_mgr.start_trial()
                    def on_done():
                        if ok:
                            self._update_license_ui()
                            self._on_format_changed(self.format_seg.get())
                            dialog.destroy()
                            self._show_info_dialog("Trial Activated", msg)
                        else:
                            trial_act_btn.configure(state="normal", text="⚡ Start 7-Day Free Trial (0$)")
                            self._show_info_dialog("Notice", msg, is_error=True)
                    self.after(100, on_done)
                threading.Thread(target=worker, daemon=True).start()

            trial_act_btn = ctk.CTkButton(
                trial_promo_card,
                text="⚡ Start 7-Day Free Trial Now (0$ - Instant Unlock)",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#0284C7",
                hover_color="#0369A1",
                height=36,
                corner_radius=8,
                command=start_trial_action
            )
            trial_act_btn.pack(fill="x", padx=14, pady=(2, 8))

        # Step 1: Hardware ID Box
        hwid_box = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        hwid_box.pack(fill="x", pady=(0, 12), ipady=4)

        hwid_title_row = ctk.CTkFrame(hwid_box, fg_color="transparent")
        hwid_title_row.pack(fill="x", padx=14, pady=(8, 2))

        ctk.CTkLabel(
            hwid_title_row,
            text="1️⃣ YOUR MACHINE HARDWARE ID (HWID):",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkLabel(
            hwid_box,
            text="Send this HWID to the administrator/seller to generate your custom Pro key:",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=14, pady=(0, 6))

        hwid_val_row = ctk.CTkFrame(hwid_box, fg_color="transparent")
        hwid_val_row.pack(fill="x", padx=14, pady=(0, 8))

        hwid_entry = ctk.CTkEntry(
            hwid_val_row,
            height=34,
            font=ctk.CTkFont(size=11, family="Consolas", weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color=BORDER_COLOR
        )
        hwid_entry.insert(0, self.license_mgr.hwid)
        hwid_entry.configure(state="readonly")
        hwid_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def copy_hwid_action():
            pyperclip.copy(self.license_mgr.hwid)
            status_msg.configure(text="✔ Machine HWID copied to clipboard! Send this to the seller.", text_color=COLOR_SUCCESS)

        copy_hwid_btn = ctk.CTkButton(
            hwid_val_row,
            text="📋 Copy HWID",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=95,
            height=34,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            command=copy_hwid_action
        )
        copy_hwid_btn.pack(side="left")

        # Step 2: License Key Input Box (PRIMARY SECTION)
        key_box = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        key_box.pack(fill="x", pady=(0, 10), ipady=4)

        ctk.CTkLabel(
            key_box,
            text="2️⃣ ENTER PRO LICENSE KEY:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=14, pady=(8, 2))

        ctk.CTkLabel(
            key_box,
            text="Paste the activation key provided by the seller (starts with MDP-...):",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=14, pady=(0, 6))

        input_row = ctk.CTkFrame(key_box, fg_color="transparent")
        input_row.pack(fill="x", padx=14, pady=(0, 10))

        key_var = ctk.StringVar()
        current_status = self.license_mgr.get_status()
        if current_status.get("is_pro") and current_status.get("license_key") != "None":
            key_var.set(current_status.get("license_key", ""))

        key_entry = ctk.CTkEntry(
            input_row,
            textvariable=key_var,
            placeholder_text="MDP-LFT-XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(size=13, family="Consolas", weight="bold"),
            height=40,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_CARD_SUBTLE
        )
        key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def paste_key_action():
            try:
                txt = pyperclip.paste().strip()
                if txt:
                    key_var.set(txt.upper())
            except Exception:
                pass

        paste_btn = ctk.CTkButton(
            input_row,
            text="📋 Paste Key",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90,
            height=40,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            command=paste_key_action
        )
        paste_btn.pack(side="left")

        # Feedback / Status Message Label
        status_msg = ctk.CTkLabel(
            frame,
            text="Enter your Pro key, then click 'Activate Pro License'.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            wraplength=500,
            justify="left"
        )
        status_msg.pack(anchor="w", pady=(0, 12))

        # Action Buttons
        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        def perform_activation():
            raw_k = key_var.get().strip()

            # Smart validation check to prevent confusing HWID with Pro Key
            if not raw_k:
                status_msg.configure(text="⚠️ Please enter or paste your Pro License Key.", text_color="#F59E0B")
                return

            if raw_k == self.license_mgr.hwid or raw_k.startswith("HWID-"):
                status_msg.configure(
                    text="⚠️ That is your Machine HWID! Please enter your Pro Key (starts with MDP-) issued by the seller.",
                    text_color="#F59E0B"
                )
                return

            status_msg.configure(text="Verifying cryptographic signature...", text_color=COLOR_ACCENT)
            activate_cta.configure(state="disabled", text="Verifying...")

            def worker():
                ok, msg = self.license_mgr.activate(raw_k)
                def on_done():
                    if ok:
                        status_msg.configure(text=f"✔ {msg}", text_color=COLOR_SUCCESS)
                        activate_cta.configure(text="✔ ACTIVATED!", fg_color=COLOR_SUCCESS)
                        self._update_license_ui()
                        dialog.after(1600, dialog.destroy)
                    else:
                        status_msg.configure(text=f"✖ {msg}", text_color=COLOR_DANGER)
                        activate_cta.configure(state="normal", text="⚡ Activate Pro License")
                dialog.after(100, on_done)

            threading.Thread(target=worker, daemon=True).start()

        activate_cta = ctk.CTkButton(
            btn_box,
            text="⚡ Activate Pro License",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#F59E0B",
            hover_color="#D97706",
            height=42,
            corner_radius=10,
            command=perform_activation
        )
        activate_cta.pack(side="left", fill="x", expand=True, padx=(0, 8))

        buy_online_btn = ctk.CTkButton(
            btn_box,
            text="🌐 Buy Key Online (From $1.99)",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=42,
            corner_radius=10,
            command=lambda: webbrowser.open("https://prodownloader.site#pricing")
        )
        buy_online_btn.pack(side="left", padx=(0, 8))

        close_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            width=70,
            height=42,
            corner_radius=10,
            command=dialog.destroy
        )
        close_btn.pack(side="left")

    def _deactivate_license_confirmed(self):
        """Ask confirmation and deactivate license to release device slot for transfer."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Transfer / Deactivate License")
        dialog.geometry("460x280")
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 460) // 2
        y = self.winfo_y() + (self.winfo_height() - 280) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(dialog, fg_color=BG_WINDOW, corner_radius=0)
        f.pack(fill="both", expand=True, padx=22, pady=22)

        ctk.CTkLabel(
            f,
            text="🔌 Deactivate License?",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COLOR_DANGER
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            f,
            text="This will unbind your license key from this computer.\nYour activation slot will be freed so you can activate and use your Pro license on another PC.\n\nAre you sure you want to proceed?",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=410
        ).pack(anchor="w", pady=(0, 20))

        b_row = ctk.CTkFrame(f, fg_color="transparent")
        b_row.pack(fill="x", side="bottom")

        def do_deactivate():
            ok, msg = self.license_mgr.deactivate()
            self._update_license_ui()
            dialog.destroy()

        btn_confirm = ctk.CTkButton(
            b_row,
            text="Yes, Deactivate",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=38,
            corner_radius=8,
            command=do_deactivate
        )
        btn_confirm.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_cancel = ctk.CTkButton(
            b_row,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            width=80,
            height=38,
            corner_radius=8,
            command=dialog.destroy
        )
        btn_cancel.pack(side="left")

    def _show_pro_upsell_dialog(self, feature_title: str, feature_desc: str):
        """Show clean modal dialog explaining a Pro feature and offering activation or free trial."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Pro Feature")
        can_trial = self.license_mgr.can_start_trial()
        dlg_h = 390 if can_trial else 320
        dialog.geometry(f"520x{dlg_h}")
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 520) // 2
        y = self.winfo_y() + (self.winfo_height() - dlg_h) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(dialog, fg_color=BG_WINDOW, corner_radius=0)
        f.pack(fill="both", expand=True, padx=22, pady=20)

        ctk.CTkLabel(
            f,
            text=f"👑 {feature_title}",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#F59E0B"
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            f,
            text=feature_desc,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=470
        ).pack(anchor="w", pady=(0, 12))

        if can_trial:
            trial_box = ctk.CTkFrame(f, fg_color=BG_CARD, border_width=1, border_color="#00F2FE", corner_radius=10)
            trial_box.pack(fill="x", pady=(0, 14), ipady=4)

            tb_head = ctk.CTkFrame(trial_box, fg_color="transparent")
            tb_head.pack(fill="x", padx=12, pady=(6, 2))
            ctk.CTkLabel(tb_head, text="🎁 SPECIAL PROMOTION: 7-DAY FREE TRIAL", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00F2FE").pack(side="left")
            ctk.CTkLabel(tb_head, text="100% FREE · 1 PC", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(side="right")

            def start_trial_click():
                btn_trial.configure(state="disabled", text="Activating Trial...")
                def worker():
                    ok, msg = self.license_mgr.start_trial()
                    def on_done():
                        if ok:
                            dialog.destroy()
                            self._update_license_ui()
                            self._on_format_changed(self.format_seg.get())
                            self._show_info_dialog("Trial Activated", msg)
                        else:
                            btn_trial.configure(state="normal", text="⚡ Start 7-Day Free Trial (0$)")
                            self._show_info_dialog("Trial Notice", msg, is_error=True)
                    self.after(100, on_done)
                threading.Thread(target=worker, daemon=True).start()

            btn_trial = ctk.CTkButton(
                trial_box,
                text="⚡ Start 7-Day Free Trial (0$ - 1 PC)",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#0284C7",
                hover_color="#0369A1",
                height=34,
                corner_radius=8,
                command=start_trial_click
            )
            btn_trial.pack(fill="x", padx=12, pady=(4, 6))

        b_row = ctk.CTkFrame(f, fg_color="transparent")
        b_row.pack(fill="x", side="bottom")

        def go_activate():
            dialog.destroy()
            self._open_activation_dialog()

        btn_act = ctk.CTkButton(
            b_row,
            text="🔑 Enter Pro Key",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#F59E0B",
            hover_color="#D97706",
            height=38,
            corner_radius=8,
            command=go_activate
        )
        btn_act.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_buy = ctk.CTkButton(
            b_row,
            text="🌐 Buy Key ($1.99+)",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            width=90,
            height=38,
            corner_radius=8,
            command=lambda: webbrowser.open("https://prodownloader.site#pricing")
        )
        btn_buy.pack(side="left", padx=(0, 8))

        btn_dismiss = ctk.CTkButton(
            b_row,
            text="Maybe Later",
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            width=95,
            height=38,
            corner_radius=8,
            command=dialog.destroy
        )
        btn_dismiss.pack(side="left")

    # ---------------- Download Execution (Single & Playlist) ----------------

    def _on_download_clicked(self):
        url = self.url_var.get().strip()
        if not url:
            self.input_msg_lbl.configure(text="Please provide a valid YouTube, TikTok, or Playlist link first.", text_color=COLOR_WARNING)
            return

        if self.is_downloading:
            return

        format_choice = self.format_seg.get()
        if "MP3" in format_choice:
            format_type = "audio_mp3"
        elif "M4A" in format_choice:
            format_type = "audio_m4a"
        else:
            format_type = "video"

        quality_choice = self.quality_menu.get()
        if "Best" in quality_choice:
            quality = "best"
        elif "2160p" in quality_choice:
            quality = "2160p"
        elif "1440p" in quality_choice:
            quality = "1440p"
        elif "1080p" in quality_choice:
            quality = "1080p"
        elif "720p" in quality_choice:
            quality = "720p"
        elif "480p" in quality_choice:
            quality = "480p"
        elif "360p" in quality_choice:
            quality = "360p"
        elif "320" in quality_choice:
            quality = "320"
        elif "256" in quality_choice:
            quality = "256"
        elif "192" in quality_choice:
            quality = "192"
        elif "128" in quality_choice:
            quality = "128"
        else:
            quality = "best"

        # Check Pro restrictions on >720p resolutions and 60fps
        if not self.license_mgr.is_pro() and format_type == "video":
            if any(k in quality_choice for k in ["2160p", "1440p", "1080p", "4K", "2K", "60fps", "[PRO]"]):
                self._show_pro_upsell_dialog(
                    feature_title="1080p, 4K & 60FPS Video Streams",
                    feature_desc="Downloading in 1080p Full HD, 4K Ultra HD or 60FPS requires Media Downloader Pro.\n\nThe Free edition is strictly limited to 720p at 30fps max.\n\nStart your 7-Day Free Trial (100% Free on this PC) or activate a license key to unlock 4K 60FPS!"
                )
                return

        is_pl = self.current_video_info and self.current_video_info.get("is_playlist")

        if is_pl:
            # ---------------- PLAYLIST DOWNLOAD ----------------
            selected_indices = [idx for idx, v in self.playlist_item_vars.items() if v.get()]
            if not selected_indices:
                self.input_msg_lbl.configure(text="Please select at least 1 video from the playlist to download.", text_color=COLOR_WARNING)
                return

            if not self.license_mgr.is_pro() and len(selected_indices) > 3:
                self._show_pro_upsell_dialog(
                    feature_title="Unlimited Playlist Batch Downloads",
                    feature_desc=f"You selected {len(selected_indices)} videos from this playlist. The Free edition is limited to 3 playlist videos per batch.\n\nActivate Media Downloader Pro to batch download entire playlists with dozens or hundreds of videos at once!"
                )
                return

        self.is_downloading = True
        self.active_cancel_token = CancelToken()

        self.download_btn.configure(state="disabled", text="⏳ DOWNLOADING...")
        self.cancel_btn.configure(state="normal", fg_color=COLOR_DANGER)
        self.paste_btn.configure(state="disabled")

        self.complete_bar.pack_forget()
        self.progress_bar.set(0.0)

        if is_pl:
            # ---------------- PLAYLIST DOWNLOAD ----------------
            selected_indices = [idx for idx, v in self.playlist_item_vars.items() if v.get()]

            self.status_title.configure(text="PLAYLIST QUEUE")
            self.lbl_sp_t.configure(text="CURRENT VIDEO")
            self.status_lbl.configure(text=f"Starting: 0 / {len(selected_indices)}", text_color=COLOR_ACCENT)
            self.speed_lbl.configure(text="Initializing...", text_color=TEXT_PRIMARY)
            self.size_lbl.configure(text="-- / --", text_color=TEXT_PRIMARY)
            self.eta_lbl.configure(text="--:--", text_color=TEXT_PRIMARY)

            def playlist_task():
                try:
                    files = self.downloader.download_playlist(
                        playlist_info=self.current_video_info,
                        selected_indices=selected_indices,
                        download_dir=self.download_dir,
                        format_type=format_type,
                        quality=quality,
                        progress_callback=self._on_download_progress,
                        cancel_token=self.active_cancel_token
                    )
                    self.run_on_ui_thread(self._on_playlist_download_success, files, format_type, quality)
                except Exception as e:
                    err_text = str(e)
                    self.run_on_ui_thread(self._on_download_error, err_text)

            threading.Thread(target=playlist_task, daemon=True).start()

        else:
            # ---------------- SINGLE VIDEO / TIKTOK DOWNLOAD ----------------
            self.status_title.configure(text="STATUS")
            self.lbl_sp_t.configure(text="DOWNLOAD SPEED")
            self.status_lbl.configure(text="Initializing...", text_color=COLOR_ACCENT)
            self.speed_lbl.configure(text="Calculating...", text_color=TEXT_PRIMARY)
            self.size_lbl.configure(text="-- / --", text_color=TEXT_PRIMARY)
            self.eta_lbl.configure(text="--:--", text_color=TEXT_PRIMARY)

            def task():
                try:
                    out_path = self.downloader.download(
                        url=url,
                        download_dir=self.download_dir,
                        format_type=format_type,
                        quality=quality,
                        progress_callback=self._on_download_progress,
                        cancel_token=self.active_cancel_token
                    )
                    self.run_on_ui_thread(self._on_download_success, out_path, format_type, quality)
                except Exception as e:
                    err_text = str(e)
                    self.run_on_ui_thread(self._on_download_error, err_text)

            threading.Thread(target=task, daemon=True).start()

    def _on_download_progress(self, data: Dict[str, Any]):
        self.run_on_ui_thread(self._update_progress_ui, data)

    def _update_progress_ui(self, data: Dict[str, Any]):
        is_pl = data.get("is_playlist", False)
        status = data.get("status", "")

        if is_pl:
            # Playlist progress telemetry
            curr_item = data.get("overall_current", 1)
            total_items = data.get("overall_total", 1)
            item_title = data.get("current_title", "")
            if len(item_title) > 28:
                item_title = item_title[:28] + "..."

            pct = data.get("percent", 0.0)
            overall_pct = ((curr_item - 1) + (pct / 100.0)) / total_items
            self.progress_bar.set(min(max(overall_pct, 0.0), 1.0))

            self.status_lbl.configure(
                text=f"Video {curr_item} of {total_items} ({pct:.0f}%)",
                text_color=COLOR_PRIMARY
            )
            self.speed_lbl.configure(text=item_title)

            speed = data.get("speed", "")
            downloaded = data.get("downloaded", "")
            total = data.get("total", "")
            eta = data.get("eta", "")

            if downloaded and total:
                self.size_lbl.configure(text=f"{downloaded}/{total}")
            if eta and eta != "N/A":
                self.eta_lbl.configure(text=eta)

        else:
            # Single video telemetry
            if status == "downloading":
                pct = data.get("percent", 0.0)
                self.progress_bar.set(pct / 100.0)
                self.status_lbl.configure(
                    text=f"Downloading ({pct:.1f}%)",
                    text_color=COLOR_PRIMARY
                )

                speed = data.get("speed", "")
                if speed:
                    self.speed_lbl.configure(text=speed)

                downloaded = data.get("downloaded", "")
                total = data.get("total", "")
                if downloaded and total:
                    self.size_lbl.configure(text=f"{downloaded} / {total}")

                eta = data.get("eta", "")
                if eta and eta != "N/A":
                    self.eta_lbl.configure(text=eta)

            elif status == "processing":
                self.progress_bar.set(1.0)
                msg = data.get("message", "Processing & Merging...")
                self.status_lbl.configure(text=msg, text_color=COLOR_WARNING)
                self.speed_lbl.configure(text="Merging")
                self.eta_lbl.configure(text="Finalizing")

    def _on_download_success(self, file_path: str, format_type: str, quality: str):
        self.is_downloading = False
        self.last_downloaded_file = file_path
        self.last_downloaded_folder = os.path.dirname(file_path)

        btn_text = "⬇   DOWNLOAD TIKTOK VIDEO" if self.current_video_info and self.current_video_info.get("is_tiktok") else "⬇   START DOWNLOAD"
        self.download_btn.configure(state="normal", text=btn_text)
        self.cancel_btn.configure(state="disabled", fg_color=BG_CARD_SUBTLE)
        self.paste_btn.configure(state="normal")

        self.progress_bar.set(1.0)
        self.status_lbl.configure(text="Finished ✓", text_color=COLOR_SUCCESS)
        self.speed_lbl.configure(text="Done")
        self.eta_lbl.configure(text="00:00")

        filename = os.path.basename(file_path)
        short_name = filename if len(filename) <= 45 else filename[:45] + "..."
        self.complete_msg.configure(text=f"🎉 Successfully Saved: {short_name}")
        self.play_file_btn.configure(state="normal", text="▶ Play File")
        self.show_file_btn.configure(text="📂 Locate in Folder")
        self.complete_bar.pack(fill="x", padx=16, pady=(12, 4))

        title = self.current_video_info.get("title") if self.current_video_info else filename
        self.history_mgr.add(title=title, file_path=file_path, format_type=format_type, quality=quality, is_playlist=False)

    def _on_playlist_download_success(self, files: List[str], format_type: str, quality: str):
        self.is_downloading = False
        total_count = len(files)

        total_in_pl = len(self.playlist_item_vars)
        self.download_btn.configure(state="normal", text=f"⬇   DOWNLOAD PLAYLIST ({total_in_pl} VIDEOS)")
        self.cancel_btn.configure(state="disabled", fg_color=BG_CARD_SUBTLE)
        self.paste_btn.configure(state="normal")

        self.progress_bar.set(1.0)
        self.status_lbl.configure(text="Playlist Complete ✓", text_color=COLOR_SUCCESS)
        self.speed_lbl.configure(text=f"{total_count} Files")
        self.eta_lbl.configure(text="00:00")

        pl_title = self.current_video_info.get("title", "Playlist") if self.current_video_info else "Playlist"
        target_dir = os.path.dirname(files[0]) if files else self.download_dir
        self.last_downloaded_folder = target_dir
        self.last_downloaded_file = files[0] if files else None

        self.complete_msg.configure(text=f"🎉 Playlist Saved! {total_count} files organized in folder '{os.path.basename(target_dir)}'.")
        self.play_file_btn.configure(state="normal", text="▶ Play First")
        self.show_file_btn.configure(text="📂 Open Playlist Folder")
        self.complete_bar.pack(fill="x", padx=16, pady=(12, 4))

        self.history_mgr.add(
            title=f"[Playlist] {pl_title}",
            file_path=target_dir,
            format_type=format_type,
            quality=quality,
            is_playlist=True,
            count=total_count
        )

    def _on_download_error(self, err_msg: str):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="⬇   START DOWNLOAD")
        self.cancel_btn.configure(state="disabled", fg_color=BG_CARD_SUBTLE)
        self.paste_btn.configure(state="normal")

        if "cancelled" in err_msg.lower():
            self.status_lbl.configure(text="Cancelled", text_color=COLOR_WARNING)
        else:
            cleaned = clean_error_message(err_msg)
            self.status_lbl.configure(text=f"Error: {cleaned}", text_color=COLOR_DANGER)

    def _on_cancel_clicked(self):
        if self.active_cancel_token and self.is_downloading:
            self.status_lbl.configure(text="Cancelling...", text_color=COLOR_WARNING)
            self.active_cancel_token.cancel()

    def _play_last_downloaded(self):
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            try:
                os.startfile(self.last_downloaded_file)
            except Exception as e:
                self.status_lbl.configure(text=f"Could not open: {e}", text_color=COLOR_DANGER)
        elif self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
            try:
                os.startfile(self.last_downloaded_folder)
            except Exception:
                pass

    def _locate_last_downloaded(self):
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            locate_in_explorer(self.last_downloaded_file)
        elif self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
            try:
                os.startfile(self.last_downloaded_folder)
            except Exception:
                pass


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
        except Exception:
            pass

    app = YouTubeDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
