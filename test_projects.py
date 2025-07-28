#!/usr/bin/env python3
"""
Test data generator for Claude Web Runner.
Creates sample projects, threads, and messages for testing the application.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Optional
from test_api import ClaudeAPITester

class TestDataGenerator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.tester = ClaudeAPITester(base_url)
        self.created_projects = []
        self.created_threads = {}  # project_name -> [thread_ids]
        
    def check_api_health(self) -> bool:
        """Check if API is available before generating test data."""
        print("🏥 Checking API health...")
        return self.tester.health_check()
    
    def create_test_projects(self) -> bool:
        """Create several test projects with different purposes."""
        projects = [
            {
                "name": "Web Development",
                "description": "Frontend and backend development tasks"
            },
            {
                "name": "Data Analysis",
                "description": "Python data science and analysis projects"
            },
            {
                "name": "DevOps Setup",
                "description": "Infrastructure and deployment automation"
            },
            {
                "name": "Learning Python",
                "description": "Python tutorials and practice exercises"
            },
            {
                "name": "API Testing",
                "description": "REST API development and testing"
            }
        ]
        
        print(f"\n🏗️  Creating {len(projects)} test projects...")
        
        for project in projects:
            project_name = self.tester.create_project(project["name"])
            if project_name:
                self.created_projects.append(project_name)
                self.created_threads[project_name] = []
                print(f"✅ Created project: {project_name}")
            else:
                print(f"❌ Failed to create project: {project['name']}")
                return False
        
        return True
    
    def create_test_threads(self) -> bool:
        """Create multiple threads in each project."""
        thread_configs = {
            "Web Development": [
                "React Component Help",
                "CSS Styling Issues", 
                "Node.js Backend Setup",
                "Database Integration"
            ],
            "Data Analysis": [
                "Pandas Data Cleaning",
                "Matplotlib Visualization",
                "Statistical Analysis",
                "Machine Learning Model"
            ],
            "DevOps Setup": [
                "Docker Configuration",
                "CI/CD Pipeline",
                "AWS Deployment",
                "Monitoring Setup"
            ],
            "Learning Python": [
                "Basic Syntax Help",
                "Object-Oriented Programming",
                "Error Handling",
                "Advanced Topics"
            ],
            "API Testing": [
                "REST Endpoint Design",
                "Authentication Setup",
                "Database Models",
                "Testing Framework"
            ]
        }
        
        print(f"\n🧵 Creating test threads...")
        
        for project_name, thread_names in thread_configs.items():
            # Find the actual project name (sanitized)
            actual_project = None
            expected_name = project_name.lower().replace(' ', '-')
            for created_project in self.created_projects:
                if expected_name == created_project.lower():
                    actual_project = created_project
                    break
            
            if not actual_project:
                print(f"❌ Could not find project for: {project_name} (expected: {expected_name})")
                print(f"   Available projects: {self.created_projects}")
                continue
                    
            for thread_name in thread_names:
                thread_id = self.tester.create_thread(actual_project, thread_name)
                if thread_id:
                    self.created_threads[actual_project].append(thread_id)
                    print(f"✅ Created thread '{thread_name}' in {actual_project}")
                else:
                    print(f"❌ Failed to create thread: {thread_name}")
        
        return True
    
    def send_test_messages(self) -> bool:
        """Send sample messages to test threads."""
        test_messages = {
            "React Component Help": [
                "Help me create a reusable button component in React with TypeScript",
                "How do I handle form validation in React?"
            ],
            "CSS Styling Issues": [
                "My flexbox layout isn't working properly. Can you help debug it?",
                "How do I create a responsive navigation menu?"
            ],
            "Pandas Data Cleaning": [
                "I have a CSV file with missing values. How do I clean it using pandas?",
                "Show me how to handle duplicate rows in a DataFrame"
            ],
            "Docker Configuration": [
                "Create a Dockerfile for a Python Flask application",
                "How do I set up multi-stage builds in Docker?"
            ],
            "Basic Syntax Help": [
                "Explain Python list comprehensions with examples",
                "What's the difference between lists and tuples?"
            ],
            "REST Endpoint Design": [
                "Help me design RESTful endpoints for a blog API",
                "How do I handle pagination in REST APIs?"
            ]
        }
        
        print(f"\n💬 Sending test messages...")
        
        # Send a few test messages to selected threads
        message_count = 0
        for project_name, thread_ids in self.created_threads.items():
            if not thread_ids:
                continue
                
            # Send messages to first 2 threads of each project
            for i, thread_id in enumerate(thread_ids[:2]):
                # Find matching messages for this thread
                messages_sent = 0
                for thread_name, messages in test_messages.items():
                    if messages_sent >= 1:  # Only send 1 message per thread to avoid long waits
                        break
                        
                    # Send first message from matching thread type
                    message = messages[0]
                    print(f"📤 Sending message to {project_name}/{thread_id}: '{message[:50]}...'")
                    
                    response = self.tester.send_message(project_name, thread_id, message)
                    if response:
                        message_count += 1
                        messages_sent += 1
                        print(f"✅ Message sent successfully")
                    else:
                        print(f"❌ Failed to send message")
                    
                    # Add delay between messages to avoid overwhelming the system
                    time.sleep(1)
        
        print(f"✅ Sent {message_count} test messages")
        return True
    
    def generate_summary(self):
        """Print summary of created test data."""
        print(f"\n📊 Test Data Generation Summary")
        print("=" * 50)
        print(f"📁 Projects Created: {len(self.created_projects)}")
        
        total_threads = sum(len(threads) for threads in self.created_threads.values())
        print(f"🧵 Threads Created: {total_threads}")
        
        print(f"\n📋 Project Details:")
        for project_name in self.created_projects:
            thread_count = len(self.created_threads.get(project_name, []))
            print(f"  • {project_name}: {thread_count} threads")
        
        print(f"\n🚀 Ready for testing! Use the web interface at http://localhost:8000")
        print(f"💡 Or test with: python test_api.py")
    
    def cleanup_test_data(self, confirm: bool = False):
        """Remove all created test data."""
        if not confirm:
            response = input(f"\n⚠️  Delete all {len(self.created_projects)} test projects? This will remove all data. (y/N): ")
            if response.lower() != 'y':
                print("❌ Cleanup cancelled")
                return False
        
        print(f"\n🗑️ Cleaning up test data...")
        
        deleted_count = 0
        for project_name in self.created_projects:
            if self.tester.delete_project(project_name, confirm=True):
                deleted_count += 1
                print(f"✅ Deleted project: {project_name}")
            else:
                print(f"❌ Failed to delete project: {project_name}")
        
        print(f"✅ Cleanup complete. Deleted {deleted_count}/{len(self.created_projects)} projects")
        return deleted_count == len(self.created_projects)

def main():
    """Main entry point with command-line options."""
    print("🧪 Claude Web Runner - Test Data Generator")
    print("=" * 50)
    
    generator = TestDataGenerator()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'cleanup':
            # Check if projects exist first
            existing_projects = generator.tester.list_projects()
            if not existing_projects:
                print("ℹ️  No projects found to clean up")
                return
                
            generator.created_projects = [p['sanitized_name'] for p in existing_projects]
            generator.cleanup_test_data(confirm=True)
            return
            
        elif command == 'health':
            generator.check_api_health()
            return
            
        elif command in ['help', '-h', '--help']:
            print("Usage:")
            print("  python test_projects.py          # Generate test data")
            print("  python test_projects.py cleanup  # Remove all test projects")
            print("  python test_projects.py health   # Check API health")
            return
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python test_projects.py help' for usage info")
            return
    
    # Default: Generate test data
    try:
        # Check API health first
        if not generator.check_api_health():
            print("❌ API is not available. Make sure to start the server first:")
            print("   python start.py")
            sys.exit(1)
        
        # Generate test data
        print(f"\n🚀 Starting test data generation...")
        
        if not generator.create_test_projects():
            print("❌ Failed to create test projects")
            sys.exit(1)
        
        if not generator.create_test_threads():
            print("❌ Failed to create test threads")
            sys.exit(1)
        
        print(f"\n⏳ Sending sample messages (this may take a few minutes)...")
        if not generator.send_test_messages():
            print("⚠️  Some messages failed to send, but continuing...")
        
        generator.generate_summary()
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Generation interrupted by user")
        print(f"🧹 You can clean up partial data with: python test_projects.py cleanup")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during test data generation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()