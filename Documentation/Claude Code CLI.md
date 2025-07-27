Output Markdown
Please enter the URL of a web page

Source Web Page
https://docs.anthropic.com/en/docs/claude-code/cli-reference
Include Title
Ignore Links
Clean / Filter
# CLI reference - Anthropic
CLI commands
------------



* Command: claude
  * Description: Start interactive REPL
  * Example: claude
* Command: claude "query"
  * Description: Start REPL with initial prompt
  * Example: claude "explain this project"
* Command: claude -p "query"
  * Description: Query via SDK, then exit
  * Example: claude -p "explain this function"
* Command: cat file | claude -p "query"
  * Description: Process piped content
  * Example: cat logs.txt | claude -p "explain"
* Command: claude -c
  * Description: Continue most recent conversation
  * Example: claude -c
* Command: claude -c -p "query"
  * Description: Continue via SDK
  * Example: claude -c -p "Check for type errors"
* Command: claude -r "<session-id>" "query"
  * Description: Resume session by ID
  * Example: claude -r "abc123" "Finish this PR"
* Command: claude update
  * Description: Update to latest version
  * Example: claude update
* Command: claude mcp
  * Description: Configure Model Context Protocol (MCP) servers
  * Example: See the Claude Code MCP documentation.


CLI flags
---------

Customize Claude Code’s behavior with these command-line flags:



* Flag: --add-dir
  * Description: Add additional working directories for Claude to access (validates each path exists as a directory)
  * Example: claude --add-dir ../apps ../lib
* Flag: --allowedTools
  * Description: A list of tools that should be allowed without prompting the user for permission, in addition to settings.json files
  * Example: "Bash(git log:*)" "Bash(git diff:*)" "Read"
* Flag: --disallowedTools
  * Description: A list of tools that should be disallowed without prompting the user for permission, in addition to settings.json files
  * Example: "Bash(git log:*)" "Bash(git diff:*)" "Edit"
* Flag: --print, -p
  * Description: Print response without interactive mode (see SDK documentation for programmatic usage details)
  * Example: claude -p "query"
* Flag: --output-format
  * Description: Specify output format for print mode (options: text, json, stream-json)
  * Example: claude -p "query" --output-format json
* Flag: --input-format
  * Description: Specify input format for print mode (options: text, stream-json)
  * Example: claude -p --output-format json --input-format stream-json
* Flag: --verbose
  * Description: Enable verbose logging, shows full turn-by-turn output (helpful for debugging in both print and interactive modes)
  * Example: claude --verbose
* Flag: --max-turns
  * Description: Limit the number of agentic turns in non-interactive mode
  * Example: claude -p --max-turns 3 "query"
* Flag: --model
  * Description: Sets the model for the current session with an alias for the latest model (sonnet or opus) or a model’s full name
  * Example: claude --model claude-sonnet-4-20250514
* Flag: --permission-mode
  * Description: Begin in a specified permission mode
  * Example: claude --permission-mode plan
* Flag: --permission-prompt-tool
  * Description: Specify an MCP tool to handle permission prompts in non-interactive mode
  * Example: claude -p --permission-prompt-tool mcp_auth_tool "query"
* Flag: --resume
  * Description: Resume a specific session by ID, or by choosing in interactive mode
  * Example: claude --resume abc123 "query"
* Flag: --continue
  * Description: Load the most recent conversation in the current directory
  * Example: claude --continue
* Flag: --dangerously-skip-permissions
  * Description: Skip permission prompts (use with caution)
  * Example: claude --dangerously-skip-permissions


For detailed information about print mode (`-p`) including output formats, streaming, verbose logging, and programmatic usage, see the [SDK documentation](https://docs.anthropic.com/en/docs/claude-code/sdk).

See also
--------

*   [Interactive mode](https://docs.anthropic.com/en/docs/claude-code/interactive-mode) - Shortcuts, input modes, and interactive features
*   [Slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) - Interactive session commands
*   [Quickstart guide](https://docs.anthropic.com/en/docs/claude-code/quickstart) - Getting started with Claude Code
*   [Common workflows](https://docs.anthropic.com/en/docs/claude-code/common-workflows) - Advanced workflows and patterns
*   [Settings](https://docs.anthropic.com/en/docs/claude-code/settings) - Configuration options
*   [SDK documentation](https://docs.anthropic.com/en/docs/claude-code/sdk) - Programmatic usage and integrations
Uses heroku, turndown, Readability and jsdom. Source on github.