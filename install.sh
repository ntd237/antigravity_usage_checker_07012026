#!/bin/bash
# Antigravity Usage Checker - Install Script for macOS/Linux
# Author: ntd237

set -e

echo ""
echo "🚀 Antigravity Usage Checker - Installation"
echo "─────────────────────────────────────────────"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}🔍 Checking Python installation...${NC}"

PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1)
        if [[ $VERSION =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
            MAJOR=${BASH_REMATCH[1]}
            MINOR=${BASH_REMATCH[2]}
            if [ $MAJOR -ge 3 ] && [ $MINOR -ge 8 ]; then
                PYTHON_CMD=$cmd
                echo -e "${GREEN}✅ Found $VERSION${NC}"
                break
            fi
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Python 3.8+ not found!${NC}"
    echo -e "${YELLOW}   Please install Python from https://www.python.org/${NC}"
    exit 1
fi

# Check pip
echo ""
echo -e "${YELLOW}🔍 Checking pip...${NC}"
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip is available${NC}"

# Clone/Download repository
echo ""
echo -e "${YELLOW}📦 Setting up Antigravity Usage Checker...${NC}"

REPO_URL="https://github.com/ntd237/antigravity_usage_checker_07012026.git"
INSTALL_DIR="$HOME/.agusage"

# Check if git is available
if command -v git &> /dev/null; then
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}   Directory exists, pulling latest...${NC}"
        cd "$INSTALL_DIR"
        git pull
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
else
    echo -e "${YELLOW}📥 Downloading repository...${NC}"
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

# Install dependencies
echo ""
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
cd "$INSTALL_DIR"

$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

# Install package
echo ""
echo -e "${YELLOW}🔧 Installing agusage command...${NC}"
$PYTHON_CMD -m pip install -e .

# Verify installation
echo ""
echo -e "${YELLOW}✅ Verifying installation...${NC}"

if command -v agcheck &> /dev/null; then
    echo -e "${GREEN}✅ Installation successful!${NC}"
    echo ""
    echo "─────────────────────────────────────────────"
    echo -e "${CYAN}🎉 Antigravity Usage Checker installed!${NC}"
    echo "─────────────────────────────────────────────"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  agcheck              Check quota"
    echo "  agcheck --verbose    Debug mode"
    echo "  agcheck --no-cache   Disable cache"
    echo ""
    echo -e "${CYAN}GitHub: https://github.com/ntd237/antigravity_usage_checker_07012026${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Command 'agcheck' not found in PATH${NC}"
    echo -e "${YELLOW}   You may need to add Python bin directory to PATH${NC}"
    echo -e "${YELLOW}   Try: export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
fi
