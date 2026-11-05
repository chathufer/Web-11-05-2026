"""
YouTube & TikTok Video Downloader PC App - v2.2 Turbo
Supports YouTube Videos, Shorts, TikTok (Without Watermark), and Full Playlists
Optimized for any screen resolution (720p, 1080p, 2K, 4K, Ultra-Wide)
"""

import os
import sys
import json
import time
import shutil
import threading
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

# ----------------- App Metadata & Paths -----------------
APP_NAME = "Media Downloader Pro"
APP_VERSION = "v2.2 Turbo"
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


# ----------------- Design System Colors -----------------
# Tuple format: (Light Mode Color, Dark Mode Color)
BG_WINDOW = ("#F4F5F8", "#0F0F12")
BG_SIDEBAR = ("#FFFFFF", "#141418")
BG_CARD = ("#FFFFFF", "#1C1C22")
BG_CARD_SUBTLE = ("#F8F9FA", "#23232B")
BG_CARD_HOVER = ("#EDF0F5", "#292934")
BORDER_COLOR = ("#E2E4E9", "#2D2D36")
BORDER_ACTIVE = ("#FF4D4D", "#E62117")

COLOR_PRIMARY = "#E50914"           # YouTube Red
COLOR_PRIMARY_HOVER = "#BF0811"
COLOR_PRIMARY_SUBTLE = ("#FEE2E2", "#381212")

COLOR_TIKTOK = "#00F2FE"            # TikTok Cyan Accent
COLOR_TIKTOK_SUBTLE = ("#E0F2FE", "#083344")

COLOR_ACCENT = "#2563EB"            # Electric Blue
COLOR_ACCENT_HOVER = "#1D4ED8"
COLOR_ACCENT_SUBTLE = ("#DBEAFE", "#172554")

COLOR_SUCCESS = "#10B981"           # Emerald Green
COLOR_SUCCESS_BG = ("#D1FAE5", "#064E3B")

COLOR_WARNING = "#F59E0B"           # Amber
COLOR_WARNING_BG = ("#FEF3C7", "#78350F")

COLOR_DANGER = "#EF4444"            # Crimson
COLOR_DANGER_HOVER = "#DC2626"

TEXT_PRIMARY = ("#111827", "#F9FAFB")
TEXT_SECONDARY = ("#4B5563", "#9CA3AF")
TEXT_MUTED = ("#9CA3AF", "#6B7280")


