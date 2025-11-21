#!/bin/bash
# Automated cleanup - removes games, unnecessary files, and Warp

set -e

echo "=========================================="
echo "  Automated Disk Cleanup"
echo "=========================================="
echo ""

BEFORE=$(df -h / | tail -1 | awk '{print $3 " used, " $4 " free"}')
echo "Before: $BEFORE"
echo ""

# 1. Uninstall Warp Terminal
echo "1. Uninstalling Warp Terminal..."
if dpkg -l | grep -q warp-terminal; then
    sudo apt remove --purge -y warp-terminal
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

# 5. Delete old installers in Downloads
echo ""
echo "5. Deleting old installers (.deb files)..."
rm -f ~/Downloads/*.deb 2>/dev/null || true
echo "   ✓ Old installers removed"

# 6. Delete old Discord installers
echo ""
echo "6. Deleting old Discord installers..."
rm -f ~/Downloads/discord-*.deb 2>/dev/null || true
echo "   ✓ Discord installers removed"

# 7. Delete Warp installer
echo ""
echo "7. Deleting Warp installer..."
rm -f ~/Downloads/warp-terminal*.deb 2>/dev/null || true
echo "   ✓ Warp installer removed"

# 8. Delete BalenaEtcher (if already installed)
echo ""
echo "8. Deleting BalenaEtcher installer..."
rm -f ~/Downloads/balenaEtcher*.zip 2>/dev/null || true
echo "   ✓ BalenaEtcher installer removed"

# 9. Delete older SD card image (keep newest)
echo ""
echo "9. Deleting older SD card image (keeping newest)..."
if [ -f ~/Downloads/jp60-orin-nano-sd-card-image.zip ] && [ -f ~/Downloads/jp62-orin-nano-sd-card-image.zip ]; then
    rm -f ~/Downloads/jp60-orin-nano-sd-card-image.zip
    echo "   ✓ Deleted jp60 (kept jp62)"
fi

# 10. Clean Chrome cache
echo ""
echo "10. Cleaning Chrome cache..."
rm -rf ~/.cache/google-chrome/* 2>/dev/null || true
echo "   ✓ Chrome cache cleaned"

# 11. Clean Solana (not needed for robotics)
echo ""
echo "11. Removing Solana data..."
rm -rf ~/.local/share/solana 2>/dev/null || true
echo "   ✓ Solana removed"

# 12. Clean HuggingFace cache (WARNING: models will need re-download)
echo ""
echo "12. Cleaning HuggingFace cache (models will need re-download)..."
rm -rf ~/.cache/huggingface/* 2>/dev/null || true
echo "   ✓ HuggingFace cache cleaned"

# 13. Delete old zip files in Downloads (older than 30 days)
echo ""
echo "13. Deleting old zip files (older than 30 days)..."
find ~/Downloads -type f -name "*.zip" -mtime +30 -not -name "jp62-orin-nano-sd-card-image.zip" -not -name "isaac-sim-standalone*.zip" -delete 2>/dev/null || true
echo "   ✓ Old zip files removed"

# Check disk space after
echo ""
echo "=========================================="
AFTER=$(df -h / | tail -1 | awk '{print $3 " used, " $4 " free"}')
echo "After: $AFTER"
echo "=========================================="

