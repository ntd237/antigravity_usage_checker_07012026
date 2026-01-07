"""
Utils module - Constants và helper functions
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

# Constants
PORT_RANGE_START = 50000
PORT_RANGE_END = 60000
CACHE_DIR = Path.home() / ".agusage"
CACHE_FILE = CACHE_DIR / "cache.json"
CACHE_MAX_AGE_HOURS = 24

# Process names liên quan đến Antigravity
ANTIGRAVITY_PROCESS_NAMES = [
    "antigravity",
    "google-code",
    "code-server",
    "editor-service",
]


def ensure_cache_dir():
    """Tạo cache directory nếu chưa tồn tại"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def format_time_remaining(seconds):
    """
    Format số giây thành human-readable string (e.g., "4h 56m")
    
    Args:
        seconds: Số giây
        
    Returns:
        str: Formatted time string
    """
    if seconds <= 0:
        return "0m"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def format_timestamp(timestamp):
    """
    Format timestamp thành readable string
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        str: Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_percentage(used, limit):
    """
    Tính % đã sử dụng
    
    Args:
        used: Số lượng đã dùng
        limit: Giới hạn
        
    Returns:
        int: Phần trăm (0-100)
    """
    if limit == 0:
        return 0
    return int((used / limit) * 100)
