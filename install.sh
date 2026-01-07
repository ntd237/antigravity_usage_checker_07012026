#!/bin/bash
# Antigravity Usage Checker - Install Script for macOS/Linux
# Repository: https://github.com/ntd237/antigravity_usage_checker_07012026

set -e

echo ""
echo "========================================="
echo "  Antigravity Usage Checker - Installer  "
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}[*] Checking Python installation...${NC}"

PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1)
        if [[ $VERSION =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
            MAJOR=${BASH_REMATCH[1]}
            MINOR=${BASH_REMATCH[2]}
            if [ $MAJOR -ge 3 ] && [ $MINOR -ge 8 ]; then
                PYTHON_CMD=$cmd
                echo -e "${GREEN}[OK] Found $VERSION${NC}"
                break
            fi
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[ERROR] Python 3.8+ not found!${NC}"
    echo -e "${YELLOW}        Please install Python from https://www.python.org/${NC}"
    exit 1
fi

# Check pip
echo ""
echo -e "${YELLOW}[*] Checking pip...${NC}"
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}[ERROR] pip not found!${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] pip is available${NC}"

# Clone/Download repository
echo ""
echo -e "${YELLOW}[*] Setting up Antigravity Usage Checker...${NC}"

REPO_URL="https://github.com/ntd237/antigravity_usage_checker_07012026.git"
INSTALL_DIR="$HOME/.agusage"

# Check if git is available
if command -v git &> /dev/null; then
    echo -e "${YELLOW}[*] Cloning repository...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}    Directory exists, pulling latest...${NC}"
        cd "$INSTALL_DIR"
        git pull 2>/dev/null || echo -e "${YELLOW}[!] Git pull failed, continuing...${NC}"
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
else
    echo -e "${YELLOW}[*] Downloading repository...${NC}"
    ZIP_URL="https://github.com/ntd237/antigravity_usage_checker_07012026/archive/refs/heads/main.zip"
    ZIP_FILE="/tmp/agusage.zip"
    
    curl -fsSL "$ZIP_URL" -o "$ZIP_FILE"
    
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
    fi
    
    unzip -q "$ZIP_FILE" -d /tmp
    mv /tmp/antigravity_usage_checker_07012026-main "$INSTALL_DIR"
    rm "$ZIP_FILE"
fi

# Verify install directory
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}[ERROR] Installation directory not found!${NC}"
    exit 1
fi

if [ ! -f "$INSTALL_DIR/setup.py" ]; then
    echo -e "${RED}[ERROR] setup.py not found in $INSTALL_DIR${NC}"
    exit 1
fi

# Install dependencies
echo ""
echo -e "${YELLOW}[*] Installing dependencies...${NC}"
cd "$INSTALL_DIR"

$PYTHON_CMD -m pip install --upgrade pip --quiet 2>/dev/null || true
$PYTHON_CMD -m pip install -r requirements.txt --quiet
echo -e "${GREEN}[OK] Dependencies installed${NC}"

# Install package with --user flag for non-root installation
echo ""
echo -e "${YELLOW}[*] Installing agcheck command...${NC}"
$PYTHON_CMD -m pip install -e . --user --quiet 2>/dev/null || $PYTHON_CMD -m pip install -e . --quiet
echo -e "${GREEN}[OK] Package installed${NC}"

# Add ~/.local/bin to PATH if not already there
LOCAL_BIN="$HOME/.local/bin"
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo ""
    echo -e "${YELLOW}[*] Adding $LOCAL_BIN to PATH...${NC}"
    
    # Detect shell config file
    SHELL_CONFIG=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        # Check if already added
        if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" "$SHELL_CONFIG" 2>/dev/null; then
            echo '' >> "$SHELL_CONFIG"
            echo '# Antigravity Usage Checker' >> "$SHELL_CONFIG"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
            echo -e "${GREEN}[OK] Added to $SHELL_CONFIG${NC}"
        fi
    fi
    
    # Also export for current session
    export PATH="$LOCAL_BIN:$PATH"
fi

# Verify installation
echo ""
echo -e "${YELLOW}[*] Verifying installation...${NC}"

# Check if agcheck exists
AGCHECK_FOUND=false
if command -v agcheck &> /dev/null; then
    AGCHECK_FOUND=true
elif [ -f "$LOCAL_BIN/agcheck" ]; then
    AGCHECK_FOUND=true
fi

if [ "$AGCHECK_FOUND" = true ]; then
    echo -e "${GREEN}[OK] Installation successful!${NC}"
    echo ""
    echo "========================================="
    echo -e "${CYAN}  Antigravity Usage Checker installed!   ${NC}"
    echo "========================================="
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  agcheck              Check quota"
    echo "  agcheck --verbose    Debug mode"
    echo "  agcheck --no-cache   Disable cache"
    echo ""
else
    echo -e "${YELLOW}[!] Command 'agcheck' not found in PATH${NC}"
    echo ""
    echo -e "${YELLOW}Please restart your terminal or run:${NC}"
    echo -e "  ${CYAN}source ~/.bashrc${NC}  (or ~/.zshrc)"
    echo ""
    echo -e "${YELLOW}Then try:${NC}"
    echo -e "  ${CYAN}agcheck${NC}"
    echo ""
fi
