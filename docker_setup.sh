#!/bin/bash

# Docker Setup Script for Container Environment
echo "🐳 Setting up Docker in container environment..."

# Create docker group if it doesn't exist
sudo groupadd docker 2>/dev/null || true

# Add current user to docker group
sudo usermod -aG docker $USER

# Create docker socket directory
sudo mkdir -p /var/run
sudo chmod 666 /var/run 2>/dev/null || true

# Start Docker daemon with proper permissions
echo "🚀 Starting Docker daemon..."
sudo dockerd \
    --host=unix:///var/run/docker.sock \
    --host=tcp://0.0.0.0:2375 \
    --storage-driver=vfs \
    --iptables=false \
    --bridge=none \
    --exec-opt native.cgroupdriver=cgroupfs \
    > /tmp/docker.log 2>&1 &

# Wait for Docker to start
echo "⏳ Waiting for Docker to initialize..."
for i in {1..30}; do
    if sudo docker version > /dev/null 2>&1; then
        echo "✅ Docker is running!"
        sudo docker version
        break
    fi
    sleep 1
    echo -n "."
done

# Test Docker functionality
echo ""
echo "🧪 Testing Docker functionality..."
if sudo docker run --rm hello-world > /dev/null 2>&1; then
    echo "✅ Docker is fully functional!"
else
    echo "⚠️  Docker started but may have limitations in this environment"
fi

echo ""
echo "💡 Note: In this container environment, you may need to use 'sudo docker' for commands"
echo "📝 Docker logs available at: /tmp/docker.log"