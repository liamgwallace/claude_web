# Claude Code SDK - Anthropic
The Claude Code SDK enables running Claude Code as a subprocess, providing a way to build AI-powered coding assistants and tools that leverage Claude’s capabilities.

The SDK is available for command line, TypeScript, and Python usage.

Authentication
--------------

The Claude Code SDK supports multiple authentication methods:

### Anthropic API key

To use the Claude Code SDK directly with Anthropic’s API, we recommend creating a dedicated API key:

1.  Create an Anthropic API key in the [Anthropic Console](https://console.anthropic.com/)
2.  Then, set the `ANTHROPIC_API_KEY` environment variable. We recommend storing this key securely (e.g., using a Github [secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions))

### Third-Party API credentials

The SDK also supports third-party API providers:

*   **Amazon Bedrock**: Set `CLAUDE_CODE_USE_BEDROCK=1` environment variable and configure AWS credentials
*   **Google Vertex AI**: Set `CLAUDE_CODE_USE_VERTEX=1` environment variable and configure Google Cloud credentials

For detailed configuration instructions for third-party providers, see the [Amazon Bedrock](https://docs.anthropic.com/en/docs/claude-code/amazon-bedrock) and [Google Vertex AI](https://docs.anthropic.com/en/docs/claude-code/google-vertex-ai) documentation.

Basic SDK usage
---------------

The Claude Code SDK allows you to use Claude Code in non-interactive mode from your applications.

### Command line

Here are a few basic examples for the command line SDK:

### TypeScript

The TypeScript SDK is included in the main [`@anthropic-ai/claude-code`](https://www.npmjs.com/package/@anthropic-ai/claude-code) package on NPM:

The TypeScript SDK accepts all arguments supported by the command line SDK, as well as:



* Argument: abortController
  * Description: Abort controller
  * Default: new AbortController()
* Argument: cwd
  * Description: Current working directory
  * Default: process.cwd()
* Argument: executable
  * Description: Which JavaScript runtime to use
  * Default: node when running with Node.js, bun when running with Bun
* Argument: executableArgs
  * Description: Arguments to pass to the executable
  * Default: []
* Argument: pathToClaudeCodeExecutable
  * Description: Path to the Claude Code executable
  * Default: Executable that ships with @anthropic-ai/claude-code


### Python

The Python SDK is available as [`claude-code-sdk`](https://github.com/anthropics/claude-code-sdk-python) on PyPI:

**Prerequisites:**

*   Python 3.10+
*   Node.js
*   Claude Code CLI: `npm install -g @anthropic-ai/claude-code`

Basic usage:

The Python SDK accepts all arguments supported by the command line SDK through the `ClaudeCodeOptions` class:

Advanced usage
--------------

The documentation below uses the command line SDK as an example, but can also be used with the TypeScript and Python SDKs.

### Multi-turn conversations

For multi-turn conversations, you can resume conversations or continue from the most recent session:

### Custom system prompts

You can provide custom system prompts to guide Claude’s behavior:

You can also append instructions to the default system prompt:

### MCP Configuration

The Model Context Protocol (MCP) allows you to extend Claude Code with additional tools and resources from external servers. Using the `--mcp-config` flag, you can load MCP servers that provide specialized capabilities like database access, API integrations, or custom tooling.

Create a JSON configuration file with your MCP servers:

Then use it with Claude Code:

### Custom permission prompt tool

Optionally, use `--permission-prompt-tool` to pass in an MCP tool that we will use to check whether or not the user grants the model permissions to invoke a given tool. When the model invokes a tool the following happens:

1.  We first check permission settings: all [settings.json files](https://docs.anthropic.com/en/docs/claude-code/settings), as well as `--allowedTools` and `--disallowedTools` passed into the SDK; if one of these allows or denies the tool call, we proceed with the tool call
2.  Otherwise, we invoke the MCP tool you provided in `--permission-prompt-tool`

The `--permission-prompt-tool` MCP tool is passed the tool name and input, and must return a JSON-stringified payload with the result. The payload must be one of:

For example, a TypeScript MCP permission prompt tool implementation might look like this:

To use this tool, add your MCP server (eg. with `--mcp-config`), then invoke the SDK like so:

Usage notes:

*   Use `updatedInput` to tell the model that the permission prompt mutated its input; otherwise, set `updatedInput` to the original input, as in the example above. For example, if the tool shows a file edit diff to the user and lets them edit the diff manually, the permission prompt tool should return that updated edit.
*   The payload must be JSON-stringified

Available CLI options
---------------------

The SDK leverages all the CLI options available in Claude Code. Here are the key ones for SDK usage:



* Flag: --print, -p
  * Description: Run in non-interactive mode
  * Example: claude -p "query"
* Flag: --output-format
  * Description: Specify output format (text, json, stream-json)
  * Example: claude -p --output-format json
* Flag: --resume, -r
  * Description: Resume a conversation by session ID
  * Example: claude --resume abc123
* Flag: --continue, -c
  * Description: Continue the most recent conversation
  * Example: claude --continue
* Flag: --verbose
  * Description: Enable verbose logging
  * Example: claude --verbose
* Flag: --max-turns
  * Description: Limit agentic turns in non-interactive mode
  * Example: claude --max-turns 3
* Flag: --system-prompt
  * Description: Override system prompt (only with --print)
  * Example: claude --system-prompt "Custom instruction"
* Flag: --append-system-prompt
  * Description: Append to system prompt (only with --print)
  * Example: claude --append-system-prompt "Custom instruction"
* Flag: --allowedTools
  * Description: Space-separated list of allowed tools, or  string of comma-separated list of allowed tools
  * Example: claude --allowedTools mcp__slack mcp__filesystemclaude --allowedTools "Bash(npm install),mcp__filesystem"
* Flag: --disallowedTools
  * Description: Space-separated list of denied tools, or  string of comma-separated list of denied tools
  * Example: claude --disallowedTools mcp__splunk mcp__githubclaude --disallowedTools "Bash(git commit),mcp__github"
* Flag: --mcp-config
  * Description: Load MCP servers from a JSON file
  * Example: claude --mcp-config servers.json
* Flag: --permission-prompt-tool
  * Description: MCP tool for handling permission prompts (only with --print)
  * Example: claude --permission-prompt-tool mcp__auth__prompt


For a complete list of CLI options and features, see the [CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference) documentation.

Output formats
--------------

The SDK supports multiple output formats:

### Text output (default)

Returns just the response text:

### JSON output

Returns structured data including metadata:

Response format:

### Streaming JSON output

Streams each message as it is received:

Each conversation begins with an initial `init` system message, followed by a list of user and assistant messages, followed by a final `result` system message with stats. Each message is emitted as a separate JSON object.

Message schema
--------------

Messages returned from the JSON API are strictly typed according to the following schema:

We will soon publish these types in a JSONSchema-compatible format. We use semantic versioning for the main Claude Code package to communicate breaking changes to this format.

`Message` and `MessageParam` types are available in Anthropic SDKs. For example, see the Anthropic [TypeScript](https://github.com/anthropics/anthropic-sdk-typescript) and [Python](https://github.com/anthropics/anthropic-sdk-python/) SDKs.

Input formats
-------------

The SDK supports multiple input formats:

### Text input (default)

Input text can be provided as an argument:

Or input text can be piped via stdin:

### Streaming JSON input

A stream of messages provided via `stdin` where each message represents a user turn. This allows multiple turns of a conversation without re-launching the `claude` binary and allows providing guidance to the model while it is processing a request.

Each message is a JSON ‘User message’ object, following the same format as the output message schema. Messages are formatted using the [jsonl](https://jsonlines.org/) format where each line of input is a complete JSON object. Streaming JSON input requires `-p` and `--output-format stream-json`.

Currently this is limited to text-only user messages.

Examples
--------

### Simple script integration

### Processing files with Claude

### Session management

Best practices
--------------

1.  **Use JSON output format** for programmatic parsing of responses:
    
2.  **Handle errors gracefully** - check exit codes and stderr:
    
3.  **Use session management** for maintaining context in multi-turn conversations
    
4.  **Consider timeouts** for long-running operations:
    
5.  **Respect rate limits** when making multiple requests by adding delays between calls
    

Real-world applications
-----------------------

The Claude Code SDK enables powerful integrations with your development workflow. One notable example is the [Claude Code GitHub Actions](https://docs.anthropic.com/en/docs/claude-code/github-actions), which uses the SDK to provide automated code review, PR creation, and issue triage capabilities directly in your GitHub workflow.

*   [CLI usage and controls](https://docs.anthropic.com/en/docs/claude-code/cli-reference) - Complete CLI documentation
*   [GitHub Actions integration](https://docs.anthropic.com/en/docs/claude-code/github-actions) - Automate your GitHub workflow with Claude
*   [Common workflows](https://docs.anthropic.com/en/docs/claude-code/common-workflows) - Step-by-step guides for common use cases