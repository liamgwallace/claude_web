# Claude Code Commands and MCP Integration

## Overview

This document covers Claude Code's command system, including built-in slash commands, custom command creation, and Model Context Protocol (MCP) integration for extending Claude's capabilities.

## Table of Contents

1. [Slash Commands Overview](#slash-commands-overview)
2. [Built-in Commands](#built-in-commands)
3. [Custom Commands](#custom-commands)
4. [MCP Integration](#mcp-integration)
5. [Command Development](#command-development)
6. [Best Practices](#best-practices)

## Slash Commands Overview

Slash commands provide a quick way to invoke specific functionality within Claude Code. Commands are triggered by typing `/` followed by the command name.

### Command Types

1. **Built-in Commands**: Core Claude Code functionality
2. **Project Commands**: Custom commands stored in `.claude/commands/`
3. **User Commands**: Personal commands stored in `~/.claude/commands/`
4. **MCP Commands**: Commands provided by MCP servers

### Command Discovery

Commands are discovered in the following order:
1. Built-in commands (highest priority)
2. MCP server commands
3. Project commands (shared with team)
4. User commands (personal)

## Built-in Commands

### Core Commands

#### `/help`
- **Purpose**: List available commands and usage information
- **Usage**: `/help [command-name]`
- **Examples**:
  - `/help` - List all available commands
  - `/help config` - Show help for config command

#### `/config`
- **Purpose**: View and modify configuration settings
- **Usage**: `/config [action] [key] [value]`
- **Actions**:
  - `list` - Show all settings
  - `get <key>` - Get specific setting
  - `set <key> <value>` - Set configuration value
  - `add <key> <value>` - Add to array setting
  - `remove <key> <value>` - Remove from array setting
- **Examples**:
  - `/config list` - Show all current settings
  - `/config set model claude-3-5-sonnet-20241022`
  - `/config add allowed-tools bash`

### Session Management

#### `/clear`
- **Purpose**: Clear current conversation history
- **Usage**: `/clear`
- **Effect**: Starts fresh conversation while keeping session context

#### `/model`
- **Purpose**: Select AI model for current session
- **Usage**: `/model [model-name]`
- **Examples**:
  - `/model` - Show current model
  - `/model claude-3-5-sonnet-20241022` - Switch to specific model

### Memory and Context

#### `/memory`
- **Purpose**: Edit memory files (CLAUDE.md)
- **Usage**: `/memory [type]`
- **Types**:
  - `project` - Edit project CLAUDE.md
  - `user` - Edit user CLAUDE.md
- **Examples**:
  - `/memory` - Edit current project memory
  - `/memory user` - Edit personal memory file

#### `/init`
- **Purpose**: Bootstrap CLAUDE.md file for project
- **Usage**: `/init`
- **Effect**: Creates initial CLAUDE.md template

### Directory Management

#### `/add-dir`
- **Purpose**: Add additional working directories
- **Usage**: `/add-dir <path>`
- **Examples**:
  - `/add-dir ./lib` - Add lib directory to working set
  - `/add-dir ../shared` - Add sibling directory

### Agent Management

#### `/agents`
- **Purpose**: Manage AI subagents
- **Usage**: `/agents [action] [agent-name]`
- **Actions**:
  - `list` - Show available agents
  - `create <name>` - Create new agent
  - `edit <name>` - Edit existing agent
  - `delete <name>` - Remove agent
- **Examples**:
  - `/agents list` - Show all agents
  - `/agents create reviewer` - Create code review agent

### Utility Commands

#### `/bug`
- **Purpose**: Report bugs to Claude Code team
- **Usage**: `/bug <description>`
- **Example**: `/bug Session not resuming properly after restart`

## Custom Commands

### Command Structure

Custom commands are Markdown files with optional YAML frontmatter for configuration.

#### Basic Command Template
```markdown
---
description: "Brief description of what this command does"
argument-hint: "Description of expected arguments"
allowed-tools: ["bash", "edit", "read"]
model: "claude-3-5-sonnet-20241022"
---

# Command Name

Command instructions and prompt template.

Use $ARGUMENTS to reference command arguments.

## Example Usage
Provide examples of how to use this command.
```

#### Command Frontmatter Options

```yaml
---
description: "Human-readable command description"
argument-hint: "Hint for command arguments" 
allowed-tools: ["bash", "edit", "read", "write"]
model: "claude-3-5-sonnet-20241022"
working-directories: ["./src", "./tests"]
environment:
  NODE_ENV: "development"
  DEBUG: "app:*"
permissions:
  bash: "allowed"
  edit: "ask"
---
```

### Command Examples

#### Debug Command
**File**: `.claude/commands/debug.md`
```markdown
---
description: "Debug current issue with systematic approach"
argument-hint: "Description of the problem or error"
allowed-tools: ["bash", "edit", "read"]
---

# Debug Command

I need to debug the following issue: $ARGUMENTS

Please follow this systematic approach:

1. **Identify the Problem**
   - Examine error messages and logs
   - Identify the specific component or functionality affected

2. **Reproduce the Issue**
   - Create minimal reproduction steps
   - Verify the issue exists in current state

3. **Investigate Root Cause**
   - Check recent changes in git history
   - Review relevant code paths
   - Run diagnostic commands

4. **Implement Fix**
   - Create focused solution
   - Test the fix thoroughly
   - Ensure no regression introduced

5. **Verify Resolution**
   - Run full test suite
   - Test edge cases
   - Document the solution

Start by examining the current state and gathering information about: $ARGUMENTS
```

#### Test Command
**File**: `.claude/commands/test.md`
```markdown
---
description: "Run comprehensive test suite with analysis"
argument-hint: "Specific test pattern or component to focus on"
allowed-tools: ["bash", "read"]
---

# Test Command

Run tests and analyze results for: $ARGUMENTS

## Test Execution Plan

1. **Run Test Suite**
   ```bash
   npm test $ARGUMENTS
   ```

2. **Analyze Results**
   - Review test output for failures
   - Check coverage reports
   - Identify flaky tests

3. **Fix Issues**
   - Address failing tests
   - Improve test coverage where needed
   - Optimize slow tests

4. **Verify Quality**
   - Ensure all tests pass
   - Check coverage thresholds
   - Review test quality and maintainability

Focus on: $ARGUMENTS
```

#### Component Generator
**File**: `.claude/commands/frontend/component.md`
```markdown
---
description: "Generate React component with tests and styles"
argument-hint: "Component name and description"
allowed-tools: ["write", "edit"]
model: "claude-3-5-sonnet-20241022"
---

# Component Generator

Create a new React component: $ARGUMENTS

## Component Structure

Generate the following files:
1. **Component File**: `src/components/[ComponentName]/[ComponentName].tsx`
2. **Test File**: `src/components/[ComponentName]/[ComponentName].test.tsx`
3. **Style File**: `src/components/[ComponentName]/[ComponentName].module.css`
4. **Index File**: `src/components/[ComponentName]/index.ts`

## Requirements

- Use TypeScript with proper type definitions
- Include PropTypes or TypeScript interfaces
- Write comprehensive tests with React Testing Library
- Follow accessibility guidelines
- Use CSS Modules for styling
- Include proper documentation comments

## Component Specifications
$ARGUMENTS

Create a production-ready component following project conventions.
```

### Namespaced Commands

Organize commands in subdirectories for better organization:

```
.claude/commands/
├── debug.md              # /debug
├── test.md               # /test
├── frontend/             # Frontend namespace
│   ├── component.md      # /frontend:component
│   ├── hook.md           # /frontend:hook
│   └── style.md          # /frontend:style
├── backend/              # Backend namespace
│   ├── api.md            # /backend:api
│   ├── model.md          # /backend:model
│   └── migration.md      # /backend:migration
└── deploy/               # Deployment namespace
    ├── staging.md        # /deploy:staging
    ├── production.md     # /deploy:production
    └── rollback.md       # /deploy:rollback
```

## MCP Integration

### MCP Overview

Model Context Protocol (MCP) allows Claude Code to integrate with external tools and services through standardized server interfaces.

### MCP Configuration

#### .mcp.json Structure
```json
{
  "servers": {
    "server-name": {
      "command": "executable-command",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "cwd": "/working/directory",
      "timeout": 30000
    }
  }
}
```

#### Common MCP Servers

**Puppeteer Server** (Web Automation):
```json
{
  "servers": {
    "puppeteer": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-puppeteer"],
      "env": {
        "PUPPETEER_SKIP_DOWNLOAD": "true"
      }
    }
  }
}
```

**Sentry Server** (Error Monitoring):
```json
{
  "servers": {
    "sentry": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-sentry"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}",
        "SENTRY_ORG": "your-org",
        "SENTRY_PROJECT": "your-project"
      }
    }
  }
}
```

**Database Server** (Database Operations):
```json
{
  "servers": {
    "database": {
      "command": "python",
      "args": ["-m", "mcp_server_database"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

**GitHub Server** (Repository Management):
```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_REPO": "owner/repo"
      }
    }
  }
}
```

### MCP Commands

MCP servers automatically provide slash commands following the format:
`/mcp__<server-name>__<prompt-name>`

#### Example MCP Commands

**Puppeteer Commands**:
- `/mcp__puppeteer__screenshot` - Take website screenshot
- `/mcp__puppeteer__scrape` - Extract website content
- `/mcp__puppeteer__click` - Simulate user interactions

**Sentry Commands**:
- `/mcp__sentry__issues` - List recent issues
- `/mcp__sentry__search` - Search error logs
- `/mcp__sentry__resolve` - Mark issues as resolved

**Database Commands**:
- `/mcp__database__query` - Execute database queries
- `/mcp__database__schema` - Inspect database schema
- `/mcp__database__migrate` - Run database migrations

### Custom MCP Servers

#### Creating Simple MCP Server

**server.py**:
```python
#!/usr/bin/env python3
import asyncio
import json
import sys
from typing import Dict, Any

class SimpleMCPServer:
    def __init__(self):
        self.prompts = {
            "hello": {
                "name": "hello",
                "description": "Say hello with custom message",
                "arguments": [
                    {
                        "name": "message",
                        "description": "Custom message to include",
                        "required": False
                    }
                ]
            }
        }
        
        self.tools = {
            "echo": {
                "name": "echo",
                "description": "Echo a message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            }
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        
        if method == "prompts/list":
            return {
                "prompts": list(self.prompts.values())
            }
        elif method == "prompts/get":
            name = request["params"]["name"]
            return {"prompt": self.prompts.get(name)}
        elif method == "tools/list":
            return {
                "tools": list(self.tools.values())
            }
        elif method == "tools/call":
            return await self.call_tool(request["params"])
        
        return {"error": "Method not found"}

    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params["name"]
        arguments = params["arguments"]
        
        if name == "echo":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Echo: {arguments.get('message', '')}"
                    }
                ]
            }
        
        return {"error": "Tool not found"}

async def main():
    server = SimpleMCPServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
```

**MCP Configuration**:
```json
{
  "servers": {
    "simple": {
      "command": "python",
      "args": ["./tools/simple_mcp_server.py"],
      "cwd": "."
    }
  }
}
```

## Command Development

### Development Workflow

1. **Create Command File**
   ```bash
   touch .claude/commands/my-command.md
   ```

2. **Define Command Structure**
   ```markdown
   ---
   description: "Command description"
   allowed-tools: ["bash", "edit"]
   ---
   
   # My Command
   
   Command implementation with $ARGUMENTS
   ```

3. **Test Command**
   - Use `/help` to verify command appears
   - Test with various argument patterns
   - Verify tool permissions work correctly

4. **Iterate and Improve**
   - Refine prompt based on usage
   - Add error handling
   - Update documentation

### Command Testing

#### Manual Testing
```bash
# List commands to verify command appears
claude -c "/help"

# Test command with arguments
claude -c "/my-command test argument"

# Test command without arguments
claude -c "/my-command"
```

#### Automated Testing
Create test scripts for complex commands:

```bash
#!/bin/bash
# test-commands.sh

echo "Testing debug command..."
claude -p "/debug Cannot connect to database" --output-format json > debug-test.json

echo "Testing component command..."
claude -p "/frontend:component Button A reusable button component" --output-format json > component-test.json

echo "Validating outputs..."
if grep -q "error" debug-test.json; then
    echo "Debug command failed"
    exit 1
fi

echo "All command tests passed"
```

### Command Optimization

#### Performance Considerations
- Keep command prompts focused and specific
- Use appropriate tool permissions
- Avoid unnecessary file operations
- Cache results where appropriate

#### Error Handling
```markdown
---
description: "Robust command with error handling"
allowed-tools: ["bash", "read"]
---

# Robust Command

Handle the following request: $ARGUMENTS

## Error Handling Strategy

1. **Validate Input**
   - Check if required arguments are provided
   - Validate argument format and constraints

2. **Graceful Degradation**
   - Provide helpful error messages
   - Suggest alternative approaches
   - Fall back to simpler methods if needed

3. **Recovery Options**
   - Offer troubleshooting steps
   - Provide manual alternatives
   - Log issues for future improvement

If no arguments provided: Please specify what you'd like me to help with.
If invalid arguments: Please check the argument format and try again.
```

## Best Practices

### Command Design

#### Clear and Specific Prompts
- Use specific, actionable language
- Include examples and expected outputs
- Define success criteria clearly

#### Argument Handling
- Always handle the case when no arguments are provided
- Validate arguments before processing
- Provide helpful hints about expected input format

#### Tool Usage
- Request only necessary tool permissions
- Use tools efficiently and safely
- Handle tool failures gracefully

### Organization

#### Command Naming
- Use descriptive, memorable names
- Follow consistent naming conventions
- Use namespaces for related commands

#### File Structure
- Group related commands in directories
- Use consistent file naming (kebab-case.md)
- Include clear documentation in each command

#### Version Control
- Commit command files to share with team
- Use meaningful commit messages for command changes
- Document command purposes in commit descriptions

### Security

#### Permission Management
- Grant minimal necessary permissions
- Use "ask" permission for sensitive operations
- Review permissions regularly

#### Sensitive Data
- Never include secrets in command files
- Use environment variables for sensitive configuration
- Validate user input to prevent command injection

#### Access Control
- Limit command access appropriately
- Use project vs. user commands strategically
- Consider enterprise policy requirements

### Documentation

#### Command Documentation
- Include clear descriptions in frontmatter
- Provide usage examples in command body
- Document expected outcomes and side effects

#### Team Communication
- Share new commands with team members
- Document command purposes and use cases
- Maintain command changelog for important updates

This comprehensive guide covers all aspects of Claude Code's command system and MCP integration, providing everything needed to create, manage, and optimize commands for enhanced development workflows.