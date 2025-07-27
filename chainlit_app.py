"""
Chainlit frontend for Claude Web Runner with project-based organization.
This provides a web interface for interacting with Claude Code through projects and threads.
"""

import chainlit as cl
import requests
import json
import asyncio
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeAPIClient:
    """Client for communicating with the Flask API backend."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        result = self._make_request('GET', '/health')
        return result.get('success') is not False
    
    def list_projects(self) -> List[Dict]:
        """List all available projects."""
        result = self._make_request('GET', '/projects')
        if result.get('success'):
            return result.get('projects', [])
        return []
    
    def create_project(self, name: str) -> Optional[Dict]:
        """Create a new project."""
        data = {"name": name}
        result = self._make_request('POST', '/project/new', data)
        if result.get('success'):
            return result
        return None
    
    def list_threads(self, project_name: str) -> List[Dict]:
        """List all threads in a project."""
        result = self._make_request('GET', f'/project/{project_name}/threads')
        if result.get('success'):
            return result.get('threads', [])
        return []
    
    def create_thread(self, project_name: str, name: Optional[str] = None) -> Optional[Dict]:
        """Create a new thread in a project."""
        data = {"name": name} if name else {}
        result = self._make_request('POST', f'/project/{project_name}/thread/new', data)
        if result.get('success'):
            return result
        return None
    
    def send_message(self, project_name: str, thread_id: str, message: str) -> Optional[Dict]:
        """Send a message to Claude."""
        data = {"message": message}
        result = self._make_request('POST', f'/project/{project_name}/thread/{thread_id}/message', data)
        if result.get('success'):
            return result
        return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a job."""
        result = self._make_request('GET', f'/status/{job_id}')
        if result.get('success'):
            return result
        return None
    
    def get_files(self, project_name: str) -> Optional[Dict]:
        """Get file tree for a project."""
        result = self._make_request('GET', f'/project/{project_name}/files')
        if result.get('success'):
            return result.get('file_tree')
        return None
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project."""
        result = self._make_request('DELETE', f'/project/{project_name}')
        return result.get('success', False)
    
    def delete_thread(self, project_name: str, thread_id: str) -> bool:
        """Delete a thread."""
        result = self._make_request('DELETE', f'/project/{project_name}/thread/{thread_id}')
        return result.get('success', False)


# Initialize API client
api_client = ClaudeAPIClient()


def format_file_tree(node: Dict, prefix: str = "") -> str:
    """Recursively format file tree for display."""
    if not node or not node.get('name'):
        return ""
    
    icon = "📁" if node.get('type') == 'directory' else "📄"
    result = f"{prefix}{icon} {node['name']}\n"
    
    for child in node.get('children', []):
        result += format_file_tree(child, prefix + "  ")
    
    return result


async def display_project_navigation():
    """Display project navigation actions."""
    projects = api_client.list_projects()
    
    actions = [
        cl.Action(name="create_project", value="create", description="➕ Create New Project", label="➕ Create New Project"),
        cl.Action(name="list_projects", value="list", description="📋 List All Projects", label="📋 List All Projects"),
        cl.Action(name="help", value="help", description="❓ Help", label="❓ Help")
    ]
    
    # Add project selection actions
    for i, project in enumerate(projects[:5]):  # Limit to 5 projects in actions
        actions.append(
            cl.Action(
                name=f"select_project_{i}", 
                value=f"select:{project['sanitized_name']}", 
                description=f"📂 {project['name']}",
                label=f"📂 {project['name']}"
            )
        )
    
    await cl.Message(
        content="Welcome to Claude Web Runner! Choose an option to get started:",
        actions=actions
    ).send()


async def display_thread_navigation(project_name: str):
    """Display thread navigation for a project."""
    threads = api_client.list_threads(project_name)
    
    actions = [
        cl.Action(name="create_thread", value=f"create_thread:{project_name}", description="➕ Create New Thread", label="➕ Create New Thread"),
        cl.Action(name="view_files", value=f"view_files:{project_name}", description="📁 View Files", label="📁 View Files"),
        cl.Action(name="back_to_projects", value="back", description="⬅️ Back to Projects", label="⬅️ Back to Projects")
    ]
    
    # Add thread selection actions
    for i, thread in enumerate(threads[:5]):  # Limit to 5 threads in actions
        actions.append(
            cl.Action(
                name=f"select_thread_{i}", 
                value=f"select_thread:{project_name}:{thread['id']}", 
                description=f"💬 {thread['name']} ({thread['message_count']} msgs)",
                label=f"💬 {thread['name']} ({thread['message_count']} msgs)"
            )
        )
    
    current_project = cl.user_session.get("current_project", "")
    await cl.Message(
        content=f"📂 **Project: {current_project}**\n\nSelect a thread to start chatting or create a new one:",
        actions=actions
    ).send()


async def wait_for_claude_response(job_id: str) -> Optional[str]:
    """Wait for Claude response and return the result."""
    max_wait = 300  # 5 minutes
    wait_time = 0
    
    # Show initial processing message
    processing_msg = await cl.Message(content="⏳ Processing your request...").send()
    
    while wait_time < max_wait:
        status_result = api_client.get_job_status(job_id)
        
        if not status_result:
            await processing_msg.update(content="❌ Failed to get job status")
            return None
        
        status = status_result.get('status')
        
        if status == 'done':
            response = status_result.get('response', '')
            await processing_msg.remove()
            return response
        elif status == 'failed':
            error = status_result.get('error', 'Unknown error')
            await processing_msg.update(content=f"❌ Claude request failed: {error}")
            return None
        else:
            # Update processing message with status
            await processing_msg.update(content=f"⏳ Status: {status}...")
            await asyncio.sleep(2)
            wait_time += 2
    
    await processing_msg.update(content="⏰ Request timed out")
    return None


@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session."""
    # Check API health
    if not api_client.health_check():
        await cl.Message(
            content="❌ **API Connection Failed**\n\nThe backend API is not available. Please make sure the Flask server is running on http://localhost:5000"
        ).send()
        return
    
    # Initialize session state
    cl.user_session.set("current_project", None)
    cl.user_session.set("current_thread", None)
    cl.user_session.set("chat_mode", False)
    
    # Welcome message
    welcome_msg = """# 🚀 Welcome to Claude Web Runner!

This interface allows you to:
- **Create and manage projects** - Organize your work into separate project folders
- **Manage chat threads** - Have multiple conversations within each project  
- **Work with Claude Code** - All Claude operations happen in your project directories
- **View generated files** - See what Claude creates in your projects

**Getting Started:**
1. Create a new project or select an existing one
2. Create a thread within that project
3. Start chatting with Claude!

All Claude Code operations will happen in your selected project's directory.
"""
    
    await cl.Message(content=welcome_msg).send()
    await display_project_navigation()


