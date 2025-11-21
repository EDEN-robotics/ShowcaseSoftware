# Fixing NVIDIA Drivers with Secure Boot Enabled

## Problem
- NVIDIA drivers are installed (version 575)
- Secure Boot is enabled
- NVIDIA kernel modules cannot load because they're unsigned
- Result: `nvidia-smi` fails

## Solution Options

### Option 1: Disable Secure Boot (Recommended - Easiest)

1. **Reboot and enter BIOS/UEFI**
   - Press F2, F10, Del, or Esc during boot (varies by manufacturer)
   - For Lenovo Yoga: Usually F2 or F12

2. **Find Secure Boot setting**
   - Look in "Security" or "Boot" menu
   - Find "Secure Boot" option

3. **Disable Secure Boot**
   - Set to "Disabled"
   - Save changes (usually F10)

4. **Reboot**
   - After reboot, NVIDIA modules should load automatically

5. **Verify**
   ```bash
   nvidia-smi
   python3 -c 'import torch; print(torch.cuda.is_available())'
   ```

### Option 2: Sign NVIDIA Modules (Keeps Secure Boot Enabled)

This is more complex but keeps Secure Boot enabled:

```bash
# Install required tools
sudo apt install mokutil

# Create signing key (if not exists)
sudo openssl req -new -x509 -newkey rsa:2048 -keyout MOK.priv -outform DER -out MOK.der -nodes -days 36500 -subj "/CN=Local Signing Key"

# Sign the modules
sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 ./MOK.priv ./MOK.der $(modinfo -n nvidia)
sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 ./MOK.priv ./MOK.der $(modinfo -n nvidia_uvm)
sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 ./MOK.priv ./MOK.der $(modinfo -n nvidia_drm)

# Enroll key in MOK
sudo mokutil --import MOK.der

# Reboot - you'll see MOK Manager screen
# Choose "Enroll MOK" → "Continue" → "Yes" → Enter password → Reboot
```

**Note**: Option 1 is much simpler and recommended for development.

## After Fixing

Once `nvidia-smi` works:

```bash
# Install vLLM
pip install vllm==0.9.2

# Verify CUDA in PyTorch
python3 -c 'import torch; print("CUDA available:", torch.cuda.is_available())'

# Restart planning layer
lsof -ti :8001 | xargs kill -9
python3 -m planning_layer.planning_server
```

The planning layer will automatically detect Cosmos and use it instead of Ollama.

