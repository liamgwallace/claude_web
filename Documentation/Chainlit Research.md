# Chainlit Research - Key Information for Building Claude Web Interface

## Overview
Chainlit is a Python framework for building interactive LLM interfaces with minimal code. It's designed to create chat applications quickly without frontend development complexity.

## Installation
```bash
pip install chainlit
# Optional: pip install chainlit langchain langchain-community
```

## Core Components

### 1. Basic App Structure
```python
import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    # Runs when new chat session begins
    # Good for greeting users, initializing session state
    pass

@cl.on_message
async def on_message(message: cl.Message):
    # Runs when users send messages
    # Process input and return responses
    await cl.Message(content="Response").send()
```

### 2. UI Configuration (config.toml)
```toml
[UI]
name = "Claude Web Interface"
description = "Web interface for Claude Code with project management"
default_collapse_content = true
default_expand_messages = false
cot = "full"  # Chain of thought: "hidden", "tool_call", or "full"
```

### 3. UI Actions
```python
# Add buttons with actions
actions = [
    cl.Action(name="create_project", value="create", description="Create New Project"),
    cl.Action(name="select_project", value="select", description="Select Project")
]

@cl.action_callback("create_project")
async def on_action(action):
    # Handle button clicks
    pass
```

## Project-Specific Implementation Strategy

### Current Sidebar Limitations
- Chainlit 2.0.2 has reported issues with sidebar functionality
- Traditional sidebar like Streamlit is not readily available
- Need to use alternative approaches for project/thread management

### Alternative UI Approaches for Project Management

#### Option 1: Actions-Based Navigation
```python
# Use action buttons for project selection
project_actions = [
    cl.Action(name="project_1", value="proj1", description="Project 1"),
    cl.Action(name="project_2", value="proj2", description="Project 2"),
    cl.Action(name="new_project", value="new", description="+ New Project")
]
```

#### Option 2: Session State Management
```python
# Store current project/thread in session
cl.user_session.set("current_project", project_name)
cl.user_session.set("current_thread", thread_id)
```

#### Option 3: Chat Commands
```python
# Use chat commands for navigation
# /project list
# /project create "My Project"
# /project select 1
# /thread list
# /thread create "My Thread"
```

## Integration with Flask API Backend

### API Client Setup
```python
import requests

class ClaudeAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def list_projects(self):
        response = requests.get(f"{self.base_url}/projects")
        return response.json()
    
    def create_project(self, name):
        response = requests.post(f"{self.base_url}/project/new", json={"name": name})
        return response.json()
    
    def send_message(self, project_name, thread_id, message):
        response = requests.post(
            f"{self.base_url}/project/{project_name}/thread/{thread_id}/message",
            json={"message": message}
        )
        return response.json()
```

## File Viewing Implementation
```python
# Display file tree
file_tree = api_client.get_files(project_name)
await cl.Message(content=f"```\n{format_file_tree(file_tree)}\n```").send()

# Display file content
file_content = api_client.get_file_content(project_name, file_path)
await cl.Message(content=f"```python\n{file_content}\n```").send()
```

## Recommended Implementation Plan

1. **Start Simple**: Use action buttons and session state for project/thread management instead of sidebar
2. **Progressive Enhancement**: Build core functionality first, enhance UI later
3. **API Integration**: Connect to existing Flask backend for all Claude operations
4. **File Management**: Use formatted messages to display file trees and content
5. **State Management**: Use Chainlit's session state to track current project/thread

## Key Benefits of Chainlit for This Project
- Rapid development with minimal frontend code
- Built-in chat interface
- Session management
- Easy deployment
- Good for MVP/prototype development

## Limitations to Consider
- Sidebar functionality challenges in recent versions
- Less UI customization compared to full frontend frameworks
- Need creative solutions for complex navigation