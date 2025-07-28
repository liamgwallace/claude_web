# Claude Web Runner

A modern web interface for interacting with Claude Code through projects and threads.

![Claude Web Runner](https://img.shields.io/badge/Claude-Web%20Runner-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-red)
![Web](https://img.shields.io/badge/Frontend-HTML%2FJS-orange)

## Features

- 💬 **Clean Chat Interface** - Modern chat bubbles with different colors for user and Claude
- 📁 **Project Management** - Organize work into separate project folders
- 🧵 **Thread Management** - Multiple chat conversations within each project
- 📂 **File Tree View** - Browse files created by Claude in your projects
- 🔄 **Session Persistence** - Remembers your last project and thread
- ⌨️ **Keyboard Shortcuts** - Ctrl+Enter to send messages
- 📱 **Mobile Responsive** - Works on desktop and mobile devices

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Application**
   ```bash
   python start.py
   ```

3. **Open Your Browser**
   - The app will automatically open at http://localhost:8000
   - Or manually navigate to http://localhost:8000

## Usage

### Getting Started
1. Click the hamburger menu (☰) to open the project sidebar
2. Create a new project or select an existing one
3. Create a thread within that project
4. Start chatting with Claude!

### Interface Overview

**Header**
- Left: Hamburger menu (☰) - toggles project/thread sidebar
- Right: Folder icon (📁) - toggles file tree sidebar

**Left Sidebar**
- Tree view of projects and threads
- Buttons: New Project, Delete Project, New Thread, Delete Thread
- Smart button enabling based on your selection

**Right Sidebar**
- File tree showing all files in the selected project
- Updates automatically when you switch projects

**Chat Area**
- Clean chat bubbles (blue for you, gray for Claude)
- Status indicator shows Claude's response progress
- Text input with auto-resize and send button

### Keyboard Shortcuts
- **Ctrl+Enter** - Send message
- **Escape** - Close sidebars (mobile)

## Architecture

This is a **single-service web application** that combines both backend API and frontend in one Flask server.

### Services & Ports
- **Main Application**: `start.py` → Runs Flask on **port 8000**
  - **Backend API**: Flask REST API endpoints (`app.py`)
  - **Frontend**: Static HTML/CSS/JS served from Flask (`web_app.html`)
  - **URL**: http://localhost:8000 (both API and web interface)

### Project Structure
```
claude_web/
├── start.py            # Main startup script (launches Flask on port 8000)
├── app.py              # Flask API backend + static file serving
├── claude_wrapper.py   # Claude CLI integration with session management
├── web_app.html       # Single-page web application (HTML/CSS/JS)
├── test_api.py        # API testing client
├── requirements.txt   # Python dependencies
└── data/
    └── projects/      # Project working directories
        ├── project-1/ # Individual project folder (Claude workspace)
        │   ├── <generated files by Claude>
        │   └── .threads/    # Thread metadata storage
        │       ├── thread-1.json
        │       └── threads.json
        └── project-2/
```

### Key Components
1. **Flask Backend** (`app.py`): REST API + serves static HTML
2. **Claude Integration** (`claude_wrapper.py`): Session management with CLI
3. **Web Frontend** (`web_app.html`): Complete SPA with chat UI
4. **Startup Script** (`start.py`): Dependency checks + launches Flask

## Troubleshooting

**"Failed to fetch" errors:**
- Make sure the Flask server is running on port 8000
- Install flask-cors: `pip install flask-cors`

**Claude CLI not found:**
- Ensure Claude CLI is installed and in your PATH
- On Windows, check common installation paths

## Technical Details

### Session Management
- Each project thread corresponds to a unique Claude CLI session
- Session IDs are stored in thread metadata for conversation continuity
- Claude CLI handles conversation history automatically via `--resume` flag

### Async Processing
- Flask uses background job queue for Claude CLI calls
- Jobs tracked with status: `queued` → `running` → `done`/`failed`
- Frontend polls `/status/<job_id>` for real-time updates

### File Organization
- **Projects**: Physical directories where Claude CLI executes
- **Threads**: JSON metadata files linking to Claude sessions
- **Generated Files**: Created directly by Claude in project directories
