# Selenium MCP Server Helm Chart

This Helm chart deploys the Selenium MCP Server to Kubernetes. The chart supports both deploying browserless alongside the MCP server or connecting to an existing browserless service.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.8+
- kubectl configured to access your cluster

## Installation

### Option 1: Install from GitHub Repository

You can install directly from the GitHub repository without publishing to a chart repository:

```bash
# Add the chart directly from GitHub
helm install selenium-mcp oci://ghcr.io/fbettag/selenium-mcp-chart

# Or install from local chart directory
helm install selenium-mcp ./charts/selenium-mcp/

# With custom values
helm install selenium-mcp ./charts/selenium-mcp/ -f my-values.yaml
```

### Option 2: Install with Browserless

If you want to deploy browserless alongside the MCP server:

```bash
# Create values file for browserless deployment
cat > values-with-browserless.yaml << EOF
browserless:
  enabled: true
  service:
    port: 3000

mcp:
  browserlessUrl: "http://selenium-mcp-browserless:3000"
EOF

# Install with browserless
helm install selenium-mcp ./charts/selenium-mcp/ -f values-with-browserless.yaml
```

### Option 3: Use Existing Browserless Service

If you already have browserless running:

```bash
# Create values file for existing browserless
cat > values-existing-browserless.yaml << EOF
browserless:
  enabled: false
  service:
    existingService: "my-existing-browserless"
    existingServiceNamespace: "browserless-namespace"
    port: 3000

mcp:
  browserlessUrl: "http://my-existing-browserless.browserless-namespace.svc.cluster.local:3000"
  # Optional: if browserless requires authentication
  browserlessToken: "your-bearer-token-here"
  # Or use a secret:
  # existingSecret: "browserless-secrets"
  # existingSecretKey: "token"
EOF

helm install selenium-mcp ./charts/selenium-mcp/ -f values-existing-browserless.yaml
```

## Configuration

### Values File

Create a custom values file to override default settings:

```yaml
# values-prod.yaml
replicaCount: 3

image:
  repository: ghcr.io/fbettag/selenium-mcp-server
  tag: "latest"

browserless:
  enabled: false
  service:
    existingService: "production-browserless"
    existingServiceNamespace: "browserless"
    port: 3000

mcp:
  browserlessUrl: "http://production-browserless.browserless.svc.cluster.local:3000"
  browserlessToken: "production-token-123"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Environment Variables

The chart automatically sets these environment variables:

- `BROWSERLESS_URL`: Configured based on your browserless setup
- `BROWSERLESS_TOKEN`: Optional authentication token
- `PYTHONPATH`: Set to `/app/src`
- `PYTHONUNBUFFERED`: Set to `1`

### Secrets Management

For production deployments, use Kubernetes secrets for authentication tokens:

```bash
# Create a secret for browserless token
kubectl create secret generic browserless-secrets \
  --namespace=your-namespace \
  --from-literal=token=your-secret-token

# Reference the secret in your values file
mcp:
  existingSecret: "browserless-secrets"
  existingSecretKey: "token"
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade selenium-mcp ./charts/selenium-mcp/ -f values-updated.yaml

# Upgrade to new chart version
helm upgrade selenium-mcp oci://ghcr.io/fbettag/selenium-mcp-chart --version 0.2.0
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall selenium-mcp

# Optional: delete associated resources
kubectl delete pvc -l app.kubernetes.io/instance=selenium-mcp
```

## GitHub Repository Installation

Since this chart is in your GitHub repository, you can install it directly:

### Method 1: Clone and Install

```bash
git clone https://github.com/fbettag/selenium-mcp.git
cd selenium-mcp

# Install from local chart
helm install selenium-mcp charts/selenium-mcp/
```

### Method 2: Raw GitHub URL

```bash
# Install using raw GitHub URL
helm install selenium-mcp \
  https://raw.githubusercontent.com/fbettag/selenium-mcp/main/charts/selenium-mcp/Chart.yaml

# Or using the directory
helm install selenium-mcp \
  https://github.com/fbettag/selenium-mcp/tree/main/charts/selenium-mcp
```

### Method 3: GitHub Packages (OCI)

First, package and push the chart to GitHub Packages:

```bash
# Package the chart
helm package charts/selenium-mcp/

# Login to GitHub Packages
helm registry login ghcr.io \
  --username YOUR_GITHUB_USERNAME \
  --password YOUR_GITHUB_TOKEN

# Push the chart
helm push selenium-mcp-0.1.0.tgz oci://ghcr.io/fbettag/charts

# Install from OCI registry
helm install selenium-mcp oci://ghcr.io/fbettag/charts/selenium-mcp --version 0.1.0
```

## CI/CD Integration

The GitHub Actions workflow includes Helm linting and testing:

```yaml
# In your GitHub workflow
jobs:
  helm-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Helm
        uses: azure/setup-helm@v3
      - name: Lint Helm chart
        run: helm lint charts/selenium-mcp/
      - name: Test template rendering
        run: helm template selenium-mcp charts/selenium-mcp/ --debug
```

## Troubleshooting

### Common Issues

1. **Browserless Connection Issues**:
   ```bash
   # Check browserless service
   kubectl get svc -l app=browserless
   
   # Test connectivity
   kubectl run test-pod --rm -it --image=curlimages/curl -- curl http://browserless-service:3000/health
   ```

2. **Authentication Issues**:
   ```bash
   # Check secrets
   kubectl get secrets
   
   # Verify token in secret
   kubectl get secret browserless-secrets -o jsonpath='{.data.token}' | base64 -d
   ```

3. **Resource Issues**:
   ```bash
   # Check pod status
   kubectl get pods -l app.kubernetes.io/name=selenium-mcp
   
   # Check logs
   kubectl logs deployment/selenium-mcp
   ```

### Getting Help

- Check the [main project README](https://github.com/fbettag/selenium-mcp)
- Open an issue on GitHub
- Check Kubernetes events: `kubectl get events --sort-by=.metadata.creationTimestamp`

## Contributing

1. Fork the repository
2. Make changes to the chart
3. Test with: `helm lint charts/selenium-mcp/` and `helm template test charts/selenium-mcp/`
4. Submit a pull request

## License

This chart is licensed under the MIT License. See the main project LICENSE file for details.