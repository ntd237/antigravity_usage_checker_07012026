# 🚀 Antigravity Usage Checker

CLI tool để kiểm tra mức sử dụng (quota) của các AI models trong Antigravity IDE.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## ✨ Features

- 🔍 **Auto-detect** Antigravity server - Tự động tìm và kết nối đến Antigravity language server
- 🎨 **Color-coded display** - Màu xanh/vàng/đỏ dựa trên % quota còn lại (>50% / 20-50% / <20%)
- 📊 **Unicode progress bars** - Hiển thị progress bars đẹp mắt với `█` và `░`
- 🧮 **Smart quota calculation** - Tự động detect và deduplicate shared quota pools
- ⏱️ **Reset time countdown** - Hiển thị thời gian reset quota (e.g., "4h 56m")
- 💾 **Offline cache** - Hoạt động ngay cả khi Antigravity không chạy (sử dụng cached data)
- ⚡ **Fast & lightweight** - Python CLI tool đơn giản, không dependencies phức tạp

## 📋 Requirements

- Python 3.8 trở lên
- Antigravity IDE (để fetch live quota data)

## 🔧 Installation

### Windows (PowerShell)

```powershell
iwr https://raw.githubusercontent.com/ntd237/antigravity_usage_checker_07012026/main/install.ps1 -OutFile $env:TEMP\install.ps1; . $env:TEMP\install.ps1
```

### macOS / Linux (Bash)

```bash
curl -fsSL https://raw.githubusercontent.com/ntd237/antigravity_usage_checker_07012026/main/install.sh | bash
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/ntd237/antigravity_usage_checker_07012026.git
cd antigravity_usage_checker_07012026

# Install dependencies
pip install -r requirements.txt

# Install tool globally
pip install -e .
```

## 🚀 Usage

### Basic Usage

```bash
agcheck
```

**Output example:**
```
🔍 Scanning for Antigravity server...
✅ Found server on port 53325 (PID: 49504)
📡 Fetching quota data...

🚀 Antigravity Usage Monitor
──────────────────────────────────────────────────────────────────────
Model                  Used Limit   Left Progress       Reset
──────────────────────────────────────────────────────────────────────
Gemini 3 Pro (Low)        2   100     98 ░░░░░░░░░░  2% 4h 56m
Gemini 3 Flash            0   100    100 ░░░░░░░░░░  0% 4h 59m
Claude Sonnet 4.5         2   100     98 ░░░░░░░░░░  2% 3h 32m
Claude Sonnet 4.5 (...    2   100     98 ░░░░░░░░░░  2% 3h 32m
Claude Opus 4.5 (Th...    2   100     98 ░░░░░░░░░░  2% 3h 32m
GPT-OSS 120B (Medium)     2   100     98 ░░░░░░░░░░  2% 3h 32m
Gemini 3 Pro (High)       2   100     98 ░░░░░░░░░░  2% 4h 56m
──────────────────────────────────────────────────────────────────────
📊 Total: 2/200 used (99% remaining)
──────────────────────────────────────────────────────────────────────
```

### Verbose Mode

```bash
agcheck --verbose
```

Hiển thị debug logs chi tiết về quá trình scan, connect và fetch data.

### Disable Cache

```bash
agcheck --no-cache
```

Không sử dụng cached data, luôn fetch fresh data từ server.

### Help

```bash
agcheck --help
```

## 📊 Output Explanation

### Color Indicators

- 🟢 **Green** - Còn >50% quota (healthy)
- 🟡 **Yellow** - Còn 20-50% quota (moderate usage)
- 🔴 **Red** - Còn <20% quota (low, cần chú ý)

### Progress Bars

- `██████████` - Filled portion (đã sử dụng)
- `░░░░░░░░░░` - Empty portion (còn lại)

### Smart Total Calculation

Tool tự động detect các models dùng chung quota pool (như Claude models thường share pool) và deduplicate khi tính total để tránh đếm trùng.

## 🛠️ Troubleshooting

### "Server not found"

**Nguyên nhân:** Antigravity IDE chưa chạy hoặc tool không detect được server.

**Giải pháp:**
1. Đảm bảo Antigravity IDE đang mở và active
2. Thử restart Antigravity IDE
3. Chạy với `--verbose` để xem chi tiết lỗi
4. Nếu có cached data, tool sẽ tự động sử dụng

### "Command 'agcheck' not found"

**Nguyên nhân:** Python Scripts directory chưa có trong PATH.

**Giải pháp:**

**Windows:**
```powershell
# Thêm vào PATH (restart terminal sau khi add)
$env:PATH += ";$env:APPDATA\Python\Python3X\Scripts"
```

**macOS/Linux:**
```bash
# Thêm vào ~/.bashrc hoặc ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell config
source ~/.bashrc  # hoặc source ~/.zshrc
```

### "No valid cache found"

**Nguyên nhân:** Cache không tồn tại hoặc đã quá cũ (>24 giờ).

**Giải pháp:**
1. Mở Antigravity IDE để fetch fresh data
2. Cache sẽ tự động được tạo sau lần fetch đầu tiên

## 🏗️ Architecture

```
antigravity_usage_checker_07012026/
├── main.py                 # Entry point chính
├── requirements.txt        # Dependencies
├── setup.py                # Package setup
├── install.ps1             # Windows installer
├── install.sh              # macOS/Linux installer
└── src/
    ├── __init__.py
    ├── utils.py            # Constants & helpers
    ├── port_detector.py    # Detect Antigravity server
    ├── api_client.py       # API client để fetch quota
    ├── formatter.py        # Display formatter với colors
    └── cache_manager.py    # Offline cache manager
```

## ⚠️ Disclaimer

Tool này **không phải là official tool** từ Google/Antigravity. Tool dựa trên internal mechanisms của Antigravity language server, có thể thay đổi trong tương lai.

## 📝 License

MIT License - see LICENSE file for details.

## 👨‍💻 Author

**ntd237**
- Email: ntd237.work@gmail.com
- GitHub: [@ntd237](https://github.com/ntd237)

## 🤝 Contributing

Contributions, issues và feature requests đều được welcome!

Repository: https://github.com/ntd237/antigravity_usage_checker_07012026

---

⭐ Nếu tool hữu ích, đừng quên star repo nhé!
