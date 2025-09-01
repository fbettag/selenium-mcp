FROM python:3.13-alpine

# Install system dependencies
RUN apk add --no-cache \
    curl \
    build-base

# Install UV for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Install Python dependencies with UV
RUN uv sync --frozen --no-dev

# Copy source code
COPY server.py ./

# Create non-root user
RUN adduser -D -u 1000 appuser

# Change ownership of the app directory to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV BROWSERLESS_URL=http://browserless:3000
ENV BROWSERLESS_TOKEN=
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose MCP server port
EXPOSE 8000

# Run the MCP server directly with Python
CMD ["python", "server.py"]