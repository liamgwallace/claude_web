
#!/usr/bin/env python3
"""
Simple startup script for Claude Web Runner.
Just runs the Flask app that serves both the API and web interface.
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import flask_cors
        import requests
        import pydantic
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_claude_cli():
    """Check if Claude CLI is available."""
    try:
        result = subprocess.run(['claude', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Claude CLI is available")
            return True
        else:
            print("⚠️  Claude CLI found but may have issues")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Claude CLI not found in PATH")
        print("Please install Claude CLI and ensure it's in your PATH")
        return False

def main():
    print("🚀 Claude Web Runner Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if not check_claude_cli():
        print("⚠️  Continuing without Claude CLI - some features may not work")
    
    # Ensure data directory exists
    data_dir = Path("data/projects")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n🌐 Starting Flask server...")
    print("📊 Backend API: http://localhost:8000")
    print("🖥️  Web Interface: http://localhost:8000")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:8000')
        except:
            pass
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app from src directory
    try:
        # Change to src directory and run server
        original_dir = os.getcwd()
        os.chdir('src')
        os.system('python server.py 8000')
    except KeyboardInterrupt:
        print("\n👋 Shutting down Claude Web Runner")
    finally:
        os.chdir(original_dir)
        sys.exit(0)

if __name__ == "__main__":
    main()