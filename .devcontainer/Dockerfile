FROM mcr.microsoft.com/devcontainers/python:1-3.13

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.cargo/bin/uv /usr/local/bin/uv

# Install additional tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Set working directory
WORKDIR /workspace

# Copy package files
COPY pyproject.toml ./
COPY requirements.txt ./
COPY uv.lock ./

# Install dependencies with UV
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set permissions
RUN chown -R $USERNAME:$USERNAME /workspace

USER $USERNAME

# Set environment variables
ENV BROWSERLESS_TOKEN=
ENV PYTHONPATH=/workspace/src
ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON=/usr/local/bin/python

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1