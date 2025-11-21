#!/bin/bash
# Fix GPU Setup for Cosmos

echo "=========================================="
echo "  GPU Setup Fix for RTX 4050"
echo "=========================================="
echo ""

# Check current status
echo "Current status:"
if nvidia-smi > /dev/null 2>&1; then
    echo "✓ NVIDIA drivers working"
    nvidia-smi --query-gpu=name,driver_version --format=csv
else
    echo "✗ NVIDIA drivers not working"
fi

echo ""
echo "Step 1: Install NVIDIA drivers (if needed)"
read -p "Install NVIDIA drivers? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt update
    sudo apt install -y nvidia-driver-535
    echo ""
    echo "✓ Drivers installed. REBOOT REQUIRED!"
    echo "Run: sudo reboot"
    echo "Then run this script again to continue setup."
    exit 0
fi

echo ""
echo "Step 2: Check if CUDA works after reboot"
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>&1

if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    echo "✓ CUDA is working!"
    
    echo ""
    echo "Step 3: Install vLLM"
    read -p "Install vLLM? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install vllm==0.9.2
        echo ""
        echo "✓ vLLM installed"
    fi
    
    echo ""
    echo "Step 4: Restart planning layer"
    echo "Kill old process: lsof -ti :8001 | xargs kill -9"
    echo "Start fresh: python3 -m planning_layer.planning_server"
    
else
    echo ""
    echo "✗ CUDA still not available"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure you rebooted after installing drivers"
    echo "2. Check: nvidia-smi (should show GPU info)"
    echo "3. Check: lsmod | grep nvidia (should show modules)"
    echo "4. Try: sudo modprobe nvidia"
fi

echo ""
echo "=========================================="



