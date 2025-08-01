"""
Claude CLI wrapper for project-based thread management.
Projects are physical folders where Claude CLI runs.
Threads are chat conversations stored as metadata within projects.
"""

import subprocess
import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import uuid
from datetime import datetime
# from template_manager import TemplateManager  # TODO: Implement if needed

logger = logging.getLogger(__name__)

class ClaudeWrapper:
    def __init__(self, base_projects_dir: str = "../data/projects"):
        self.base_projects_dir = Path(base_projects_dir)
        self.base_projects_dir.mkdir(parents=True, exist_ok=True)
        # self.template_manager = TemplateManager()  # TODO: Implement if needed
        
    def create_project(self, project_name: str) -> str:
        """
        Create a new project folder.
        Returns the project name (sanitized).
        """
        # Sanitize project name for filesystem
        sanitized_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        sanitized_name = sanitized_name.replace(' ', '-')
        
        if not sanitized_name:
            sanitized_name = f"project-{str(uuid.uuid4())[:8]}"
            
        project_dir = self.base_projects_dir / sanitized_name
        
        # Handle name conflicts
        counter = 1
        original_name = sanitized_name
        while project_dir.exists():
            sanitized_name = f"{original_name}-{counter}"
            project_dir = self.base_projects_dir / sanitized_name
            counter += 1
        
        project_dir.mkdir(exist_ok=True)
        
        # Initialize Claude project with templates
        # self.template_manager.initialize_claude_project(  # TODO: Implement if needed
        #     str(project_dir), 
        #     project_name,
        #     f"A project created via Claude Web Interface"
        # )
        
        threads_dir = project_dir / ".threads"
        threads_dir.mkdir(exist_ok=True)
        
        # Create project metadata
        project_metadata = {
            "name": project_name,
            "sanitized_name": sanitized_name,
            "created": datetime.utcnow().isoformat(),
            "threads": {}
        }
        
        threads_file = threads_dir / "threads.json"
        with open(threads_file, 'w') as f:
            json.dump(project_metadata, f, indent=2)
            
        logger.info(f"Created project {sanitized_name} at {project_dir}")
        return sanitized_name
    
    def list_projects(self) -> List[Dict]:
        """
        List all available projects.
        Returns list of project metadata.
        """
        projects = []
        
        for project_dir in self.base_projects_dir.iterdir():
            if project_dir.is_dir():
                threads_file = project_dir / ".threads" / "threads.json"
                if threads_file.exists():
                    try:
                        with open(threads_file, 'r') as f:
                            metadata = json.load(f)
                            projects.append({
                                "name": metadata.get("name", project_dir.name),
                                "sanitized_name": project_dir.name,
                                "created": metadata.get("created", ""),
                                "thread_count": len(metadata.get("threads", {}))
                            })
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid threads.json in {project_dir}")
                else:
                    # Legacy project or manually created - add basic info
                    projects.append({
                        "name": project_dir.name,
                        "sanitized_name": project_dir.name,
                        "created": "",
                        "thread_count": 0
                    })
                        
        return sorted(projects, key=lambda x: x.get("created", ""), reverse=True)
    
    def create_thread(self, project_name: str, thread_name: Optional[str] = None) -> str:
        """
        Create a new thread within a project.
        Returns the thread ID.
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            raise ValueError(f"Project {project_name} not found")
            
        threads_dir = project_dir / ".threads"
        threads_dir.mkdir(exist_ok=True)
        
        thread_id = str(uuid.uuid4())[:8]
        
        # Load existing threads metadata
        threads_file = threads_dir / "threads.json"
        try:
            with open(threads_file, 'r') as f:
                project_metadata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            project_metadata = {
                "name": project_name,
                "sanitized_name": project_name,
                "created": datetime.utcnow().isoformat(),
                "threads": {}
            }
        
        # Create thread metadata
        thread_metadata = {
            "id": thread_id,
            "name": thread_name or f"Thread {thread_id}",
            "created": datetime.utcnow().isoformat(),
            "session_id": None,  # Claude CLI session ID will be set on first message
            "message_count": 0,
            "messages": []  # Store conversation history
        }
        
        # Add to project threads
        project_metadata["threads"][thread_id] = {
            "name": thread_metadata["name"],
            "created": thread_metadata["created"]
        }
        
        # Save thread metadata
        thread_file = threads_dir / f"{thread_id}.json"
        with open(thread_file, 'w') as f:
            json.dump(thread_metadata, f, indent=2)
            
        # Save updated project metadata
        with open(threads_file, 'w') as f:
            json.dump(project_metadata, f, indent=2)
            
        logger.info(f"Created thread {thread_id} in project {project_name}")
        return thread_id
    
    def list_threads(self, project_name: str) -> List[Dict]:
        """
        List all threads in a project.
        Returns list of thread metadata.
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            return []
            
        threads_dir = project_dir / ".threads"
        threads = []
        
        for thread_file in threads_dir.glob("*.json"):
            if thread_file.name == "threads.json":
                continue
                
            try:
                with open(thread_file, 'r') as f:
                    metadata = json.load(f)
                    threads.append({
                        "id": metadata.get("id", thread_file.stem),
                        "name": metadata.get("name", thread_file.stem),
                        "created": metadata.get("created", ""),
                        "message_count": metadata.get("message_count", 0)
                    })
            except json.JSONDecodeError:
                logger.warning(f"Invalid thread file {thread_file}")
                
        return sorted(threads, key=lambda x: x.get("created", ""), reverse=True)
    
    def send_message(self, project_name: str, thread_id: str, message: str) -> Tuple[bool, str, Dict]:
        """
        Send a message to Claude CLI using session management.
        Each thread has its own Claude session that persists conversation history.
        Returns (success, response, metadata).
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            return False, f"Project {project_name} not found", {}
            
        threads_dir = project_dir / ".threads"
        thread_file = threads_dir / f"{thread_id}.json"
        
        if not thread_file.exists():
            return False, f"Thread {thread_id} not found in project {project_name}", {}
        
        # Load existing thread metadata
        try:
            with open(thread_file, 'r') as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            return False, f"Invalid thread metadata for {thread_id}", {}
        
        # Get existing session ID if available
        session_id = metadata.get("session_id")
        
        try:
            # Build Claude CLI command
            # Try to find Claude CLI executable
            claude_cmd = self._find_claude_executable()
            if not claude_cmd:
                raise Exception("Claude CLI not found. Please ensure Claude CLI is installed and in PATH.")
            
            # Build base command with permissions and environment
            base_cmd = [claude_cmd, "--dangerously-skip-permissions"]
            
            if session_id:
                # Resume existing session
                cmd = base_cmd + ["--resume", session_id, "-p", message, "--output-format", "json"]
                logger.info(f"Resuming session {session_id} for thread {thread_id}")
            else:
                # Start new session
                cmd = base_cmd + ["-p", message, "--output-format", "json"]
                logger.info(f"Starting new session for thread {thread_id}")
            
            # Get full environment from current process
            env = os.environ.copy()
            
            result = subprocess.run(
                cmd,
                cwd=str(project_dir),  # Run in project directory
                env=env,  # Pass full environment
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=False  # Use direct exec for better control
            )
            
            if result.returncode == 0:
                try:
                    # Parse JSON response
                    response_data = json.loads(result.stdout)
                    response_text = response_data.get("result", response_data.get("content", result.stdout))
                    
                    # Extract session ID from response
                    new_session_id = response_data.get("session_id")
                    
                except json.JSONDecodeError:
                    response_text = result.stdout
                    response_data = {"content": result.stdout}
                    new_session_id = None
                
                # Update thread metadata with session ID and increment message count
                if new_session_id:
                    metadata["session_id"] = new_session_id
                
                # Ensure messages array exists (for backwards compatibility)
                if "messages" not in metadata:
                    metadata["messages"] = []
                
                # Add user message and Claude response to conversation history
                message_timestamp = datetime.utcnow().isoformat()
                
                # Add user message
                metadata["messages"].append({
                    "role": "user", 
                    "content": message,
                    "timestamp": message_timestamp
                })
                
                # Add Claude response
                metadata["messages"].append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": message_timestamp
                })
                    
                metadata["message_count"] = metadata.get("message_count", 0) + 1
                metadata["last_activity"] = message_timestamp
                
                # Save updated thread metadata
                with open(thread_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Successfully sent message to thread {thread_id} in project {project_name} (session: {new_session_id or session_id})")
                return True, response_text, response_data
            else:
                error_msg = result.stderr or "Claude CLI command failed"
                logger.error(f"Claude CLI error in project {project_name}, thread {thread_id}: {error_msg}")
                return False, error_msg, {}
                
        except subprocess.TimeoutExpired:
            error_msg = "Claude CLI command timed out"
            logger.error(f"Timeout in project {project_name}, thread {thread_id}")
            return False, error_msg, {}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error in project {project_name}, thread {thread_id}: {error_msg}")
            return False, error_msg, {}
    
    def _find_claude_executable(self) -> Optional[str]:
        """Find Claude CLI executable on the system."""
        import platform
        import shutil
        
        # Common executable names to try
        if platform.system() == "Windows":
            candidates = ["claude.exe", "claude.cmd", "claude"]
        else:
            candidates = ["claude"]
        
        # Try to find in PATH
        for candidate in candidates:
            if shutil.which(candidate):
                return candidate
        
        # Try common installation paths on Windows
        if platform.system() == "Windows":
            import os
            common_paths = [
                os.path.expanduser("~/.local/bin/claude.exe"),
                os.path.expanduser("~/AppData/Local/Programs/Claude/claude.exe"),
                "C:/Program Files/Claude/claude.exe",
                "C:/Program Files (x86)/Claude/claude.exe"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def get_messages(self, project_name: str, thread_id: str) -> Optional[List[Dict]]:
        """
        Get conversation message history for a thread.
        Returns list of messages or None if not found.
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            return None
            
        thread_file = project_dir / ".threads" / f"{thread_id}.json"
        
        if not thread_file.exists():
            return None
            
        try:
            with open(thread_file, 'r') as f:
                metadata = json.load(f)
                
                # Return stored conversation messages
                messages = metadata.get("messages", [])
                
                # If no messages exist but there's a session, show info message
                if not messages and metadata.get("session_id"):
                    return [{
                        "role": "system",
                        "content": f"Thread has {metadata.get('message_count', 0)} messages but history not stored in this format. Future messages will be saved.",
                        "timestamp": metadata.get("created", "")
                    }]
                
                return messages
                
        except json.JSONDecodeError:
            logger.error(f"Invalid thread file for {project_name}/{thread_id}")
            return None
    
    def get_file_tree(self, project_name: str) -> Optional[Dict]:
        """
        Get file tree for a project directory.
        Returns nested dict representing file structure.
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            return None
            
        def build_tree(path: Path) -> Dict:
            tree = {"name": path.name, "type": "directory" if path.is_dir() else "file", "children": []}
            
            if path.is_dir():
                try:
                    for child in sorted(path.iterdir()):
                        # Skip .threads directory and other hidden files
                        if child.name.startswith('.'):
                            continue
                        tree["children"].append(build_tree(child))
                except PermissionError:
                    pass
                    
            return tree
        
        return build_tree(project_dir)
    
    def get_file_content(self, project_name: str, file_path: str) -> Optional[str]:
        """
        Get content of a specific file in the project directory.
        Returns file content or None if not found.
        """
        project_dir = self.base_projects_dir / project_name
        target_file = project_dir / file_path
        
        # Security check - ensure file is within project directory
        try:
            target_file.resolve().relative_to(project_dir.resolve())
        except ValueError:
            logger.warning(f"Attempted access outside project directory: {file_path}")
            return None
            
        if not target_file.exists() or not target_file.is_file():
            return None
            
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError) as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def write_file_content(self, project_name: str, file_path: str, content: str) -> Tuple[bool, str]:
        """
        Write content to a specific file in the project directory.
        Returns (success, message) tuple.
        """
        project_dir = self.base_projects_dir / project_name
        
        # Check if project exists
        if not project_dir.exists():
            return False, f"Project '{project_name}' not found"
            
        target_file = project_dir / file_path
        
        # Security check - ensure file is within project directory
        try:
            target_file.resolve().relative_to(project_dir.resolve())
        except ValueError:
            logger.warning(f"Attempted write outside project directory: {file_path}")
            return False, "Access denied: file path outside project directory"
        
        try:
            # Ensure parent directories exist
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully wrote file {file_path} in project {project_name}")
            return True, f"File '{file_path}' saved successfully"
            
        except PermissionError as e:
            logger.error(f"Permission error writing file {file_path}: {e}")
            return False, f"Permission denied: unable to write file"
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False, f"Error saving file: {str(e)}"
    
    def get_thread_status(self, project_name: str, thread_id: str) -> Dict:
        """
        Get status information for a thread in a project.
        Returns status dict with thread info.
        """
        project_dir = self.base_projects_dir / project_name
        
        if not project_dir.exists():
            return {"status": "project_not_found", "project_name": project_name, "thread_id": thread_id}
            
        thread_file = project_dir / ".threads" / f"{thread_id}.json"
        
        if not thread_file.exists():
            return {"status": "thread_not_found", "project_name": project_name, "thread_id": thread_id}
        
        try:
            with open(thread_file, 'r') as f:
                metadata = json.load(f)
                
            return {
                "status": "ready",
                "project_name": project_name,
                "thread_id": thread_id,
                "name": metadata.get("name", thread_id),
                "created": metadata.get("created", ""),
                "session_id": metadata.get("session_id", "No session started"),
                "message_count": metadata.get("message_count", 0),
                "last_activity": metadata.get("last_activity", "Never")
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "project_name": project_name,
                "thread_id": thread_id,
                "error": "Invalid thread metadata"
            }
    
    def delete_thread(self, project_name: str, thread_id: str) -> Tuple[bool, str]:
        """
        Delete a thread and its Claude session.
        This will remove all chat history and thread metadata.
        Returns (success, message).
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            return False, f"Project {project_name} not found"
            
        threads_dir = project_dir / ".threads"
        thread_file = threads_dir / f"{thread_id}.json"
        
        if not thread_file.exists():
            return False, f"Thread {thread_id} not found in project {project_name}"
        
        try:
            # Remove thread file
            thread_file.unlink()
            
            # Update project threads metadata
            threads_file = threads_dir / "threads.json"
            if threads_file.exists():
                try:
                    with open(threads_file, 'r') as f:
                        project_metadata = json.load(f)
                    
                    # Remove thread from project metadata
                    if thread_id in project_metadata.get("threads", {}):
                        del project_metadata["threads"][thread_id]
                        
                    # Save updated project metadata
                    with open(threads_file, 'w') as f:
                        json.dump(project_metadata, f, indent=2)
                        
                except (json.JSONDecodeError, KeyError):
                    logger.warning(f"Could not update project metadata when deleting thread {thread_id}")
            
            logger.info(f"Deleted thread {thread_id} from project {project_name}")
            return True, f"Thread {thread_id} deleted successfully"
            
        except Exception as e:
            error_msg = f"Error deleting thread {thread_id}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_project(self, project_name: str) -> Tuple[bool, str]:
        """
        Delete an entire project including all threads and generated files.
        This will remove all chat sessions and files in the project directory.
        Returns (success, message).
        """
        project_dir = self.base_projects_dir / project_name
        if not project_dir.exists():
            return False, f"Project {project_name} not found"
        
        try:
            import shutil
            
            # Remove entire project directory including all files and threads
            shutil.rmtree(project_dir)
            
            logger.info(f"Deleted project {project_name} and all its contents")
            return True, f"Project {project_name} and all its contents deleted successfully"
            
        except Exception as e:
            error_msg = f"Error deleting project {project_name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg