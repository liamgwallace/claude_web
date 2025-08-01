#!/usr/bin/env python3
"""
Server startup script for Claude Web Runner.
Launches the Flask application with proper configuration.
"""

import os
import sys
import argparse
from app import app

def main():
    """Main server startup function."""
    parser = argparse.ArgumentParser(description='Start Claude Web Runner server')
    parser.add_argument('port', nargs='?', default=8000, type=int,
                        help='Port to run the server on (default: 8000)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # Ensure data directory exists
    os.makedirs('../data/projects', exist_ok=True)
    
    print(f"🌐 Starting Claude Web Runner on http://localhost:{args.port}")
    print(f"📁 Data directory: {os.path.abspath('../data/projects')}")
    print(f"🎯 Debug mode: {'ON' if args.debug else 'OFF'}")
    print("-" * 50)
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()