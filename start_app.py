#!/usr/bin/env python3
"""
Startup script for Claude Web Runner.
This script helps start both the Flask API backend and Chainlit frontend.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import requests
        print("✅ Flask and requests are installed")
        
        # Check chainlit separately to handle potential issues
        try:
            import chainlit
            print("✅ Chainlit is installed")
        except Exception as e:
            print(f"⚠️ Chainlit import issue: {e}")
            print("📦 Try: pip install --upgrade chainlit pydantic")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please run: pip install -r requirements.txt")
        return False

def check_claude_cli():
    """Check if Claude CLI is available."""
    try:
        # Try different ways to find claude on Windows
        claude_commands = ['claude', 'claude.cmd', 'npx claude']
        
        for cmd in claude_commands:
            try:
                result = subprocess.run([cmd, '--help'], capture_output=True, text=True, timeout=5, shell=True)
                if result.returncode == 0:
                    print(f"✅ Claude CLI is available ({cmd})")
                    return True
            except:
                continue
                
        print("❌ Claude CLI not found in PATH from Python script")
        print("💡 Try running from regular Command Prompt (not VS Code terminal)")
        print("💡 Or restart your terminal after installing Claude CLI")
        return False
    except Exception as e:
        print(f"❌ Error checking Claude CLI: {e}")
        return False

def start_backend():
    """Start the Flask API backend."""
    print("🚀 Starting Flask API backend...")
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    return subprocess.Popen([
        sys.executable, 'app.py'
    ], env=env)

def start_frontend():
    """Start the Chainlit frontend."""
    print("🌐 Starting Chainlit frontend...")
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    return subprocess.Popen([
        'chainlit', 'run', 'chainlit_app.py', '--host', '0.0.0.0', '--port', '8000'
    ], env=env)

def wait_for_backend():
    """Wait for backend to be ready."""
    import requests
    
    print("⏳ Waiting for backend API to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://localhost:5000/health', timeout=1)
            if response.status_code == 200:
                print("✅ Backend API is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        if i % 5 == 0:
            print(f"⏳ Still waiting... ({i}/30 seconds)")
    
    print("❌ Backend API failed to start")
    return False

def main():
    """Main startup function."""
    print("🚀 Claude Web Runner Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('chainlit_app.py').exists():
        print("❌ Please run this script from the claude_web directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Claude CLI
    if not check_claude_cli():
        print("⚠️  Claude CLI not available - the app will still run but Claude interactions will fail")
        input("Press Enter to continue anyway or Ctrl+C to exit...")
    
    # Ensure data directory exists
    os.makedirs('data/projects', exist_ok=True)
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        
        # Wait for backend to be ready
        if not wait_for_backend():
            print("❌ Failed to start backend, exiting...")
            return
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("\n" + "=" * 50)
        print("🎉 Claude Web Runner is starting up!")
        print("📊 Backend API: http://localhost:5000")
        print("🌐 Frontend UI: http://localhost:8000")
        print("=" * 50)
        print("\n📋 To use the app:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Create or select a project")
        print("3. Create or select a thread")
        print("4. Start chatting with Claude!")
        print("\n🛑 Press Ctrl+C to stop both services")
        
        # Wait for processes
        while True:
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"❌ Process {i} has stopped unexpectedly")
                    return
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Clean up processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✅ All processes stopped")

if __name__ == "__main__":
    main()