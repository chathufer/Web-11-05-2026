# Script to update app.py with Calm Palettes, Theme Switcher, and Browse Quality Dialog
import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Design System Colors & CALM_PALETTES
old_colors_start = '# ----------------- Design System Colors (Cyber-Luxury Obsidian Edition) -----------------'
new_colors_block = '''# ----------------- Design System Colors & Calm Palettes -----------------
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
'''

old_colors_end = 'TEXT_MUTED = ("#94A3B8", "#64748B")'
pos_start = content.find(old_colors_start)
pos_end = content.find(old_colors_end)
if pos_start != -1 and pos_end != -1:
    pos_end += len(old_colors_end)
    content = content[:pos_start] + new_colors_block + content[pos_end:]
    print("Replaced colors block successfully")
else:
    print("Could not find colors block")

# 2. Update ConfigManager default dict
old_config_init = '''        self.data = {
            "download_dir": DEFAULT_DOWNLOAD_DIR,
            "theme": "Dark",
            "ui_scale": "100%",
            "auto_clipboard": True,
            "default_format": "video"
        }'''

new_config_init = '''        self.data = {
            "download_dir": DEFAULT_DOWNLOAD_DIR,
            "theme": "Dark",
            "theme_palette": "Ocean",
            "ui_scale": "100%",
            "auto_clipboard": True,
            "default_format": "video"
        }'''

content = content.replace(old_config_init, new_config_init)
print("Updated ConfigManager default dict")

# 3. Update YouTubeDownloaderApp.__init__ palette loading
old_app_init = '''        # Apply Appearance & Scaling
        initial_theme = self.config.get("theme", "Dark")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")

        self._apply_ui_scaling(self.config.get("ui_scale", "100%"))'''

new_app_init = '''        # Apply Appearance & Scaling
        initial_theme = self.config.get("theme", "Dark")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")

        self.current_palette_key = self.config.get("theme_palette", "Ocean")
        self._load_palette_constants(self.current_palette_key)

        self._apply_ui_scaling(self.config.get("ui_scale", "100%"))'''

content = content.replace(old_app_init, new_app_init)
print("Updated YouTubeDownloaderApp.__init__")

# 4. In _build_sidebar_content: make logo_icon self.logo_icon and add palette selector
old_logo = '''        logo_icon = ctk.CTkLabel(
            logo_box,
            text=" 👑 ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF",
            fg_color=COLOR_PRIMARY,
            corner_radius=10,
            width=38,
            height=38
        )
        logo_icon.pack(side="left", padx=(0, 10))'''

new_logo = '''        self.logo_icon = ctk.CTkLabel(
            logo_box,
            text=" 👑 ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF",
            fg_color=COLOR_PRIMARY,
            corner_radius=10,
            width=38,
            height=38
        )
        self.logo_icon.pack(side="left", padx=(0, 10))'''

content = content.replace(old_logo, new_logo)

old_sidebar_bottom = '''        self.theme_switch = ctk.CTkSwitch(
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
        self.theme_switch.pack(anchor="w", padx=12, pady=(4, 10))'''

new_sidebar_bottom = '''        self.theme_switch = ctk.CTkSwitch(
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
        self.sidebar_palette_menu.pack(fill="x", padx=12, pady=(0, 10))'''

content = content.replace(old_sidebar_bottom, new_sidebar_bottom)
print("Updated sidebar bottom with palette menu")

# 5. In _build_browse_search_results_section: update download buttons to call quality dialog
old_mp4_btn = '''            # 1-Click MP4 Download
            ctk.CTkButton(
                right_btns,
                text="⚡ MP4",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=65,
                height=30,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                corner_radius=6,
                command=lambda it=item: self._queue_single_browse_video(it, format_type="video")
            ).pack(side="left", padx=2)

            # 1-Click MP3 Download
            ctk.CTkButton(
                right_btns,
                text="🎵 MP3",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=65,
                height=30,
                fg_color="#0284C7",
                hover_color="#0369A1",
                corner_radius=6,
                command=lambda it=item: self._queue_single_browse_video(it, format_type="audio_mp3")
            ).pack(side="left", padx=2)'''

