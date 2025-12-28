# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A web interface for interacting with Claude Code through projects and threads. Flask backend with subprocess calls to Claude CLI, custom HTML/CSS/JS frontend, and Docker deployment support.

## Development Commands

### Running the Application
```bash
# Quick start (recommended)
python scripts/start.py

# Manual start - Flask on port 8000
cd src && python server.py 8000

# Docker development
docker-compose up -d

# Backend testing only
python scripts/test_api.py
```

### Dependencies
```bash
# Install Python requirements
pip install -r requirements.txt

# Core dependencies: flask==3.0.0, flask-cors==4.0.0, requests==2.31.0, pydantic>=2.0.0
```

## Architecture

### Backend (`src/`)
- **`app.py`**: Flask REST API + static file serving
- **`claude_wrapper.py`**: Claude CLI session management via subprocess 
- **`template_manager.py`**: Auto-initialization of Claude projects
- **`server.py`**: Alternative server entry point

### Frontend (`web/`)
- **`index.html`**: Single-page web application
- **`css/styles.css`**: Responsive styles with mobile optimization
- **`js/app.js`**: Modular JavaScript with API client (`ClaudeWebApp` class)

### Data Organization
- **`data/projects/<name>/`**: Individual Claude workspaces
- **`.threads/<id>.json`**: Thread metadata with Claude session IDs
- **`templates/claude_project/`**: Default project templates

## Claude CLI Integration

The core integration uses Claude CLI's built-in session management:

```bash
# New session
claude -p "message" --output-format json

# Resume session  
claude --resume <session-id> -p "message" --output-format json
```

**Key Implementation** (`src/claude_wrapper.py:50-100`):
- Session IDs captured from JSON responses
- Thread metadata stores session continuity
- Subprocess calls handle Claude CLI execution
- Projects are physical directories where Claude runs

## API Endpoints

```
GET  /projects                              # List projects
POST /project/new                           # Create project
GET  /project/:name/threads                 # Get threads
POST /project/:name/thread/new              # Create thread
POST /project/:name/thread/:id/message      # Send to Claude
GET  /project/:name/files                   # File tree
GET  /project/:name/file?path=:path         # View file
POST /project/:name/file/:path/save         # Save file
DELETE /project/:name/thread/:id            # Delete thread
DELETE /project/:name                       # Delete project
GET  /status/:job_id                        # Async job status
```

## Docker Deployment

### Environment Variables
- **`CLAUDE_API_KEY`** (required): Anthropic API key
- **`FLASK_ENV`**: production/development
- **`FLASK_DEBUG`**: 0/1

### Startup Flow (`docker/start.sh`)
1. Configure Claude CLI with API key
2. Install Playwright MCP support
3. Create data directory structure
4. Launch Flask on port 8000

## Project Structure

```
claude_web/
├── src/                    # Backend Flask application
├── web/                    # Frontend HTML/CSS/JS
├── data/projects/          # Claude workspace directories
├── templates/              # Project initialization templates
├── docker/                 # Docker configuration
├── Documentation/          # Reference materials
└── requirements.txt        # Python dependencies
```

## Development Notes

- **Session Management**: Each thread = unique Claude CLI session with `--resume` support
- **File Organization**: Projects are physical folders; threads are JSON metadata
- **Template System**: New projects auto-initialized with Claude Code configuration
- **Mobile Support**: Responsive design with virtual keyboard handling
- **Async Processing**: Background job queue for Claude CLI calls with status polling