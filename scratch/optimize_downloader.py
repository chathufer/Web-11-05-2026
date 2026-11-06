with open("downloader.py", "r", encoding="utf-8") as f:
    code = f.read()

target = """        # Base YDL options for YouTube
        ydl_opts: Dict[str, Any] = {
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [yt_progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
            'windowsfilenames': True,
        }"""

replacement = """        # Base YDL options for YouTube (Optimized for speed & clean telemetry)
        ydl_opts: Dict[str, Any] = {
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'socket_timeout': 20,
            'buffersize': 1024 * 64,       # 64KB stream buffer
            'http_chunk_size': 10485760,   # 10MB chunking for max download speed
            'progress_hooks': [yt_progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
            'windowsfilenames': True,
        }"""

if target in code:
    code = code.replace(target, replacement)
    with open("downloader.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("[OK] Optimized ydl_opts in downloader.py")
else:
    print("[WARN] target not found in downloader.py")
