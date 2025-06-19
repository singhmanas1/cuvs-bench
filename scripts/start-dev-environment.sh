#!/bin/bash

# Configuration
IMAGE_NAME="nvidia/cuda:12.8.1-devel-ubuntu22.04"
CONTAINER_DIR="/myworkspace"

# Function to check prerequisites
check_prerequisites() {
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then 
        echo "Please run as root (use sudo)"
        exit 1
    fi

    # Check for Docker
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed"
        echo "Please install Docker first: https://docs.docker.com/engine/install/"
        exit 1
    fi

    # Check for NVIDIA drivers and toolkit
    if ! command -v nvidia-smi &> /dev/null; then
        echo "Error: NVIDIA drivers not found"
        echo "Please install NVIDIA drivers and Container Toolkit"
        exit 1
    fi
}

# Main execution
echo "Setting up cuVS development environment..."

# Run checks
check_prerequisites

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_DIR="${REPO_ROOT}"

echo "Starting development container..."
echo "Mounting: ${HOST_DIR} -> ${CONTAINER_DIR}"

# Pull the latest image
docker pull ${IMAGE_NAME}

# Start the container
docker run -it --rm \
    --net=host \
    --gpus all \
    -u root \
    -v "${HOST_DIR}:${CONTAINER_DIR}" \
    -w "${CONTAINER_DIR}" \
    --entrypoint bash \
    "${IMAGE_NAME}" 