new_mp4_btn = '''            # Quality Selection MP4 Download
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
            ).pack(side="left", padx=2)'''

content = content.replace(old_mp4_btn, new_mp4_btn)
print("Updated MP4 and MP3 buttons in browse results to open quality dialog")

# 6. Update _on_download_selected_browse_clicked
old_batch_click = '''    def _on_download_selected_browse_clicked(self):
        """Batch queue all checked search result videos."""
        selected_ids = [vid for vid, v in self.browse_item_vars.items() if v.get()]
        if not selected_ids:
            self.browse_sel_count_lbl.configure(text="⚠️ Please check at least 1 video first!", text_color=COLOR_WARNING)
            return

        fmt_choice = self.browse_batch_format_seg.get()
        format_type = "audio_mp3" if "MP3" in fmt_choice else "video"

        q_choice = self.browse_batch_quality_menu.get()
        if "720p" in q_choice:
            quality = "720p"
        elif "480p" in q_choice:
            quality = "480p"
        elif "360p" in q_choice:
            quality = "360p"
        else:
            quality = "best"

        # Check Free tier quality limit
        if not self.license_mgr.is_pro() and format_type == "video":
            quality = "720p"

        items_to_add = []
        for it in self.browse_search_results:
            if it["id"] in selected_ids:
                items_to_add.append({
                    "url": it["url"],
                    "title": it["title"],
                    "uploader": it.get("uploader", ""),
                    "thumbnail": it.get("thumbnail", ""),
                    "duration_str": it.get("duration_str", ""),
                    "format_type": format_type,
                    "quality": quality
                })

        self.queue_mgr.add_batch(items_to_add, download_dir=self.download_dir)
        self._deselect_all_browse_results()
        self._update_queue_badge()

        # Switch to queue tab so user sees their 2 or 3 parallel downloads in action
        self._set_browse_subtab("queue")'''

new_batch_click = '''    def _on_download_selected_browse_clicked(self):
        """Batch queue all checked search result videos with quality selection dialog."""
        selected_ids = [vid for vid, v in self.browse_item_vars.items() if v.get()]
        if not selected_ids:
            self.browse_sel_count_lbl.configure(text="⚠️ Please check at least 1 video first!", text_color=COLOR_WARNING)
            return

        fmt_choice = self.browse_batch_format_seg.get()
        default_format = "audio_mp3" if "MP3" in fmt_choice else "video"
        items_to_add = [it for it in self.browse_search_results if it["id"] in selected_ids]
        self._open_browse_quality_dialog(items_to_add, default_format=default_format)'''

content = content.replace(old_batch_click, new_batch_click)
print("Updated _on_download_selected_browse_clicked")

# 7. Add _open_browse_quality_dialog method right before _queue_single_browse_video
quality_dialog_code = '''    def _open_browse_quality_dialog(self, items: List[Dict[str, Any]], default_format: str = "video"):
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

'''

target_single = '    def _queue_single_browse_video(self, video_data: Dict[str, Any], format_type: str = "video"):'
content = content.replace(target_single, quality_dialog_code + target_single)
print("Added _open_browse_quality_dialog method")

# 8. In _build_settings_view: add Visual Customization Card right before Display scaling card
old_display_card = '        # Card 1: Display & Resolution Scaling\n        display_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)'
if old_display_card not in content:
    # Try with CRLF
    old_display_card = '        # Card 1: Display & Resolution Scaling\r\n        display_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)'

new_palette_card = '''        # Card: Theme Palette & Visual Customization
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
        display_card = ctk.CTkFrame(self.view_settings, corner_radius=14, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR)'''

content = content.replace(old_display_card, new_palette_card)
print("Added palette customization card to settings view")

# 9. Add palette switching methods to YouTubeDownloaderApp
palette_methods = '''    def _load_palette_constants(self, palette_key: str):
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

'''

# Insert palette methods before _on_theme_switched
target_theme = '    def _on_theme_switched(self):'
content = content.replace(target_theme, palette_methods + target_theme)
print("Added palette methods before _on_theme_switched")

# Write back with utf-8 encoding
with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("ALL UPDATES SUCCESSFULLY APPLIED TO app.py!")
