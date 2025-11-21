#!/bin/bash
# Check NVIDIA Driver Status

echo "=========================================="
echo "  NVIDIA Driver Status Check"
echo "=========================================="
echo ""

echo "1. Hardware Detection:"
if lspci | grep -i nvidia > /dev/null; then
    echo "   ✓ GPU detected:"
    lspci | grep -i nvidia
else
    echo "   ✗ No NVIDIA GPU found"
fi

echo ""
echo "2. Driver Installation:"
if dpkg -l | grep -i "nvidia-driver" > /dev/null; then
    echo "   ✓ NVIDIA drivers installed:"
    dpkg -l | grep -i "nvidia-driver" | head -3
else
    echo "   ✗ No NVIDIA drivers installed"
fi

echo ""
echo "3. Kernel Modules:"
if lsmod | grep nvidia > /dev/null; then
    echo "   ✓ NVIDIA modules loaded:"
    lsmod | grep nvidia | head -3
else
    echo "   ✗ NVIDIA modules NOT loaded"
    echo "   → This usually means you need to reboot"
fi

echo ""
echo "4. nvidia-smi Test:"
if command -v nvidia-smi > /dev/null; then
    if nvidia-smi > /dev/null 2>&1; then
        echo "   ✓ nvidia-smi working:"
        nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
    else
        echo "   ✗ nvidia-smi failed"
        echo "   → Check dmesg: sudo dmesg | grep -i nvidia | tail -5"
    fi
else
    echo "   ✗ nvidia-smi not found"
fi

echo ""
echo "5. Secure Boot Status:"
if command -v mokutil > /dev/null; then
    SB_STATE=$(mokutil --sb-state 2>/dev/null || echo "unknown")
    echo "   Secure Boot: $SB_STATE"
    if echo "$SB_STATE" | grep -i "enabled" > /dev/null; then
        echo "   ⚠️  Secure Boot is enabled - NVIDIA drivers may need signing"
    fi
else
    echo "   (mokutil not available)"
fi

echo ""
echo "=========================================="
echo "  Recommendations"
echo "=========================================="
echo ""

if ! lsmod | grep nvidia > /dev/null; then
    echo "→ REBOOT REQUIRED: sudo reboot"
    echo ""
fi

if ! command -v nvidia-smi > /dev/null || ! nvidia-smi > /dev/null 2>&1; then
    echo "→ Install drivers: sudo ./fix_nvidia_drivers.sh"
    echo "→ Or manually: sudo apt install nvidia-driver-535"
    echo ""
fi

echo "After fixing, verify with:"
echo "  nvidia-smi"
echo "  python3 -c 'import torch; print(torch.cuda.is_available())'"
echo ""

