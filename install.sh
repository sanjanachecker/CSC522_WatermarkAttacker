#!/bin/bash

# Installation script for WatermarkAttacker dependencies
# This script handles the compressai build issue on macOS

set -e

echo "Installing WatermarkAttacker dependencies..."

# Check if we have a C++ compiler available
HAS_COMPILER=false
if command -v clang++ &> /dev/null; then
    # Test if clang++ supports C++11
    if clang++ -std=c++11 -x c++ - -o /dev/null <<< "" &> /dev/null 2>&1; then
        HAS_COMPILER=true
    fi
fi

# Check Xcode command line tools status
XCODE_TOOLS_INSTALLED=false
if xcode-select -p &> /dev/null; then
    XCODE_TOOLS_INSTALLED=true
fi

if [ "$HAS_COMPILER" = false ] && [ "$XCODE_TOOLS_INSTALLED" = false ]; then
    echo "⚠️  Xcode Command Line Tools not found or installation in progress!"
    echo ""
    echo "📋 NEXT STEPS:"
    echo ""
    echo "If you just ran 'xcode-select --install':"
    echo "  1. Look for a dialog window that appeared - click 'Install'"
    echo "  2. Wait for the installation to complete (this may take 10-15 minutes)"
    echo "  3. Accept the license agreement if prompted"
    echo "  4. Verify installation: xcode-select -p"
    echo "  5. Run this script again: ./install.sh"
    echo ""
    echo "If no dialog appeared or installation seems stuck:"
    echo "  - Check System Preferences > Software Update"
    echo "  - Download manually from: https://developer.apple.com/download/all/"
    echo "  - Or try: sudo xcode-select --reset"
    echo ""
    echo "💡 While waiting, you can install other dependencies (except compressai):"
    echo "   pip install transformers diffusers torch torchvision opencv-python invisible-watermark scikit-image matplotlib bm3d torch_fidelity accelerate onnxruntime"
    echo ""
    exit 1
fi

if [ "$HAS_COMPILER" = true ]; then
    echo "✓ C++ compiler found (clang++)"
elif [ "$XCODE_TOOLS_INSTALLED" = true ]; then
    echo "✓ Xcode Command Line Tools found"
else
    echo "⚠️  Warning: Compiler status unclear, but proceeding..."
fi

# Set compiler environment variables for C++11 support
export CC=clang
export CXX=clang++
export CXXFLAGS="-std=c++11 -stdlib=libc++"
export LDFLAGS="-stdlib=libc++"

# Try to install compressai first (the problematic package)
echo ""
echo "Installing compressai (this may take a few minutes)..."
pip install compressai --no-cache-dir || {
    echo ""
    echo "⚠️  Failed to install compressai from source."
    echo "Trying alternative installation methods..."
    
    # Try installing with explicit C++11 flags
    pip install compressai --no-cache-dir --no-build-isolation \
        --global-option="build_ext" \
        --global-option="--compiler=unix" || {
        echo ""
        echo "❌ Still failed. Trying to install from pre-built wheel..."
        pip install compressai --only-binary :all: || {
            echo ""
            echo "❌ Could not install compressai."
            echo "Please ensure:"
            echo "1. Xcode Command Line Tools are installed: xcode-select --install"
            echo "2. You have a C++ compiler with C++11 support"
            echo "3. Try: pip install --upgrade pip setuptools wheel"
            exit 1
        }
    }
}

echo "✓ compressai installed successfully"

# Install remaining dependencies
echo ""
echo "Installing remaining dependencies..."
pip install -r requirements.txt --no-cache-dir

echo ""
echo "✅ All dependencies installed successfully!"
