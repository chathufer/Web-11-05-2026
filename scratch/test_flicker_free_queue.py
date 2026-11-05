import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import YouTubeDownloaderApp
from queue_manager import QueueItem

def test_flicker_free_queue():
    print("Testing flicker-free in-place queue updates...")
    app = YouTubeDownloaderApp()
    app.withdraw()

    # Create dummy queue item
    item = app.queue_mgr.add_to_queue(
        url="https://www.youtube.com/watch?v=mock_flicker_test",
        title="Counter Strike 2 | Live Stream High FPS",
        uploader="Vimuwa Streams",
        format_type="video",
        quality="1080p",
        download_dir=app.download_dir
    )

    print(f"Added item {item.item_id}")
    app._refresh_queue_ui()

    assert item.item_id in app.queue_card_widgets, "Item card was not created in queue_card_widgets"
    card_info = app.queue_card_widgets[item.item_id]
    original_frame = card_info["card"]
    original_status_pill = card_info["status_pill"]
    original_bar = card_info["p_bar"]

    print("Simulating 50 rapid download progress updates (testing zero-flicker stability)...")
    for i in range(1, 51):
        item.status = "downloading"
        item.percent = float(i * 2)
        item.speed = f"{5.0 + (i % 5) * 0.8:.1f} MB/s"
        item.eta = f"00:{50 - i:02d}"
        item.downloaded = f"{i * 2} MB"
        item.total = "100 MB"

        app._refresh_queue_ui()

        # Crucial assertion: the widgets MUST BE the exact same instances (not destroyed and recreated!)
        current_card_info = app.queue_card_widgets[item.item_id]
        assert current_card_info["card"] is original_frame, f"Card widget was recreated on step {i}! That causes flickering!"
        assert current_card_info["status_pill"] is original_status_pill, f"Status pill was recreated on step {i}!"
        assert current_card_info["p_bar"] is original_bar, f"Progress bar was recreated on step {i}!"

    print("  [OK] 50 rapid progress updates verified: 100% IN-PLACE WIDGET REUSE (ZERO FLICKER).")

    # Simulate completion
    print("Simulating completion transition...")
    item.status = "finished"
    item.percent = 100.0
    item.output_file = os.path.join(app.download_dir, "test_file.mp4")
    app._refresh_queue_ui()

    assert card_info["last_status"] == "finished"
    assert "COMPLETED" in card_info["last_st_text"]
    print("  [OK] Transition to COMPLETED verified.")

    # Simulate clearing completed
    print("Testing clearing completed...")
    app.queue_mgr.clear_completed()
    app._refresh_queue_ui()
    assert item.item_id not in app.queue_card_widgets
    print("  [OK] Cleared completed cards cleaned up cleanly.")

    app.destroy()
    print("\nALL FLICKER-FREE QUEUE TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_flicker_free_queue()
