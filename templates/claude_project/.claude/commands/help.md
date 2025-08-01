# /help - Project Help Command

Shows helpful information about this project and available commands.

## Usage
```
/help [topic]
```

## Examples
- `/help` - Show general project help
- `/help setup` - Show setup instructions
- `/help commands` - List all available commands

## Implementation

This command provides context-aware help for the current project, including:

- Project overview and purpose
- Setup and installation instructions
- Available custom commands
- Common workflows and tasks
- Troubleshooting tips

The help content is dynamically generated based on the project's CLAUDE.md file and available commands.