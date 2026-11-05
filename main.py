"""
Main Launcher for YouTube Video Downloader
"""

import sys
import os

# Ensure local directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import main

if __name__ == "__main__":
    main()
