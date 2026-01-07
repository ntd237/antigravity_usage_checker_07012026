"""
Antigravity Usage Checker - Backward compatibility wrapper

CLI tool để kiểm tra mức sử dụng (quota) của các AI models trong Antigravity IDE.

Author: ntd237 (ntd237.work@gmail.com)
GitHub: https://github.com/ntd237/antigravity_usage_checker_07012026

NOTE: Main logic đã được di chuyển vào src/cli.py
File này chỉ để backward compatibility nếu user chạy trực tiếp: python main.py
"""

from src.cli import main

if __name__ == "__main__":
    main()
