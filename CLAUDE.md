# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple hobby project to create a web interface for interacting with Claude Code. The goal is to build a straightforward MVP that allows users to chat with Claude through a modern web UI and view generated files without complex architecture.

## Current Architecture

This project follows a clean, simple structure:

- **Frontend**: Custom HTML/CSS/JS web interface (`web/` directory)
- **Backend**: Python Flask API with subprocess calls to Claude CLI
- **Storage**: JSON files for chat history and metadata (no database needed)
- **Queue**: Simple Python queue for handling parallel requests
- **File Organization**: Project-based folders for organizing chat sessions

## Current Folder Structure

```
claude_web/
├── scripts/
│   ├── start.py              # Main startup script (launches Flask on port 8000)
│   └── test_api.py           # API testing client
├── src/                      # Backend source code
│   ├── app.py                # Flask API backend
│   ├── claude_wrapper.py     # Claude CLI wrapper with session management
│   ├── server.py             # Alternative server entry point
│   └── template_manager.py   # Claude project template system
├── web/                      # Frontend assets
│   ├── index.html            # Main web application
│   ├── css/
│   │   └── styles.css        # Application styles
│   └── js/
│       └── app.js            # Application JavaScript
├── templates/                # Claude project templates
│   └── claude_project/       # Default Claude Code project template
│       ├── CLAUDE.md         # Project instructions
│       ├── .claude/          # Claude configuration
│       │   ├── settings.json
│       │   ├── settings.local.json
│       │   └── commands/     # Custom slash commands
│       ├── .gitignore        # Git ignore rules
│       └── README.md         # Project documentation
├── data/
│   └── projects/             # Project working directories
│       ├── project-1/        # Individual project folder (Claude workspace)
│       │   ├── <generated files by Claude>
│       │   ├── CLAUDE.md     # Auto-generated from template
│       │   ├── .claude/      # Claude configuration
│       │   └── .threads/     # Thread metadata storage
│       │       ├── thread-1.json
│       │       └── threads.json
│       └── project-2/
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── README.md                 # Main documentation
├── CLAUDE.md                 # This file
├── CONTRIBUTING.md           # Contribution guidelines
├── LICENSE                   # Project license
└── Documentation/            # Claude CLI and SDK reference docs
    ├── Claude Code CLI.md
    ├── Claude Code SDK.md
    ├── Claude web runner prd.md
    └── Chainlit Research.md
```

## Core Development Approach

- Keep it simple and straightforward - focus on getting a working MVP quickly
- Use subprocess calls to interact with Claude CLI directly
- Save all outputs to JSON files for persistence
- Handle errors with simple try/catch blocks
- Don't over-engineer - get it working first

## Claude CLI Integration with Session Management

The project uses Claude CLI's built-in session management instead of manually storing chat history. Each thread corresponds to a unique Claude session that persists conversation context.

### Session Management Flow
1. **New Thread**: `claude -p "message" --output-format json` creates new session
2. **Continuing Thread**: `claude --resume <session-id> -p "message" --output-format json` 
3. **Session ID Storage**: Captured from JSON response and stored in thread metadata
4. **Conversation Persistence**: Claude CLI automatically maintains chat history per session

### Important CLI Commands
- `claude -p "query" --output-format json` - Start new session (non-interactive mode)
- `claude --resume <session-id> -p "query" --output-format json` - Resume existing session
- `claude --verbose` - Enable verbose logging for debugging

### Key Benefits
- **Automatic History**: Claude CLI manages conversation history internally
- **Session Isolation**: Each thread has its own independent Claude session
- **Context Preservation**: Full conversation context maintained across API calls
- **No Manual Storage**: No need to manually store/retrieve message history

## Key Components

1. **Flask Backend** (`src/app.py`): REST API + serves static files
2. **Claude Integration** (`src/claude_wrapper.py`): Session management with CLI
3. **Template System** (`src/template_manager.py`): Auto-initialization of Claude projects
4. **Web Frontend** (`web/`): Modern HTML/CSS/JS interface
5. **Startup Script** (`scripts/start.py`): Dependency checks + launches Flask
6. **Project Templates** (`templates/`): Claude Code configuration templates

## File Organization Strategy

- **Projects**: Physical folders in `data/projects/<project-name>/` where Claude CLI runs
- **Threads**: Metadata stored in `data/projects/<project-name>/.threads/<thread-id>.json`
- **Session Management**: Each thread stores its Claude session ID for conversation continuity
- **Generated Files**: Claude creates files directly in project root directory
- **Thread Metadata**: Contains session_id, message_count, last_activity (no manual message storage)

## Running the Application

### Quick Start
Use the startup script to run the application:
```bash
python scripts/start.py
```

### Manual Start
1. **Start Flask Application**:
   ```bash
   cd src && python server.py 8000
   ```
   Both API and web interface will be available at http://localhost:8000

### Testing Backend Only
Use the test client for API testing:
```bash
python scripts/test_api.py
```

## Application Architecture

### Complete Implementation Status
✅ **Backend API** (Flask)
- Project and thread management
- Claude CLI integration with session management  
- File operations and viewing
- Delete functionality
- Job queue for async processing

✅ **Frontend UI** (Custom Web Interface)
- Project-based organization with action buttons
- Thread management within projects
- Real-time chat with Claude
- File viewing and navigation with syntax highlighting
- Session state management
- Mobile-responsive design

✅ **Integration Layer**
- API client for frontend-backend communication
- Session management and error handling
- File tree display and project navigation

### Key Features
- **Project Management**: Create/select projects (working directories)
- **Thread Management**: Multiple chat conversations per project
- **Claude Integration**: Full Claude CLI session management with --resume
- **File Operations**: View generated files and project structure  
- **Delete Operations**: Clean removal of projects and threads
- **Real-time UI**: Responsive web interface with action buttons

## Current Status

The project is **complete and functional** with both backend API and frontend UI implemented. Users can:
1. Create and manage projects
2. Create and manage threads within projects  
3. Chat with Claude with full session persistence
4. View files created by Claude
5. Delete projects and threads safely

See `README.md` for detailed usage instructions and features.