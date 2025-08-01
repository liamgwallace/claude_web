# Claude Code Configuration Guide

## Overview

This guide provides comprehensive information about configuring Claude Code projects, including CLAUDE.md files, settings, directory structure, and custom instructions.

## Table of Contents

1. [CLAUDE.md Files](#claudemd-files)
2. [Configuration Files and Settings](#configuration-files-and-settings)
3. [Directory Structure](#directory-structure)
4. [Custom Commands](#custom-commands)
5. [MCP Integration](#mcp-integration)
6. [Memory Management](#memory-management)
7. [Best Practices](#best-practices)

## CLAUDE.md Files

### Purpose and Function

CLAUDE.md is a special file that Claude automatically pulls into context when starting a conversation. This makes it an ideal place for:

- Repository etiquette (branch naming, merge vs. rebase, etc.)
- Developer environment setup (pyenv use, compiler preferences)
- Project-specific warnings or behaviors
- Bash commands and core utility functions
- Code style guidelines
- Testing instructions

### File Locations

CLAUDE.md files can be placed in multiple locations with different scopes:

1. **Project Memory**: `./CLAUDE.md` - Team-shared project instructions
2. **User Memory**: `~/.claude/CLAUDE.md` - Personal preferences across all projects
3. **Recursive Discovery**: Claude searches up the directory tree to find CLAUDE.md files

### File Import System

CLAUDE.md files support importing additional files using the `@path/to/import` syntax:

- Both relative and absolute paths are allowed
- Imports from user's home directory enable individual team member instructions
- Maximum import depth of 5 hops
- Imports are not evaluated inside code spans or blocks

### Bootstrap and Management

- Use `/init` command to bootstrap a CLAUDE.md for your codebase
- Use `#` key to quickly add memory items
- Use `/memory` command to edit memory files
- No required format - flexibility in structure is encouraged

## Configuration Files and Settings

### Settings File Hierarchy

Claude Code uses a hierarchical settings system with the following precedence (highest to lowest):

1. **Enterprise policies**
2. **Command line arguments**
3. **Local project settings**
4. **Shared project settings**
5. **User settings**

### Settings File Locations

#### User Settings
- **Location**: `~/.claude/settings.json`
- **Scope**: Apply to all projects globally
- **Usage**: Personal preferences and default configurations

#### Project Settings
- **Shared Settings**: `.claude/settings.json`
  - Checked into source control
  - Shared with team members
  - Contains team-wide configurations
  
- **Local Settings**: `.claude/settings.local.json`
  - Personal settings not checked into git
  - Useful for experimentation and individual preferences
  - Git-ignored by default

#### Enterprise Settings
- **macOS**: `/Library/Application Support/ClaudeCode/managed-settings.json`
- **Linux/WSL**: `/etc/claude-code/managed-settings.json`
- **Windows**: `C:\ProgramData\ClaudeCode\managed-settings.json`

### Configuration Management

Use CLI commands to manage configurations:

```bash
# List all configuration options
claude config list

# Get a specific setting
claude config get setting_name

# Set a project setting
claude config set setting_name value

# Set a global setting
claude config set --global setting_name value

# Add to array settings
claude config add setting_name value

# Remove from settings
claude config remove setting_name
```

### Key Configuration Options

- **Permissions**: Control tool access and capabilities
- **Environment Variables**: Manage API keys and service configurations
- **Model Selection**: Choose between different Claude models
- **Authentication**: Configure API keys and service connections
- **Subagent Configurations**: Define custom AI agents

### Important Environment Variables

- `ANTHROPIC_API_KEY`: API authentication for Anthropic services
- `CLAUDE_CODE_USE_BEDROCK`: Enable AWS Bedrock integration
- `CLAUDE_CODE_USE_VERTEX`: Enable Google Vertex AI integration
- `DISABLE_TELEMETRY`: Opt-out of usage tracking

## Directory Structure

### Project-Level Structure

```
your-project/
├── CLAUDE.md                    # Project instructions and memory
├── .claude/
│   ├── settings.json           # Shared team settings
│   ├── settings.local.json     # Personal settings (git-ignored)
│   ├── commands/               # Custom slash commands
│   │   ├── debug.md           # /debug command
│   │   ├── test.md            # /test command
│   │   └── frontend/          # Namespaced commands
│   │       └── component.md   # /frontend:component command
│   └── agents/                # Project-specific subagents
│       ├── reviewer.md        # Code review agent
│       └── tester.md          # Testing specialist agent
├── .mcp.json                   # MCP server configurations
└── your-project-files...
```

### User-Level Structure

```
~/.claude/
├── CLAUDE.md                   # Global user instructions
├── settings.json              # Global user settings
├── commands/                  # Personal commands (all projects)
│   ├── personal-debug.md     # Personal debugging workflow
│   └── shortcuts/            # Personal shortcuts
│       └── quick-fix.md      # /shortcuts:quick-fix
└── agents/                   # User subagents (all projects)
    ├── assistant.md          # Personal coding assistant
    └── optimizer.md          # Performance optimization agent
```

## Custom Commands

### Creating Custom Commands

Store prompt templates in Markdown files within the `.claude/commands/` folder for repeated workflows:

#### Basic Command Structure

```markdown
---
description: "Debug the current issue"
argument-hint: "Optional description of the problem"
allowed-tools: ["bash", "edit"]
model: "claude-3-5-sonnet-20241022"
---

# Debug Command

Please help me debug the following issue: $ARGUMENTS

Start by examining the recent changes and running any relevant tests.
```

#### Command Features

- **Dynamic Arguments**: Use `$ARGUMENTS` to pass parameters from command invocation
- **Namespacing**: Organize commands in subdirectories (e.g., `.claude/commands/frontend/component.md` creates `/frontend:component`)
- **Tool Permissions**: Specify allowed tools in frontmatter
- **Model Selection**: Override default model for specific commands

#### Command Types

1. **Project Commands**: Stored in `.claude/commands/` and shared with team
2. **User Commands**: Stored in `~/.claude/commands/` and available across all projects

### Built-in Slash Commands

- `/add-dir`: Add working directories
- `/agents`: Manage AI subagents
- `/bug`: Report bugs to Claude Code team
- `/clear`: Clear conversation history
- `/config`: View/modify configuration
- `/help`: Get usage help and list available commands
- `/init`: Bootstrap CLAUDE.md file
- `/memory`: Edit memory files
- `/model`: Select AI model for current session

## MCP Integration

### MCP Configuration File

Create a `.mcp.json` file in your project root for Model Context Protocol server configurations:

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
    }
  }
}
```

### MCP Slash Commands

MCP servers automatically provide slash commands following the format:
`/mcp__<server-name>__<prompt-name>`

### Benefits of Project-Scoped MCP

- **Team Collaboration**: All team members get the same MCP tools
- **Version Control**: Configuration is checked into git
- **Consistency**: Ensures uniform development environment

## Memory Management

### Memory Types and Scope

1. **Project Memory**: Team-shared instructions in project CLAUDE.md
2. **User Memory**: Personal preferences in ~/.claude/CLAUDE.md
3. **Recursive Memory**: Claude searches parent directories for additional CLAUDE.md files

### Memory Best Practices

- **Be Specific**: "Use 2-space indentation" is better than "Format code properly"
- **Use Structure**: Format memories as bullet points under descriptive markdown headings
- **Keep Concise**: Maintain human-readable, focused instructions
- **Regular Updates**: Periodically review and refine instructions

### Quick Memory Management

- **Add Memory**: Use `#` key during conversation to quickly add a memory
- **Edit Memory**: Use `/memory` command to open memory files for editing
- **Bootstrap**: Use `/init` command to create initial CLAUDE.md structure

## Best Practices

### CLAUDE.md Best Practices

1. **Document Key Information**:
   - Bash commands and aliases
   - Core files and utility functions
   - Code style guidelines
   - Testing procedures
   - Build and deployment instructions

2. **Structure Organization**:
   - Use clear markdown headings
   - Group related information together
   - Include examples where helpful
   - Keep instructions actionable

3. **Team Collaboration**:
   - Include repository etiquette guidelines
   - Document branching strategies
   - Specify code review requirements
   - Define merge/rebase preferences

### Configuration Best Practices

1. **Settings Management**:
   - Use project settings for team-shared configurations
   - Keep personal preferences in local settings
   - Document important settings in CLAUDE.md
   - Use environment variables for sensitive data

2. **Command Organization**:
   - Create commands for repetitive workflows
   - Use namespacing for complex command sets
   - Include helpful descriptions and argument hints
   - Test commands thoroughly before sharing

3. **Security Considerations**:
   - Never commit API keys or secrets to git
   - Use environment variables for sensitive configuration
   - Keep personal settings in .local.json files
   - Review enterprise policies for compliance

### Development Workflow

1. **Project Setup**:
   - Run `claude doctor` to verify installation
   - Initialize CLAUDE.md with `/init` command
   - Configure project settings for team consistency
   - Set up MCP servers as needed

2. **Ongoing Maintenance**:
   - Regularly update CLAUDE.md with new insights
   - Refine commands based on usage patterns
   - Review and clean up unused configurations
   - Keep documentation current with project changes

## Programmatic Setup

To programmatically create a Claude Code project with custom instructions:

1. **Create Project Directory Structure**:
   ```bash
   mkdir -p your-project/.claude/{commands,agents}
   ```

2. **Create CLAUDE.md File**:
   ```bash
   cat > your-project/CLAUDE.md << 'EOF'
   # Project Instructions
   
   ## Code Style
   - Use 2-space indentation
   - Follow ESLint configuration
   
   ## Testing
   - Run `npm test` before committing
   - Write tests for new features
   
   ## Common Commands
   - `npm run dev` - Start development server
   - `npm run build` - Build for production
   EOF
   ```

3. **Create Settings File**:
   ```bash
   cat > your-project/.claude/settings.json << 'EOF'
   {
     "permissions": {
       "bash": "allowed",
       "edit": "allowed"
     },
     "model": "claude-3-5-sonnet-20241022"
   }
   EOF
   ```

4. **Create Custom Commands**:
   ```bash
   cat > your-project/.claude/commands/test.md << 'EOF'
   ---
   description: "Run project tests"
   allowed-tools: ["bash"]
   ---
   
   # Test Command
   
   Run the project test suite and analyze any failures:
   
   !npm test
   EOF
   ```

This structure provides Claude with all the context and instructions needed to work effectively within your project.