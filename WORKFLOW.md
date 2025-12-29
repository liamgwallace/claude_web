# Automated Build & Deploy Workflow

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR DEVELOPMENT                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  git push origin main │
                    └──────────┬───────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      GITHUB ACTIONS (Automatic)                      │
├─────────────────────────────────────────────────────────────────────┤
│  1. Code pushed detected                                             │
│  2. .github/workflows/docker-build.yml triggered                     │
│  3. Checkout repository                                              │
│  4. Setup Docker Buildx (multi-platform support)                     │
│  5. Build for linux/amd64 + linux/arm64                             │
│  6. Run security scan (Trivy)                                        │
│  7. Tag with multiple versions:                                      │
│     - latest (main branch)                                           │
│     - sha-abc123 (commit hash)                                       │
│     - v1.0.0 (if tagged)                                             │
│  8. Push to GitHub Container Registry                                │
│  9. (Optional) Push to Docker Hub                                    │
│  10. Generate SBOM + Provenance                                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      IMAGE REGISTRIES                                │
├─────────────────────────────────────────────────────────────────────┤
│  GitHub Container Registry:                                          │
│  └─ ghcr.io/username/claude_web:latest                              │
│  └─ ghcr.io/username/claude_web:sha-abc123                          │
│  └─ ghcr.io/username/claude_web:v1.0.0                              │
│                                                                       │
│  Docker Hub (optional):                                              │
│  └─ username/claude-web:latest                                       │
│  └─ username/claude-web:sha-abc123                                   │
│  └─ username/claude-web:v1.0.0                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT TARGETS                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   Portainer     │  │    Coolify      │  │   Your Server   │    │
│  │                 │  │                 │  │                 │    │
│  │ docker-compose  │  │ docker-compose  │  │   docker pull   │    │
│  │    pull image   │  │    pull image   │  │   docker run    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │    Railway      │  │     Render      │  │     Fly.io      │    │
│  │                 │  │                 │  │                 │    │
│  │  Deploy from    │  │  Deploy from    │  │  Deploy from    │    │
│  │  GHCR/Docker Hub│  │  GHCR/Docker Hub│  │  GHCR/Docker Hub│    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Timeline Example

```
00:00  Developer: git commit -m "Add new feature"
00:00  Developer: git push origin main
00:01  GitHub Actions: Workflow triggered
00:02  GitHub Actions: Building for AMD64...
00:05  GitHub Actions: Building for ARM64...
00:08  GitHub Actions: Running security scan...
00:09  GitHub Actions: Pushing to ghcr.io...
00:10  GitHub Actions: ✅ Build complete!

       Image available at:
       - ghcr.io/you/claude_web:latest
       - ghcr.io/you/claude_web:sha-abc123

00:11  Portainer: docker-compose pull
00:12  Portainer: Recreating container...
00:13  ✅ New version deployed!
```

## File Triggers

### What Triggers a Build?

**Automatic Triggers:**
```bash
# Push to main/master
git push origin main           # → Builds & publishes :latest

# Create version tag
git tag v1.0.0
git push origin v1.0.0         # → Builds & publishes :v1.0.0, :v1.0, :v1

# Push to any branch
git push origin feature-branch # → Builds but tags as :feature-branch
```

**Manual Trigger:**
- GitHub → Actions → "Build and Publish Docker Image" → Run workflow

### What Files Control This?

| File | What It Does |
|------|--------------|
| `.github/workflows/docker-build.yml` | Main build workflow (GHCR) |
| `.github/workflows/docker-hub.yml` | Optional Docker Hub publishing |
| `.github/workflows/ci.yml` | Tests (includes Docker build test) |
| `Dockerfile` | Image build instructions |
| `.dockerignore` | What NOT to include in image |
| `docker/start.sh` | Container startup script |

## The Build Process

### What Gets Built?

```dockerfile
# From Dockerfile
FROM python:3.11-slim              # Base image

# Install system dependencies
- curl, git, ca-certificates
- Node.js 18+ (for Claude CLI)

# Install Python packages
- flask, flask-cors, requests, pydantic

# Install Claude Code CLI
- @anthropic-ai/claude-code (npm)

# Copy application
- src/ (backend)
- web/ (frontend)
- templates/ (project templates)

# Size: ~800MB (compressed: ~280MB)
```

### Multi-Architecture Support

Both AMD64 and ARM64 are built simultaneously:

```
linux/amd64 → Intel/AMD servers, most cloud providers
linux/arm64 → Apple Silicon (M1/M2), AWS Graviton, Raspberry Pi 4+
```