# ----------------- Persistent Storage -----------------
class ConfigManager:
    """Manages application settings persisted as JSON."""
    def __init__(self):
        self.file_path = os.path.join(get_data_dir(), "settings.json")
        self.data = {
            "download_dir": DEFAULT_DOWNLOAD_DIR,
            "theme": "Dark",
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
        self.active_tab = "downloader"

        # Apply Appearance & Scaling
        initial_theme = self.config.get("theme", "Dark")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")

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

        # Background silent license validation
        threading.Thread(target=self.license_mgr.verify_background, daemon=True).start()

        # Bind Resize Listener for Dynamic Wrap and Layout Adaptation
        self.bind("<Configure>", self._on_window_configure)

        # Start Clipboard Monitor (if enabled)
        if self.config.get("auto_clipboard", True):
            self.after(600, self._check_clipboard_loop)

        # Switch to Downloader Tab by Default
        self._switch_tab("downloader")

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
        """Debounced resize handler to adapt text wraplength and thumbnail scaling dynamically."""
        if event.widget == self:
            if self._resize_timer is not None:
                self.after_cancel(self._resize_timer)
            self._resize_timer = self.after(80, self._handle_window_resize, event.width, event.height)

    def _handle_window_resize(self, width: int, height: int):
        self._resize_timer = None
        content_w = max(420, width - 260)

        # 1. Update video title wrap length
        if hasattr(self, "preview_title") and self.preview_title.winfo_exists():
            thumb_w = 260 if width >= 920 else 200
            dynamic_title_wrap = max(220, content_w - thumb_w - 60)
            self.preview_title.configure(wraplength=dynamic_title_wrap)

        # 2. Update playlist title wrap length
        if hasattr(self, "playlist_title") and self.playlist_title.winfo_exists():
            thumb_w = 260 if width >= 920 else 200
            self.playlist_title.configure(wraplength=max(220, content_w - thumb_w - 60))

        # 3. Update thumbnail display size if loaded
        if self.raw_thumbnail_pil and hasattr(self, "thumb_label") and self.thumb_label.winfo_exists():
            target_w = 260 if width >= 920 else 200
            target_h = int(target_w * 9 / 16)
            self._render_thumbnail(target_w, target_h)

        # 4. Update status wrap length
        if hasattr(self, "status_lbl") and self.status_lbl.winfo_exists():
            self.status_lbl.configure(wraplength=max(200, int(content_w * 0.45)))

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
        self._build_history_view()
        self._build_settings_view()

    def _build_sidebar_content(self, parent):
        # Brand Logo & Title Header
        brand_frame = ctk.CTkFrame(parent, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(18, 14))

        logo_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_box.pack(side="left")

        logo_icon = ctk.CTkLabel(
            logo_box,
            text=" ▶ ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF",
            fg_color=COLOR_PRIMARY,
            corner_radius=8,
            width=36,
            height=36
        )
        logo_icon.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="ALL MEDIA",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box,
            text="DOWNLOADER PRO",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=TEXT_MUTED
        )
        sub_lbl.pack(anchor="w")

        # Supported Platforms Chips Pill
        platforms_pill = ctk.CTkLabel(
            parent,
            text="▶ YouTube  •  📱 TikTok  •  📑 Playlists",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_SECONDARY,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=6,
            height=26
        )
        platforms_pill.pack(fill="x", padx=14, pady=(0, 16))

        # Nav Buttons Container
        self.nav_btns_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.nav_btns_frame.pack(fill="x", padx=12, expand=True, anchor="n")

        self.nav_btn_downloader = self._create_nav_button(
            self.nav_btns_frame,
            text="  ⚡  Downloader",
            command=lambda: self._switch_tab("downloader")
        )
        self.nav_btn_downloader.pack(fill="x", pady=4)

        self.nav_btn_history = self._create_nav_button(
            self.nav_btns_frame,
            text="  🕒  Library & History",
            command=lambda: self._switch_tab("history")
        )
        self.nav_btn_history.pack(fill="x", pady=4)

        self.nav_btn_settings = self._create_nav_button(
            self.nav_btns_frame,
            text="  ⚙️  Settings & Tools",
            command=lambda: self._switch_tab("settings")
        )
        self.nav_btn_settings.pack(fill="x", pady=4)

        # Bottom System Info & Theme Toggle
        bottom_frame = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        bottom_frame.pack(fill="x", side="bottom", padx=12, pady=16)

        # Pro Subscription Card in Sidebar (packed above bottom_frame)
        self.sidebar_pro_card = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=10,
            border_width=1,
            border_color="#D97706"
        )
        self.sidebar_pro_card.pack(fill="x", side="bottom", padx=12, pady=(0, 10))

        sp_head = ctk.CTkFrame(self.sidebar_pro_card, fg_color="transparent")
        sp_head.pack(fill="x", padx=10, pady=(8, 2))

        self.sidebar_pro_badge = ctk.CTkLabel(
            sp_head,
            text="⭐ FREE EDITION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#F59E0B"
        )
        self.sidebar_pro_badge.pack(side="left")

        self.sidebar_pro_desc = ctk.CTkLabel(
            self.sidebar_pro_card,
            text="Unlock 4K, Playlists & Multi-thread Boost",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
            wraplength=170,
            justify="left"
        )
        self.sidebar_pro_desc.pack(anchor="w", padx=10, pady=(0, 8))

        self.sidebar_pro_btn = ctk.CTkButton(
            self.sidebar_pro_card,
            text="⚡ Activate Pro",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            fg_color="#D97706",
            hover_color="#B45309",
            text_color="#FFFFFF",
            corner_radius=6,
            command=self._open_activation_dialog
        )
        self.sidebar_pro_btn.pack(fill="x", padx=10, pady=(0, 10))

        ffmpeg_ok = bool(get_ffmpeg_dir())
        ff_color = COLOR_SUCCESS if ffmpeg_ok else COLOR_WARNING
        ff_text = "● FFmpeg Engine Ready" if ffmpeg_ok else "● FFmpeg Missing"
        self.ffmpeg_badge = ctk.CTkLabel(
            bottom_frame,
            text=ff_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ff_color
        )
        self.ffmpeg_badge.pack(anchor="w", padx=12, pady=(10, 4))

        self.theme_switch = ctk.CTkSwitch(
            bottom_frame,
            text="Dark Mode",
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
        self.theme_switch.pack(anchor="w", padx=12, pady=(4, 10))

    def _create_nav_button(self, parent, text: str, command):
        return ctk.CTkButton(
            parent,
            text=text,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            corner_radius=8,
            height=38,
            command=command
        )

    def _switch_tab(self, tab_name: str):
        self.active_tab = tab_name

        nav_map = {
            "downloader": self.nav_btn_downloader,
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
        self.view_history.grid_forget()
        self.view_settings.grid_forget()

        if tab_name == "downloader":
            self.view_downloader.grid(row=0, column=0, sticky="nsew")
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
        header_card.pack(fill="x", padx=content_pad, pady=(16, 10))

        header_left = ctk.CTkFrame(header_card, fg_color="transparent")
        header_left.pack(side="left", fill="both", expand=True)

        head_title = ctk.CTkLabel(
            header_left,
            text="High-Speed Media Downloader",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        head_title.pack(anchor="w")

        head_sub = ctk.CTkLabel(
            header_left,
            text=APP_SUBTITLE,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        head_sub.pack(anchor="w")

        # Pro Status / Upgrade CTA in Header
        header_right = ctk.CTkFrame(header_card, fg_color="transparent")
        header_right.pack(side="right", padx=(10, 0))

        self.header_pro_btn = ctk.CTkButton(
            header_right,
            text="⭐ Activate Pro Key",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#D97706",
            hover_color="#B45309",
            text_color="#FFFFFF",
            corner_radius=8,
            height=34,
            command=self._open_activation_dialog
        )
        self.header_pro_btn.pack(side="right")

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

        # 3. Streamlined URL Input Section
        self._build_input_section(self.view_downloader, padx=content_pad)

        # 4. Dynamic Media Preview Section (Single Video or Full Playlist Hub)
        self._build_preview_section(self.view_downloader, padx=content_pad)

        # 5. Format & Quality Configuration Card
        self._build_options_section(self.view_downloader, padx=content_pad)

        # 6. Action, Telemetry HUD & Progress Section
        self._build_progress_section(self.view_downloader, padx=content_pad)

    def _build_input_section(self, parent, padx: int):
        input_card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        input_card.pack(fill="x", padx=padx, pady=(0, 14), ipady=4)

        lbl_row = ctk.CTkFrame(input_card, fg_color="transparent")
        lbl_row.pack(fill="x", padx=16, pady=(12, 6))

        lbl = ctk.CTkLabel(
            lbl_row,
            text="Media URL (YouTube, TikTok No-Watermark, or Full Playlist):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl.pack(side="left")

        self.auto_badge = ctk.CTkLabel(
            lbl_row,
            text="⚡ Auto-Fetch Active",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLOR_SUCCESS,
            fg_color=COLOR_SUCCESS_BG,
            corner_radius=6,
            height=20,
            padx=8
        )
        self.auto_badge.pack(side="right")

        # Input Row
        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 8))

        self.url_var = ctk.StringVar()
        self.url_var.trace_add("write", self._on_url_entry_changed)

        self.url_entry = ctk.CTkEntry(
            row,
            textvariable=self.url_var,
            placeholder_text="Paste YouTube, TikTok (No Watermark), or Playlist link here...",
            font=ctk.CTkFont(size=13),
            height=42,
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
            width=120,
            height=42,
            corner_radius=8,
            command=self._on_paste_button_clicked
        )
        self.paste_btn.pack(side="left", padx=(0, 6))

        self.clear_btn = ctk.CTkButton(
            row,
            text="✕",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=42,
            height=42,
            corner_radius=8,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            command=self._on_clear_clicked
        )
        self.clear_btn.pack(side="left")

        # Feedback/status message below entry
        self.input_msg_lbl = ctk.CTkLabel(
            input_card,
            text="✨ Tip: Simply paste or press Ctrl+V — videos, TikToks without watermark, and playlists load automatically!",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.input_msg_lbl.pack(anchor="w", padx=16, pady=(0, 8))

    def _build_preview_section(self, parent, padx: int):
        self.preview_card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.preview_card.pack(fill="x", padx=padx, pady=(0, 14), ipady=4)

        # 1. Idle Placeholder State
        self.preview_placeholder = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        self.preview_placeholder.pack(fill="x", pady=25)

        ph_icon = ctk.CTkLabel(
            self.preview_placeholder,
            text="🎬",
            font=ctk.CTkFont(size=32)
        )
        ph_icon.pack(pady=(0, 6))

        ph_title = ctk.CTkLabel(
            self.preview_placeholder,
            text="Ready to Download",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        ph_title.pack()

        ph_desc = ctk.CTkLabel(
            self.preview_placeholder,
            text="Paste any YouTube video, TikTok (No Watermark), or full Playlist link above",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        ph_desc.pack(pady=(2, 12))

        # Supported Feature Badges Pill Row
        pills_row = ctk.CTkFrame(self.preview_placeholder, fg_color="transparent")
        pills_row.pack()

        for tag in ["📱 TikTok (No Watermark)", "📑 Full Playlists", "🌟 4K UHD", "⚡ 60 FPS", "🎵 MP3 320k"]:
            tag_lbl = ctk.CTkLabel(
                pills_row,
                text=tag,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_SECONDARY,
                fg_color=BG_CARD_SUBTLE,
                corner_radius=6,
                padx=8,
                pady=2
            )
            tag_lbl.pack(side="left", padx=4)

        # 2. Loaded Single Video Preview Content
        self.preview_content = ctk.CTkFrame(self.preview_card, fg_color="transparent")

        # Left: Thumbnail Box
        self.thumb_box = ctk.CTkFrame(
            self.preview_content,
            fg_color=BG_CARD_SUBTLE,
            corner_radius=8,
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
            text="👤 Creator Name",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.preview_channel.pack(side="left", padx=(0, 10))

        self.max_res_badge = ctk.CTkLabel(
            channel_row,
            text="4K UHD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=COLOR_PRIMARY,
            corner_radius=4,
            padx=6,
            pady=1
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
            height=28,
            corner_radius=6,
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
            height=28,
            corner_radius=6,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD_HOVER,
            command=self._copy_video_link
        )
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
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.options_card.pack(fill="x", padx=padx, pady=(0, 14), ipady=6)

        card_title = ctk.CTkLabel(
            self.options_card,
            text="Download Settings & Output Quality",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        card_title.pack(anchor="w", padx=16, pady=(10, 8))

        # Format & Quality Matrix Row
        grid_frame = ctk.CTkFrame(self.options_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=16, pady=(0, 10))

        # Col 1: Format Selector
        col1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))

        f_lbl = ctk.CTkLabel(
            col1,
            text="Format:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        f_lbl.pack(anchor="w", pady=(0, 4))

        self.format_seg = ctk.CTkSegmentedButton(
            col1,
            values=["🎥 Video (MP4)", "🎵 Music (MP3)", "🎧 Audio (M4A)"],
            command=self._on_format_changed,
            height=36,
            selected_color=COLOR_PRIMARY,
            selected_hover_color=COLOR_PRIMARY_HOVER,
            unselected_color=BG_CARD_SUBTLE,
            unselected_hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY
        )
        self.format_seg.set("🎥 Video (MP4)")
        self.format_seg.pack(fill="x")

        # Col 2: Quality Dropdown
        col2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(10, 0))

        q_lbl = ctk.CTkLabel(
            col2,
            text="Quality / Resolution:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        q_lbl.pack(anchor="w", pady=(0, 4))

        self.quality_menu = ctk.CTkOptionMenu(
            col2,
            values=["🌟 Best Available Quality", "1080p (Full HD)", "720p (HD)", "480p (SD)", "360p"],
            height=36,
            fg_color=BG_CARD_SUBTLE,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_CARD_HOVER
        )
        self.quality_menu.set("🌟 Best Available Quality")
        self.quality_menu.pack(fill="x")

        # Quick Preset Buttons Row
        self.presets_row = ctk.CTkFrame(self.options_card, fg_color="transparent")
        self.presets_row.pack(fill="x", padx=16, pady=(0, 10))

        presets_lbl = ctk.CTkLabel(
            self.presets_row,
            text="Quick Presets:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        presets_lbl.pack(side="left", padx=(0, 8))

        p1 = ctk.CTkButton(
            self.presets_row,
            text="🌟 Max Quality",
            font=ctk.CTkFont(size=11),
            height=26,
            width=90,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            command=lambda: self._apply_quick_preset("video", "best")
        )
        p1.pack(side="left", padx=3)

        p2 = ctk.CTkButton(
            self.presets_row,
            text="1080p FHD",
            font=ctk.CTkFont(size=11),
            height=26,
            width=80,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            command=lambda: self._apply_quick_preset("video", "1080p")
        )
        p2.pack(side="left", padx=3)

        p3 = ctk.CTkButton(
            self.presets_row,
            text="720p HD",
            font=ctk.CTkFont(size=11),
            height=26,
            width=70,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            command=lambda: self._apply_quick_preset("video", "720p")
        )
        p3.pack(side="left", padx=3)

        p4 = ctk.CTkButton(
            self.presets_row,
            text="🎵 MP3 320k",
            font=ctk.CTkFont(size=11),
            height=26,
            width=80,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            command=lambda: self._apply_quick_preset("audio_mp3", "320")
        )
        p4.pack(side="left", padx=3)

        # Destination Folder Selector Row
        folder_row = ctk.CTkFrame(self.options_card, fg_color="transparent")
        folder_row.pack(fill="x", padx=16, pady=(4, 10))

        folder_lbl = ctk.CTkLabel(
            folder_row,
            text="Save To:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        folder_lbl.pack(side="left", padx=(0, 10))

        self.folder_display = ctk.CTkEntry(
            folder_row,
            font=ctk.CTkFont(size=12),
            height=34,
            fg_color=BG_CARD_SUBTLE,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.folder_display.insert(0, self.download_dir)
        self.folder_display.configure(state="readonly")
        self.folder_display.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            folder_row,
            text="📁 Browse...",
            font=ctk.CTkFont(size=12),
            width=90,
            height=34,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            command=self._on_browse_folder
        )
        browse_btn.pack(side="left", padx=(0, 6))

        open_folder_btn = ctk.CTkButton(
            folder_row,
            text="📂 Open Folder",
            font=ctk.CTkFont(size=12),
            width=100,
            height=34,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            command=lambda: os.startfile(self.download_dir)
        )
        open_folder_btn.pack(side="left")

    def _build_progress_section(self, parent, padx: int):
        self.progress_card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.progress_card.pack(fill="x", padx=padx, pady=(0, 16), ipady=8)

        # Primary Action CTA Button Row
        action_row = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        action_row.pack(fill="x", padx=16, pady=(10, 12))

        self.download_btn = ctk.CTkButton(
            action_row,
            text="⬇   START DOWNLOAD",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            corner_radius=10,
            height=48,
            command=self._on_download_clicked
        )
        self.download_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(
            action_row,
            text="✖ Cancel",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            hover_color=COLOR_DANGER_HOVER,
            corner_radius=10,
            state="disabled",
            width=105,
            height=48,
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
            height=12,
            corner_radius=6
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 10))

        # 4-Card Real-Time Telemetry HUD
        hud_frame = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        hud_frame.pack(fill="x", padx=16, pady=(0, 4))
        hud_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # HUD 1: Status
        card_status = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=8, height=44)
        card_status.grid(row=0, column=0, sticky="nsew", padx=3)
        card_status.grid_propagate(False)
        self.status_title = ctk.CTkLabel(card_status, text="STATUS", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.status_title.pack(anchor="w", padx=10, pady=(4, 0))
        self.status_lbl = ctk.CTkLabel(card_status, text="Ready", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        self.status_lbl.pack(anchor="w", padx=10)

        # HUD 2: Speed / Item
        card_speed = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=8, height=44)
        card_speed.grid(row=0, column=1, sticky="nsew", padx=3)
        card_speed.grid_propagate(False)
        self.lbl_sp_t = ctk.CTkLabel(card_speed, text="DOWNLOAD SPEED", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_sp_t.pack(anchor="w", padx=10, pady=(4, 0))
        self.speed_lbl = ctk.CTkLabel(card_speed, text="-- MB/s", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        self.speed_lbl.pack(anchor="w", padx=10)

        # HUD 3: Size
        card_size = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=8, height=44)
        card_size.grid(row=0, column=2, sticky="nsew", padx=3)
        card_size.grid_propagate(False)
        self.lbl_sz_t = ctk.CTkLabel(card_size, text="TRANSFERRED", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_sz_t.pack(anchor="w", padx=10, pady=(4, 0))
        self.size_lbl = ctk.CTkLabel(card_size, text="-- / --", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        self.size_lbl.pack(anchor="w", padx=10)

        # HUD 4: ETA
        card_eta = ctk.CTkFrame(hud_frame, fg_color=BG_CARD_SUBTLE, corner_radius=8, height=44)
        card_eta.grid(row=0, column=3, sticky="nsew", padx=3)
        card_eta.grid_propagate(False)
        self.lbl_et_t = ctk.CTkLabel(card_eta, text="ESTIMATED TIME", font=ctk.CTkFont(size=9, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_et_t.pack(anchor="w", padx=10, pady=(4, 0))
        self.eta_lbl = ctk.CTkLabel(card_eta, text="--:--", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        self.eta_lbl.pack(anchor="w", padx=10)

        # Download Success Banner (Hidden until finished)
        self.complete_bar = ctk.CTkFrame(
            self.progress_card,
            fg_color=COLOR_SUCCESS_BG,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_SUCCESS
        )

        self.complete_msg = ctk.CTkLabel(
            self.complete_bar,
            text="🎉 Download Complete! Saved to your downloads folder.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        self.complete_msg.pack(side="left", padx=14, pady=10)

        self.play_file_btn = ctk.CTkButton(
            self.complete_bar,
            text="▶ Play File",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=90,
            height=30,
            fg_color=COLOR_SUCCESS,
            hover_color="#0D9467",
            command=self._play_last_downloaded
        )
        self.play_file_btn.pack(side="right", padx=(4, 12), pady=8)

        self.show_file_btn = ctk.CTkButton(
            self.complete_bar,
            text="📂 Locate in Folder",
            font=ctk.CTkFont(size=12),
            width=120,
            height=30,
            fg_color=BG_CARD_SUBTLE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_CARD_HOVER,
            command=self._locate_last_downloaded
        )
        self.show_file_btn.pack(side="right", padx=4, pady=8)

    # ---------------- 2. History & Library View ----------------

    def _build_history_view(self):
        self.view_history = ctk.CTkFrame(self.content_container, corner_radius=0, fg_color="transparent")

        header = ctk.CTkFrame(self.view_history, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 12))

        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x")

        title_box = ctk.CTkFrame(top_row, fg_color="transparent")
        title_box.pack(side="left")

        h_title = ctk.CTkLabel(
            title_box,
            text="Downloads Library",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        h_title.pack(anchor="w")

        self.history_count_lbl = ctk.CTkLabel(
            title_box,
            text="All downloaded files in this session and history",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.history_count_lbl.pack(anchor="w")

        actions_box = ctk.CTkFrame(top_row, fg_color="transparent")
        actions_box.pack(side="right")

        open_folder_btn = ctk.CTkButton(
            actions_box,
            text="📂 Open Folder",
            font=ctk.CTkFont(size=12),
            width=110,
            height=34,
            corner_radius=8,
            fg_color=BG_CARD,
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
            font=ctk.CTkFont(size=12),
            width=110,
            height=34,
            corner_radius=8,
            fg_color=BG_CARD,
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
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        search_card.pack(fill="x", padx=18, pady=(0, 12))

        self.history_search_var = ctk.StringVar()
        self.history_search_var.trace_add("write", lambda *a: self._refresh_history_ui())

        search_entry = ctk.CTkEntry(
            search_card,
            textvariable=self.history_search_var,
            placeholder_text="🔍 Filter history by title or format...",
            font=ctk.CTkFont(size=12),
            height=36,
            border_width=0,
            fg_color="transparent"
        )
        search_entry.pack(fill="x", padx=12, pady=4)

        self.history_scroll = ctk.CTkScrollableFrame(
            self.view_history,
            fg_color="transparent",
            corner_radius=0
        )
        self.history_scroll.pack(fill="both", expand=True, padx=18, pady=(0, 16))

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

        self.history_count_lbl.configure(text=f"{len(all_items)} total downloaded items recorded")

        if not filtered:
            empty_box = ctk.CTkFrame(self.history_scroll, fg_color="transparent")
            empty_box.pack(pady=50)

            empty_lbl = ctk.CTkLabel(
                empty_box,
                text="📂 No downloads found." if query else "🎉 No downloads yet! Completed downloads will appear here.",
                font=ctk.CTkFont(size=13),
                text_color=TEXT_MUTED
            )
            empty_lbl.pack()
            return

        for orig_idx, item in filtered:
            self._create_history_card(self.history_scroll, orig_idx, item)

    def _create_history_card(self, parent, orig_idx: int, item: Dict[str, Any]):
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.pack(fill="x", pady=4)

        is_pl = item.get("is_playlist", False)
        is_video = "video" in item.get("format_type", "video")

        if is_pl:
            icon_symbol = "📑"
        elif is_video:
            icon_symbol = "🎥"
        else:
            icon_symbol = "🎵"

        icon_box = ctk.CTkLabel(
            card,
            text=icon_symbol,
            font=ctk.CTkFont(size=18),
            width=36
        )
        icon_box.pack(side="left", padx=(12, 6), pady=10)

        info_box = ctk.CTkFrame(card, fg_color="transparent")
        info_box.pack(side="left", fill="x", expand=True, pady=8)

        title = item.get("title", "Untitled")
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
            meta_text = f"{item.get('timestamp', '')} • Playlist ({count} items)"
        else:
            size_str = ""
            if exists:
                try:
                    mb = os.path.getsize(file_path) / (1024 * 1024)
                    size_str = f" • {mb:.1f} MB"
                except Exception:
                    pass
            else:
                size_str = " • (File moved or deleted)"
            meta_text = f"{item.get('timestamp', '')}{size_str}"

        meta_lbl = ctk.CTkLabel(
            info_box,
            text=meta_text,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED if exists else COLOR_WARNING,
            anchor="w"
        )
        meta_lbl.pack(anchor="w")

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(side="right", padx=10, pady=8)

        if exists:
            if not is_pl:
                play_btn = ctk.CTkButton(
                    btn_box,
                    text="▶ Play",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    width=65,
                    height=30,
                    corner_radius=6,
                    fg_color=COLOR_SUCCESS,
                    hover_color="#0D9467",
                    command=lambda p=file_path: os.startfile(p)
                )
                play_btn.pack(side="left", padx=3)

            locate_btn = ctk.CTkButton(
                btn_box,
                text="📂 Folder" if is_pl else "📂 Show",
                font=ctk.CTkFont(size=11),
                width=65,
                height=30,
                corner_radius=6,
                fg_color=BG_CARD_SUBTLE,
                text_color=TEXT_PRIMARY,
                hover_color=BG_CARD_HOVER,
                command=lambda p=file_path: os.startfile(p) if is_pl else subprocess.run(f'explorer /select,"{os.path.abspath(p)}"')
            )
            locate_btn.pack(side="left", padx=3)

        del_btn = ctk.CTkButton(
            btn_box,
            text="✕",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=30,
            height=30,
            corner_radius=6,
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
        head.pack(fill="x", padx=18, pady=(16, 14))

        ctk.CTkLabel(
            head,
            text="Settings & Preferences",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            head,
            text="Customize application behavior, display scaling, and manage engine tools",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w")

        # Card 0: Subscription & Pro License Management
        self.license_card = ctk.CTkFrame(self.view_settings, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        self.license_card.pack(fill="x", padx=18, pady=(0, 14), ipady=8)

        lic_header_row = ctk.CTkFrame(self.license_card, fg_color="transparent")
        lic_header_row.pack(fill="x", padx=16, pady=(10, 4))

        ctk.CTkLabel(
            lic_header_row,
            text="Subscription & License",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        self.lic_badge_pill = ctk.CTkLabel(
            lic_header_row,
            text="FREE EDITION",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=BG_CARD_SUBTLE,
            text_color=COLOR_WARNING,
            corner_radius=6,
            height=22,
            padx=10
        )
        self.lic_badge_pill.pack(side="right")

        self.lic_desc_lbl = ctk.CTkLabel(
            self.license_card,
            text="Unlock 4K Ultra HD, unlimited playlist downloads, and high-speed multi-threaded acceleration.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.lic_desc_lbl.pack(anchor="w", padx=16, pady=(0, 10))

        # License Details Box
        self.lic_details_frame = ctk.CTkFrame(self.license_card, fg_color=BG_CARD_SUBTLE, corner_radius=8)
        self.lic_details_frame.pack(fill="x", padx=16, pady=(0, 12))

        # Plan Row
        row1 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(row1, text="Active Plan:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        self.lic_plan_lbl = ctk.CTkLabel(row1, text="Free Edition", font=ctk.CTkFont(size=11), text_color=TEXT_PRIMARY)
        self.lic_plan_lbl.pack(side="right")

        # Expiry Row
        row2 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(row2, text="Expiration:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        self.lic_exp_lbl = ctk.CTkLabel(row2, text="N/A", font=ctk.CTkFont(size=11), text_color=TEXT_PRIMARY)
        self.lic_exp_lbl.pack(side="right")

        # Key Row
        row3 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row3.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(row3, text="License Key:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        self.lic_key_lbl = ctk.CTkLabel(row3, text="None", font=ctk.CTkFont(size=11, family="Consolas"), text_color=TEXT_PRIMARY)
        self.lic_key_lbl.pack(side="right")

        # HWID Row
        row4 = ctk.CTkFrame(self.lic_details_frame, fg_color="transparent")
        row4.pack(fill="x", padx=12, pady=(4, 8))
        ctk.CTkLabel(row4, text="Machine Hardware ID (HWID):", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")
        hwid_right = ctk.CTkFrame(row4, fg_color="transparent")
        hwid_right.pack(side="right")
        self.lic_hwid_lbl = ctk.CTkLabel(hwid_right, text=self.license_mgr.hwid, font=ctk.CTkFont(size=10, family="Consolas"), text_color=TEXT_MUTED)
        self.lic_hwid_lbl.pack(side="left", padx=(0, 6))
        copy_hwid_btn = ctk.CTkButton(
            hwid_right,
            text="📋 Copy",
            font=ctk.CTkFont(size=10, weight="bold"),
            width=55,
            height=22,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            command=lambda: self._copy_text(self.license_mgr.hwid, "HWID copied to clipboard!")
        )
        copy_hwid_btn.pack(side="left")

        # Button Row
        self.lic_actions_frame = ctk.CTkFrame(self.license_card, fg_color="transparent")
        self.lic_actions_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.lic_activate_btn = ctk.CTkButton(
            self.lic_actions_frame,
            text="⚡ Activate Pro License Key",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#D97706",
            hover_color="#B45309",
            height=34,
            command=self._open_activation_dialog
        )
        self.lic_activate_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.lic_deactivate_btn = ctk.CTkButton(
            self.lic_actions_frame,
            text="🔌 Deactivate / Transfer PC",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=34,
            command=self._deactivate_license_confirmed
        )

        # Card 1: Display & Resolution Scaling
        display_card = ctk.CTkFrame(self.view_settings, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        display_card.pack(fill="x", padx=18, pady=(0, 14), ipady=8)

        ctk.CTkLabel(
            display_card,
            text="Display & Resolution Optimization",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(10, 4))

        ctk.CTkLabel(
            display_card,
            text="Adjust UI zoom scaling for 4K UHD, high-DPI monitors, or compact laptop displays.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(0, 10))

        scale_row = ctk.CTkFrame(display_card, fg_color="transparent")
        scale_row.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(scale_row, text="Interface Scaling:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")

        self.scale_menu = ctk.CTkOptionMenu(
            scale_row,
            values=["85% (Compact)", "100% (Standard)", "115% (Comfortable)", "125% (Large)"],
            font=ctk.CTkFont(size=12),
            height=32,
            width=160,
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
        auto_card = ctk.CTkFrame(self.view_settings, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        auto_card.pack(fill="x", padx=18, pady=(0, 14), ipady=8)

        ctk.CTkLabel(
            auto_card,
            text="Download Automation",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(10, 4))

        clip_row = ctk.CTkFrame(auto_card, fg_color="transparent")
        clip_row.pack(fill="x", padx=16, pady=(6, 10))

        clip_info = ctk.CTkFrame(clip_row, fg_color="transparent")
        clip_info.pack(side="left")

        ctk.CTkLabel(clip_info, text="Clipboard Auto-Detection", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(clip_info, text="Detect YouTube & TikTok links copied from web browsers in real time.", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w")

        self.clip_switch = ctk.CTkSwitch(
            clip_row,
            text="",
            command=self._on_toggle_auto_clipboard
        )
        if self.config.get("auto_clipboard", True):
            self.clip_switch.select()
        else:
            self.clip_switch.deselect()
        self.clip_switch.pack(side="right")

        # Card 3: Engine Diagnostics & Capabilities
        diag_card = ctk.CTkFrame(self.view_settings, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        diag_card.pack(fill="x", padx=18, pady=(0, 14), ipady=8)

        ctk.CTkLabel(
            diag_card,
            text="Engine & Platform Capabilities",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(10, 4))

        ffmpeg_dir = get_ffmpeg_dir() or "Not Found"
        info_lines = [
            f"• YouTube Engine: Ultra HD 4K, 1080p 60fps, Shorts & Playlists",
            f"• TikTok Engine: Watermark-Free Direct Stream Extractor Enabled",
            f"• FFmpeg Location: {ffmpeg_dir}",
            f"• Python Runtime: {sys.version.split()[0]} ({sys.platform})",
        ]
        for line in info_lines:
            ctk.CTkLabel(
                diag_card,
                text=line,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_SECONDARY
            ).pack(anchor="w", padx=16, pady=2)

        # Card 4: About
        about_card = ctk.CTkFrame(self.view_settings, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)
        about_card.pack(fill="x", padx=18, pady=(0, 20), ipady=8)

        ctk.CTkLabel(
            about_card,
            text=f"{APP_NAME} {APP_VERSION}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=16, pady=(10, 2))

        ctk.CTkLabel(
            about_card,
            text="Engineered for ad-free downloads across YouTube, TikTok (No Watermark), and Full Playlists.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(0, 8))

    def _on_scale_selected(self, choice: str):
        self.config.set("ui_scale", choice)
        self._apply_ui_scaling(choice)

    def _on_toggle_auto_clipboard(self):
        val = bool(self.clip_switch.get())
        self.config.set("auto_clipboard", val)
        if val:
            self._check_clipboard_loop()

    # ---------------- Clipboard & Auto-Fetch Engine ----------------

    def _check_clipboard_loop(self):
        if not self.config.get("auto_clipboard", True):
            return

        try:
            clip = pyperclip.paste()
            if clip:
                clip = clip.strip()
                if clip != self.last_clipboard_content:
                    self.last_clipboard_content = clip
                    if is_valid_media_url(clip):
                        current_entry = self.url_var.get().strip()
                        if clip != current_entry:
                            self._show_clipboard_banner(clip)
        except Exception:
            pass

        self.after(1500, self._check_clipboard_loop)

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
                self.after(0, self._on_info_fetched_success, info)
            except Exception as e:
                err_msg = str(e)
                self.after(0, self._on_info_fetched_error, err_msg)

        threading.Thread(target=task, daemon=True).start()

    def _on_info_fetched_success(self, info: Dict[str, Any]):
        self.is_fetching = False
        self.current_video_info = info
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
            if thumb_url:
                self._load_thumbnail_threaded(thumb_url)

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
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    img_data = Image.open(BytesIO(resp.content))
                    img_data.thumbnail((180, 100), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=img_data.size)
                    self.after(0, lambda: self.pl_thumb_label.configure(image=ctk_img, text=""))
            except Exception:
                pass

        threading.Thread(target=task, daemon=True).start()

    def _on_info_fetched_error(self, err_msg: str):
        self.is_fetching = False
        self.auto_badge.configure(text="⚠ Fetch Failed", text_color=COLOR_DANGER, fg_color=COLOR_PRIMARY_SUBTLE)

        first_line = err_msg.split("\n")[0] if "\n" in err_msg else err_msg
        if len(first_line) > 80:
            first_line = first_line[:80] + "..."
        self.input_msg_lbl.configure(text=f"⚠ Error: {first_line}", text_color=COLOR_DANGER)

    def _load_thumbnail_threaded(self, url: str):
        def task():
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    img_data = Image.open(BytesIO(resp.content))
                    self.raw_thumbnail_pil = img_data
                    self.after(0, self._render_thumbnail_auto)
            except Exception:
                pass

        threading.Thread(target=task, daemon=True).start()

    def _render_thumbnail_auto(self):
        target_w = 260 if self.winfo_width() >= 920 else 200
        target_h = int(target_w * 9 / 16)
        self._render_thumbnail(target_w, target_h)

    def _render_thumbnail(self, width: int, height: int):
        if not self.raw_thumbnail_pil:
            return
        try:
            copy_img = self.raw_thumbnail_pil.copy()
            copy_img.thumbnail((width, height), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=copy_img, dark_image=copy_img, size=copy_img.size)
            self.cached_thumbnail_ctk = ctk_img
            self.thumb_box.configure(width=width, height=height)
            self.thumb_label.configure(image=ctk_img, text="")
        except Exception:
            pass

    # ---------------- Format & Options Handlers ----------------

    def _on_format_changed(self, value: str):
        if "Video" in value:
            options = ["🌟 Best Available Quality", "1080p (Full HD)", "720p (HD)", "480p (SD)", "360p"]
            if self.current_video_info and self.current_video_info.get("available_heights"):
                heights = self.current_video_info["available_heights"]
                custom_opts = ["🌟 Best Available Quality"]
                if 2160 in heights:
                    custom_opts.append("2160p (4K UHD)")
                if 1440 in heights:
                    custom_opts.append("1440p (2K QHD)")
                if 1080 in heights:
                    custom_opts.append("1080p (Full HD)")
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
        """Update all badges, labels, and buttons reflecting current Pro status."""
        status = self.license_mgr.get_status()
        is_pro = status.get("is_pro", False)

        # 1. Update Header Button
        if hasattr(self, "header_pro_btn") and self.header_pro_btn.winfo_exists():
            if is_pro:
                self.header_pro_btn.configure(
                    text="👑 PRO ACTIVATED",
                    fg_color="#10B981",
                    hover_color="#059669"
                )
            else:
                self.header_pro_btn.configure(
                    text="⭐ Activate Pro Key",
                    fg_color="#D97706",
                    hover_color="#B45309"
                )

        # 2. Update Sidebar Card
        if hasattr(self, "sidebar_pro_card") and self.sidebar_pro_card.winfo_exists():
            if is_pro:
                self.sidebar_pro_card.configure(border_color="#10B981")
                self.sidebar_pro_badge.configure(text="👑 PRO MEMBER", text_color="#10B981")
                plan_t = status.get("plan_title", "Pro Plan")
                exp_t = status.get("expires_at", "Lifetime")
                self.sidebar_pro_desc.configure(text=f"{plan_t}\nExpires: {exp_t}")
                self.sidebar_pro_btn.configure(
                    text="Manage License",
                    fg_color="#10B981",
                    hover_color="#059669"
                )
            else:
                self.sidebar_pro_card.configure(border_color="#D97706")
                self.sidebar_pro_badge.configure(text="⭐ FREE EDITION", text_color="#F59E0B")
                self.sidebar_pro_desc.configure(text="Unlock 4K, Playlists & Multi-thread Boost")
                self.sidebar_pro_btn.configure(
                    text="⚡ Activate Pro",
                    fg_color="#D97706",
                    hover_color="#B45309"
                )

        # 3. Update Settings Card
        if hasattr(self, "lic_badge_pill") and self.lic_badge_pill.winfo_exists():
            if is_pro:
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
            else:
                self.lic_badge_pill.configure(
                    text="FREE EDITION",
                    fg_color=BG_CARD_SUBTLE,
                    text_color=COLOR_WARNING
                )
                self.lic_plan_lbl.configure(text="Free Edition")
                self.lic_exp_lbl.configure(text="N/A")
                self.lic_key_lbl.configure(text="None")
                self.lic_desc_lbl.configure(text="Unlock 4K Ultra HD, unlimited playlist downloads, and high-speed multi-threaded acceleration.")
                self.lic_activate_btn.configure(text="⚡ Activate Pro License Key", fg_color="#D97706", hover_color="#B45309", text_color="#FFFFFF")
                self.lic_deactivate_btn.pack_forget()

    def _open_activation_dialog(self):
        """Open modern modal dialog for activating license key."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Activate Media Downloader Pro")
        dialog.geometry("540x630")
        dialog.minsize(500, 580)
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 540) // 2
        y = self.winfo_y() + (self.winfo_height() - 630) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        frame = ctk.CTkFrame(dialog, fg_color=BG_CARD, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Box
        head_box = ctk.CTkFrame(frame, fg_color="transparent")
        head_box.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            head_box,
            text="👑 Media Downloader Pro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F59E0B"
        ).pack(anchor="w")

        ctk.CTkLabel(
            head_box,
            text="Enter your subscription license key to unlock unlimited downloads.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w")

        # Pro Perks Box
        perks_card = ctk.CTkFrame(frame, fg_color=BG_CARD_SUBTLE, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        perks_card.pack(fill="x", pady=(0, 14), ipady=4)

        ctk.CTkLabel(
            perks_card,
            text="PRO SUBSCRIPTION PERKS:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=12, pady=(8, 4))

        perks = [
            "🚀 Unlimited Full Playlist Batch Downloads",
            "🌟 Ultra HD 4K & 2K 60fps Video Resolutions",
            "⚡ High-Speed Multi-Threaded Download Acceleration",
            "🎵 Studio Quality 320kbps MP3 / Hi-Fi M4A Audio",
            "📱 TikTok Clean Stream Extractor (100% No Watermark)"
        ]
        for p in perks:
            ctk.CTkLabel(
                perks_card,
                text=p,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_SECONDARY
            ).pack(anchor="w", padx=12, pady=1)

        # License Key Input Box (PRIMARY SECTION)
        key_box = ctk.CTkFrame(frame, fg_color="transparent")
        key_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            key_box,
            text="🔑 Enter License Key:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 4))

        input_row = ctk.CTkFrame(key_box, fg_color="transparent")
        input_row.pack(fill="x")

        key_var = ctk.StringVar()
        current_status = self.license_mgr.get_status()
        if current_status.get("is_pro") and current_status.get("license_key") != "None":
            key_var.set(current_status.get("license_key", ""))

        key_entry = ctk.CTkEntry(
            input_row,
            textvariable=key_var,
            placeholder_text="MDP-LFT-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(size=14, family="Consolas", weight="bold"),
            height=44,
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
            text="📋 Paste",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=75,
            height=44,
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            command=paste_key_action
        )
        paste_btn.pack(side="left")

        # Feedback / Status Message Label
        status_msg = ctk.CTkLabel(
            frame,
            text="Paste the activation key provided by the seller, then click Activate.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        status_msg.pack(anchor="w", pady=(0, 10))

        # Hardware ID Box (Informational Footer)
        hwid_box = ctk.CTkFrame(frame, fg_color=BG_CARD_SUBTLE, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        hwid_box.pack(fill="x", pady=(0, 14), padx=2, ipady=3)

        hwid_lbl_row = ctk.CTkFrame(hwid_box, fg_color="transparent")
        hwid_lbl_row.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(
            hwid_lbl_row,
            text="💻 Your Machine HWID (Only send to seller if requested for support):",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_MUTED
        ).pack(side="left")

        hwid_val_row = ctk.CTkFrame(hwid_box, fg_color="transparent")
        hwid_val_row.pack(fill="x", padx=10, pady=(0, 6))

        hwid_entry = ctk.CTkEntry(
            hwid_val_row,
            height=28,
            font=ctk.CTkFont(size=10, family="Consolas"),
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER_COLOR
        )
        hwid_entry.insert(0, self.license_mgr.hwid)
        hwid_entry.configure(state="readonly")
        hwid_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def copy_hwid_action():
            pyperclip.copy(self.license_mgr.hwid)
            status_msg.configure(text="✔ Machine HWID copied to clipboard!", text_color=COLOR_SUCCESS)

        copy_hwid_btn = ctk.CTkButton(
            hwid_val_row,
            text="📋 Copy",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=65,
            height=28,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            command=copy_hwid_action
        )
        copy_hwid_btn.pack(side="left")

        # Action Buttons
        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        def perform_activation():
            raw_k = key_var.get().strip()
            if not raw_k:
                # If blank, auto-fill with machine HWID
                raw_k = self.license_mgr.hwid

            status_msg.configure(text="Verifying credentials...", text_color=COLOR_ACCENT)
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
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#D97706",
            hover_color="#B45309",
            height=42,
            command=perform_activation
        )
        activate_cta.pack(side="left", fill="x", expand=True, padx=(0, 8))

        close_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            width=80,
            height=42,
            command=dialog.destroy
        )
        close_btn.pack(side="left")

    def _deactivate_license_confirmed(self):
        """Ask confirmation and deactivate license to release device slot for transfer."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Transfer / Deactivate License")
        dialog.geometry("450x270")
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 270) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(dialog, fg_color=BG_CARD, corner_radius=0)
        f.pack(fill="both", expand=True, padx=20, pady=20)

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
            wraplength=400
        ).pack(anchor="w", pady=(0, 16))

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
            height=36,
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
            height=36,
            command=dialog.destroy
        )
        btn_cancel.pack(side="left")

    def _show_pro_upsell_dialog(self, feature_title: str, feature_desc: str):
        """Show clean modal dialog explaining a Pro feature and offering activation."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Pro Feature")
        dialog.geometry("460x310")
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 460) // 2
        y = self.winfo_y() + (self.winfo_height() - 310) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(dialog, fg_color=BG_CARD, corner_radius=0)
        f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            f,
            text=f"👑 {feature_title}",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#F59E0B"
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            f,
            text=feature_desc,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=410
        ).pack(anchor="w", pady=(0, 20))

        b_row = ctk.CTkFrame(f, fg_color="transparent")
        b_row.pack(fill="x", side="bottom")

        def go_activate():
            dialog.destroy()
            self._open_activation_dialog()

        btn_act = ctk.CTkButton(
            b_row,
            text="⚡ Activate Pro License",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#D97706",
            hover_color="#B45309",
            height=38,
            command=go_activate
        )
        btn_act.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_dismiss = ctk.CTkButton(
            b_row,
            text="Maybe Later",
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD_SUBTLE,
            hover_color=BG_CARD_HOVER,
            width=90,
            height=38,
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

        # Check Pro restrictions on 4K / 2K resolutions
        if not self.license_mgr.is_pro() and quality in ["2160p", "1440p"]:
            self._show_pro_upsell_dialog(
                feature_title="Ultra HD 4K & 2K Video Streams",
                feature_desc="Downloading in Ultra HD 4K (2160p) and Quad HD 2K (1440p) requires an active Media Downloader Pro license.\n\nActivate your Pro key to enjoy crystal-clear Ultra HD downloads without restrictions!"
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
                    self.after(0, self._on_playlist_download_success, files, format_type, quality)
                except Exception as e:
                    err_text = str(e)
                    self.after(0, self._on_download_error, err_text)

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
                    self.after(0, self._on_download_success, out_path, format_type, quality)
                except Exception as e:
                    err_text = str(e)
                    self.after(0, self._on_download_error, err_text)

            threading.Thread(target=task, daemon=True).start()

    def _on_download_progress(self, data: Dict[str, Any]):
        self.after(0, self._update_progress_ui, data)

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
            first_line = err_msg.split("\n")[0] if "\n" in err_msg else err_msg
            if len(first_line) > 50:
                first_line = first_line[:50] + "..."
            self.status_lbl.configure(text=f"Error: {first_line}", text_color=COLOR_DANGER)

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
            try:
                subprocess.run(f'explorer /select,"{os.path.abspath(self.last_downloaded_file)}"')
            except Exception:
                if self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
                    os.startfile(self.last_downloaded_folder)
        elif self.last_downloaded_folder and os.path.exists(self.last_downloaded_folder):
            os.startfile(self.last_downloaded_folder)


def main():
    app = YouTubeDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
