#!/usr/bin/env python3
"""
Simple startup script for Claude Web Runner - Windows compatible.
This script avoids potential Chainlit import issues during dependency checking.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    """Simple startup - just run both components."""
    print("🚀 Claude Web Runner - Simple Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('chainlit_app.py').exists():
        print("❌ Please run this script from the claude_web directory")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Ensure data directory exists
    os.makedirs('data/projects', exist_ok=True)
    
    print("🎯 Quick Start Guide:")
    print("1. Start Backend (Terminal 1): python app.py")
    print("2. Start Frontend (Terminal 2): chainlit run chainlit_app.py")
    print("3. Open browser: http://localhost:8000")
    print("\n" + "=" * 50)
    
    choice = input("\n🤔 What would you like to do?\n1. Start backend only\n2. Start frontend only\n3. Show manual commands\n4. Exit\n\nChoice (1-4): ").strip()
    
    if choice == '1':
        print("🚀 Starting Flask backend...")
        print("📊 Backend will be available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            subprocess.run([sys.executable, 'app.py'])
        except KeyboardInterrupt:
            print("\n🛑 Backend stopped")
            
    elif choice == '2':
        print("🌐 Starting Chainlit frontend...")
        print("📱 Frontend will be available at: http://localhost:8000")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            subprocess.run(['chainlit', 'run', 'chainlit_app.py', '--host', '0.0.0.0', '--port', '8000'])
        except KeyboardInterrupt:
            print("\n🛑 Frontend stopped")
            
    elif choice == '3':
        print("\n📋 Manual Commands:")
        print("🔧 Backend (Terminal 1):")
        print("   python app.py")
        print("\n🌐 Frontend (Terminal 2):")
        print("   chainlit run chainlit_app.py")
        print("\n🌍 Then open: http://localhost:8000")
        print("\n💡 Tip: Make sure backend starts first!")
        
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()