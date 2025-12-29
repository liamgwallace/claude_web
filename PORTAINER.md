# Portainer Deployment Guide

Deploy Claude Web using pre-built Docker images from GitHub Container Registry.

## Prerequisites

1. **Push code to GitHub** (triggers automatic build)
2. **Wait for build** (~5-10 min): GitHub → Actions → "Build and Publish Docker Image"
3. **Make image public**: GitHub → Packages → claude_web → Change visibility → Public

## Deploy in Portainer

### Method 1: Docker Compose Stack (Recommended)

1. **Portainer** → **Stacks** → **Add stack**
2. **Name:** `claude-web`
3. **Paste this configuration:**

```yaml
version: '3.8'

services:
  claude-web:
    image: ghcr.io/YOUR_GITHUB_USERNAME/claude_web:latest
    container_name: claude-web
    ports:
      - "8000:8000"
    environment:
      - CLAUDE_API_KEY=sk-ant-api03-your-api-key-here
      - FLASK_ENV=production
    volumes:
      - claude-web-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  claude-web-data:
```

4. **Replace:**
   - `YOUR_GITHUB_USERNAME` → Your GitHub username
   - `your-api-key-here` → Get from [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys)

5. **Deploy the stack**

6. **Access:** `http://YOUR_SERVER_IP:8000`

### Method 2: Container Creation

1. **Containers** → **Add container**
2. **Name:** `claude-web`
3. **Image:** `ghcr.io/YOUR_USERNAME/claude_web:latest`
4. **Port mapping:** Host `8000` → Container `8000`
5. **Environment variables:**
   - `CLAUDE_API_KEY` = Your API key
   - `FLASK_ENV` = `production`
6. **Volume:** Container `/app/data` → New volume `claude-web-data`
7. **Restart policy:** Always
8. **Deploy**

## Updating to Latest Version

### Using Portainer UI

**Stacks** → Select `claude-web` → **Pull and redeploy**

Or:

**Stacks** → `claude-web` → **Editor** → **Update the stack** → Check "Re-pull image and redeploy"

### Using Specific Versions

Pin to specific versions instead of `:latest`:

```yaml
# Specific version tag
image: ghcr.io/YOUR_USERNAME/claude_web:v1.0.0

# Specific commit (for exact reproducibility)
image: ghcr.io/YOUR_USERNAME/claude_web:sha-f409a2b

# Latest (auto-updates when you pull)
image: ghcr.io/YOUR_USERNAME/claude_web:latest
```

## Troubleshooting

### "Image not found"

1. Verify build completed: GitHub → Actions
2. Check package is public: GitHub → Packages → claude_web
3. Confirm image name format: `ghcr.io/username/claude_web:latest` (note: underscore, not dash)

### "Authentication required"

**Option A:** Make package public (see Prerequisites above)

**Option B:** Add registry authentication:
1. Portainer → **Registries** → **Add registry**
2. Type: GitHub Container Registry
3. Username: Your GitHub username
4. Token: Generate at GitHub → Settings → Developer settings → Personal access tokens → With `read:packages` scope

### Container unhealthy or won't start

Check logs: **Containers** → `claude-web` → **Logs**

Common issues:
- Missing or invalid `CLAUDE_API_KEY`
- Port 8000 already in use
- Firewall blocking port 8000

### Can't access web interface

1. **Check container status:** Should show green "running" and healthy
2. **Test locally on server:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```
3. **Check firewall:**
   ```bash
   sudo ufw allow 8000
   ```

## Auto-Updates with Watchtower (Optional)

Add Watchtower to automatically pull and deploy new images:

```yaml
services:
  claude-web:
    # ... existing config ...
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    restart: always
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=300  # Check every 5 minutes
    command: --label-enable
```

Now Watchtower will:
- Check for new images every 5 minutes
- Pull and restart containers automatically
- Clean up old images

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_API_KEY` | ✅ Yes | - | Get from [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys) |
| `FLASK_ENV` | No | `production` | Environment mode |
| `FLASK_DEBUG` | No | `0` | Debug mode (0 or 1) |

## Multi-Environment Setup

Deploy different versions across environments:

```yaml
# Production: Pinned version
image: ghcr.io/YOUR_USERNAME/claude_web:v1.0.0

# Staging: Latest
image: ghcr.io/YOUR_USERNAME/claude_web:latest

# Testing: Specific commit
image: ghcr.io/YOUR_USERNAME/claude_web:sha-abc123
```

---

**Need more deployment options?** See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway, Render, Fly.io, and more.
