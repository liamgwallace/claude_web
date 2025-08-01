# Claude Code Settings and Directory Structure

## Overview

This document provides comprehensive information about Claude Code's configuration system, including settings files, directory structure, and programmatic setup for projects.

## Settings Hierarchy and Precedence

Claude Code uses a hierarchical settings system with the following precedence (highest to lowest):

1. **Enterprise Policies** (managed by organization)
2. **Command Line Arguments** (session-specific overrides)
3. **Local Project Settings** (`.claude/settings.local.json`)
4. **Shared Project Settings** (`.claude/settings.json`)
5. **User Settings** (`~/.claude/settings.json`)

## Settings File Locations

### User-Level Settings

#### Primary User Settings
- **File**: `~/.claude/settings.json`
- **Scope**: Global settings applied to all projects
- **Purpose**: Personal defaults and preferences
- **Git Status**: Not checked into version control

**Example User Settings:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "permissions": {
    "bash": "allowed",
    "edit": "allowed",
    "browser": "ask"
  },
  "editor": "code",
  "telemetry": false
}
```

#### User Commands and Agents
- **Commands**: `~/.claude/commands/` - Personal slash commands
- **Agents**: `~/.claude/agents/` - Personal subagents
- **Memory**: `~/.claude/CLAUDE.md` - Global personal instructions

### Project-Level Settings

#### Shared Project Settings
- **File**: `.claude/settings.json`
- **Scope**: Team-shared project configurations
- **Purpose**: Consistent settings across all team members
- **Git Status**: Checked into version control

**Example Project Settings:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "permissions": {
    "bash": "allowed",
    "edit": "allowed",
    "browser": "allowed"
  },
  "allowed-tools": ["bash", "edit", "read", "write"],
  "working-directories": ["./src", "./tests"],
  "environment": {
    "NODE_ENV": "development"
  }
}
```

#### Local Project Settings
- **File**: `.claude/settings.local.json`
- **Scope**: Personal project overrides
- **Purpose**: Individual developer customizations
- **Git Status**: Git-ignored (not shared with team)

**Example Local Settings:**
```json
{
  "permissions": {
    "bash": "allowed"
  },
  "editor": "vim",
  "debug": true,
  "personal-shortcuts": {
    "test-cmd": "npm test --watch"
  }
}
```

### Enterprise Settings

#### Managed Settings Locations
- **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
- **Linux/WSL**: `/etc/claude-code/managed-settings.json`
- **Windows**: `C:\ProgramData\ClaudeCode\managed-settings.json`

**Enterprise Settings Example:**
```json
{
  "policies": {
    "allowed-models": ["claude-3-5-sonnet-20241022"],
    "required-permissions": ["ask"],
    "blocked-tools": ["browser"],
    "max-session-duration": 3600
  },
  "compliance": {
    "audit-logging": true,
    "data-retention": 90
  }
}
```

## Complete Directory Structure

### Project Root Structure
```
your-project/
├── CLAUDE.md                      # Project instructions and context
├── .claude/                       # Claude Code configuration directory
│   ├── settings.json             # Shared team settings (checked in)
│   ├── settings.local.json       # Personal settings (git-ignored)
│   ├── commands/                 # Custom slash commands
│   │   ├── debug.md             # /debug command
│   │   ├── test.md              # /test command
│   │   ├── deploy.md            # /deploy command
│   │   └── frontend/            # Namespaced commands
│   │       ├── component.md     # /frontend:component
│   │       ├── style.md         # /frontend:style
│   │       └── build.md         # /frontend:build
│   ├── agents/                  # Project-specific subagents
│   │   ├── reviewer.md          # Code review specialist
│   │   ├── tester.md            # Testing specialist
│   │   ├── optimizer.md         # Performance optimizer
│   │   └── documenter.md        # Documentation generator
│   └── memory/                  # Additional memory files (optional)
│       ├── architecture.md      # System architecture context
│       ├── conventions.md       # Coding conventions
│       └── troubleshooting.md   # Common issues and solutions
├── .mcp.json                     # Model Context Protocol servers
├── .claudeignore                 # Files to ignore (similar to .gitignore)
└── your-project-files...
```