Docker automatically pulls the right architecture for your platform.

## Tagging Strategy

Every build creates multiple tags:

```bash
# Commit to main:
git push origin main
# Creates:
- ghcr.io/you/claude_web:latest      # Always points to newest main
- ghcr.io/you/claude_web:sha-f409a2b # Specific commit

# Version tag:
git tag v1.2.3 && git push --tags
# Creates:
- ghcr.io/you/claude_web:v1.2.3      # Exact version
- ghcr.io/you/claude_web:v1.2        # Minor updates
- ghcr.io/you/claude_web:v1          # Major updates
- ghcr.io/you/claude_web:latest      # Also updates latest
- ghcr.io/you/claude_web:sha-abc123  # Plus commit SHA
```

## Security Features

### Automatic Scanning

Every build includes:

1. **Trivy vulnerability scan**
   - Checks base image for known CVEs
   - Scans all installed packages
   - Results appear in GitHub Security tab

2. **SBOM (Software Bill of Materials)**
   - Lists all packages and versions
   - Helps track dependencies
   - Useful for compliance

3. **Provenance**
   - Cryptographically signed build record
   - Proves image came from your repo
   - Supply chain security

### View Security Reports

```
GitHub → Your Repo → Security → Code scanning alerts
```

## Using the Images

### Pull Image

```bash
# Latest version
docker pull ghcr.io/YOUR_USERNAME/claude_web:latest

# Specific version
docker pull ghcr.io/YOUR_USERNAME/claude_web:v1.0.0

# Specific commit
docker pull ghcr.io/YOUR_USERNAME/claude_web:sha-abc123
```

### Run Container

```bash
docker run -d \
  --name claude-web \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=sk-ant-your-key \
  -v claude-data:/app/data \
  --restart unless-stopped \
  ghcr.io/YOUR_USERNAME/claude_web:latest
```

### Update to Latest

```bash
# Pull new image
docker pull ghcr.io/YOUR_USERNAME/claude_web:latest

# Recreate container
docker stop claude-web
docker rm claude-web
docker run -d ... # same command as above

# Or with docker-compose:
docker-compose pull && docker-compose up -d
```

## Monitoring Builds

### GitHub Actions UI

```
GitHub → Actions tab
→ Click workflow run
→ View logs in real-time
→ Download artifacts
→ Check security scan results
```

### Build Status Badge

Add to README:

```markdown
![Docker Build](https://github.com/YOUR_USERNAME/claude_web/actions/workflows/docker-build.yml/badge.svg)
```

### Notifications

Configure in: Repo → Settings → Notifications
- Email on build failure
- Slack webhook integration
- Discord webhook integration

## Cost & Limits

### GitHub Container Registry (GHCR)

- **Public repos:** Unlimited free storage
- **Private repos:** 500MB free, then paid
- **Bandwidth:** Unlimited public pulls
- **Actions minutes:** 2,000 free/month, then $0.008/min

### Docker Hub

- **Free tier:**
  - Unlimited public repos
  - 200 pulls per 6 hours (anonymous)
  - 200 pulls per 6 hours (authenticated)
- **Pro tier ($5/month):**
  - Unlimited pulls
  - Private repos

## Troubleshooting Builds

### Build Fails

1. Check workflow logs: Actions → Failed run → View logs
2. Common issues:
   - Dockerfile syntax error
   - Missing file referenced in COPY
   - requirements.txt has invalid package
   - Docker layer too large

### Image Won't Pull

1. Check image exists: GitHub → Packages
2. Check visibility: Package should be "Public"
3. Verify image name is exactly correct
4. Try explicit tag instead of :latest

### Build is Slow

- First build: ~10 minutes (no cache)
- Subsequent builds: ~3-5 minutes (with cache)
- Speed up:
  - Use build cache (already enabled)
  - Reduce dependencies
  - Use smaller base image

## Advanced: Custom Builds

### Build Locally

```bash
# Single platform
docker build -t claude-web:local .

# Multi-platform
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t claude-web:local .
```

### Trigger Build via API

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/YOUR_USERNAME/claude_web/actions/workflows/docker-build.yml/dispatches \
  -d '{"ref":"main"}'
```

## Summary

1. **You code** → Push to GitHub
2. **GitHub Actions** → Builds image automatically (5-10 min)
3. **Registry** → Image published (GHCR + optional Docker Hub)
4. **You deploy** → Pull and run from anywhere

**No local building required. Just push and deploy!**