@cl.action_callback("create_project")
async def create_project_action(action):
    """Handle create project action."""
    await cl.Message(content="Please enter a name for your new project:").send()
    cl.user_session.set("awaiting_project_name", True)


@cl.action_callback("list_projects")
async def list_projects_action(action):
    """Handle list projects action."""
    projects = api_client.list_projects()
    
    if not projects:
        await cl.Message(content="No projects found. Create your first project to get started!").send()
        return
    
    project_list = "## 📋 Your Projects\n\n"
    for project in projects:
        project_list += f"- **{project['name']}** ({project['thread_count']} threads)\n"
        project_list += f"  - Created: {project.get('created', 'Unknown')}\n\n"
    
    await cl.Message(content=project_list).send()
    await display_project_navigation()


@cl.action_callback("help")
async def help_action(action):
    """Handle help action."""
    help_text = """## ❓ Help - How to Use Claude Web Runner

### Project Management
- **Projects** are folders where Claude Code will run and create files
- Each project maintains its own file structure and context
- Create projects to organize different coding tasks or experiments

### Thread Management  
- **Threads** are separate chat conversations within a project
- Each thread maintains its own chat history with Claude
- Use threads to separate different discussions or features within a project

### Chat Flow
1. **Select/Create Project** → Choose your working directory
2. **Select/Create Thread** → Choose your conversation
3. **Chat with Claude** → All operations happen in your project folder

### Available Commands
- Use the action buttons to navigate between projects and threads
- Type `/back` in chat mode to return to thread selection
- Type `/files` in chat mode to view project files
- Type `/help` for this help message

### File Management
- All files created by Claude are saved in your project directory
- Use the "View Files" option to see the current project structure
- Generated code, documents, and other files persist between sessions
"""
    
    await cl.Message(content=help_text).send()
    await display_project_navigation()


@cl.action_callback("back_to_projects")
async def back_to_projects_action(action):
    """Handle back to projects action."""
    cl.user_session.set("current_project", None)
    cl.user_session.set("current_thread", None)
    cl.user_session.set("chat_mode", False)
    await display_project_navigation()


@cl.action_callback("create_thread")
async def create_thread_action(action):
    """Handle create thread action."""
    project_name = action.value.split(":", 1)[1]
    await cl.Message(content=f"Enter a name for your new thread in project **{project_name}** (or press Enter for auto-generated):").send()
    cl.user_session.set("awaiting_thread_name", project_name)


