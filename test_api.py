#!/usr/bin/env python3
"""
Simple test client for the Claude Web API.
Projects are physical folders where Claude CLI runs.
Threads are chat conversations within projects.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Optional

class ClaudeAPITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.current_project_name = None
        self.current_thread_id = None
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        print("🏥 Checking API health...")
        result = self._make_request('GET', '/health')
        
        if result.get('success') is not False:
            print(f"✅ API is healthy: {result}")
            return True
        else:
            print(f"❌ API health check failed: {result}")
            return False
    
    def list_projects(self) -> List[Dict]:
        """List all available projects."""
        print("\n📋 Listing all projects...")
        result = self._make_request('GET', '/projects')
        
        if result.get('success'):
            projects = result.get('projects', [])
            print(f"✅ Found {len(projects)} projects:")
            for i, project in enumerate(projects):
                print(f"  {i}: {project['name']} ({project['thread_count']} threads)")
            return projects
        else:
            print(f"❌ Failed to list projects: {result.get('error')}")
            return []
    
    def create_project(self, name: Optional[str] = None) -> Optional[str]:
        """Create a new project."""
        if not name:
            name = input("📝 Enter project name: ").strip()
            
        if not name:
            print("❌ Project name is required")
            return None
            
        print(f"🆕 Creating project: {name}...")
        
        data = {"name": name}
        result = self._make_request('POST', '/project/new', data)
        
        if result.get('success'):
            project_name = result['project_name']
            print(f"✅ Created project: {project_name}")
            self.current_project_name = project_name
            return project_name
        else:
            print(f"❌ Failed to create project: {result.get('error')}")
            return None
    
    def select_project(self, projects: List[Dict]) -> Optional[str]:
        """Let user select a project by index."""
        if not projects:
            print("No projects available.")
            return None
            
        try:
            index = int(input(f"🎯 Select project by index (0-{len(projects)-1}): "))
            if 0 <= index < len(projects):
                project_name = projects[index]['sanitized_name']
                self.current_project_name = project_name
                print(f"✅ Selected project: {project_name}")
                return project_name
            else:
                print("❌ Invalid index")
                return None
        except ValueError:
            print("❌ Invalid input, please enter a number")
            return None
    
    def list_threads(self, project_name: str) -> List[Dict]:
        """List all threads in a project."""
        print(f"\n📋 Listing threads in project {project_name}...")
        result = self._make_request('GET', f'/project/{project_name}/threads')
        
        if result.get('success'):
            threads = result.get('threads', [])
            print(f"✅ Found {len(threads)} threads:")
            for i, thread in enumerate(threads):
                print(f"  {i}: {thread['id']} - {thread['name']} ({thread['message_count']} messages)")
            return threads
        else:
            print(f"❌ Failed to list threads: {result.get('error')}")
            return []
    
    def create_thread(self, project_name: str, name: Optional[str] = None) -> Optional[str]:
        """Create a new thread in a project."""
        if not name:
            name = input("📝 Enter thread name (or press Enter for auto-generated): ").strip()
            
        print(f"🆕 Creating thread in project {project_name}: {name or 'auto-generated'}...")
        
        data = {"name": name} if name else {}
        result = self._make_request('POST', f'/project/{project_name}/thread/new', data)
        
        if result.get('success'):
            thread_id = result['thread_id']
            print(f"✅ Created thread: {thread_id}")
            self.current_thread_id = thread_id
            return thread_id
        else:
            print(f"❌ Failed to create thread: {result.get('error')}")
            return None
    
    def select_thread(self, project_name: str, threads: List[Dict]) -> Optional[str]:
        """Let user select a thread by index."""
        if not threads:
            print("No threads available.")
            return None
            
        try:
            index = int(input(f"🎯 Select thread by index (0-{len(threads)-1}): "))
            if 0 <= index < len(threads):
                thread_id = threads[index]['id']
                self.current_thread_id = thread_id
                print(f"✅ Selected thread: {thread_id}")
                return thread_id
            else:
                print("❌ Invalid index")
                return None
        except ValueError:
            print("❌ Invalid input, please enter a number")
            return None
    
    def send_message(self, project_name: str, thread_id: str, message: str) -> Optional[str]:
        """Send a message to Claude in the specified project/thread."""
        print(f"💬 Sending message to project {project_name}, thread {thread_id}...")
        print(f"Message: {message}")
        
        data = {"message": message}
        result = self._make_request('POST', f'/project/{project_name}/thread/{thread_id}/message', data)
        
        if result.get('success'):
            job_id = result['job_id']
            print(f"✅ Message queued with job ID: {job_id}")
            
            # Poll for completion
            print("⏳ Waiting for Claude response...")
            return self.wait_for_job(job_id)
        else:
            print(f"❌ Failed to send message: {result.get('error')}")
            return None
    
    def wait_for_job(self, job_id: str, max_wait: int = 300) -> Optional[str]:
        """Wait for a job to complete and return the response."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self._make_request('GET', f'/status/{job_id}')
            
            if result.get('success'):
                status = result.get('status')
                print(f"📊 Job status: {status}")
                
                if status == 'done':
                    response = result.get('response', '')
                    print(f"✅ Claude responded:")
                    print(f"{'='*50}")
                    print(response)  # Just show the response text, not the full JSON
                    print(f"{'='*50}")
                    return response
                elif status == 'failed':
                    error = result.get('error', 'Unknown error')
                    print(f"❌ Job failed: {error}")
                    return None
                else:
                    time.sleep(2)  # Wait 2 seconds before checking again
            else:
                print(f"❌ Failed to get job status: {result.get('error')}")
                return None
        
        print("⏰ Job timed out")
        return None
    
    def view_messages(self, project_name: str, thread_id: str):
        """View message history for a thread."""
        print(f"\n💬 Message history for project {project_name}, thread {thread_id}:")
        result = self._make_request('GET', f'/project/{project_name}/thread/{thread_id}/messages')
        
        if result.get('success'):
            messages = result.get('messages', [])
            if not messages:
                print("No messages in this thread.")
                return
                
            for i, msg in enumerate(messages):
                print(f"\n--- Message {i+1} ({msg.get('timestamp', 'unknown time')}) ---")
                print(f"User: {msg.get('user_message', '')}")
                print(f"Claude: {msg.get('claude_response', '')}")
        else:
            print(f"❌ Failed to get messages: {result.get('error')}")
    
    def view_files(self, project_name: str):
        """View file tree for a project."""
        print(f"\n📁 Files in project {project_name}:")
        result = self._make_request('GET', f'/project/{project_name}/files')
        
        if result.get('success'):
            file_tree = result.get('file_tree', {})
            self._print_tree(file_tree)
        else:
            print(f"❌ Failed to get files: {result.get('error')}")
    
    def _print_tree(self, node: Dict, prefix: str = ""):
        """Recursively print file tree."""
        if node.get('name'):
            icon = "📁" if node.get('type') == 'directory' else "📄"
            print(f"{prefix}{icon} {node['name']}")
            
            for child in node.get('children', []):
                self._print_tree(child, prefix + "  ")
    
    def delete_thread(self, project_name: str, thread_id: str, confirm: bool = False) -> bool:
        """Delete a thread and its Claude session."""
        if not confirm:
            response = input(f"⚠️  Are you sure you want to delete thread {thread_id}? This will remove all chat history. (y/N): ")
            if response.lower() != 'y':
                print("❌ Thread deletion cancelled")
                return False
        
        print(f"🗑️ Deleting thread {thread_id} from project {project_name}...")
        result = self._make_request('DELETE', f'/project/{project_name}/thread/{thread_id}')
        
        if result.get('success'):
            print(f"✅ {result.get('message', 'Thread deleted successfully')}")
            if self.current_thread_id == thread_id:
                self.current_thread_id = None
                print("📍 Current thread cleared")
            return True
        else:
            print(f"❌ Failed to delete thread: {result.get('error')}")
            return False
    
    def delete_project(self, project_name: str, confirm: bool = False) -> bool:
        """Delete an entire project including all threads and files."""
        if not confirm:
            response = input(f"⚠️  Are you sure you want to delete project '{project_name}'? This will remove ALL threads, chat history, and generated files. (y/N): ")
            if response.lower() != 'y':
                print("❌ Project deletion cancelled")
                return False
        
        print(f"🗑️ Deleting project {project_name} and all its contents...")
        result = self._make_request('DELETE', f'/project/{project_name}')
        
        if result.get('success'):
            print(f"✅ {result.get('message', 'Project deleted successfully')}")
            if self.current_project_name == project_name:
                self.current_project_name = None
                self.current_thread_id = None
                print("📍 Current project and thread cleared")
            return True
        else:
            print(f"❌ Failed to delete project: {result.get('error')}")
            return False
    
    def interactive_mode(self):
        """Run interactive testing mode."""
        print("🚀 Claude Web API Tester (Project/Thread Mode)")
        print("=" * 50)
        
        # Check API health
        if not self.health_check():
            print("❌ API is not available. Make sure the server is running.")
            return
        
        while True:
            print("\n🎮 Main Menu:")
            print("1. List projects")
            print("2. Create new project")
            print("3. Select project and manage threads")
            print("4. Select project and view files")
            print("5. Delete project")
            print("6. Exit")
            
            if self.current_project_name:
                print(f"\n📍 Current project: {self.current_project_name}")
            if self.current_thread_id:
                print(f"📍 Current thread: {self.current_thread_id}")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                self.list_projects()
                
            elif choice == '2':
                self.create_project()
                
            elif choice == '3':
                projects = self.list_projects()
                if projects:
                    project_name = self.select_project(projects)
                    if project_name:
                        self.project_thread_mode(project_name)
                        
            elif choice == '4':
                projects = self.list_projects()
                if projects:
                    project_name = self.select_project(projects)
                    if project_name:
                        self.view_files(project_name)
                        
            elif choice == '5':
                projects = self.list_projects()
                if projects:
                    project_name = self.select_project(projects)
                    if project_name:
                        self.delete_project(project_name)
                        
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice")
    
    def project_thread_mode(self, project_name: str):
        """Manage threads within a project."""
        while True:
            print(f"\n🗂️ Project: {project_name}")
            print("1. List threads")
            print("2. Create new thread")
            print("3. Select thread and chat")
            print("4. View messages in current thread")
            print("5. Delete thread")
            print("6. Back to main menu")
            
            if self.current_thread_id:
                print(f"\n📍 Current thread: {self.current_thread_id}")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                self.list_threads(project_name)
                
            elif choice == '2':
                self.create_thread(project_name)
                
            elif choice == '3':
                threads = self.list_threads(project_name)
                if threads:
                    thread_id = self.select_thread(project_name, threads)
                    if thread_id:
                        self.chat_mode(project_name, thread_id)
                        
            elif choice == '4':
                if self.current_thread_id:
                    self.view_messages(project_name, self.current_thread_id)
                else:
                    print("❌ No thread selected")
                    
            elif choice == '5':
                threads = self.list_threads(project_name)
                if threads:
                    thread_id = self.select_thread(project_name, threads)
                    if thread_id:
                        self.delete_thread(project_name, thread_id)
                    
            elif choice == '6':
                break
                
            else:
                print("❌ Invalid choice")
    
    def chat_mode(self, project_name: str, thread_id: str):
        """Enter chat mode for a specific project/thread."""
        print(f"\n💬 Chat Mode - Project: {project_name}, Thread: {thread_id}")
        print("Type 'exit' to return to project menu")
        print("-" * 50)
        
        while True:
            message = input("\n🤔 You: ").strip()
            
            if message.lower() == 'exit':
                break
                
            if message:
                self.send_message(project_name, thread_id, message)
            else:
                print("❌ Please enter a message")

def main():
    """Main entry point."""
    tester = ClaudeAPITester()
    
    if len(sys.argv) > 1:
        # Command line mode for quick testing
        if sys.argv[1] == 'health':
            tester.health_check()
        elif sys.argv[1] == 'list-projects':
            tester.list_projects()
        elif sys.argv[1] == 'create-project':
            name = sys.argv[2] if len(sys.argv) > 2 else None
            tester.create_project(name)
        else:
            print("Usage: python test_api.py [health|list-projects|create-project [name]]")
    else:
        # Interactive mode
        tester.interactive_mode()

if __name__ == '__main__':
    main()