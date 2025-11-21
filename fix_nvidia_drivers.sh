#!/bin/bash
# Comprehensive NVIDIA Driver Fix for RTX 4050

set -e

echo "=========================================="
echo "  NVIDIA Driver Fix for RTX 4050"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "This script needs sudo privileges."
    echo "Run: sudo ./fix_nvidia_drivers.sh"
    exit 1
fi

echo "Step 1: Removing old/conflicting NVIDIA packages..."
apt-get remove --purge -y '^nvidia-.*' '^libnvidia-.*' 2>/dev/null || true
apt-get autoremove -y

echo ""
echo "Step 2: Adding NVIDIA PPA (for latest drivers)..."
add-apt-repository -y ppa:graphics-drivers/ppa 2>/dev/null || true
apt-get update

echo ""
echo "Step 3: Detecting recommended driver version..."
RECOMMENDED=$(ubuntu-drivers devices 2>/dev/null | grep "recommended" | awk '{print $3}' | head -1)
if [ -z "$RECOMMENDED" ]; then
    RECOMMENDED="535"
    echo "   Using default: nvidia-driver-535"
else
    echo "   Recommended: nvidia-driver-$RECOMMENDED"
fi

echo ""
echo "Step 4: Installing NVIDIA drivers..."
apt-get install -y nvidia-driver-$RECOMMENDED

echo ""
echo "Step 5: Installing additional packages..."
apt-get install -y nvidia-utils-$RECOMMENDED nvidia-settings

echo ""
echo "Step 6: Blacklisting nouveau (open-source driver)..."
cat > /etc/modprobe.d/blacklist-nouveau.conf << EOF
blacklist nouveau
options nouveau modeset=0
EOF

echo ""
echo "Step 7: Updating initramfs..."
update-initramfs -u

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: You MUST reboot for changes to take effect:"
echo "  sudo reboot"
echo ""
echo "After reboot, verify with:"
echo "  nvidia-smi"
echo ""

