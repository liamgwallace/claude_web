**Product Requirements Document (PRD): Claude Project Runner with Project Management**

---

**Project Overview**

This is a simple hobby project to create a web interface for interacting with Claude Code with project-based organization. Keep it simple, straightforward, and focused on getting a working MVP quickly. The interface allows users to create projects, manage multiple chat threads within each project, and have Claude Code work in the appropriate project directories.

**Target User**

Hobbyists and developers who want a simple web interface to interact with Claude Code with organized project management, allowing them to separate different coding projects and maintain multiple conversation threads within each project.

**High-Level Features**

* Simple web interface using Chainlit with project sidebar
* Project-based organization with multiple chat threads per project
* JSON file storage for projects and chat history (no database needed)
* Claude CLI spawns in corresponding project directories
* File management and viewing within project contexts

---

**Enhanced Folder Structure**

```
claude-runner/
├── app.py                 # Main Chainlit app
├── claude_wrapper.py      # Claude CLI wrapper with project context
├── data/
│   ├── projects.json      # Project metadata and chat threads
│   └── projects/          # Project directories
│       ├── project-1/     # Individual project folder
│       │   ├── <generated files and folders>
│       │   └── .claude/   # Claude-specific metadata for this project
│       └── project-2/     # Another project folder
│           ├── <generated files and folders>
│           └── .claude/
├── requirements.txt
└── README.md
```

---

**Project-Based Architecture**

* Chainlit provides the web interface with project sidebar
* Left sidebar shows list of projects with + button to create new projects
* Each project contains multiple chat threads/conversations
* Python wrapper calls Claude CLI in the appropriate project directory
* JSON files store project metadata and chat history per project
* Generated files are saved in their respective project folders

---

**Enhanced Web UI (Chainlit)**

* **Left Sidebar**: 
  - List of all projects
  - + button to create new project
  - Each project shows its chat threads
  - + button to create new thread within a project
* **Main Chat Interface**: Standard Chainlit chat interface for messaging Claude
* **File Viewer**: View and open generated files within the current project context
* **Project Context**: All Claude operations happen within the selected project's directory

---

**Core Functionality**

* **Project Management**:
  - Create new projects (creates folder in `data/projects/`)
  - Select active project from sidebar
  - Each project maintains its own file structure
* **Thread Management**:
  - Create multiple chat threads within each project
  - Switch between threads within the same project
  - Each thread maintains separate chat history
* **Claude Integration**:
  - Claude CLI spawns with `cwd` set to the current project directory
  - All file operations happen within the project context
  - Generated files are saved in the appropriate project folder

---

**Simple Tech Stack**

* **Frontend**: Chainlit (provides chat interface out of the box)
* **Backend**: Python with basic subprocess calls to Claude CLI
* **Storage**: JSON files (no database needed)
* **Queue**: Simple Python queue for handling parallel requests
* **Deployment**: Basic Python app, optionally containerized later

---

**Data Structure**

**projects.json structure:**
```json
{
  "projects": {
    "project-1": {
      "name": "My First Project",
      "created": "2024-01-01T00:00:00Z",
      "threads": {
        "thread-1": {
          "name": "Initial Setup",
          "created": "2024-01-01T00:00:00Z",
          "messages": [...chat history...]
        },
        "thread-2": {
          "name": "Feature Development",
          "created": "2024-01-01T01:00:00Z", 
          "messages": [...chat history...]
        }
      }
    }
  }
}
```

---

**Keep It Simple**

* Use project-based folders with thread organization
* Call Claude CLI with `cwd` set to project directory
* Save all chat data to projects.json file
* Create physical project folders when projects are created
* Handle errors with simple try/catch blocks
* Don't over-engineer - focus on getting it working first

---

**Next Steps**

1. **Read Documentation**: Check the Documentation folder for Claude CLI info (especially --resume and -p flags)
2. **Light Chainlit Research**: Do a quick web search on Chainlit basics and save key info as markdown
3. **Start Simple**: 
   - Create basic Chainlit app with project sidebar
   - Add project creation/selection functionality
   - Add thread management within projects
   - Add Claude CLI wrapper with project context (cwd)
   - Implement JSON storage for projects and threads
   - Add basic file viewing for generated files within project context

**MVP Goal**: A working web interface with project organization that allows users to create projects, manage chat threads within those projects, and have Claude Code work in the appropriate project directories. Keep it simple and get it working first!

---

Let’s build something cool!
