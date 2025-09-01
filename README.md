# Selenium MCP Server

A Model Context Protocol (MCP) server that provides browser automation capabilities using Selenium WebDriver connected to a browserless service. This server runs without local browsers, connecting to browserless via TCP for scalable, containerized deployments.

## Features

- **Browser Automation**: Navigate to URLs, interact with elements, execute JavaScript
- **Browserless Integration**: Connects to browserless service via WebDriver protocol
- **Async Python**: Built with FastMCP for high-performance async operations
- **Container Ready**: Alpine-based Docker image with no local browsers
- **Session Management**: Automatic session handling per MCP context

## Quick Start

### Prerequisites

- Python 3.13+
- Browserless service running (local or remote)
- UV package manager (recommended)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd selenium-mcp-server

# Install with UV
uv sync

# Or with pip
pip install -e .
```

### Environment Setup

Set the browserless service URL and optional authentication token:

```bash
export BROWSERLESS_URL=http://localhost:3000  # Local browserless
export BROWSERLESS_URL=http://browserless:3000  # Kubernetes service

# Optional: Set authentication token if browserless requires it
export BROWSERLESS_TOKEN=your-bearer-token-here
```

### Run the Server

```bash
# With UV
uv run selenium-mcp

# Or directly
python -m selenium_mcp.server
```

## Claude Desktop Setup

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "selenium": {
      "command": "uv",
      "args": ["run", "selenium-mcp"],
      "env": {
        "BROWSERLESS_URL": "http://localhost:3000",
        "BROWSERLESS_TOKEN": "your-bearer-token-here"
      }
    }
  }
}
```

## Available Tools

### Navigate to URL
```python
navigate_to_url({
  "url": "https://example.com"
})
```

### Find Element
```python
find_element({
  "selector": ".button-primary",
  "by": "css"  # css, xpath, id, name, class_name, tag_name, link_text, partial_link_text
})
```

### Click Element
```python
click_element({
  "selector": "#submit-button",
  "by": "id"
})
```

### Execute JavaScript
```python
execute_javascript({
  "script": "return document.title;"
})
```

### Take Screenshot
```python
take_screenshot({})
```

### Get Page Info
```python
get_page_info({})
```

### Close Browser
```python
close_browser({})
```

## Docker Deployment

### Build the Image

```bash
docker build -t selenium-mcp-server .
```

### Run with Docker Compose

```yaml
version: '3.8'
services:
  browserless:
    image: browserless/chrome:latest
    ports:
      - "3000:3000"
    environment:
      - CONNECTION_TIMEOUT=60000
      - MAX_CONCURRENT_SESSIONS=10

  selenium-mcp:
    image: selenium-mcp-server:latest
    environment:
      - BROWSERLESS_URL=http://browserless:3000
      - BROWSERLESS_TOKEN=${BROWSERLESS_TOKEN:-}
    ports:
      - "8000:8000"
    depends_on:
      - browserless
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: selenium-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: selenium-mcp
  template:
    metadata:
      labels:
        app: selenium-mcp
    spec:
      containers:
      - name: selenium-mcp
        image: selenium-mcp-server:latest
        env:
        - name: BROWSERLESS_URL
          value: "http://browserless-service:3000"
        - name: BROWSERLESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: browserless-secrets
              key: token
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"

---
apiVersion: v1
kind: Service
metadata:
  name: browserless-service
spec:
  selector:
    app: browserless
  ports:
  - port: 3000
    targetPort: 3000
```

## Development

### Virtual Environment

```bash
# Create virtual environment
uv venv .venv

# Activate on Unix/macOS
source .venv/bin/activate

# Activate on Windows
.venv\\Scripts\\activate

# Install dependencies
uv sync
```

### Testing

```bash
# Run tests
uv run pytest

# Start local browserless for testing
docker run -p 3000:3000 browserless/chrome:latest

# Test the server
BROWSERLESS_URL=http://localhost:3000 uv run selenium-mcp
```

### Linting and Formatting

```bash
# Format code
uv run black src/

# Lint code
uv run ruff check src/

# Type checking
uv run mypy src/
```

## GitHub CI/CD Pipeline

The repository includes a GitHub Actions workflow that:

1. **Tests**: Spins up browserless container and runs tests
2. **Builds**: Creates Docker image with UV
3. **Pushes**: Deploys to container registry on main branch

See `.github/workflows/ci.yml` for details.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BROWSERLESS_URL` | Browserless service URL | Required |
| `BROWSERLESS_TOKEN` | Optional bearer token for browserless authentication | Empty |
| `PYTHONPATH` | Python path for imports | `/app/src` |
| `PYTHONUNBUFFERED` | Unbuffered Python output | `1` |

## Browserless Configuration

This MCP server requires a browserless service. Recommended browserless configuration:

```bash
docker run -p 3000:3000 \
  -e CONNECTION_TIMEOUT=60000 \
  -e MAX_CONCURRENT_SESSIONS=10 \
  -e DEFAULT_BLOCK_ADS=true \
  browserless/chrome:latest
```

## Performance Considerations

- **Session Management**: Each MCP context gets its own browser session
- **Connection Pooling**: Browserless handles multiple concurrent sessions
- **Resource Limits**: Set appropriate memory/cpu limits in Kubernetes
- **Timeouts**: Configure browserless timeouts based on use case

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure browserless is running and accessible
2. **Authentication failed**: Check if `BROWSERLESS_TOKEN` is required and correctly set
3. **Session timeout**: Increase browserless timeout settings
4. **Element not found**: Use appropriate wait strategies in your scripts

### Logs

Enable debug logging by setting environment variables:

```bash
export LOG_LEVEL=DEBUG
export BROWSERLESS_DEBUG=true
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## Support

For issues and questions, please open a GitHub issue or check the browserless documentation.