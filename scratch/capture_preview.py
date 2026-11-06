import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import ImageGrab
from app import YouTubeDownloaderApp
from downloader import YouTubeDownloader

print("Launching app...")
app = YouTubeDownloaderApp()
app.update()

# Position window at top-left
app.geometry("1100x800+50+50")
app.update()

dl = YouTubeDownloader()
url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"
print("Fetching info...")
info = dl.fetch_info(url)

print("Calling _on_info_fetched_success...")
app._on_info_fetched_success(info)

for _ in range(50):
    app.update()
    time.sleep(0.06)

# Get window position and size
x = app.winfo_rootx()
y = app.winfo_rooty()
w = app.winfo_width()
h = app.winfo_height()

print(f"Grabbing screenshot of window at ({x}, {y}, {w}, {h})...")
bbox = (x, y, x + w, y + h)
shot = ImageGrab.grab(bbox=bbox)
out_path = r"C:\Users\Chathufer\.gemini\antigravity\brain\10534e66-e2c1-4b4d-8d91-98d5d0ab5110\local_app_test.png"
shot.save(out_path)
print("Saved screenshot to:", out_path)

app.destroy()
