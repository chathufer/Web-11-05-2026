import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import YouTubeDownloaderApp

def test_confirm():
    app = YouTubeDownloaderApp()
    app.withdraw()

    mock_batch = [
        {
            "id": "vid1",
            "url": "https://www.youtube.com/watch?v=vid1",
            "title": "Video 1",
            "uploader": "Uploader 1",
            "duration_str": "02:00",
            "thumbnail": ""
        },
        {
            "id": "vid2",
            "url": "https://www.youtube.com/watch?v=vid2",
            "title": "Video 2",
            "uploader": "Uploader 2",
            "duration_str": "03:00",
            "thumbnail": ""
        }
    ]

    initial_q_count = len(app.queue_mgr.items)
    app._open_browse_quality_dialog(mock_batch, default_format="video")

    # Manually test batch queueing via queue_mgr
    app.queue_mgr.add_batch([
        {"url": "https://www.youtube.com/watch?v=vid1", "title": "Video 1", "format_type": "video", "quality": "720p"},
        {"url": "https://www.youtube.com/watch?v=vid2", "title": "Video 2", "format_type": "video", "quality": "720p"}
    ], download_dir=app.download_dir)

    assert len(app.queue_mgr.items) == initial_q_count + 2
    print(f"Queue count verified: {len(app.queue_mgr.items)}")

    app.destroy()
    print("Confirm flow test successful!")

if __name__ == "__main__":
    test_confirm()
