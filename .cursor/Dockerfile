FROM ubuntu:22.04

# Install development tools and dependencies as needed
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    # add other tools you need
    && rm -rf /var/lib/apt/lists/*

# Set a non-root user (recommended for dev environments)
RUN useradd -ms /bin/bash ubuntu
USER ubuntu

# Set the working directory to the user's home
WORKDIR /home/ubuntu
