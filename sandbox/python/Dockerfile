FROM python:3.11-slim

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
