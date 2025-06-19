#!/bin/bash

# Exit on any error
set -e

echo "Setting up development environment..."

# Update package list
echo "Updating package list..."
apt update

# Install NCCL
echo "Installing NCCL..."
apt install -y libnccl2 libnccl-dev --allow-change-held-packages

# Install system dependencies
echo "Installing system dependencies..."
apt install -y \
    htop \
    nvtop \
    wget \
    git \
    pip \
    nano \
    ninja-build \
    maven \
    curl \
    zip \
    httpie \
    lsof \
    --allow-change-held-packages

# Install Java
echo "Installing Java..."
wget -nc https://download.oracle.com/java/22/archive/jdk-22.0.2_linux-x64_bin.deb
dpkg -i jdk-22.0.2_linux-x64_bin.deb
export JAVA_HOME=/usr/lib/jvm/jdk-22.0.2-oracle-x64
echo "export JAVA_HOME=/usr/lib/jvm/jdk-22.0.2-oracle-x64" >> ~/.bashrc

# Install basic Python packages
echo "Installing basic Python packages..."
pip install \
    cmake==3.30.4 \
    jpype1 \
    numpy \
    pandas \
    jupyterlab \
    tqdm \
    requests

# Install NVIDIA RAPIDS packages
echo "Installing NVIDIA RAPIDS packages..."
pip install \
    --extra-index-url=https://pypi.nvidia.com \
    "cudf-cu12==25.6.*" \
    "cuvs-cu12==25.6.*" \
    "rmm-cu12==25.6.*" \
    "pylibraft-cu12==25.6.*" \
    "cupy-cuda12x"

# Print setup completion message
echo "Development environment setup complete!"
echo "To start Jupyter Lab, run: jupyter lab --allow-root --ip 0.0.0.0 --no-browser" 