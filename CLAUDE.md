# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple hobby project to create a web interface for interacting with Claude Code using Chainlit. The goal is to build a straightforward MVP that allows users to chat with Claude through a web UI and view generated files without complex architecture.

## Planned Architecture

Based on the PRD in `Documentation/Claude web runner prd.md`, this project will follow a simple structure:

- **Frontend**: Chainlit (provides chat interface out of the box)
- **Backend**: Python with subprocess calls to Claude CLI
- **Storage**: JSON files for chat history and metadata (no database needed)
- **Queue**: Simple Python queue for handling parallel requests
- **File Organization**: Timestamp-based folders for each chat session

## Current Folder Structure

```
claude_web/
├── app.py                    # Flask API backend
├── claude_wrapper.py         # Claude CLI wrapper with session management
├── test_api.py              # Interactive API test client
├── chainlit_app.py          # Chainlit web frontend
├── start_app.py             # Startup script for both backend and frontend
├── .chainlit/
│   └── config.toml          # Chainlit configuration
├── data/
│   └── projects/            # Project directories
│       ├── project-1/       # Individual project folder (Claude working directory)
│       │   ├── <generated files and folders by Claude>
│       │   └── .threads/    # Thread metadata
│       │       ├── thread-1.json  # Thread with session_id, message_count
│       │       ├── thread-2.json
│       │       └── threads.json   # Project thread list
│       └── project-2/       # Another project
│           ├── <generated files and folders>
│           └── .threads/
├── requirements.txt
├── README_CHAINLIT.md       # Frontend documentation
└── Documentation/           # Claude CLI and SDK reference docs
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

## Development Tasks (from PRD)

1. **Read Documentation**: The Documentation folder contains Claude CLI and SDK reference info
2. **Research Chainlit**: Do web search on Chainlit basics and save key info as markdown
3. **Start Simple**: 
   - Create basic Chainlit app that can send messages
   - Add simple Claude CLI wrapper with subprocess
   - Implement JSON storage for chat history
   - Add basic file viewing for generated files

## File Organization Strategy

- **Projects**: Physical folders in `data/projects/<project-name>/` where Claude CLI runs
- **Threads**: Metadata stored in `data/projects/<project-name>/.threads/<thread-id>.json`
- **Session Management**: Each thread stores its Claude session ID for conversation continuity
- **Generated Files**: Claude creates files directly in project root directory
- **Thread Metadata**: Contains session_id, message_count, last_activity (no manual message storage)

## Running the Application

### Quick Start
Use the startup script to run both backend and frontend:
```bash
python start_app.py
```

### Manual Start
1. **Start Flask API Backend** (Terminal 1):
   ```bash
   python app.py
   ```
   API will be available at http://localhost:5000

2. **Start Chainlit Frontend** (Terminal 2):
   ```bash
   chainlit run chainlit_app.py
   ```
   Web interface will be available at http://localhost:8000

### Testing Backend Only
Use the test client for API testing:
```bash
python test_api.py
```

## Application Architecture

### Complete Implementation Status
✅ **Backend API** (Flask)
- Project and thread management
- Claude CLI integration with session management  
- File operations and viewing
- Delete functionality
- Job queue for async processing

✅ **Frontend UI** (Chainlit)
- Project-based organization with action buttons
- Thread management within projects
- Real-time chat with Claude
- File viewing and navigation
- Session state management

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

See `README_CHAINLIT.md` for detailed usage instructions.