### User Home Structure
```
~/.claude/
├── CLAUDE.md                     # Global user instructions
├── settings.json                 # Global user settings
├── commands/                     # Personal commands (all projects)
│   ├── personal-debug.md        # Personal debugging workflow
│   ├── quick-fix.md            # Quick fix patterns
│   ├── shortcuts/              # Personal shortcuts
│   │   ├── git.md              # /shortcuts:git
│   │   ├── npm.md              # /shortcuts:npm
│   │   └── docker.md           # /shortcuts:docker
│   └── templates/              # Code templates
│       ├── component.md        # /templates:component
│       ├── test.md             # /templates:test
│       └── api.md              # /templates:api
├── agents/                      # Personal subagents (all projects)
│   ├── assistant.md            # General coding assistant
│   ├── optimizer.md            # Performance optimizer
│   ├── security.md             # Security reviewer
│   └── mentor.md               # Code mentoring agent
└── cache/                      # Claude Code cache files
    ├── sessions/               # Session data
    ├── models/                 # Model cache
    └── temp/                   # Temporary files
```

## Configuration Management

### CLI Configuration Commands

#### Basic Configuration
```bash
# List all configuration options
claude config list

# List project-specific settings
claude config list --project

# List global settings
claude config list --global

# Get specific setting value
claude config get permissions.bash

# Get global setting
claude config get --global model
```

#### Setting Configuration Values
```bash
# Set project setting
claude config set model claude-3-5-sonnet-20241022

# Set global setting
claude config set --global editor "code"

# Set permission level
claude config set permissions.bash allowed

# Set environment variable
claude config set environment.NODE_ENV development
```

#### Array and Object Settings
```bash
# Add to array setting
claude config add allowed-tools bash
claude config add working-directories ./lib

# Remove from array
claude config remove allowed-tools browser
claude config remove working-directories ./temp

# Set nested object values
claude config set permissions.bash allowed
claude config set permissions.edit ask
claude config set permissions.browser denied
```

### Programmatic Configuration

#### Creating Settings Files Programmatically

**Project Settings Setup:**
```bash
#!/bin/bash
# Create project configuration

# Create .claude directory structure
mkdir -p .claude/{commands,agents}

# Create shared project settings
cat > .claude/settings.json << 'EOF'
{
  "model": "claude-3-5-sonnet-20241022",
  "permissions": {
    "bash": "allowed",
    "edit": "allowed",
    "read": "allowed",
    "write": "allowed"
  },
  "allowed-tools": ["bash", "edit", "read", "write", "grep", "find"],
  "working-directories": ["./src", "./tests", "./docs"],
  "environment": {
    "NODE_ENV": "development",
    "DEBUG": "app:*"
  }
}
EOF

# Create git-ignored local settings
cat > .claude/settings.local.json << 'EOF'
{
  "debug": true,
  "verbose": true,
  "personal-shortcuts": {
    "dev-server": "npm run dev",
    "test-watch": "npm test -- --watch"
  }
}
EOF

# Add to .gitignore
echo ".claude/settings.local.json" >> .gitignore
```

**User Settings Setup:**
```bash
#!/bin/bash
# Create user configuration

# Create user .claude directory
mkdir -p ~/.claude/{commands,agents}

# Create user settings
cat > ~/.claude/settings.json << 'EOF'
{
  "model": "claude-3-5-sonnet-20241022",
  "editor": "code",
  "permissions": {
    "bash": "ask",
    "edit": "allowed",
    "browser": "ask"
  },
  "telemetry": false,
  "theme": "dark"
}
EOF
```

## Environment Variables

### Core Environment Variables

#### Authentication
```bash
# Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Alternative authentication methods
export CLAUDE_CODE_USE_BEDROCK=true    # Use AWS Bedrock
export CLAUDE_CODE_USE_VERTEX=true     # Use Google Vertex AI
```

#### Configuration Overrides
```bash
# Disable telemetry
export DISABLE_TELEMETRY=true

# Override settings file location
export CLAUDE_CONFIG_PATH="/custom/path/settings.json"

# Set debug mode
export CLAUDE_DEBUG=true

# Override default model
export CLAUDE_MODEL="claude-3-5-sonnet-20241022"
```

