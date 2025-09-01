# DevContainer Setup

This project includes a development container configuration for VS Code that provides a complete development environment with:

- **Python 3.13** with UV package manager
- **Browserless** service for testing
- **Pre-configured VS Code** with Python, Ruff, Black, and Docker extensions
- **Automatic dependency installation** on container creation

## Quick Start

1. **Open in VS Code**: Open the project folder in VS Code
2. **Reopen in Container**: Click "Reopen in Container" when prompted, or use the command palette (Ctrl+Shift+P / Cmd+Shift+P) and search for "Reopen in Container"
3. **Wait for setup**: The container will build and install all dependencies automatically

## Features

- **Pre-installed extensions**: Python, Pylance, Ruff, Black, Docker, GitHub Actions
- **Browserless integration**: Browserless service runs alongside the dev container
- **UV package management**: Fast dependency installation and management
- **Formatting & linting**: Automatic code formatting with Black and linting with Ruff
- **Testing environment**: Complete setup for running tests with browserless

## Environment Variables

The dev container automatically sets:

- `BROWSERLESS_URL=http://browserless:3000`
- `PYTHONPATH=/workspace/src`
- `PYTHONUNBUFFERED=1`

## Usage

Once the dev container is running:

```bash
# Run the MCP server
uv run selenium-mcp

# Run tests
uv run pytest -v

# Format code
uv run black src/

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/
```

## Browserless Service

The dev container includes a browserless service running on port 3000. You can access it at:

- **Health check**: http://localhost:3000/health
- **WebDriver**: http://localhost:3000/webdriver

## Manual Setup (without dev container)

If you prefer to develop outside the dev container:

```bash
# Create virtual environment
uv venv .venv

# Activate (Unix/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\\Scripts\\activate

# Install dependencies
uv sync --all-extras --dev

# Start browserless for testing
docker run -p 3000:3000 browserless/chrome:latest

# Run server
BROWSERLESS_URL=http://localhost:3000 uv run selenium-mcp
```

## Troubleshooting

### Container build issues

- Ensure Docker is running and you have sufficient resources
- Check that ports 3000 (browserless) are available

### Browserless connection issues

- Verify browserless is running: `curl http://localhost:3000/health`
- Check environment variable: `echo $BROWSERLESS_URL`

### Dependency issues

- Rebuild container: Reopen in Container
- Manual fix: `uv sync --all-extras --dev`