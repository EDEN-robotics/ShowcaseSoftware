#!/bin/bash
# GPU Setup Checker for Cosmos

echo "=========================================="
echo "  GPU Setup Checker"
echo "=========================================="
echo ""

echo "1. Checking GPU Hardware..."
if lspci | grep -i nvidia > /dev/null; then
    echo "   ✓ NVIDIA GPU detected"
    lspci | grep -i nvidia
else
    echo "   ✗ No NVIDIA GPU found"
fi

echo ""
echo "2. Checking NVIDIA Drivers..."
if command -v nvidia-smi > /dev/null; then
    echo "   ✓ nvidia-smi found"
    nvidia-smi 2>&1 | head -5
else
    echo "   ✗ nvidia-smi not found"
    echo "   → Install NVIDIA drivers: sudo apt install nvidia-driver-535"
fi

echo ""
echo "3. Checking CUDA..."
if command -v nvcc > /dev/null; then
    echo "   ✓ CUDA compiler found"
    nvcc --version | head -3
else
    echo "   ✗ CUDA compiler not found"
    echo "   → Install CUDA toolkit if needed"
fi

echo ""
echo "4. Checking PyTorch CUDA Support..."
python3 << EOF
import torch
print(f"   PyTorch version: {torch.__version__}")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA version: {torch.version.cuda}")
    print(f"   GPU count: {torch.cuda.device_count()}")
    print(f"   GPU name: {torch.cuda.get_device_name(0)}")
else:
    print("   ✗ CUDA not available in PyTorch")
    print("   → Install PyTorch with CUDA:")
    print("     pip install torch --index-url https://download.pytorch.org/whl/cu121")
EOF

echo ""
echo "5. Checking vLLM..."
python3 << EOF
try:
    import vllm
    print(f"   ✓ vLLM installed: {vllm.__version__}")
except ImportError:
    print("   ✗ vLLM not installed")
    print("   → Install: pip install vllm==0.9.2")
EOF

echo ""
echo "=========================================="
echo "  Summary"
echo "=========================================="
echo ""
echo "If GPU is detected but CUDA unavailable:"
echo "  1. Install NVIDIA drivers: sudo apt install nvidia-driver-535"
echo "  2. Reboot: sudo reboot"
echo "  3. Install PyTorch with CUDA: pip install torch --index-url https://download.pytorch.org/whl/cu121"
echo "  4. Verify: python3 -c 'import torch; print(torch.cuda.is_available())'"
echo ""



