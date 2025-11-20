#!/bin/bash

# EDEN Planning Layer Setup Script
# Installs vLLM and dependencies for NVIDIA Cosmos Reason1-7B

set -e

echo "=== EDEN Planning Layer Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check CUDA availability
echo ""
echo "Checking CUDA availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    CUDA_AVAILABLE=true
else
    echo "Warning: nvidia-smi not found. GPU may not be available."
    CUDA_AVAILABLE=false
fi

# Detect CUDA version
if [ "$CUDA_AVAILABLE" = true ]; then
    CUDA_VERSION=$(nvcc --version 2>/dev/null | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
    if [ -z "$CUDA_VERSION" ]; then
        echo "Warning: Could not detect CUDA version"
    else
        echo "Detected CUDA version: $CUDA_VERSION"
    fi
fi

# Install PyTorch (CUDA 12.1 compatible)
echo ""
echo "Installing PyTorch with CUDA support..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --user

# Install vLLM (pinned version)
echo ""
echo "Installing vLLM==0.9.2..."
echo "Note: This may take several minutes..."
pip3 install vllm==0.9.2 --user

# Install quantization support
echo ""
echo "Installing autoawq for quantization..."
pip3 install autoawq --user

# Install HuggingFace Hub
echo ""
echo "Installing HuggingFace Hub..."
pip3 install huggingface_hub --user

# Verify installations
echo ""
echo "Verifying installations..."
python3 -c "import vllm; print(f'✓ vllm version: {vllm.__version__}')" || echo "✗ vllm installation failed"
python3 -c "import torch; print(f'✓ PyTorch version: {torch.__version__}')" || echo "✗ PyTorch installation failed"
python3 -c "import torch; print(f'✓ CUDA available: {torch.cuda.is_available()}')" || echo "✗ CUDA check failed"

# Model download instructions
echo ""
echo "=== Model Download Instructions ==="
echo ""
echo "IMPORTANT: Download the model BEFORE the showcase (Wi-Fi may be slow)"
echo ""
echo "Run this command to download the model:"
echo "  huggingface-cli download nvidia/Cosmos-Reason1-7B --local-dir ./models/cosmos-reason1-7b"
echo ""
echo "Or use Python:"
echo "  python3 -c \"from huggingface_hub import snapshot_download; snapshot_download('nvidia/Cosmos-Reason1-7B', local_dir='./models/cosmos-reason1-7b')\""
echo ""
echo "The model is ~15GB, so ensure you have enough disk space."
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Download the model (see instructions above)"
echo "2. Test GPU: python3 -c \"import torch; print(torch.cuda.is_available())\""
echo "3. Start planning server: python3 -m planning_layer.planning_server"

