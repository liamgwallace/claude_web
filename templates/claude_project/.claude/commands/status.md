# /status - Project Status Command

Shows the current status of the project including file changes, git status, and development environment.

## Usage
```
/status [--detailed]
```

## Examples
- `/status` - Show basic project status
- `/status --detailed` - Show detailed status with file listings

## Implementation

This command provides:

- Git repository status (if applicable)
- Recently modified files
- Current branch information
- Pending changes or uncommitted work
- Development server status
- Any running processes related to the project

Helps quickly assess the current state of the project before making changes.