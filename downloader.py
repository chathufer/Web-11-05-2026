"""
Media Downloader Backend Engine (YouTube & TikTok)
Powered by yt-dlp, direct watermark-free APIs, and FFmpeg
Supports YouTube Videos, Shorts, TikTok (No Watermark), and Full Playlists
"""

import os
import sys
import re
import time
import shutil
import subprocess
import threading
from typing import Callable, Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup
import yt_dlp

# Suppress yt-dlp JS runtime warnings from cluttering stdout/stderr
import logging
logging.getLogger("yt_dlp").setLevel(logging.ERROR)


def get_base_dir() -> str:
    """Get the base directory whether running from script or PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # type: ignore
    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_dir() -> Optional[str]:
    """Find or configure FFmpeg directory for yt-dlp and audio post-processing."""
    base_dir = get_base_dir()

    # Check local bin/ folder first
    local_bin = os.path.join(base_dir, "bin")
    if os.path.isfile(os.path.join(local_bin, "ffmpeg.exe")):
        return local_bin

    # Also check current working directory bin
    cwd_bin = os.path.join(os.getcwd(), "bin")
    if os.path.isfile(os.path.join(cwd_bin, "ffmpeg.exe")):
        return cwd_bin

    # Check if ffmpeg is in system PATH
    ffmpeg_system = shutil.which("ffmpeg")
    if ffmpeg_system:
        return os.path.dirname(ffmpeg_system)

    # Try imageio_ffmpeg only during development if bin is missing
    if not getattr(sys, 'frozen', False):
        try:
            import importlib
            img_ff = importlib.import_module("imageio_ffmpeg")
            ffmpeg_exe = img_ff.get_ffmpeg_exe()
            if ffmpeg_exe and os.path.isfile(ffmpeg_exe):
                return os.path.dirname(ffmpeg_exe)
        except Exception:
            pass

    return None


# Initialize PATH with FFmpeg if found
_ffmpeg_dir = get_ffmpeg_dir()
if _ffmpeg_dir and _ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

# Add local bin and standard Node.js directories to PATH for JS execution
_local_bin = os.path.join(get_base_dir(), "bin")
if os.path.isdir(_local_bin) and _local_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _local_bin + os.pathsep + os.environ.get("PATH", "")

for _node_dir in [r"C:\Program Files\nodejs", r"C:\Program Files (x86)\nodejs"]:
    if os.path.isdir(_node_dir) and _node_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _node_dir + os.pathsep + os.environ.get("PATH", "")


def get_js_runtime_config() -> Dict[str, Any]:
    """
    Detect available JavaScript runtimes (QuickJS, Node.js, Deno) to solve YouTube n-sig
    challenges instantly, preventing speed throttling down to 100-250 KB/s.
    Returns options dict to merge into ydl_opts.
    """
    base_dir = get_base_dir()
    runtimes: Dict[str, Any] = {}

    # 1. QuickJS (bundled in bin/qjs.exe or system PATH)
    local_qjs = os.path.join(base_dir, "bin", "qjs.exe")
    cwd_qjs = os.path.join(os.getcwd(), "bin", "qjs.exe")
    qjs_which = shutil.which("qjs") or shutil.which("quickjs")
    if os.path.isfile(local_qjs):
        runtimes['quickjs'] = {'path': local_qjs}
    elif os.path.isfile(cwd_qjs):
        runtimes['quickjs'] = {'path': cwd_qjs}
    elif qjs_which:
        runtimes['quickjs'] = {'path': qjs_which}

    # 2. Node.js (system PATH or standard install paths)
    node_which = shutil.which("node")
    standard_node_paths = [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files (x86)\nodejs\node.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\node\node.exe"),
        os.path.expandvars(r"%APPDATA%\npm\node.exe"),
    ]
    if node_which and os.path.isfile(node_which):
        runtimes['node'] = {'path': node_which}
    else:
        for np in standard_node_paths:
            if np and os.path.isfile(np):
                runtimes['node'] = {'path': np}
                break

    # 3. Deno (system PATH or standard install paths)
    deno_which = shutil.which("deno")
    deno_local = os.path.expandvars(r"%USERPROFILE%\.deno\bin\deno.exe")
    if deno_which and os.path.isfile(deno_which):
        runtimes['deno'] = {'path': deno_which}
    elif os.path.isfile(deno_local):
        runtimes['deno'] = {'path': deno_local}

    cfg: Dict[str, Any] = {
        'remote_components': {'ejs:github'},
    }
    if runtimes:
        cfg['js_runtimes'] = runtimes
    return cfg


class CancelToken:
    """Thread-safe cancellation token for downloads."""
    def __init__(self):
        self._is_cancelled = threading.Event()

    def cancel(self):
        self._is_cancelled.set()

    def is_cancelled(self) -> bool:
        return self._is_cancelled.is_set()

    def reset(self):
        self._is_cancelled.clear()


def is_valid_youtube_url(url: str) -> bool:
    """Validate whether input is a YouTube video URL (regular, share, shorts, live, music)."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    pattern = re.compile(
        r'^(https?://)?(www\.|m\.|music\.)?(youtube\.com/(watch\?.*v=|shorts/|live/|embed/)|youtu\.be/)[a-zA-Z0-9_-]{11}'
    )
    return bool(pattern.search(url))


