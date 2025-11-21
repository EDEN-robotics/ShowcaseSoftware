#!/bin/bash
# Cleanup script - removes games, unnecessary files, and Warp

set -e

echo "=========================================="
echo "  Disk Cleanup Script"
echo "=========================================="
echo ""

# Check disk space before
BEFORE=$(df -h / | tail -1 | awk '{print $4}')
echo "Disk space before: $BEFORE"
echo ""

# 1. Uninstall Warp Terminal
echo "1. Uninstalling Warp Terminal..."
if dpkg -l | grep -q warp-terminal; then
    sudo apt remove --purge -y warp-terminal 2>/dev/null || true
    echo "   ✓ Warp removed"
else
    echo "   ⚠ Warp not found"
fi

# 2. Clean APT cache
echo ""
echo "2. Cleaning APT cache..."
sudo apt clean
echo "   ✓ APT cache cleaned"

# 3. Remove old packages
echo ""
echo "3. Removing old packages..."
sudo apt autoremove -y
echo "   ✓ Old packages removed"

# 4. Clean pip cache
echo ""
echo "4. Cleaning pip cache..."
pip cache purge 2>/dev/null || true
echo "   ✓ Pip cache cleaned"

# 5. Clean HuggingFace cache (KEEP IF YOU NEED MODELS)
echo ""
read -p "Delete HuggingFace cache (9.6GB)? Models will need to re-download. (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.cache/huggingface/*
    echo "   ✓ HuggingFace cache cleaned"
else
    echo "   ⚠ Keeping HuggingFace cache"
fi

# 6. Clean Chrome cache
echo ""
read -p "Delete Chrome cache (3.6GB)? Browser will be slower initially. (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.cache/google-chrome/*
    echo "   ✓ Chrome cache cleaned"
else
    echo "   ⚠ Keeping Chrome cache"
fi

# 7. Clean Downloads folder (interactive)
echo ""
echo "7. Checking Downloads folder..."
echo "   Large files found. Review manually:"
du -sh ~/Downloads/* 2>/dev/null | sort -hr | head -10
echo ""
read -p "Delete old downloads? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Deleting old zip/deb files (keeping recent)..."
    find ~/Downloads -type f \( -name "*.zip" -o -name "*.deb" -o -name "*.tar.gz" \) -mtime +30 -delete 2>/dev/null || true
    echo "   ✓ Old downloads cleaned"
fi

# 8. Clean Solana (if not needed)
echo ""
read -p "Delete Solana data (825MB)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.local/share/solana
    echo "   ✓ Solana data removed"
fi

# Check disk space after
echo ""
echo "=========================================="
AFTER=$(df -h / | tail -1 | awk '{print $4}')
echo "Disk space after: $AFTER"
echo "=========================================="

