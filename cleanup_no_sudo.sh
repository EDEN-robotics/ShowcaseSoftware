#!/bin/bash
# Cleanup without sudo (user files only)

set -e

echo "=========================================="
echo "  Disk Cleanup (No Sudo Required)"
echo "=========================================="
echo ""

BEFORE=$(df -h / | tail -1 | awk '{print $3 " used, " $4 " free"}')
echo "Before: $BEFORE"
echo ""

FREED=0

# 1. Delete old installers in Downloads
echo "1. Deleting old installers (.deb files)..."
DEB_SIZE=$(du -sb ~/Downloads/*.deb 2>/dev/null | awk '{sum+=$1} END {print sum/1024/1024}' || echo "0")
rm -f ~/Downloads/*.deb 2>/dev/null || true
if [ "$DEB_SIZE" != "0" ]; then
    echo "   ✓ Removed ~${DEB_SIZE}MB of installers"
    FREED=$((FREED + ${DEB_SIZE%.*}))
fi

# 2. Delete old Discord installers
echo ""
echo "2. Deleting old Discord installers..."
rm -f ~/Downloads/discord-*.deb 2>/dev/null || true
echo "   ✓ Discord installers removed"

# 3. Delete Warp installer
echo ""
echo "3. Deleting Warp installer..."
rm -f ~/Downloads/warp-terminal*.deb 2>/dev/null || true
echo "   ✓ Warp installer removed"

# 4. Delete BalenaEtcher installer
echo ""
echo "4. Deleting BalenaEtcher installer..."
rm -f ~/Downloads/balenaEtcher*.zip 2>/dev/null || true
echo "   ✓ BalenaEtcher installer removed"

# 5. Delete older SD card image (keep newest jp62)
echo ""
echo "5. Deleting older SD card image (keeping jp62)..."
if [ -f ~/Downloads/jp60-orin-nano-sd-card-image.zip ]; then
    rm -f ~/Downloads/jp60-orin-nano-sd-card-image.zip
    echo "   ✓ Deleted jp60 SD card image (~12GB)"
    FREED=$((FREED + 12288))
fi

# 6. Clean Chrome cache
echo ""
echo "6. Cleaning Chrome cache..."
CHROME_SIZE=$(du -sb ~/.cache/google-chrome 2>/dev/null | awk '{print $1/1024/1024}' || echo "0")
rm -rf ~/.cache/google-chrome/* 2>/dev/null || true
if [ "$CHROME_SIZE" != "0" ]; then
    echo "   ✓ Cleaned Chrome cache (~${CHROME_SIZE%.*}MB)"
    FREED=$((FREED + ${CHROME_SIZE%.*}))
fi

# 7. Clean Solana
echo ""
echo "7. Removing Solana data..."
SOLANA_SIZE=$(du -sb ~/.local/share/solana 2>/dev/null | awk '{print $1/1024/1024}' || echo "0")
rm -rf ~/.local/share/solana 2>/dev/null || true
if [ "$SOLANA_SIZE" != "0" ]; then
    echo "   ✓ Removed Solana (~${SOLANA_SIZE%.*}MB)"
    FREED=$((FREED + ${SOLANA_SIZE%.*}))
fi

# 8. Clean HuggingFace cache
echo ""
echo "8. Cleaning HuggingFace cache..."
HF_SIZE=$(du -sb ~/.cache/huggingface 2>/dev/null | awk '{print $1/1024/1024}' || echo "0")
rm -rf ~/.cache/huggingface/* 2>/dev/null || true
if [ "$HF_SIZE" != "0" ]; then
    echo "   ✓ Cleaned HuggingFace cache (~${HF_SIZE%.*}MB)"
    FREED=$((FREED + ${HF_SIZE%.*}))
fi

# 9. Clean pip cache
echo ""
echo "9. Cleaning pip cache..."
PIP_SIZE=$(du -sb ~/.cache/pip 2>/dev/null | awk '{print $1/1024/1024}' || echo "0")
pip cache purge 2>/dev/null || true
if [ "$PIP_SIZE" != "0" ]; then
    echo "   ✓ Cleaned pip cache (~${PIP_SIZE%.*}MB)"
    FREED=$((FREED + ${PIP_SIZE%.*}))
fi

# 10. Delete old zip files (keep important ones)
echo ""
echo "10. Deleting old zip files (keeping robotics ones)..."
find ~/Downloads -type f -name "*.zip" -mtime +30 -not -name "jp62-orin-nano-sd-card-image.zip" -not -name "isaac-sim-standalone*.zip" -delete 2>/dev/null || true
echo "   ✓ Old zip files removed"

# Check disk space after
echo ""
echo "=========================================="
AFTER=$(df -h / | tail -1 | awk '{print $3 " used, " $4 " free"}')
echo "After: $AFTER"
echo ""
echo "Estimated freed: ~$((FREED/1024))GB"
echo "=========================================="
echo ""
echo "For system cleanup (APT cache, old packages, Warp uninstall), run:"
echo "  sudo apt clean && sudo apt autoremove -y && sudo apt remove --purge warp-terminal"

