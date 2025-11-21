#!/bin/bash
# Start script that suppresses GPU warnings but keeps GPU enabled for WebGL

# Suppress libva and OpenGL warnings (redirect stderr)
export LIBVA_DRIVER_NAME=i965 2>/dev/null
export MESA_GL_VERSION_OVERRIDE=3.3 2>/dev/null

# Start Electron - keep GPU enabled for WebGL, only disable sandbox
exec electron . --disable-gpu-sandbox "$@" 2>/dev/null

