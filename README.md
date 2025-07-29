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

### Advanced Features Implementation

**🎨 Syntax Highlighting (Prism.js)**
- **CDN Integration**: Loads Prism.js components on demand
- **50+ Languages**: Automatic language detection from file extensions
- **Line Numbers**: Professional code display with line numbering
- **Themes**: Clean, readable syntax highlighting theme

```html
<!-- Auto-loaded based on file type -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
```

**📱 Mobile Optimization**
- **Viewport Handling**: Prevents zoom on input focus
- **Touch Targets**: Minimum 44px touch areas for accessibility
- **Keyboard Management**: Smart virtual keyboard handling
- **Pull-to-Refresh Prevention**: Avoids accidental page reloads
- **Responsive Typography**: Scales appropriately across devices

**✏️ In-Browser File Editing**
- **Real-time Validation**: Checks for unsaved changes
- **Auto-save Protection**: Prevents accidental data loss
- **Keyboard Shortcuts**: Standard editing shortcuts (Ctrl+S, Escape)
- **Visual Feedback**: Clear edit/view mode indicators

### Security & Safety Features

**File Operations**
- **Path Traversal Protection**: Prevents access outside project directories
- **File Type Validation**: Safe handling of binary vs text files
- **Size Limits**: Reasonable file size restrictions
- **Backup on Edit**: Preserves original content during editing

**Error Handling**
- **Graceful Degradation**: Continues operation when non-critical features fail
- **User Feedback**: Clear error messages with actionable guidance
- **Recovery Options**: Automatic retry and fallback mechanisms
- **Debug Information**: Detailed logging for troubleshooting

### Performance Optimizations

**Frontend**
- **Lazy Loading**: CDN resources loaded only when needed
- **Efficient DOM Updates**: Minimal reflows and repaints
- **Memory Management**: Proper cleanup of event listeners
- **Caching Strategy**: Smart use of browser cache for static assets

**Backend**
- **Process Management**: Efficient subprocess handling for Claude CLI
- **Resource Cleanup**: Proper cleanup of temporary files and processes
- **Connection Pooling**: Efficient handling of concurrent requests
- **File System Optimization**: Minimal disk I/O with smart caching

### API Documentation

**Core Endpoints**
```
GET  /projects                              # List all projects
POST /project/new                           # Create new project
GET  /project/:name/threads                 # Get project threads
POST /project/:name/thread/new              # Create new thread
POST /project/:name/thread/:id/message      # Send message to Claude
GET  /project/:name/files                   # Get project file tree
GET  /project/:name/file?path=:path         # View specific file
POST /project/:name/file/:path/save         # Save file content
DELETE /project/:name/thread/:id            # Delete thread
DELETE /project/:name                       # Delete project
GET  /status/:job_id                        # Get async job status
```

**Response Formats**
- **Success**: `{"success": true, "data": {...}}`
- **Error**: `{"success": false, "error": "message", "details": {...}}`
- **Async**: `{"job_id": "uuid", "status": "queued"}`

---

## 🚀 Development & Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd claude_web

# Install dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_DEBUG=1
python start.py
```

### Contributing Guidelines
- 🧪 **Test thoroughly** on both desktop and mobile
- 📱 **Mobile-first** - always test mobile experience
- 🎨 **Maintain consistency** with existing UI patterns
- 🔧 **Document changes** - update README for new features
- 🛡️ **Security first** - validate all user inputs

### Future Roadmap
- 🌙 **Dark Mode** - Theme switching capability
- 🔍 **Search** - Global search across projects and conversations
- 📊 **Analytics** - Usage statistics and insights
- 🔄 **Sync** - Cloud synchronization for projects
- 🎯 **Templates** - Project templates for common workflows

---

**Built with ❤️ for the Claude Code community**

*Claude Web Runner transforms Claude Code into a powerful, accessible web platform that works everywhere - from your desktop to your phone. Experience the future of AI-powered development with professional project management, advanced file operations, and a mobile-first design that never compromises on functionality.*
