"""
Concurrent Download Queue Engine for Media Downloader Pro.
Handles multi-item queuing, concurrent parallel downloads (2-3 simultaneous workers),
live progress callbacks, cancellation, and auto-dispatching.
"""

import os
import time
import uuid
import threading
from typing import Dict, Any, List, Optional, Callable

from downloader import YouTubeDownloader, CancelToken


class QueueItem:
    """Individual item in the download queue."""

    def __init__(
        self,
        url: str,
        title: str,
        uploader: str = "",
        thumbnail: str = "",
        duration_str: str = "",
        format_type: str = "video",
        quality: str = "best",
        download_dir: str = "",
        item_id: Optional[str] = None
    ):
        self.item_id = item_id or str(uuid.uuid4())[:8]
        self.url = url
        self.title = title
        self.uploader = uploader
        self.thumbnail = thumbnail
        self.duration_str = duration_str
        self.format_type = format_type
        self.quality = quality
        self.download_dir = download_dir
        self.status = "queued"  # "queued", "downloading", "finished", "error", "cancelled"
        self.percent = 0.0
        self.speed = "Waiting in queue..."
        self.eta = "--:--"
        self.downloaded = "--"
        self.total = "--"
        self.error_msg = ""
        self.output_file = ""
        self.cancel_token = CancelToken()
        self.created_at = time.time()


class DownloadQueueManager:
    """
    Orchestrates queued media downloads with configurable parallel concurrency (e.g. 2 or 3 simultaneous).
    """

    def __init__(
        self,
        downloader: YouTubeDownloader,
        on_queue_updated: Optional[Callable[[], None]] = None,
        on_item_finished: Optional[Callable[[QueueItem], None]] = None,
        max_concurrent: int = 2
    ):
        self.downloader = downloader
        self.on_queue_updated = on_queue_updated
        self.on_item_finished = on_item_finished
        self.max_concurrent = max_concurrent
        self.items: List[QueueItem] = []
        self._lock = threading.Lock()
        self.is_paused = False

    def add_to_queue(
        self,
        url: str,
        title: str,
        uploader: str = "",
        thumbnail: str = "",
        duration_str: str = "",
        format_type: str = "video",
        quality: str = "best",
        download_dir: str = ""
    ) -> QueueItem:
        with self._lock:
            item = QueueItem(
                url=url,
                title=title,
                uploader=uploader,
                thumbnail=thumbnail,
                duration_str=duration_str,
                format_type=format_type,
                quality=quality,
                download_dir=download_dir
            )
            self.items.append(item)

        self._notify_ui()
        self._dispatch()
        return item

    def add_batch(self, items_data: List[Dict[str, Any]], download_dir: str):
        with self._lock:
            for d in items_data:
                item = QueueItem(
                    url=d["url"],
                    title=d.get("title", "Video"),
                    uploader=d.get("uploader", ""),
                    thumbnail=d.get("thumbnail", ""),
                    duration_str=d.get("duration_str", ""),
                    format_type=d.get("format_type", "video"),
                    quality=d.get("quality", "best"),
                    download_dir=download_dir
                )
                self.items.append(item)

        self._notify_ui()
        self._dispatch()

    def set_concurrency(self, limit: int):
        self.max_concurrent = max(1, min(limit, 5))
        self._dispatch()

    def pause_queue(self):
        self.is_paused = True
        self._notify_ui()

    def resume_queue(self):
        self.is_paused = False
        self._notify_ui()
        self._dispatch()

    def cancel_item(self, item_id: str):
        with self._lock:
            for it in self.items:
                if it.item_id == item_id:
                    if it.status == "downloading":
                        it.cancel_token.cancel()
                    elif it.status == "queued":
                        it.status = "cancelled"
                    break
        self._notify_ui()
        self._dispatch()

    def clear_completed(self):
        with self._lock:
            self.items = [it for it in self.items if it.status in ("queued", "downloading")]
        self._notify_ui()

    def get_stats(self) -> Dict[str, int]:
        with self._lock:
            active = sum(1 for it in self.items if it.status == "downloading")
            queued = sum(1 for it in self.items if it.status == "queued")
            finished = sum(1 for it in self.items if it.status == "finished")
            error = sum(1 for it in self.items if it.status == "error")
            total = len(self.items)
            return {
                "active": active,
                "queued": queued,
                "finished": finished,
                "error": error,
                "total": total
            }

    def _dispatch(self):
        if self.is_paused:
            return

        with self._lock:
            active_count = sum(1 for it in self.items if it.status == "downloading")
            slots_available = self.max_concurrent - active_count
            if slots_available <= 0:
                return

            candidates = [it for it in self.items if it.status == "queued"]
            to_start = candidates[:slots_available]
            for it in to_start:
                it.status = "downloading"
                it.speed = "Initializing..."
                threading.Thread(target=self._worker, args=(it,), daemon=True).start()

    def _worker(self, item: QueueItem):
        last_notify_time = 0.0

        def progress_cb(d: Dict[str, Any]):
            nonlocal last_notify_time
            status = d.get('status', '')
            if status == 'downloading':
                item.percent = d.get('percent', 0.0)
                item.speed = d.get('speed', 'Calculating...')
                item.eta = d.get('eta', '--:--')
                item.downloaded = d.get('downloaded', '')
                item.total = d.get('total', '')
            elif status == 'processing':
                item.percent = 100.0
                item.speed = 'Remuxing stream...'

            now = time.time()
            if (now - last_notify_time >= 0.08) or status == 'processing':
                last_notify_time = now
                self._notify_ui()

        try:
            from licensing import LicenseManager
            is_pro = LicenseManager().is_pro()
        except Exception:
            is_pro = False

        try:
            file_path = self.downloader.download(
                url=item.url,
                download_dir=item.download_dir,
                format_type=item.format_type,
                quality=item.quality,
                progress_callback=progress_cb,
                cancel_token=item.cancel_token,
                is_pro=is_pro
            )
            item.status = "finished"
            item.percent = 100.0
            item.speed = "Done"
            item.output_file = file_path
            if self.on_item_finished:
                try:
                    self.on_item_finished(item)
                except Exception:
                    pass
        except Exception as e:
            if item.cancel_token.is_cancelled():
                item.status = "cancelled"
                item.speed = "Cancelled"
            else:
                item.status = "error"
                item.error_msg = str(e)
                item.speed = "Error"
        finally:
            self._notify_ui()
            self._dispatch()

    def _notify_ui(self):
        if self.on_queue_updated:
            try:
                self.on_queue_updated()
            except Exception:
                pass
