# Portainer Deployment Guide

This guide shows you how to deploy Claude Web using pre-built Docker images in Portainer.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. You push code to GitHub                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GitHub Actions automatically builds Docker image         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Image published to GitHub Container Registry (GHCR)      │
│     → ghcr.io/YOUR_USERNAME/claude_web:latest                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Pull image from Portainer (no building required!)        │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step: Deploy in Portainer

### Step 1: Push Code to GitHub (First Time Only)

```bash
# Make sure your changes are committed
git add .
git commit -m "Setup automated Docker builds"
git push origin main
```

### Step 2: Wait for GitHub Actions to Build

1. Go to your GitHub repository
2. Click **Actions** tab
3. Wait for "Build and Publish Docker Image" to complete (~5-10 minutes)
4. Your image will be at: `ghcr.io/YOUR_USERNAME/claude_web:latest`

### Step 3: Make Image Public (One-Time Setup)

**Option A: Public Package (No Authentication Needed)**
1. Go to your GitHub profile → **Packages** tab
2. Click on `claude_web` package
3. Click **Package settings**
4. Scroll to "Danger Zone" → **Change visibility**
5. Select **Public** → Confirm

**Option B: Private Package (Requires GitHub Token)**
If you want to keep the image private:
1. Generate GitHub token: Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Create token with `read:packages` scope
3. In Portainer, add registry credentials before deployment

### Step 4: Deploy in Portainer

#### Method 1: Using Docker Compose (Recommended)

1. **Log into Portainer**
2. Select your environment (e.g., local)
3. Go to **Stacks** → **Add stack**
4. **Name:** `claude-web`
5. **Build method:** Web editor
6. **Paste this docker-compose content:**

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
      - FLASK_DEBUG=0
      - PYTHONPATH=/app
    volumes:
      - claude-web-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

volumes:
  claude-web-data:
    driver: local
```

7. **Replace:**
   - `YOUR_GITHUB_USERNAME` with your GitHub username
   - `sk-ant-api03-your-api-key-here` with your actual Claude API key

8. Click **Deploy the stack**

9. Wait for container to start (check health status)

10. Access at: `http://YOUR_SERVER_IP:8000`

#### Method 2: Using Container Creation

1. **Log into Portainer**
2. Go to **Containers** → **Add container**
3. **Name:** `claude-web`
4. **Image:** `ghcr.io/YOUR_GITHUB_USERNAME/claude_web:latest`
5. **Port mapping:**
   - Host: `8000`
   - Container: `8000`
6. **Environment variables:** Click "Add environment variable"
   - `CLAUDE_API_KEY` = `sk-ant-api03-your-key-here`
   - `FLASK_ENV` = `production`
7. **Volumes:** Click "Add volume"
   - Container: `/app/data`
   - Create new volume: `claude-web-data`
8. **Restart policy:** Always
9. Click **Deploy the container**

## Updating to Latest Version

When you push new code to GitHub and the build completes:

### In Portainer:

1. Go to **Stacks** → select `claude-web` stack
2. Scroll down and click **Pull and redeploy**

   OR manually:

3. Click **Editor** tab
4. Make sure image line says `:latest` (not a specific tag)
5. Click **Update the stack**
6. Check **Re-pull image and redeploy**
7. Click **Update**

Your container will automatically pull the new image and restart!

## Using Specific Versions

Instead of `:latest`, you can pin to specific versions:

```yaml
# Use specific version
image: ghcr.io/YOUR_USERNAME/claude_web:v1.0.0

# Use specific commit
image: ghcr.io/YOUR_USERNAME/claude_web:sha-f409a2b

# Use latest (auto-updates)
image: ghcr.io/YOUR_USERNAME/claude_web:latest
```

## Troubleshooting

### "Image not found" error

1. **Check if build completed:**
   - GitHub → Actions tab → Verify build succeeded

2. **Check package visibility:**
   - GitHub → Your profile → Packages → claude_web → Make public

3. **Verify image name:**
   ```bash
   # Correct format:
   ghcr.io/your-username/claude_web:latest

   # Common mistakes:
   ghcr.io/YOUR_USERNAME/claude_web:latest  ← Replace YOUR_USERNAME
   ghcr.io/your-username/claude-web:latest  ← Wrong repo name (underscore vs dash)
   ```

### "Authentication required" error

Your package is private. Either:
- Make it public (see Step 3 above)
- OR add GitHub token in Portainer:
  1. Registries → Add registry
  2. Registry type: GitHub Container Registry
  3. Username: Your GitHub username
  4. Personal Access Token: Create token with `read:packages` scope

### Container unhealthy

```bash
# Check logs in Portainer:
Containers → claude-web → Logs

# Common issues:
- Missing CLAUDE_API_KEY
- Invalid API key format
- Port 8000 already in use
```

### Can't access web interface

1. **Check container status:**
   - Should show green "running" and healthy

2. **Verify port mapping:**
   - Host port 8000 → Container port 8000

3. **Check firewall:**
   ```bash
   # On your server:
   sudo ufw allow 8000
   ```

4. **Test locally:**
   ```bash
   # SSH into server:
   curl http://localhost:8000/health

   # Should return:
   {"status":"healthy"}
   ```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_API_KEY` | ✅ Yes | - | Your Anthropic API key |
| `FLASK_ENV` | No | `production` | Flask environment |
| `FLASK_DEBUG` | No | `0` | Debug mode (0 or 1) |
| `FLASK_HOST` | No | `0.0.0.0` | Bind address |
| `FLASK_PORT` | No | `8000` | Internal port |

## Automatic Updates with Watchtower

Want automatic updates when you push code? Install Watchtower:

```yaml
version: '3.8'

services:
  claude-web:
    image: ghcr.io/YOUR_USERNAME/claude_web:latest
    # ... rest of config ...
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    restart: always
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_INCLUDE_RESTARTING=true
      - WATCHTOWER_POLL_INTERVAL=300  # Check every 5 minutes
    command: --label-enable --interval 300
```

Now Watchtower will:
1. Check for new images every 5 minutes
2. Pull new versions automatically
3. Restart containers with new images
4. Clean up old images

## Multi-Server Deployment

Deploy the same pre-built image to multiple servers:

1. **Server 1 (Production):**
   ```yaml
   image: ghcr.io/YOUR_USERNAME/claude_web:v1.0.0  # Pinned version
   ```

2. **Server 2 (Staging):**
   ```yaml
   image: ghcr.io/YOUR_USERNAME/claude_web:latest  # Auto-update
   ```

3. **Server 3 (Testing):**
   ```yaml
   image: ghcr.io/YOUR_USERNAME/claude_web:sha-abc123  # Specific commit
   ```

All servers pull the same pre-built images - no building required!

## Support

- **Build issues:** Check GitHub Actions logs
- **Image issues:** Verify package visibility on GitHub
- **Runtime issues:** Check Portainer container logs
- **API issues:** Verify CLAUDE_API_KEY is correct
