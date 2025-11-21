#!/bin/bash
# Upgrade Ollama Model for Better Planning

echo "=========================================="
echo "  Upgrade Ollama Model for Planning"
echo "=========================================="
echo ""

echo "Current model: llama3"
echo ""
echo "Recommended models for physics reasoning (best to good):"
echo "1. llama3.1:8b - Better reasoning than llama3 (recommended)"
echo "2. qwen2.5:7b - Excellent reasoning, smaller size"
echo "3. mistral:7b - Good balance"
echo "4. deepseek-r1:7b - Best reasoning (if available)"
echo ""

read -p "Which model to download? (1-4, or 'skip' to keep llama3): " choice

case $choice in
    1)
        MODEL="llama3.1"
        echo "Downloading llama3.1..."
        ollama pull llama3.1
        ;;
    2)
        MODEL="qwen2.5"
        echo "Downloading qwen2.5..."
        ollama pull qwen2.5
        ;;
    3)
        MODEL="mistral"
        echo "Downloading mistral..."
        ollama pull mistral
        ;;
    4)
        MODEL="deepseek-r1"
        echo "Downloading deepseek-r1..."
        ollama pull deepseek-r1 || echo "Model not available, try another"
        ;;
    skip|"")
        echo "Keeping llama3"
        MODEL="llama3"
        ;;
    *)
        echo "Invalid choice, keeping llama3"
        MODEL="llama3"
        ;;
esac

if [ "$MODEL" != "llama3" ]; then
    echo ""
    echo "✓ Model downloaded: $MODEL"
    echo ""
    echo "Updating config..."
    # Update config.py
    sed -i "s/OLLAMA_MODEL = \".*\"/OLLAMA_MODEL = \"$MODEL\"/" planning_layer/config.py
    echo "✓ Config updated to use $MODEL"
    echo ""
    echo "Restart planning layer to use new model:"
    echo "  lsof -ti :8001 | xargs kill -9"
    echo "  python3 -m planning_layer.planning_server"
else
    echo ""
    echo "Using llama3 (no changes needed)"
fi

echo ""
echo "=========================================="

