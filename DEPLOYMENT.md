# Deployment Guide

This guide explains how to deploy Claude Web Runner using pre-built Docker images from GitHub Container Registry.

## Quick Start with Pre-built Images

### 1. Using Docker CLI

```bash
# Pull the latest image
docker pull ghcr.io/$(git config --get remote.origin.url | sed 's/.*:\(.*\)\.git/\1/'):latest

# Run the container
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=your-api-key-here \
  -v $(pwd)/data:/app/data \
  ghcr.io/$(git config --get remote.origin.url | sed 's/.*:\(.*\)\.git/\1/'):latest
```

### 2. Using Docker Compose with Pre-built Image

Create a `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  claude-web:
    image: ghcr.io/YOUR_GITHUB_USERNAME/claude_web:latest
    ports:
      - "8000:8000"
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

Then run:

```bash
# Create .env file with your API key
echo "CLAUDE_API_KEY=your-api-key-here" > .env

# Start the service
docker-compose -f docker-compose.production.yml up -d
```

## Available Image Tags

GitHub Actions automatically builds and publishes images with multiple tags:

| Tag Pattern | Description | Example |
|------------|-------------|---------|
| `latest` | Latest build from main branch | `ghcr.io/user/claude_web:latest` |
| `sha-XXXXXX` | Specific commit SHA | `ghcr.io/user/claude_web:sha-f409a2b` |
| `vX.Y.Z` | Semantic version tags | `ghcr.io/user/claude_web:v1.0.0` |
| `vX.Y` | Minor version tags | `ghcr.io/user/claude_web:v1.0` |
| `vX` | Major version tags | `ghcr.io/user/claude_web:v1` |
| `pr-N` | Pull request builds | `ghcr.io/user/claude_web:pr-42` |

### Choosing the Right Tag

- **Production**: Use semantic version tags (`v1.0.0`) for stability
- **Staging**: Use `latest` for testing the newest features
- **Rollback**: Use specific SHA tags (`sha-XXXXXX`) to pin exact versions
- **Testing**: Use PR tags (`pr-N`) to test changes before merging

## Multi-Architecture Support

All images are built for multiple architectures:

- **linux/amd64** - Standard x86_64 (Intel/AMD processors)
- **linux/arm64** - ARM64 (Apple Silicon M1/M2, AWS Graviton, Raspberry Pi 4+)

Docker automatically pulls the correct architecture for your platform.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_API_KEY` | Yes | - | Your Anthropic API key |
| `FLASK_ENV` | No | `production` | Flask environment (production/development) |
| `FLASK_DEBUG` | No | `0` | Enable Flask debug mode (0/1) |
| `FLASK_HOST` | No | `0.0.0.0` | Flask bind address |
| `FLASK_PORT` | No | `8000` | Flask port |

## Deployment Platforms

### Coolify

Use the provided `docker-compose.coolify.yml`:

1. Create a new service in Coolify
2. Point to this repository
3. Select `docker-compose.coolify.yml` as compose file
4. Set `CLAUDE_API_KEY` in environment variables
5. Deploy

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Set environment variable
railway variables set CLAUDE_API_KEY=your-api-key

# Deploy
railway up
```

### Render

1. Create a new Web Service
2. Choose "Deploy an existing image from a registry"
3. Enter: `ghcr.io/YOUR_USERNAME/claude_web:latest`
4. Add environment variable `CLAUDE_API_KEY`
5. Set health check path to `/health`
6. Deploy

### DigitalOcean App Platform

1. Create new App
2. Choose "Docker Hub" and enter `ghcr.io/YOUR_USERNAME/claude_web:latest`
3. Set HTTP port to `8000`
4. Add environment variable `CLAUDE_API_KEY`
5. Deploy

### Fly.io

Create `fly.toml`:

```toml
app = "claude-web"
primary_region = "sjc"

[build]
  image = "ghcr.io/YOUR_USERNAME/claude_web:latest"

[env]
  FLASK_ENV = "production"
  FLASK_PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

  [[services.tcp_checks]]
    interval = "15s"
    timeout = "2s"
    grace_period = "5s"
    restart_limit = 0
```

Deploy:

```bash
# Set secret
fly secrets set CLAUDE_API_KEY=your-api-key

# Deploy
fly deploy
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables or secret managers
2. **Use specific version tags** - Avoid `latest` in production for predictability
3. **Enable HTTPS** - Use reverse proxy (nginx, Caddy) or platform SSL
4. **Restrict access** - Use firewall rules or authentication proxy
5. **Monitor vulnerabilities** - Check GitHub Security tab for Trivy scan results
6. **Keep images updated** - Regularly pull new versions for security patches

## Health Checks

The application provides a health check endpoint at `/health`:

```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-29T10:30:00Z"
}
```

## Logs and Troubleshooting

```bash
# View container logs
docker logs claude-web

# Follow logs in real-time
docker logs -f claude-web

# Check container status
docker ps -a | grep claude-web

# Inspect container
docker inspect claude-web

# Execute commands in running container
docker exec -it claude-web bash
```

## Updating to New Versions

```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/claude_web:latest

# Stop and remove old container
docker stop claude-web
docker rm claude-web

# Start new container with same configuration
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=your-api-key \
  -v $(pwd)/data:/app/data \
  ghcr.io/YOUR_USERNAME/claude_web:latest
```

Or with docker-compose:

```bash
# Pull latest images
docker-compose pull

# Recreate containers
docker-compose up -d
```

## Rollback

If you need to rollback to a previous version:

```bash
# Find the commit SHA you want to rollback to
git log --oneline

# Pull that specific version
docker pull ghcr.io/YOUR_USERNAME/claude_web:sha-XXXXXX

# Update your docker-compose.yml or docker run command to use that tag
```

## Performance Tuning

### For High Traffic

```bash
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=your-api-key \
  --cpus="2" \
  --memory="2g" \
  --restart=always \
  -v $(pwd)/data:/app/data \
  ghcr.io/YOUR_USERNAME/claude_web:latest
```

### Using Gunicorn (Production Server)

For better performance, you can modify the startup script to use Gunicorn:

```bash
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=your-api-key \
  -v $(pwd)/data:/app/data \
  ghcr.io/YOUR_USERNAME/claude_web:latest \
  bash -c "pip install gunicorn && cd /app/src && gunicorn -w 4 -b 0.0.0.0:8000 app:app"
```

## Building Your Own Images

If you need to build locally instead of using pre-built images:

```bash
# Build for current platform
docker build -t claude-web:local .

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t claude-web:local \
  .
```

## Support

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions or share ideas
- **Security**: Report vulnerabilities via GitHub Security Advisory