def is_valid_youtube_playlist_url(url: str) -> bool:
    """Validate whether input is a YouTube playlist or watch link containing a playlist."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if re.search(r'^(https?://)?(www\.|m\.)?youtube\.com/playlist\?.*list=[a-zA-Z0-9_-]+', url):
        return True
    if 'list=' in url and ('youtube.com' in url or 'youtu.be' in url):
        return True
    return False


def is_valid_tiktok_url(url: str) -> bool:
    """Validate whether input is a TikTok video, share, mobile or shortened link."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    pattern = re.compile(
        r'^(https?://)?(www\.|m\.|vm\.|vt\.)?tiktok\.com/.+'
    )
    return bool(pattern.search(url))


def is_valid_media_url(url: str) -> bool:
    """Universal validator for supported platforms: YouTube, TikTok, Playlists."""
    return is_valid_youtube_url(url) or is_valid_youtube_playlist_url(url) or is_valid_tiktok_url(url)


def detect_url_type(url: str) -> str:
    """Classify URL type into 'tiktok', 'playlist', or 'youtube'."""
    if is_valid_tiktok_url(url):
        return "tiktok"
    if is_valid_youtube_playlist_url(url):
        return "playlist"
    if is_valid_youtube_url(url):
        return "youtube"
    return "unknown"


def resolve_tiktok_url(url: str) -> str:
    """Resolve shortened TikTok URLs (vm.tiktok.com, vt.tiktok.com, /t/) to canonical URL."""
    url = url.strip()
    if any(s in url for s in ['vm.tiktok.com', 'vt.tiktok.com', '/t/']):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        try:
            with requests.get(url, stream=True, allow_redirects=True, timeout=8, headers=headers) as resp:
                if resp.url:
                    return resp.url.split('?')[0]
        except Exception:
            try:
                resp = requests.head(url, allow_redirects=True, timeout=6, headers=headers)
                if resp.url:
                    return resp.url.split('?')[0]
            except Exception:
                pass
    return url


