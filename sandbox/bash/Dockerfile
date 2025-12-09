FROM ubuntu:22.04

# Install minimal bash utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 sandbox && \
    mkdir -p /workspace && \
    chown sandbox:sandbox /workspace

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER sandbox

# Default command
CMD ["/bin/bash"]
