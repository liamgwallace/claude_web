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
   - The app will automatically open at http://localhost:5000
   - Or manually navigate to http://localhost:5000

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

```
claude_web/
├── app.py              # Flask API backend
├── claude_wrapper.py   # Claude CLI integration
├── web_app.html       # Complete web interface
├── start.py           # Simple startup script
├── requirements.txt   # Python dependencies
└── data/
    └── projects/      # Project directories
        ├── project-1/ # Individual project folder
        │   ├── <generated files>
        │   └── .threads/
        └── project-2/
```

## Troubleshooting

**"Failed to fetch" errors:**
- Make sure the Flask server is running on port 5000
- Install flask-cors: `pip install flask-cors`

**Claude CLI not found:**
- Ensure Claude CLI is installed and in your PATH
- On Windows, check common installation paths

## Migration from Chainlit

This replaces the previous Chainlit-based interface with a custom web application that:
- Eliminates Pydantic validation errors
- Provides better control over UI/UX  
- Reduces complexity and dependencies
- Offers improved mobile responsiveness
- Maintains full compatibility with existing Flask backend
