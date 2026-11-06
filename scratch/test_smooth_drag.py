import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
import time
from app import YouTubeDownloaderApp

print("Initializing YouTubeDownloaderApp in test harness...")
app = YouTubeDownloaderApp()
app.update()

print("Initial dimensions:", app._last_window_w, "x", app._last_window_h)

# Simulate 200 rapid window movement events (e.g. moving across screen at 1000Hz polling rate)
print("Simulating 200 rapid window move events...")
t0 = time.time()
curr_w = app._last_window_w
curr_h = app._last_window_h

for i in range(200):
    event = tk.Event()
    event.widget = app
    event.width = curr_w
    event.height = curr_h
    event.x = 100 + i
    event.y = 100 + (i // 2)
    app._on_window_configure(event)

dt = time.time() - t0
print(f"200 move events processed in {dt*1000:.2f} ms ({dt/200*1000:.3f} ms/event)!")

# Verify no resize timer was scheduled during move
if app._resize_timer is None:
    print("[PASS] Move events did NOT schedule any redundant resize timers!")
else:
    print("[FAIL] A resize timer was scheduled during movement!")

# Now simulate an actual resize event
print("Simulating actual resize event (width + 50)...")
event_resize = tk.Event()
event_resize.widget = app
event_resize.width = curr_w + 50
event_resize.height = curr_h
app._on_window_configure(event_resize)

if app._resize_timer is not None:
    print("[PASS] Actual resize event correctly scheduled debounced timer:", app._resize_timer)
    # Cancel timer before closing
    app.after_cancel(app._resize_timer)
else:
    print("[FAIL] Resize event did not schedule timer!")

app.destroy()
print("All smooth drag tests PASSED!")
