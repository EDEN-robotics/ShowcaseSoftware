#!/bin/bash
# Check Disk Space and Find Large Files

echo "=========================================="
echo "  Disk Space Checker"
echo "=========================================="
echo ""

echo "Overall Disk Usage:"
df -h | grep -E "Filesystem|/$"

echo ""
echo "Root filesystem details:"
df -h / | tail -1

echo ""
echo "=========================================="
echo "  Large Directories (Top 10)"
echo "=========================================="
echo ""

echo "System directories:"
sudo du -h --max-depth=1 / 2>/dev/null | sort -hr | head -10

echo ""
echo "Your home directory:"
du -h --max-depth=1 ~ 2>/dev/null | sort -hr | head -10

echo ""
echo "=========================================="
echo "  Common Space Hogs"
echo "=========================================="
echo ""

echo "Docker (if installed):"
sudo du -sh /var/lib/docker 2>/dev/null || echo "Docker not found"

echo ""
echo "Snap packages:"
sudo du -sh /var/lib/snapd 2>/dev/null || echo "Snap not found"

echo ""
echo "APT cache:"
sudo du -sh /var/cache/apt 2>/dev/null || echo "APT cache not found"

echo ""
echo "Log files:"
sudo du -sh /var/log 2>/dev/null || echo "Logs not found"

echo ""
echo "Ollama models:"
du -sh ~/.ollama/models 2>/dev/null || echo "Ollama models not found"

echo ""
echo "=========================================="
echo "  Quick Cleanup Commands"
echo "=========================================="
echo ""
echo "Clean APT cache:"
echo "  sudo apt clean"
echo ""
echo "Remove old kernels:"
echo "  sudo apt autoremove"
echo ""
echo "Clean snap packages:"
echo "  sudo snap list --all | awk '/disabled/{print \$1, \$3}' | while read snapname revision; do sudo snap remove \"\$snapname\" --revision=\"\$revision\"; done"
echo ""
echo "Find large files (>100MB):"
echo "  sudo find / -type f -size +100M 2>/dev/null | head -20"
echo ""