def sanitize_filename(name: str) -> str:
    """Sanitize name to be safe for Windows file and folder names."""
    if not name:
        return "Untitled"
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)
    cleaned = cleaned.strip(". ")
    return cleaned[:100] if cleaned else "Untitled"


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds to human readable string (mm:ss or hh:mm:ss)."""
    if not seconds:
        return "Unknown duration"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_views(views: Optional[int]) -> str:
    """Format view count to readable format (e.g. 1.5M views)."""
    if views is None:
        return "Unknown views"
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B views"
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M views"
    if views >= 1_000:
        return f"{views / 1_000:.1f}K views"
    return f"{views} views"


def format_bytes(num_bytes: Optional[float]) -> str:
    """Format bytes into B, KB, MB, GB."""
    if not num_bytes:
        return "0 MB"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


class YouTubeDownloader:
    """Backend class to fetch media details and download streams (YouTube & TikTok)."""

    def __init__(self):
        self.ffmpeg_dir = get_ffmpeg_dir()
        self._tiktok_cache: Dict[str, Dict[str, Any]] = {}

    def fetch_tiktok_info(self, url: str) -> Dict[str, Any]:
        """
        Fetch TikTok video metadata and watermark-free stream URLs.
        Uses a resilient multi-tier fallback pipeline:
          Tier 1: TikWM API (Fast, direct clean video & audio URLs)
          Tier 2: SSSTik Scraper (Session token parsing)
          Tier 3: yt-dlp fallback
        """
        resolved_url = resolve_tiktok_url(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }

        # ---------------- Tier 1: TikWM API ----------------
        try:
            r = requests.post(
                'https://www.tikwm.com/api/',
                data={'url': resolved_url, 'hd': 1},
                headers=headers,
                timeout=10
            )
            if r.status_code == 200:
                res = r.json()
                if res.get('code') == 0:
                    data = res.get('data', {})
                    vid_id = str(data.get('id', ''))
                    author_obj = data.get('author', {})
                    uploader = author_obj.get('unique_id') or author_obj.get('nickname') or 'tiktok_creator'
                    if not uploader.startswith('@'):
                        uploader = f"@{uploader}"

                    title = (data.get('title') or '').strip()
                    if not title:
                        title = f"TikTok Video by {uploader}"

                    dur = int(data.get('duration', 0))
                    # Video stream without watermark
                    video_url = data.get('hdplay') or data.get('play')
                    audio_url = data.get('music')
                    cover = data.get('cover') or data.get('origin_cover') or ''
                    views = data.get('play_count')

                    info_dict = {
                        'is_playlist': False,
                        'platform': 'tiktok',
                        'is_tiktok': True,
                        'no_watermark': True,
                        'id': vid_id,
                        'title': title,
                        'uploader': uploader,
                        'duration': dur,
                        'duration_str': format_duration(dur),
                        'thumbnail': cover,
                        'view_count': views,
                        'views_str': format_views(views),
                        'upload_date': '',
                        'webpage_url': resolved_url,
                        'available_heights': [1080, 720] if data.get('hdplay') else [720],
                        'max_height': 1080 if data.get('hdplay') else 720,
                        'max_fps': 30,
                        'direct_video_url': video_url,
                        'direct_audio_url': audio_url
                    }
                    self._tiktok_cache[url] = info_dict
                    self._tiktok_cache[resolved_url] = info_dict
                    return info_dict
        except Exception:
            pass

        # ---------------- Tier 2: SSSTik Scraper ----------------
        try:
            s = requests.Session()
            s.headers.update(headers)
            r1 = s.get('https://ssstik.io/en', timeout=10)
            tt_match = re.search(r's_tt\s*=\s*["\']([^"\']+)["\']', r1.text) or re.search(r"tt:['\"]([^'\"]+)['\"]", r1.text)
            if tt_match:
                tt = tt_match.group(1)
                post_headers = {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Origin': 'https://ssstik.io',
                    'Referer': 'https://ssstik.io/en',
                    'User-Agent': headers['User-Agent']
                }
                r2 = s.post('https://ssstik.io/abc?url=dl', data={'id': resolved_url, 'locale': 'en', 'tt': tt}, headers=post_headers, timeout=15)
                if r2.status_code == 200 and 'unavailable' not in r2.text.lower():
                    soup = BeautifulSoup(r2.text, 'html.parser')
                    p = soup.find('p', class_='maintext')
                    title = p.get_text(strip=True) if p else 'TikTok Video'

                    author_el = soup.find('h2')
                    uploader = author_el.get_text(strip=True) if author_el else 'TikTok Creator'
                    if not uploader.startswith('@'):
                        uploader = f"@{uploader}"

                    img = soup.find('img', class_='result_author')
                    cover = img.get('src', '') if img else ''

                    vid_url = None
                    aud_url = None
                    for a in soup.find_all('a'):
                        classes = a.get('class', [])
                        href = a.get('href', '')
                        if 'without_watermark' in classes and 'without_watermark_hd' not in classes:
                            vid_url = href
                        elif 'music' in classes:
                            aud_url = href

                    id_m = re.search(r'/video/(\d+)', resolved_url)
                    vid_id = id_m.group(1) if id_m else 'video'

                    if vid_url:
                        info_dict = {
                            'is_playlist': False,
                            'platform': 'tiktok',
                            'is_tiktok': True,
                            'no_watermark': True,
                            'id': vid_id,
                            'title': title,
                            'uploader': uploader,
                            'duration': 0,
                            'duration_str': 'Unknown duration',
                            'thumbnail': cover,
                            'view_count': None,
                            'views_str': 'TikTok Video',
                            'upload_date': '',
                            'webpage_url': resolved_url,
                            'available_heights': [1080, 720],
                            'max_height': 1080,
                            'max_fps': 30,
                            'direct_video_url': vid_url,
                            'direct_audio_url': aud_url
                        }
                        self._tiktok_cache[url] = info_dict
                        self._tiktok_cache[resolved_url] = info_dict
                        return info_dict
        except Exception:
            pass

        # ---------------- Tier 3: yt-dlp Fallback ----------------
        try:
            ydl_opts: Dict[str, Any] = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            if self.ffmpeg_dir:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_dir
            ydl_opts.update(get_js_runtime_config())
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(resolved_url, download=False)
                if info:
                    uploader = info.get('uploader') or info.get('channel') or 'tiktok_user'
                    if not uploader.startswith('@'):
                        uploader = f"@{uploader}"
                    return {
                        'is_playlist': False,
                        'platform': 'tiktok',
                        'is_tiktok': True,
                        'no_watermark': True,
                        'id': info.get('id', ''),
                        'title': info.get('title') or f"TikTok Video by {uploader}",
                        'uploader': uploader,
                        'duration': info.get('duration', 0),
                        'duration_str': format_duration(info.get('duration')),
                        'thumbnail': info.get('thumbnail', ''),
                        'view_count': info.get('view_count'),
                        'views_str': format_views(info.get('view_count')),
                        'upload_date': info.get('upload_date', ''),
                        'webpage_url': resolved_url,
                        'available_heights': [1080, 720],
                        'max_height': 1080,
                        'max_fps': 30,
                        'direct_video_url': None,
                        'direct_audio_url': None
                    }
        except Exception:
            pass

        raise ValueError("TikTok video fetching failed. Please make sure the video is public and the link is valid.")

    def download_tiktok(
        self,
        url: str,
        download_dir: str,
        format_type: str = "video",
        quality: str = "best",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        cancel_token: Optional[CancelToken] = None,
        file_prefix: str = "",
        is_pro: Optional[bool] = None
    ) -> str:
        if is_pro is None:
            try:
                from licensing import LicenseManager
                is_pro = LicenseManager().is_pro()
            except Exception:
                is_pro = False
        """
        Download TikTok video WITHOUT WATERMARK or as pure Hi-Fi MP3 audio.
        Streams data with real-time speed, ETA, and cancellation support.
        """
        os.makedirs(download_dir, exist_ok=True)

        if cancel_token and cancel_token.is_cancelled():
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")

        # Check cache or fetch metadata
        resolved = resolve_tiktok_url(url)
        info = self._tiktok_cache.get(url) or self._tiktok_cache.get(resolved)
        if not info or not info.get('direct_video_url'):
            info = self.fetch_tiktok_info(url)

        # Determine download URL & extension
        if format_type in ("audio_mp3", "audio_m4a"):
            stream_url = info.get('direct_audio_url') or info.get('direct_video_url')
            ext = ".mp3"
            must_convert = not bool(info.get('direct_audio_url'))
        else:
            # If Free tier, use standard 720p stream if HD is restricted
            if not is_pro and info.get('direct_video_url_sd'):
                stream_url = info.get('direct_video_url_sd')
            else:
                stream_url = info.get('direct_video_url')
            ext = ".mp4"
            must_convert = False

        if not stream_url:
            raise ValueError("No direct stream URL available for this TikTok video.")

        safe_title = sanitize_filename(info.get('title', 'TikTok Video'))
        vid_id = info.get('id', 'video')
        final_filename = f"{file_prefix}{safe_title} [{vid_id}]{ext}"
        final_path = os.path.join(download_dir, final_filename)

        temp_ext = ".temp.mp4" if must_convert else f".part{ext}"
        temp_path = os.path.join(download_dir, f"{file_prefix}{safe_title} [{vid_id}]{temp_ext}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }

        r = requests.get(stream_url, headers=headers, stream=True, timeout=20)
        r.raise_for_status()
        total_bytes = int(r.headers.get('content-length', 0))

        downloaded_bytes = 0
        start_time = time.time()
        last_update = start_time

        try:
            with open(temp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if cancel_token and cancel_token.is_cancelled():
                        f.close()
                        if os.path.exists(temp_path):
                            try:
                                os.remove(temp_path)
                            except Exception:
                                pass
                        raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")

                    if chunk:
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        now = time.time()

                        if progress_callback and (now - last_update >= 0.1 or (total_bytes > 0 and downloaded_bytes == total_bytes)):
                            elapsed = now - start_time
                            speed = downloaded_bytes / elapsed if elapsed > 0 else 0
                            percent = (downloaded_bytes / total_bytes * 100.0) if total_bytes > 0 else 50.0
                            eta_sec = (total_bytes - downloaded_bytes) / speed if speed > 0 and total_bytes > downloaded_bytes else 0

                            progress_callback({
                                'status': 'downloading',
                                'percent': min(100.0, max(0.0, percent)),
                                'speed': f"{speed / (1024 * 1024):.2f} MB/s",
                                'eta': f"{int(eta_sec // 60):02d}:{int(eta_sec % 60):02d}",
                                'downloaded': format_bytes(downloaded_bytes),
                                'total': format_bytes(total_bytes) if total_bytes > 0 else "Unknown size",
                                'filename': final_filename
                            })
                            last_update = now

        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            raise e

        # If audio conversion is required (video downloaded as audio source)
        if must_convert:
            if progress_callback:
                progress_callback({
                    'status': 'processing',
                    'message': 'Converting audio to MP3 with FFmpeg...',
                    'percent': 100.0,
                    'speed': 'Converting...',
                    'eta': '00:00',
                    'downloaded': format_bytes(downloaded_bytes),
                    'total': format_bytes(total_bytes),
                    'filename': final_filename
                })

            ffmpeg_bin = os.path.join(self.ffmpeg_dir, "ffmpeg.exe") if self.ffmpeg_dir else "ffmpeg"
            cmd = [
                ffmpeg_bin,
                "-y",
                "-i", temp_path,
                "-vn",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                final_path
            ]
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, startupinfo=startupinfo)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                # If FFmpeg conversion fails, keep the original temp file renamed
                if os.path.exists(final_path):
                    pass
                else:
                    shutil.move(temp_path, final_path)
        else:
            if os.path.exists(final_path):
                try:
                    os.remove(final_path)
                except Exception:
                    pass
            shutil.move(temp_path, final_path)

        if progress_callback:
            progress_callback({
                'status': 'finished',
                'percent': 100.0,
                'speed': 'Done',
                'eta': '00:00',
                'downloaded': format_bytes(downloaded_bytes),
                'total': format_bytes(downloaded_bytes),
                'filename': final_path
            })

        return final_path

    def fetch_info(self, url: str) -> Dict[str, Any]:
        """Fetch video or playlist metadata without downloading media."""
        url = url.strip()
        is_tiktok = is_valid_tiktok_url(url)
        is_playlist_url = is_valid_youtube_playlist_url(url)

        # Route TikTok URLs directly through our dedicated engine
        if is_tiktok:
            return self.fetch_tiktok_info(url)

        ydl_opts: Dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'socket_timeout': 15,
            'retries': 5,
        }
        if self.ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_dir
        ydl_opts.update(get_js_runtime_config())

        # For playlist links, use flat extraction to quickly load items
        if is_playlist_url:
            ydl_opts['extract_flat'] = 'in_playlist'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Could not extract media details from URL.")

            # 1. PLAYLIST RESULT
            if info.get('_type') == 'playlist' or ('entries' in info and isinstance(info.get('entries'), list)):
                entries_raw = list(info.get('entries', []))
                entries = []
                for idx, e in enumerate(entries_raw, start=1):
                    if not e:
                        continue
                    e_id = e.get('id', '')
                    e_url = e.get('url') or ''
                    if not e_url.startswith('http') and e_id:
                        e_url = f"https://www.youtube.com/watch?v={e_id}"

                    e_dur = e.get('duration')
                    # Thumbnail
                    thumb = ''
                    thumbs = e.get('thumbnails', [])
                    if thumbs and isinstance(thumbs, list):
                        thumb = thumbs[-1].get('url', '')

                    entries.append({
                        'index': idx,
                        'id': e_id,
                        'title': e.get('title') or f"Track {idx}",
                        'duration': e_dur or 0,
                        'duration_str': format_duration(e_dur),
                        'uploader': e.get('uploader') or e.get('channel') or info.get('uploader') or 'Unknown Channel',
                        'url': e_url,
                        'thumbnail': thumb,
                        'is_selected': True
                    })

                # Determine playlist thumbnail
                pl_thumb = ''
                if entries and entries[0].get('thumbnail'):
                    pl_thumb = entries[0]['thumbnail']
                elif info.get('thumbnails') and isinstance(info['thumbnails'], list):
                    pl_thumb = info['thumbnails'][-1].get('url', '')

                return {
                    'is_playlist': True,
                    'platform': 'youtube',
                    'id': info.get('id', ''),
                    'title': info.get('title') or "Untitled Playlist",
                    'uploader': info.get('uploader') or info.get('channel') or "Unknown Channel",
                    'total_items': len(entries),
                    'thumbnail': pl_thumb,
                    'webpage_url': info.get('webpage_url') or url,
                    'entries': entries
                }

            # 2. SINGLE YOUTUBE VIDEO
            formats = info.get('formats', [])
            available_heights = set()
            fps_set = set()
            for f in formats:
                h = f.get('height')
                if h and isinstance(h, int):
                    available_heights.add(h)
                fps = f.get('fps')
                if fps and isinstance(fps, (int, float)) and fps > 0:
                    fps_set.add(int(round(fps)))

            sorted_heights = sorted(list(available_heights), reverse=True)
            max_fps = max(fps_set) if fps_set else None

            uploader = info.get('uploader') or info.get('channel') or 'Unknown Creator'
            vid_id = info.get('id', '')
            fast_thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ''
            thumb_candidates = []
            if vid_id:
                thumb_candidates = [
                    f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
                    f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                    f"https://i.ytimg.com/vi/{vid_id}/sddefault.jpg",
                    f"https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg"
                ]
            raw_thumb = info.get('thumbnail', '')
            if raw_thumb and raw_thumb not in thumb_candidates:
                thumb_candidates.append(raw_thumb)

            return {
                'is_playlist': False,
                'platform': 'youtube',
                'is_tiktok': False,
                'no_watermark': False,
                'id': vid_id,
                'title': info.get('title', 'Unknown Title'),
                'uploader': uploader,
                'duration': info.get('duration', 0),
                'duration_str': format_duration(info.get('duration')),
                'thumbnail': fast_thumb or raw_thumb,
                'thumbnail_fallbacks': thumb_candidates,
                'view_count': info.get('view_count'),
                'views_str': format_views(info.get('view_count')),
                'upload_date': info.get('upload_date', ''),
                'webpage_url': info.get('webpage_url', url),
                'available_heights': sorted_heights,
                'max_height': sorted_heights[0] if sorted_heights else None,
                'max_fps': max_fps
            }

    def download(
        self,
        url: str,
        download_dir: str,
        format_type: str = "video",
        quality: str = "best",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        cancel_token: Optional[CancelToken] = None,
        file_prefix: str = "",
        is_pro: Optional[bool] = None
    ) -> str:
        if is_pro is None:
            try:
                from licensing import LicenseManager
                is_pro = LicenseManager().is_pro()
            except Exception:
                is_pro = False
        """
        Download single YouTube or TikTok video/audio.
        For TikTok: automatically extracts the clean stream WITHOUT WATERMARK.
        """
        os.makedirs(download_dir, exist_ok=True)
        is_tiktok = is_valid_tiktok_url(url)

        # Route TikTok URLs directly through our dedicated engine
        if is_tiktok:
            return self.download_tiktok(
                url=url,
                download_dir=download_dir,
                format_type=format_type,
                quality=quality,
                progress_callback=progress_callback,
                cancel_token=cancel_token,
                file_prefix=file_prefix,
                is_pro=is_pro
            )

        # Output template (supports optional file prefix like "01 - ")
        outtmpl = os.path.join(download_dir, f"{file_prefix}%(title).150s [%(id)s].%(ext)s")
        downloaded_file_container = {"path": ""}

        def yt_progress_hook(d: Dict[str, Any]):
            if cancel_token and cancel_token.is_cancelled():
                raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")

            status = d.get('status', '')
            if status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes') or 0

                percent = 0.0
                if total > 0:
                    percent = (downloaded / total) * 100.0
                else:
                    p_str = d.get('_percent_str', '0%').replace('%', '').strip()
                    try:
                        percent = float(p_str)
                    except ValueError:
                        percent = 0.0

                speed_raw = d.get('speed')
                if speed_raw and isinstance(speed_raw, (int, float)) and speed_raw > 0:
                    speed_str = f"{format_bytes(speed_raw)}/s"
                else:
                    speed_str = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', str(d.get('_speed_str', 'Calculating...'))).strip()

                eta_raw = d.get('eta')
                if eta_raw and isinstance(eta_raw, (int, float)) and eta_raw > 0:
                    eta_str = format_duration(int(eta_raw))
                else:
                    eta_str = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', str(d.get('_eta_str', 'N/A'))).strip()
                total_str = format_bytes(total) if total > 0 else "Unknown size"
                downloaded_str = format_bytes(downloaded)

                if progress_callback:
                    progress_callback({
                        'status': 'downloading',
                        'percent': min(max(percent, 0.0), 100.0),
                        'speed': speed_str,
                        'eta': eta_str,
                        'downloaded': downloaded_str,
                        'total': total_str,
                        'filename': d.get('filename', '')
                    })

            elif status == 'finished':
                downloaded_file_container['path'] = d.get('filename', '')
                if progress_callback:
                    progress_callback({
                        'status': 'processing',
                        'percent': 100.0,
                        'speed': 'Done',
                        'eta': '00:00',
                        'downloaded': '',
                        'total': '',
                        'filename': d.get('filename', '')
                    })

        def postprocessor_hook(d: Dict[str, Any]):
            if cancel_token and cancel_token.is_cancelled():
                raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")

            status = d.get('status', '')
            if status == 'started':
                if progress_callback:
                    progress_callback({
                        'status': 'processing',
                        'message': 'Merging audio and video...' if format_type == 'video' else 'Extracting & converting audio...',
                        'percent': 100.0,
                    })

        # Base YDL options for YouTube (Optimized for high-speed throughput & clean telemetry)
        ydl_opts: Dict[str, Any] = {
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'socket_timeout': 30,
            'retries': 20,
            'fragment_retries': 20,
            'file_access_retries': 5,
            'http_chunk_size': 10485760,  # 10MB chunking prevents YouTube googlevideo TCP resets & enables chunk-level retries
            'buffersize': 1024 * 64,
            'retry_sleep_functions': {'http': lambda n: 1, 'fragment': lambda n: 1},
            'progress_hooks': [yt_progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
            'windowsfilenames': True,
        }
        ydl_opts.update(get_js_runtime_config())

        if self.ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_dir

        if format_type == "video":
            ydl_opts['merge_output_format'] = 'mp4'
            if not is_pro:
                # STRICT FREE TIER RESTRICTION: Max 720p height AND max 30fps
                max_h = 720
                if quality != "best":
                    h_cand = quality.replace("p", "").strip()
                    if h_cand.isdigit() and int(h_cand) < 720:
                        max_h = int(h_cand)
                ydl_opts['format'] = (
                    f'bestvideo*[height<={max_h}][fps<=30]+bestaudio/'
                    f'bestvideo*[height<={max_h}]+bestaudio/'
                    f'best[height<={max_h}][fps<=30]/'
                    f'best[height<={max_h}]/best'
                )
            else:
                # UNRESTRICTED PRO / 7-DAY TRIAL: 8K, 4K, 1440p, 1080p, 60fps
                if quality == "best":
                    ydl_opts['format'] = 'bestvideo*+bestaudio/best'
                else:
                    height = quality.replace("p", "").strip()
                    if height.isdigit():
                        ydl_opts['format'] = f'bestvideo*[height<={height}]+bestaudio/best[height<={height}]/best'
                    else:
                        ydl_opts['format'] = 'bestvideo*+bestaudio/best'

        elif format_type == "audio_mp3":
            ydl_opts['format'] = 'bestaudio/best'
            kbps = quality if quality.isdigit() else '320'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': kbps,
            }]

        elif format_type == "audio_m4a":
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # Extension adjustments
            if format_type == "audio_mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"
            elif format_type == "audio_m4a":
                filename = os.path.splitext(filename)[0] + ".m4a"
            elif format_type == "video":
                base_no_ext = os.path.splitext(filename)[0]
                if os.path.isfile(base_no_ext + ".mp4"):
                    filename = base_no_ext + ".mp4"

            return filename

    def download_playlist(
        self,
        playlist_info: Dict[str, Any],
        selected_indices: Optional[List[int]],
        download_dir: str,
        format_type: str = "video",
        quality: str = "best",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        cancel_token: Optional[CancelToken] = None,
        is_pro: Optional[bool] = None
    ) -> List[str]:
        if is_pro is None:
            try:
                from licensing import LicenseManager
                is_pro = LicenseManager().is_pro()
            except Exception:
                is_pro = False
        """
        Download a collection of playlist entries one by one into an organized subfolder.
        Reports both overall playlist progress and active video progress.
        """
        pl_title = sanitize_filename(playlist_info.get("title", "Playlist"))
        target_dir = os.path.join(download_dir, pl_title)
        os.makedirs(target_dir, exist_ok=True)

        all_entries = playlist_info.get("entries", [])
        if selected_indices is not None:
            entries_to_download = [e for e in all_entries if e.get("index") in selected_indices]
        else:
            entries_to_download = all_entries

        total_count = len(entries_to_download)
        downloaded_files: List[str] = []

        for current_idx, entry in enumerate(entries_to_download, start=1):
            if cancel_token and cancel_token.is_cancelled():
                break

            entry_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
            entry_title = entry.get("title") or f"Video {current_idx}"

            # Proxy callback to attach playlist context
            def item_progress_proxy(data: Dict[str, Any]):
                if progress_callback:
                    enriched = dict(data)
                    enriched['is_playlist'] = True
                    enriched['overall_current'] = current_idx
                    enriched['overall_total'] = total_count
                    enriched['current_title'] = entry_title
                    enriched['playlist_folder'] = target_dir
                    progress_callback(enriched)

            try:
                file_path = self.download(
                    url=entry_url,
                    download_dir=target_dir,
                    format_type=format_type,
                    quality=quality,
                    progress_callback=item_progress_proxy,
                    cancel_token=cancel_token,
                    file_prefix=f"{current_idx:02d} - ",
                    is_pro=is_pro
                )
                if file_path and os.path.exists(file_path):
                    downloaded_files.append(file_path)
            except Exception:
                if cancel_token and cancel_token.is_cancelled():
                    break
                # On individual failure (e.g. video blocked or deleted), keep downloading remainder
                continue

        return downloaded_files

    def search_youtube(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search YouTube directly for videos and return parsed results with titles,
        channels, duration, views, thumbnails, and URLs.
        """
        query = query.strip()
        if not query:
            return []

        ydl_opts: Dict[str, Any] = {
            'quiet': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
        }
        if self.ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_dir
        ydl_opts.update(get_js_runtime_config())

        search_spec = f"ytsearch{limit}:{query}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(search_spec, download=False)
            raw_entries = res.get('entries', []) if res else []
            results = []
            for idx, e in enumerate(raw_entries, start=1):
                if not e:
                    continue
                v_id = e.get('id', '')
                v_url = e.get('url') or ''
                if not v_url.startswith('http') and v_id:
                    v_url = f"https://www.youtube.com/watch?v={v_id}"

                thumb = ''
                thumbs = e.get('thumbnails', [])
                if thumbs and isinstance(thumbs, list):
                    thumb = thumbs[-1].get('url', '')
                elif v_id:
                    thumb = f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"

                dur = e.get('duration') or 0
                views = e.get('view_count')

                results.append({
                    'index': idx,
                    'id': v_id,
                    'title': e.get('title') or f"Video {idx}",
                    'uploader': e.get('uploader') or e.get('channel') or 'YouTube Creator',
                    'duration': dur,
                    'duration_str': format_duration(dur),
                    'views_str': format_views(views),
                    'thumbnail': thumb,
                    'url': v_url
                })
            return results