#### Development Variables
```bash
# Enable verbose logging
export CLAUDE_VERBOSE=true

# Custom working directory
export CLAUDE_WORKING_DIR="/path/to/project"

# Override default editor
export CLAUDE_EDITOR="vim"

# Custom cache directory
export CLAUDE_CACHE_DIR="/custom/cache/path"
```

## Configuration Schemas

### Settings Schema

#### Root Settings Object
```json
{
  "model": "string",                    // Model identifier
  "permissions": {                      // Tool permissions
    "bash": "allowed|ask|denied",
    "edit": "allowed|ask|denied",
    "read": "allowed|ask|denied",
    "write": "allowed|ask|denied",
    "browser": "allowed|ask|denied"
  },
  "allowed-tools": ["string"],          // Explicit tool allowlist
  "working-directories": ["string"],    // Allowed working directories
  "environment": {                      // Environment variables
    "KEY": "value"
  },
  "editor": "string",                   // Default editor command
  "debug": boolean,                     // Enable debug mode
  "verbose": boolean,                   // Enable verbose logging
  "telemetry": boolean,                 // Enable telemetry
  "theme": "light|dark|auto"           // UI theme preference
}
```

#### Permission Levels
- **`allowed`**: Always grant permission without asking
- **`ask`**: Prompt user for permission each time
- **`denied`**: Never grant permission

#### Common Tool Names
- `bash` - Execute shell commands
- `edit` - Modify files
- `read` - Read files and directories
- `write` - Create new files
- `browser` - Web browsing capabilities
- `git` - Git version control operations
- `npm` - Node.js package management
- `pip` - Python package management

## MCP Integration

### MCP Configuration File

#### .mcp.json Structure
```json
{
  "servers": {
    "server-name": {
      "command": "executable-path",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "cwd": "/working/directory"
    }
  }
}
```

#### Example MCP Configuration
```json
{
  "servers": {
    "puppeteer": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-puppeteer"],
      "env": {
        "PUPPETEER_SKIP_DOWNLOAD": "true"
      }
    },
    "sentry": {
      "command": "npx", 
      "args": ["@anthropic-ai/mcp-server-sentry"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}"
      }
    },
    "database": {
      "command": "python",
      "args": ["-m", "mcp_server_database"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      },
      "cwd": "./tools/database"
    }
  }
}
```

## Security Considerations

### Settings File Security

#### Sensitive Data Handling
- **Never commit API keys** to version control
- **Use environment variables** for secrets
- **Keep local settings private** with `.local.json` files
- **Review enterprise policies** for compliance requirements

#### File Permissions
```bash
# Secure user settings file
chmod 600 ~/.claude/settings.json

# Secure local project settings
chmod 600 .claude/settings.local.json

# Ensure proper directory permissions
chmod 700 ~/.claude
chmod 700 .claude
```

### Enterprise Compliance

#### Audit Logging
```json
{
  "audit": {
    "enabled": true,
    "log-level": "info",
    "retention-days": 90,
    "include-content": false
  }
}
```

#### Access Controls
```json
{
  "access-control": {
    "required-permissions": ["ask"],
    "blocked-tools": ["browser", "bash"],
    "allowed-models": ["claude-3-5-sonnet-20241022"],
    "session-timeout": 3600
  }
}
```

## Troubleshooting

### Common Configuration Issues

#### Settings Not Loading
1. Check file locations and permissions
2. Verify JSON syntax with validator
3. Ensure proper file encoding (UTF-8)
4. Check for conflicting environment variables

#### Permission Denied Errors
1. Review permission settings in hierarchy
2. Check enterprise policy restrictions
3. Verify file system permissions
4. Test with explicit permission grants

#### Environment Variable Issues
1. Verify variable names and values
2. Check shell environment inheritance
3. Test with explicit exports
4. Review system-specific variable handling

### Diagnostic Commands
```bash
# Check configuration status
claude doctor

# Validate settings files
claude config validate

# Show effective configuration
claude config show-effective

# Test permissions
claude config test-permissions

# Clear cache and reset
claude config reset --cache-only
```

This comprehensive guide provides everything needed to understand and configure Claude Code's settings and directory structure for both individual and team use.