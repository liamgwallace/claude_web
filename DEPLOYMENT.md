# Deployment Guide

Deploy Claude Web using pre-built Docker images from GitHub Container Registry.

## Quick Start

### 1. Get Your API Key

Get your Claude API key from [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys)

### 2. Docker CLI

```bash
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=sk-ant-your-key \
  -v claude-data:/app/data \
  --restart unless-stopped \
  ghcr.io/YOUR_USERNAME/claude_web:latest
```

### 3. Docker Compose

Use the provided `docker-compose.production.yml`:

```bash
cp docker-compose.production.yml docker-compose.yml
# Edit CLAUDE_API_KEY and YOUR_USERNAME
docker-compose up -d
```

## Image Tags

| Tag | Description | Use Case |
|-----|-------------|----------|
| `latest` | Newest from main branch | Development, staging |
| `v1.0.0` | Semantic version | Production (stable) |
| `sha-abc123` | Specific commit | Rollbacks, debugging |

## Multi-Architecture Support

All images support:
- **linux/amd64** - Intel/AMD (most servers)
- **linux/arm64** - ARM64 (Apple Silicon, AWS Graviton, Raspberry Pi 4+)

Docker automatically selects the correct architecture.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_API_KEY` | ✅ | - | Your Anthropic API key |
| `FLASK_ENV` | No | `production` | Environment mode |
| `FLASK_DEBUG` | No | `0` | Debug mode (0 or 1) |
| `FLASK_PORT` | No | `8000` | Server port |

## Platform Deployments

### Portainer

See detailed guide: [PORTAINER.md](PORTAINER.md)

**Quick version:**
1. Stacks → Add stack → Name: `claude-web`
2. Upload `docker-compose.portainer.yml`
3. Edit `YOUR_GITHUB_USERNAME` and `CLAUDE_API_KEY`
4. Deploy

### Coolify

1. Create new service → Docker Compose
2. Point to your GitHub repository
3. Select `docker-compose.coolify.yml`
4. Set `CLAUDE_API_KEY` in environment variables
5. Deploy

### Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway variables set CLAUDE_API_KEY=sk-ant-your-key
railway up
```

### Render

1. New Web Service → "Deploy an existing image"
2. Image: `ghcr.io/YOUR_USERNAME/claude_web:latest`
3. Add env var: `CLAUDE_API_KEY`
4. Health check path: `/health`
5. Deploy

### Fly.io

Create `fly.toml`:

```toml
app = "claude-web"

[build]
  image = "ghcr.io/YOUR_USERNAME/claude_web:latest"

[env]
  FLASK_ENV = "production"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

Deploy:
```bash
fly secrets set CLAUDE_API_KEY=sk-ant-your-key
fly deploy
```

### DigitalOcean App Platform

1. Create new App
2. Source: Docker Hub → `ghcr.io/YOUR_USERNAME/claude_web:latest`
3. HTTP port: `8000`
4. Add env var: `CLAUDE_API_KEY`
5. Deploy

## Updating

### Pull Latest Image

```bash
docker pull ghcr.io/YOUR_USERNAME/claude_web:latest
docker-compose up -d --force-recreate
```

### Portainer

Stacks → claude-web → **Pull and redeploy**

### Auto-Update with Watchtower

Add to docker-compose.yml:

```yaml
watchtower:
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  environment:
    - WATCHTOWER_CLEANUP=true
    - WATCHTOWER_POLL_INTERVAL=300
  command: --label-enable
```

## Rollback

```bash
# Find commit SHA
git log --oneline

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/claude_web:sha-abc123

# Update docker-compose.yml to use that tag
# Then restart
docker-compose up -d
```

## Health Check

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

## Logs & Troubleshooting

```bash
# View logs
docker logs claude-web

# Follow logs
docker logs -f claude-web

# Container status
docker ps -a | grep claude-web

# Execute commands in container
docker exec -it claude-web bash
```

### Common Issues

**Container won't start:**
- Verify `CLAUDE_API_KEY` is set correctly
- Check port 8000 isn't already in use: `sudo lsof -i :8000`
- Check logs: `docker logs claude-web`

**Can't access web interface:**
- Container healthy? `docker ps`
- Firewall open? `sudo ufw allow 8000`
- Test locally: `curl http://localhost:8000/health`

**Image not found:**
- Build completed? GitHub → Actions
- Package public? GitHub → Packages → claude_web
- Username correct in image URL?

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use version tags** - Avoid `:latest` in production
3. **Enable HTTPS** - Use reverse proxy (nginx/Caddy) or platform SSL
4. **Monitor vulnerabilities** - Check GitHub Security tab for scan results
5. **Keep updated** - Regularly pull new versions

## Performance Tuning

### Resource Limits

```yaml
services:
  claude-web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Production Server

For better performance, use Gunicorn:

```bash
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=sk-ant-your-key \
  -v claude-data:/app/data \
  ghcr.io/YOUR_USERNAME/claude_web:latest \
  bash -c "pip install gunicorn && cd /app/src && gunicorn -w 4 -b 0.0.0.0:8000 app:app"
```

## Building Locally (Optional)

If you need to build instead of using pre-built images:

```bash
# Current platform
docker build -t claude-web:local .

# Multi-platform
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t claude-web:local \
  .
```

## How GitHub Actions Works

When you push code to GitHub:

1. `.github/workflows/docker-build.yml` triggers automatically
2. Builds multi-architecture image (AMD64 + ARM64)
3. Runs security scan with Trivy
4. Publishes to `ghcr.io/YOUR_USERNAME/claude_web:latest`
5. Creates multiple tags (latest, sha, semver)
6. Generates SBOM and provenance

You can then pull this pre-built image from anywhere!

**First time setup:**
1. Push code → Wait ~5-10 min for build
2. Make package public: GitHub → Packages → claude_web → Change visibility
3. Deploy from registry

## Support

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and ideas
- **Portainer Guide** - [PORTAINER.md](PORTAINER.md)
- **Security** - Report via GitHub Security Advisory
