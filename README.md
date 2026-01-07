# 🚀 Antigravity Usage Checker

CLI tool để kiểm tra mức sử dụng (quota) của các AI models trong Antigravity IDE.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)

## ✨ Features

- 🔍 **Auto-detect** - Tự động tìm Antigravity language server bằng PowerShell/psutil
- 🔐 **Real API connection** - Kết nối thực tế đến Antigravity API với CSRF token
- 🎨 **Color-coded display** - Màu xanh/vàng/đỏ dựa trên % quota còn lại
- 📊 **Unicode progress bars** - Hiển thị progress bars với `█` và `░`
- 🧮 **Smart quota calculation** - Tự động detect và deduplicate shared quota pools
- ⏱️ **Reset time countdown** - Hiển thị thời gian reset quota (e.g., "2h 24m")
- 💾 **Offline cache** - Hoạt động ngay cả khi Antigravity không chạy
- ⚡ **Fast & lightweight** - Python CLI tool đơn giản

## 📋 Requirements

- Python 3.8+
- Antigravity IDE đang chạy (để fetch live quota data)
- Windows: PowerShell (để detect language server)

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
──────────────────────────────────────────────────────────────────────────────────────────
Model                           Used  Limit  Left   Progress         Reset
──────────────────────────────────────────────────────────────────────────────────────────
Gemini 3 Pro (Low)                 2    100    98   ░░░░░░░░░░   2%  3h 48m
Gemini 3 Flash                     0    100   100   ░░░░░░░░░░   0%  4h 59m
Claude Sonnet 4.5                 56    100    44   █████░░░░░  56%  2h 24m
Claude Sonnet 4.5 (Thinking)      56    100    44   █████░░░░░  56%  2h 24m
Claude Opus 4.5 (Thinking)        56    100    44   █████░░░░░  56%  2h 24m
GPT-OSS 120B (Medium)             56    100    44   █████░░░░░  56%  2h 24m
Gemini 3 Pro (High)                2    100    98   ░░░░░░░░░░   2%  3h 48m
──────────────────────────────────────────────────────────────────────────────────────────
📊 Total: 58/300 used (80% remaining)
──────────────────────────────────────────────────────────────────────────────────────────
```

### Verbose Mode

```bash
agcheck --verbose
```

Hiển thị debug logs chi tiết về quá trình scan, connect và fetch data:
- PowerShell detection process
- CSRF token extraction
- API endpoint calls
- Port scanning

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

### Supported Models

Tool hiển thị quota cho tất cả AI models trong Antigravity:
- **Gemini 3 Pro (High/Low)** - Google Gemini models
- **Gemini 3 Flash** - Fast Gemini model
- **Claude Sonnet 4.5** - Anthropic Claude model
- **Claude Sonnet 4.5 (Thinking)** - Extended thinking mode
- **Claude Opus 4.5 (Thinking)** - Most capable Claude model
- **GPT-OSS 120B (Medium)** - Open source GPT model

### Color Indicators

- 🟢 **Green** - Còn >50% quota (healthy)
- 🟡 **Yellow** - Còn 20-50% quota (moderate usage)
- 🔴 **Red** - Còn <20% quota (low, cần chú ý)

### Progress Bars

- `██████████` - Filled portion (đã sử dụng)
- `░░░░░░░░░░` - Empty portion (còn lại)

### Smart Total Calculation

Tool tự động detect các models dùng chung quota pool dựa trên **reset time**:
- Nếu nhiều models có cùng reset time → **shared pool** → chỉ count 1 lần
- Ví dụ: Claude models (Sonnet, Opus, GPT-OSS) share pool → Total = 300, không phải 700

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

### "No CSRF token"

**Nguyên nhân:** Tool không thể extract CSRF token từ process.

**Giải pháp:**
1. Chạy với `--verbose` để xem PowerShell output
2. Đảm bảo có quyền truy cập process information
3. Thử chạy terminal as Administrator

## 🏗️ Architecture

```
antigravity_usage_checker_07012026/
├── main.py                 # Backward compatibility wrapper
├── requirements.txt        # Dependencies (psutil, requests, colorama)
├── setup.py                # Package setup với entry point
├── install.ps1             # Windows installer
├── install.sh              # macOS/Linux installer
└── src/
    ├── __init__.py
    ├── cli.py              # Main CLI entry point
    ├── utils.py            # Constants & helpers
    ├── port_detector.py    # Detect server (PowerShell + psutil)
    ├── api_client.py       # API client với real endpoint
    ├── formatter.py        # Display formatter với colors
    └── cache_manager.py    # Offline cache manager
```

## 🔧 How It Works

1. **Detect Language Server** - Dùng PowerShell `Get-CimInstance Win32_Process` để tìm `language_server` process
2. **Extract Connection Info** - Parse command line để lấy `extension_server_port` và `csrf_token`
3. **Find API Port** - Test các listening ports để tìm port respond với API
4. **Fetch Quota** - Call `/exa.language_server_pb.LanguageServerService/GetUserStatus` endpoint
5. **Parse Response** - Extract quota info từ `userStatus.cascadeModelConfigData.clientModelConfigs`
6. **Display** - Format và hiển thị với colors và progress bars

## ⚠️ Disclaimer

Tool này **không phải là official tool** từ Google/Antigravity. Tool dựa trên internal mechanisms của Antigravity language server, có thể thay đổi trong tương lai.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions, issues và feature requests đều được welcome!

Repository: https://github.com/ntd237/antigravity_usage_checker_07012026

## 📄 Changelog

### v1.0.0 (2026-01-07)
- ✅ Initial release
- ✅ Real API connection với CSRF token
- ✅ PowerShell detection for Windows
- ✅ Smart quota pool deduplication
- ✅ Full model names display
- ✅ Color-coded output với progress bars
- ✅ Offline cache support

---

⭐ Nếu tool hữu ích, đừng quên star repo nhé!
