#!/bin/bash
set -e

echo "🚀 Starting Claude Web Runner in Docker..."

# Configure Claude Code CLI with API key if provided
if [ -n "$CLAUDE_API_KEY" ]; then
    echo "🔑 Configuring Claude Code CLI with API key..."
    
    # Create .claude directory if it doesn't exist
    mkdir -p ~/.claude
    
    # Create settings.json with API key helper
    cat > ~/.claude/settings.json << EOF
{
  "apiKeyHelper": "echo \$CLAUDE_API_KEY"
}
EOF
    
    # Export environment variable for Claude Code
    export ANTHROPIC_API_KEY="$CLAUDE_API_KEY"
    
    echo "✅ Claude Code CLI configured successfully"
else
    echo "⚠️  No CLAUDE_API_KEY environment variable found"
    echo "   Claude Code will require manual authentication"
fi

# Verify Claude Code installation
echo "🔍 Verifying Claude Code installation..."
if claude --version > /dev/null 2>&1; then
    echo "✅ Claude Code CLI is available"
else
    echo "❌ Claude Code CLI installation failed"
    exit 1
fi

# Create data directory structure
mkdir -p /app/data/projects

echo "🌐 Starting Flask server on port 8000..."
echo "📊 Backend API: http://localhost:8000"
echo "🖥️  Web Interface: http://localhost:8000"
echo ""

# Start the Flask application
cd /app/src && python server.py 8000