@cl.action_callback("view_files")
async def view_files_action(action):
    """Handle view files action."""
    project_name = action.value.split(":", 1)[1]
    file_tree = api_client.get_files(project_name)
    
    if not file_tree:
        await cl.Message(content=f"No files found in project **{project_name}** or project doesn't exist.").send()
        return
    
    formatted_tree = format_file_tree(file_tree)
    
    await cl.Message(
        content=f"## 📁 Files in Project: {project_name}\n\n```\n{formatted_tree}```"
    ).send()
    
    await display_thread_navigation(project_name)


# Handle project selection actions dynamically
for i in range(10):  # Support up to 10 projects in actions
    @cl.action_callback(f"select_project_{i}")
    async def select_project_action(action):
        """Handle project selection."""
        project_name = action.value.split(":", 1)[1]
        cl.user_session.set("current_project", project_name)
        await display_thread_navigation(project_name)


# Handle thread selection actions dynamically  
for i in range(10):  # Support up to 10 threads in actions
    @cl.action_callback(f"select_thread_{i}")
    async def select_thread_action(action):
        """Handle thread selection."""
        parts = action.value.split(":", 2)
        project_name = parts[1]
        thread_id = parts[2]
        
        cl.user_session.set("current_project", project_name)
        cl.user_session.set("current_thread", thread_id)
        cl.user_session.set("chat_mode", True)
        
        await cl.Message(
            content=f"💬 **Chat Mode Active**\n\nProject: **{project_name}**\nThread: **{thread_id}**\n\nYou can now chat with Claude! All operations will happen in your project directory.\n\n*Type `/back` to return to thread selection, `/files` to view project files, or start chatting!*"
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    user_input = message.content.strip()
    
    # Handle special cases first
    if cl.user_session.get("awaiting_project_name"):
        cl.user_session.set("awaiting_project_name", False)
        
        if not user_input:
            await cl.Message(content="❌ Project name cannot be empty. Please try again.").send()
            await display_project_navigation()
            return
        
        result = api_client.create_project(user_input)
        if result:
            project_name = result['project_name']
            await cl.Message(content=f"✅ Created project: **{project_name}**").send()
            cl.user_session.set("current_project", project_name)
            await display_thread_navigation(project_name)
        else:
            await cl.Message(content="❌ Failed to create project. Please try again.").send()
            await display_project_navigation()
        return
    
    if cl.user_session.get("awaiting_thread_name"):
        project_name = cl.user_session.get("awaiting_thread_name")
        cl.user_session.set("awaiting_thread_name", None)
        
        thread_name = user_input if user_input else None
        result = api_client.create_thread(project_name, thread_name)
        
        if result:
            thread_id = result['thread_id']
            await cl.Message(content=f"✅ Created thread: **{thread_id}**").send()
            cl.user_session.set("current_thread", thread_id)
            cl.user_session.set("chat_mode", True)
            
            await cl.Message(
                content=f"💬 **Chat Mode Active**\n\nProject: **{project_name}**\nThread: **{thread_id}**\n\nStart chatting with Claude!"
            ).send()
        else:
            await cl.Message(content="❌ Failed to create thread. Please try again.").send()
            await display_thread_navigation(project_name)
        return
    
    # Handle chat mode commands
    if cl.user_session.get("chat_mode"):
        if user_input == "/back":
            cl.user_session.set("chat_mode", False)
            project_name = cl.user_session.get("current_project")
            await display_thread_navigation(project_name)
            return
        
        if user_input == "/files":
            project_name = cl.user_session.get("current_project")
            file_tree = api_client.get_files(project_name)
            
            if file_tree:
                formatted_tree = format_file_tree(file_tree)
                await cl.Message(
                    content=f"## 📁 Files in Project: {project_name}\n\n```\n{formatted_tree}```"
                ).send()
            else:
                await cl.Message(content="No files found in this project.").send()
            return
        
        if user_input == "/help":
            await help_action(None)
            return
        
        # Send message to Claude
        project_name = cl.user_session.get("current_project")
        thread_id = cl.user_session.get("current_thread")
        
        if not project_name or not thread_id:
            await cl.Message(content="❌ No project or thread selected. Please go back and select one.").send()
            return
        
        # Send message via API
        result = api_client.send_message(project_name, thread_id, user_input)
        
        if result:
            job_id = result['job_id']
            claude_response = await wait_for_claude_response(job_id)
            
            if claude_response:
                await cl.Message(content=claude_response).send()
            # Error message already shown in wait_for_claude_response
        else:
            await cl.Message(content="❌ Failed to send message to Claude. Please try again.").send()
        
        return
    
    # Default: show navigation if not in chat mode
    await cl.Message(content="Please use the action buttons to navigate. Type `/help` for assistance.").send()
    await display_project_navigation()


if __name__ == "__main__":
    import os
    # Ensure the Flask API is running
    print("🚀 Starting Chainlit frontend...")
    print("📋 Make sure the Flask API is running on http://localhost:5000")
    print("🌐 Chainlit will be available at http://localhost:8000")