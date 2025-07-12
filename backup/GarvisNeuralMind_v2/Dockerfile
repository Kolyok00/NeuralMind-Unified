# GarvisNeuralMind AI System Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development environment
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Copy source code
COPY . .

# Expose development port
EXPOSE 8000

# Development command
CMD ["python", "src/main.py", "--dev"]

# Stage 3: Production environment
FROM base as production

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose production port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Production command
CMD ["python", "src/main.py", "--production"]

# Stage 4: GPU-enabled environment (for AI model inference)
FROM base as gpu

# Install CUDA dependencies (if needed)
# RUN apt-get update && apt-get install -y nvidia-cuda-toolkit

# Copy source code
COPY . .

# Install GPU-specific dependencies
RUN pip install --no-cache-dir \
    torch \
    transformers \
    accelerate

# Expose GPU port
EXPOSE 8000

# GPU command
CMD ["python", "src/main.py", "--gpu"] 