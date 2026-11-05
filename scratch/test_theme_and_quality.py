# Test suite for Theme Palettes & Browse Quality Dialog
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import YouTubeDownloaderApp, CALM_PALETTES, ConfigManager

def test_palette_and_quality():
    print("Testing ConfigManager palette...")
    cfg = ConfigManager()
    assert "theme_palette" in cfg.data, "theme_palette missing from config"
    print(f"Config default palette: {cfg.get('theme_palette')}")

    print("Checking CALM_PALETTES definitions...")
    expected_palettes = ["Ocean", "Sage", "Lavender", "Amber", "Slate", "Rose"]
    for p in expected_palettes:
        assert p in CALM_PALETTES, f"Palette {p} missing from CALM_PALETTES"
        pal = CALM_PALETTES[p]
        assert "primary" in pal, f"primary color missing in {p}"
        assert "primary_hover" in pal, f"primary_hover missing in {p}"
        assert "bg_window" in pal, f"bg_window missing in {p}"
        assert "bg_sidebar" in pal, f"bg_sidebar missing in {p}"
        print(f"  [OK] Palette '{p}': {pal['name']} -> primary {pal['primary']}")

    print("\nInstantiating YouTubeDownloaderApp...")
    app = YouTubeDownloaderApp()
    app.withdraw()  # keep off-screen during test

    # Test applying all 6 palettes dynamically
    for p in expected_palettes:
        print(f"Applying palette '{p}'...")
        app._apply_theme_palette(p, save_config=False)
        assert app.current_palette_key == p
        assert app.logo_icon.cget("fg_color") == CALM_PALETTES[p]["primary"]
        print(f"  [OK] Applied '{p}' - logo color: {app.logo_icon.cget('fg_color')}")

    # Test mock item for browse quality dialog
    mock_item = {
        "id": "test1234",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
        "uploader": "Rick Astley",
        "duration_str": "03:32",
        "thumbnail": ""
    }

    print("\nTesting _open_browse_quality_dialog for single video...")
    app._open_browse_quality_dialog([mock_item], default_format="video")
    print("  [OK] Single video quality dialog opened successfully.")

    print("\nTesting _open_browse_quality_dialog for batch items...")
    mock_batch = [
        mock_item,
        {
            "id": "test5678",
            "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "title": "PSY - GANGNAM STYLE (Official Music Video)",
            "uploader": "officialpsy",
            "duration_str": "04:13",
            "thumbnail": ""
        }
    ]
    app._open_browse_quality_dialog(mock_batch, default_format="audio_mp3")
    print("  [OK] Batch quality dialog opened successfully.")

    # Teardown
    app.destroy()
    print("\nALL THEME PALETTE & QUALITY DIALOG TESTS PASSED!")

if __name__ == "__main__":
    test_palette_and_quality()
