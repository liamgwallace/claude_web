# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for Claude Code and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18+ for Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Install Playwright and browsers at build time for production
RUN npx --yes playwright install chromium --with-deps

# Copy application code
COPY . .

# Create data directory for projects
RUN mkdir -p data/projects

# Create startup script that configures Claude Code with API key
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use startup script as entrypoint
CMD ["/start.sh"]