"""
Flask API backend for Claude Code project and thread management.
Projects are physical folders where Claude CLI runs.
Threads are chat conversations stored as metadata within projects.
"""

from flask import Flask, request, jsonify
from flask.helpers import send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os
import json
import gzip
import io
from claude_wrapper import ClaudeWrapper
import asyncio
from threading import Thread
import queue
import time

def is_image_file(extension):
    """Check if file extension indicates an image file."""
    image_extensions = {
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff', 'tif'
    }
    return extension.lower() in image_extensions

def get_language_from_extension(extension):
    """Map file extensions to Prism.js language identifiers."""
    lang_map = {
        # Web languages
        'js': 'javascript',
        'jsx': 'jsx',
        'ts': 'typescript',
        'tsx': 'tsx',
        'html': 'html',
        'htm': 'html',
        'css': 'css',
        'scss': 'scss',
        'sass': 'sass',
        'less': 'less',
        
        # Python
        'py': 'python',
        'pyx': 'python',
        'pyw': 'python',
        
        # Data formats
        'json': 'json',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
        'toml': 'toml',
        'ini': 'ini',
        'csv': 'csv',
        
        # Markup
        'md': 'markdown',
        'markdown': 'markdown',
        'rst': 'rest',
        'tex': 'latex',
        
        # Shell scripts
        'sh': 'bash',
        'bash': 'bash',
        'zsh': 'bash',
        'fish': 'bash',
        'ps1': 'powershell',
        
        # Databases
        'sql': 'sql',
        'sqlite': 'sql',
        'mysql': 'sql',
        'pgsql': 'sql',
        
        # Config files
        'conf': 'apache',
        'htaccess': 'apache',
        'nginx': 'nginx',
        'dockerfile': 'docker',
        
        # Programming languages
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'cpp': 'cpp',
        'cxx': 'cpp',
        'cc': 'cpp',
        'c': 'c',
        'h': 'c',
        'hpp': 'cpp',
        'java': 'java',
        'cs': 'csharp',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'dart': 'dart',
        'r': 'r',
        'lua': 'lua',
        'perl': 'perl',
        'pl': 'perl',
        
        # Functional languages
        'hs': 'haskell',
        'elm': 'elm',
        'clj': 'clojure',
        'ml': 'ocaml',
        'fs': 'fsharp',
        
        # Other
        'vim': 'vim',
        'diff': 'diff',
        'patch': 'diff',
        'log': 'log',
        'makefile': 'makefile',
        'cmake': 'cmake',
        'gradle': 'gradle',
        'properties': 'properties',
        'gitignore': 'git',
        'gitconfig': 'git',
    }
    
    return lang_map.get(extension, 'text')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Add request logging middleware for debugging external access issues
@app.before_request
def log_request_info():
    if '/download' in request.path:  # Only log download requests to reduce noise
        logger.info('=== REQUEST DEBUG ===')
        logger.info(f'Request method: {request.method}')
        logger.info(f'Request URL: {request.url}')
        logger.info(f'Request path: {request.path}')
        logger.info(f'Request args: {dict(request.args)}')
        logger.info(f'Request remote_addr: {request.remote_addr}')
        logger.info(f'Request user_agent: {request.headers.get("User-Agent", "Unknown")}')
        logger.info(f'Request referer: {request.headers.get("Referer", "None")}')
        logger.info('=== REQUEST DEBUG END ===')

# Enhanced CORS configuration for mobile browser compatibility
CORS(app, 
     origins=["*"],  # Allow all origins for development
     methods=["GET", "POST", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "User-Agent"],
     expose_headers=["Content-Type", "Cache-Control", "X-Content-Type-Options"],
     supports_credentials=False,
     max_age=3600  # Cache preflight requests
)

# Enhanced proxy support for VS Code port forwarding and mobile compatibility
app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=2,       # Increased for better mobile proxy handling
    x_proto=1, 
    x_host=1, 
    x_prefix=1,
    x_port=1       # Added port handling for mobile proxies
)

# Custom gzip compression for better mobile performance
def gzip_response(response):
    """Apply gzip compression if client supports it."""
    try:
        if ('gzip' in request.headers.get('Accept-Encoding', '') and 
            response.status_code == 200 and 
            hasattr(response, 'get_data') and
            not response.direct_passthrough):
            
            # Get response data safely
            response_data = response.get_data()
            if len(response_data) > 500:  # Only compress files larger than 500 bytes
                
                # Compress the response data
                gzipped_data = gzip.compress(response_data)
                
                # Update the response
                response.set_data(gzipped_data)
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(gzipped_data)
                response.headers['Vary'] = 'Accept-Encoding'
    except Exception as e:
        # If compression fails, just return original response
        app.logger.warning(f"Gzip compression failed: {e}")
        pass
    
    return response

# Initialize Claude wrapper
claude_wrapper = ClaudeWrapper()

# Enhanced request logging middleware for mobile debugging
@app.before_request
def log_request():
    user_agent = request.headers.get('User-Agent', 'Unknown')
    is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
    
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    logger.info(f"User-Agent: {user_agent}")
    logger.info(f"Mobile Device: {is_mobile}")
    logger.info(f"Accept: {request.headers.get('Accept', 'Unknown')}")
    logger.info(f"Accept-Encoding: {request.headers.get('Accept-Encoding', 'Unknown')}")
    
    # Log potential mobile-specific headers
    if is_mobile:
        logger.info(f"Mobile Headers - X-Forwarded-For: {request.headers.get('X-Forwarded-For', 'None')}")
        logger.info(f"Mobile Headers - X-Real-IP: {request.headers.get('X-Real-IP', 'None')}")
        logger.info(f"Mobile Headers - Connection: {request.headers.get('Connection', 'None')}")

# Mobile-specific response headers and compression middleware
@app.after_request
def add_mobile_headers(response):
    """Add mobile-compatible headers to all responses and apply compression."""
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad'])
    
    if is_mobile:
        # Force no caching for HTML on mobile to prevent stale layouts
        if response.content_type and 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, no-transform'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # Ensure CSS loads properly on mobile
        if response.content_type and 'text/css' in response.content_type:
            response.headers['Cache-Control'] = 'public, max-age=300, no-transform'  # Shorter cache for mobile CSS
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
        # Ensure JS loads properly on mobile
        if response.content_type and 'javascript' in response.content_type:
            response.headers['Cache-Control'] = 'public, max-age=300, no-transform'
            response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Always add these headers for better mobile compatibility
    response.headers['X-UA-Compatible'] = 'IE=edge'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Apply gzip compression for text-based content
    if response.content_type and any(content_type in response.content_type for content_type in 
                                   ['text/', 'application/javascript', 'application/json']):
        response = gzip_response(response)
    
    return response

# Simple job queue for async processing
job_queue = queue.Queue()
job_status = {}

def job_worker():
    """Background worker for processing Claude CLI jobs."""
    while True:
        try:
            job = job_queue.get(timeout=1)
            if job is None:
                break
                
            job_id = job['id']
            project_name = job['project_name']
            thread_id = job['thread_id']
            message = job['message']
            
            job_status[job_id] = {'status': 'running', 'project_name': project_name, 'thread_id': thread_id}
            
            success, response, metadata = claude_wrapper.send_message(project_name, thread_id, message)
            
            if success:
                job_status[job_id] = {
                    'status': 'done', 
                    'project_name': project_name,
                    'thread_id': thread_id,
                    'response': response,
                    'metadata': metadata
                }
            else:
                job_status[job_id] = {
                    'status': 'failed', 
                    'project_name': project_name,
                    'thread_id': thread_id,
                    'error': response
                }
                
            job_queue.task_done()
            
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Job worker error: {e}")
            if 'job_id' in locals():
                job_status[job_id] = {'status': 'failed', 'error': str(e)}

# Start background worker
worker_thread = Thread(target=job_worker, daemon=True)
worker_thread.start()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "claude-web-api"})

@app.route('/projects', methods=['GET'])
def list_projects():
    """
    GET /projects - Lists all projects
    """
    try:
        projects = claude_wrapper.list_projects()
        return jsonify({
            "success": True,
            "projects": projects,
            "count": len(projects)
        })
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/new', methods=['POST'])
def create_project():
    """
    POST /project/new – Creates a new project folder
    """
    try:
        data = request.get_json() or {}
        project_name = data.get('name')
        
        if not project_name:
            return jsonify({"success": False, "error": "Project name is required"}), 400
        
        sanitized_name = claude_wrapper.create_project(project_name)
        
        return jsonify({
            "success": True,
            "project_name": sanitized_name,
            "original_name": project_name
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/threads', methods=['GET'])
def list_project_threads(project_name):
    """
    GET /project/:project_name/threads - Lists all threads in a project
    """
    try:
        threads = claude_wrapper.list_threads(project_name)
        return jsonify({
            "success": True,
            "project_name": project_name,
            "threads": threads,
            "count": len(threads)
        })
    except Exception as e:
        logger.error(f"Error listing threads for project {project_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/thread/new', methods=['POST'])
def create_thread(project_name):
    """
    POST /project/:project_name/thread/new – Creates a new thread in a project
    """
    try:
        data = request.get_json() or {}
        thread_name = data.get('name')
        
        thread_id = claude_wrapper.create_thread(project_name, thread_name)
        
        return jsonify({
            "success": True,
            "project_name": project_name,
            "thread_id": thread_id,
            "name": thread_name or f"Thread {thread_id}"
        }), 201
        
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating thread in project {project_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/thread/<thread_id>/message', methods=['POST'])
def send_message(project_name, thread_id):
    """
    POST /project/:project_name/thread/:thread_id/message – Sends message to Claude CLI
    Returns job ID for async processing
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "Message is required"}), 400
            
        message = data['message']
        
        # Create async job
        job_id = f"job_{int(time.time() * 1000)}_{project_name}_{thread_id}"
        
        job = {
            'id': job_id,
            'project_name': project_name,
            'thread_id': thread_id,
            'message': message
        }
        
        job_status[job_id] = {'status': 'queued', 'project_name': project_name, 'thread_id': thread_id}
        job_queue.put(job)
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "project_name": project_name,
            "thread_id": thread_id,
            "status": "queued"
        }), 202
        
    except Exception as e:
        logger.error(f"Error sending message to project {project_name}, thread {thread_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/thread/<thread_id>/messages', methods=['GET'])
def get_messages(project_name, thread_id):
    """
    GET /project/:project_name/thread/:thread_id/messages – Returns history of messages
    """
    try:
        messages = claude_wrapper.get_messages(project_name, thread_id)
        
        if messages is None:
            return jsonify({"success": False, "error": "Thread not found"}), 404
            
        return jsonify({
            "success": True,
            "project_name": project_name,
            "thread_id": thread_id,
            "messages": messages,
            "count": len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error getting messages for project {project_name}, thread {thread_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/files', methods=['GET'])
def get_files(project_name):
    """
    GET /project/:project_name/files – Returns file tree of the project folder
    """
    try:
        file_tree = claude_wrapper.get_file_tree(project_name)
        
        if file_tree is None:
            return jsonify({"success": False, "error": "Project not found"}), 404
            
        return jsonify({
            "success": True,
            "project_name": project_name,
            "file_tree": file_tree
        })
        
    except Exception as e:
        logger.error(f"Error getting files for project {project_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/file', methods=['GET'])
def get_file_content(project_name):
    """
    GET /project/:project_name/file?path=relative/file.txt – Returns contents of the specified file
    """
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({"success": False, "error": "File path is required"}), 400
            
        content = claude_wrapper.get_file_content(project_name, file_path)
        
        if content is None:
            return jsonify({"success": False, "error": "File not found or cannot be read"}), 404
            
        return jsonify({
            "success": True,
            "project_name": project_name,
            "file_path": file_path,
            "content": content
        })
        
    except Exception as e:
        logger.error(f"Error getting file content for project {project_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/file/<path:file_path>/save', methods=['POST'])
def save_file_content(project_name, file_path):
    """
    POST /project/:project_name/file/:file_path/save – Saves content to the specified file
    """
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"success": False, "error": "Content is required"}), 400
            
        content = data['content']
        
        success, message = claude_wrapper.write_file_content(project_name, file_path, content)
        
        if success:
            return jsonify({
                "success": True,
                "project_name": project_name,
                "file_path": file_path,
                "message": message
            })
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400 if "not found" in message.lower() or "access denied" in message.lower() else 500
        
    except Exception as e:
        logger.error(f"Error saving file content for project {project_name}, file {file_path}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/file/<path:file_path>/download', methods=['GET'])
def download_file(project_name, file_path):
    """
    GET /project/:project_name/file/:file_path/download – Downloads the raw file content
    """
    logger.info(f"=== DOWNLOAD DEBUG START ===")
    logger.info(f"Download request received")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request remote_addr: {request.remote_addr}")
    logger.info(f"Request host: {request.host}")
    logger.info(f"Project name (raw): '{project_name}'")
    logger.info(f"File path (raw): '{file_path}'")
    logger.info(f"Project name type: {type(project_name)}")
    logger.info(f"File path type: {type(file_path)}")
    
    try:
        # Get the actual file path on disk
        project_dir = claude_wrapper.base_projects_dir / project_name
        target_file = project_dir / file_path
        
        logger.info(f"Base projects dir: {claude_wrapper.base_projects_dir}")
        logger.info(f"Project dir: {project_dir}")
        logger.info(f"Target file path: {target_file}")
        logger.info(f"Project dir exists: {project_dir.exists()}")
        logger.info(f"Target file exists: {target_file.exists()}")
        logger.info(f"Target file is file: {target_file.is_file() if target_file.exists() else 'N/A'}")
        
        # Security check - ensure the file is within the project directory
        try:
            relative_path = target_file.resolve().relative_to(project_dir.resolve())
            logger.info(f"Security check passed, relative path: {relative_path}")
        except ValueError as ve:
            logger.error(f"Security check failed: {ve}")
            logger.error(f"Target file resolved: {target_file.resolve()}")
            logger.error(f"Project dir resolved: {project_dir.resolve()}")
            return jsonify({"success": False, "error": "Access denied"}), 403
        
        if not target_file.exists():
            logger.error(f"File does not exist: {target_file}")
            return jsonify({"success": False, "error": "File not found"}), 404
            
        if not target_file.is_file():
            logger.error(f"Path is not a file: {target_file}")
            return jsonify({"success": False, "error": "Path is not a file"}), 404
        
        # Get file info
        file_size = target_file.stat().st_size
        logger.info(f"File size: {file_size} bytes")
        
        # Determine MIME type
        import mimetypes
        mime_type, encoding = mimetypes.guess_type(str(target_file))
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        logger.info(f"Detected MIME type: {mime_type}")
        logger.info(f"Detected encoding: {encoding}")
        logger.info(f"Download filename: {target_file.name}")
        
        # Read file and send as download
        from flask import send_file
        logger.info(f"Attempting to send file with send_file()")
        logger.info(f"=== DOWNLOAD DEBUG END ===")
        
        return send_file(
            target_file, 
            as_attachment=True, 
            download_name=target_file.name,
            mimetype=mime_type
        )
        
    except Exception as e:
        logger.error(f"=== DOWNLOAD ERROR ===")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception message: {str(e)}")
        logger.error(f"Exception details:", exc_info=True)
        logger.error(f"=== DOWNLOAD ERROR END ===")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    GET /status/:id – Returns job state (queued, running, done, failed)
    """
    try:
        if job_id not in job_status:
            return jsonify({"success": False, "error": "Job not found"}), 404
            
        status = job_status[job_id]
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            **status
        })
        
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/thread/<thread_id>/status', methods=['GET'])
def get_thread_status(project_name, thread_id):
    """
    GET /project/:project_name/thread/:thread_id/status – Returns thread status and metadata
    """
    try:
        status = claude_wrapper.get_thread_status(project_name, thread_id)
        
        return jsonify({
            "success": True,
            **status
        })
        
    except Exception as e:
        logger.error(f"Error getting thread status for project {project_name}, thread {thread_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>/thread/<thread_id>', methods=['DELETE'])
def delete_thread(project_name, thread_id):
    """
    DELETE /project/:project_name/thread/:thread_id – Delete a thread and its Claude session
    """
    try:
        success, message = claude_wrapper.delete_thread(project_name, thread_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "project_name": project_name,
                "thread_id": thread_id
            })
        else:
            return jsonify({
                "success": False,
                "error": message,
                "project_name": project_name,
                "thread_id": thread_id
            }), 404 if "not found" in message.lower() else 500
        
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id} from project {project_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/project/<project_name>', methods=['DELETE'])
def delete_project(project_name):
    """
    DELETE /project/:project_name – Delete entire project including all threads and files
    """
    try:
        success, message = claude_wrapper.delete_project(project_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "project_name": project_name
            })
        else:
            return jsonify({
                "success": False,
                "error": message,
                "project_name": project_name
            }), 404 if "not found" in message.lower() else 500
        
    except Exception as e:
        logger.error(f"Error deleting project {project_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/view/<project_name>/file/<path:file_path>', methods=['GET'])
def serve_file_viewer(project_name, file_path):
    """Serve the fixed file viewer for a specific project file."""
    try:
        # Handle empty file path 
        if not file_path or file_path == '':
            return """
<!DOCTYPE html>
<html>
<head><title>No File Specified</title></head>
<body style="font-family: monospace; padding: 20px;">
    <h2>No File Specified</h2>
    <p>Please specify a file path</p>
</body>
</html>
""", 400
        
        # Get file content using the existing wrapper
        content = claude_wrapper.get_file_content(project_name, file_path)
        
        if content is None:
            return f"""
<!DOCTYPE html>
<html>
<head><title>File Not Found</title></head>
<body style="font-family: monospace; padding: 20px;">
    <h2>File Not Found</h2>
    <p>Project: {project_name}</p>
    <p>File: {file_path}</p>
</body>
</html>
""", 404
        
        # Improved binary detection - check for null bytes and high ratio of non-printable chars
        try:
            # Try to ensure content is string
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Check for null bytes (definite binary indicator)
            has_null_bytes = '\0' in content
            
            # Check ratio of non-printable characters in first 1000 chars
            sample = content[:1000]
            if len(sample) > 0:
                printable_chars = sum(1 for c in sample if c.isprintable() or c in '\n\r\t')
                non_printable_ratio = (len(sample) - printable_chars) / len(sample)
                has_high_non_printable = non_printable_ratio > 0.3  # More than 30% non-printable
            else:
                has_high_non_printable = False
            
            is_binary = has_null_bytes or has_high_non_printable
        except Exception:
            # If any error in detection, assume it's binary to be safe
            is_binary = True
        
        # Get file extension for image detection
        file_extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
        
        if is_image_file(file_extension):
            # Handle image files - embed as data URL to bypass authentication issues
            try:
                # Get the actual image file data
                project_dir = claude_wrapper.base_projects_dir / project_name
                target_file = project_dir / file_path
                
                # Security check
                target_file.resolve().relative_to(project_dir.resolve())
                
                if target_file.exists() and target_file.is_file():
                    # Read the binary image data
                    with open(target_file, 'rb') as img_file:
                        image_data = img_file.read()
                    
                    # Determine MIME type based on extension
                    mime_types = {
                        'png': 'image/png',
                        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                        'gif': 'image/gif',
                        'bmp': 'image/bmp',
                        'webp': 'image/webp',
                        'svg': 'image/svg+xml',
                        'ico': 'image/x-icon',
                        'tiff': 'image/tiff', 'tif': 'image/tiff'
                    }
                    mime_type = mime_types.get(file_extension.lower(), 'image/png')
                    
                    # Convert to base64 data URL
                    import base64
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    data_url = f"data:{mime_type};base64,{base64_data}"
                    actual_file_size = len(image_data)
                    
                    file_content = f"""
                    <div class="image-container" style="text-align: center; padding: 20px;">
                        <img id="main-image" src="{data_url}" 
                             alt="{file_path}" 
                             style="max-width: 100%; max-height: 80vh; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" 
                             onload="this.style.display='block'; console.log('Image loaded successfully (data URL)');" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block'; console.error('Image failed to load (data URL)');" />
                        <div style="display: none; color: #666; margin-top: 20px;">
                            <p>Failed to load image</p>
                            <p>File size: {actual_file_size} bytes</p>
                        </div>
                        <div style="margin-top: 15px; color: #666; font-size: 14px;">
                            <p>{file_path}</p>
                            <p>Image file ({actual_file_size:,} bytes)</p>
                        </div>
                    </div>
                    """
                else:
                    file_content = "<p style='color: #666;'>Image file not found</p>"
            except Exception as e:
                logger.error(f"Error loading image {file_path}: {e}")
                file_content = f"<p style='color: #666;'>Error loading image: {str(e)}</p>"
        elif is_binary:
            file_content = f"<p style='color: #666;'>Binary file ({len(content)} bytes) - cannot display as text</p>"
        else:
            # Get language for syntax highlighting
            file_extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
            language = get_language_from_extension(file_extension)
            
            # Escape HTML and format for syntax highlighting
            import html
            escaped_content = html.escape(content)
            
            if language and language != 'text':
                # Use syntax highlighting
                file_content = f'<pre class="line-numbers"><code class="language-{language}">{escaped_content}</code></pre>'
            else:
                # Plain text
                file_content = f'<pre style="white-space: pre-wrap; word-wrap: break-word;">{escaped_content}</pre>'
        
        # Prepare data for JavaScript (using safe JSON encoding)
        import html
        is_image = is_image_file(file_extension)
        original_content_json = json.dumps(content if not is_binary and not is_image else "", ensure_ascii=False)
        project_name_json = json.dumps(project_name, ensure_ascii=False)
        file_path_json = json.dumps(file_path, ensure_ascii=False)
        escaped_content_json = json.dumps(html.escape(content) if not is_binary and not is_image else "", ensure_ascii=False)
        
        # Create response with explicit HTML content type
        from flask import Response
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{file_path.split('/')[-1]} - {project_name}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 10px;
            background: #f8f9fa;
            line-height: 1.6;
            min-height: 100vh;
        }}
        .header {{
            background: white;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .file-info-section {{
            flex: 1;
        }}
        .file-name {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .file-info {{
            font-size: 14px;
            color: #6c757d;
        }}
        .toolbar {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            color: #495057;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .btn:hover {{
            background: #e9ecef;
            border-color: #adb5bd;
        }}
        .btn.primary {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
        .btn.primary:hover {{
            background: #0056b3;
            border-color: #0056b3;
        }}
        .btn.danger {{
            background: #dc3545;
            color: white;
            border-color: #dc3545;
        }}
        .btn.danger:hover {{
            background: #c82333;
            border-color: #c82333;
        }}
        .btn.success {{
            background: #28a745;
            color: white;
            border-color: #28a745;
        }}
        .btn.success:hover {{
            background: #218838;
            border-color: #218838;
        }}
        .btn:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
        }}
        .btn:disabled:hover {{
            background: #f8f9fa;
            border-color: #ddd;
        }}
        .btn.primary:disabled:hover {{
            background: #007bff;
            border-color: #007bff;
        }}
        .close-btn {{
            background: #dc3545;
            color: white;
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            padding: 0;
        }}
        .close-btn:hover {{
            background: #c82333;
        }}
        .content {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            max-height: calc(100vh - 120px);
            overflow: auto;
            position: relative;
        }}
        .editor-container {{
            position: relative;
            min-height: 400px;
        }}
        .editor-textarea {{
            width: 100%;
            min-height: 400px;
            padding: 20px;
            border: none;
            outline: none;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
            font-size: 14px;
            line-height: 1.5;
            resize: vertical;
            background: white;
            color: #333;
            border-radius: 6px;
        }}
        /* Custom Prism.js styling */
        pre[class*="language-"] {{
            margin: 0;
            padding: 20px;
            font-size: 14px;
            line-height: 1.5;
        }}
        code[class*="language-"] {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
        }}
        .line-numbers .line-numbers-rows {{
            border-right: 1px solid #e1e5e9;
            padding-right: 8px;
            margin-right: 8px;
        }}
        /* Plain text styling */
        pre:not([class*="language-"]) {{
            margin: 0;
            padding: 20px;
            font-size: 14px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .status-message {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            display: none;
        }}
        .status-message.success {{
            background: #28a745;
        }}
        .status-message.error {{
            background: #dc3545;
        }}
        .loading-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
        }}
        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        /* Responsive design */
        @media (max-width: 768px) {{
            body {{ padding: 5px; }}
            .header {{ 
                padding: 10px 15px;
                flex-direction: column;
                align-items: stretch;
            }}
            .toolbar {{ 
                justify-content: center;
                margin-top: 10px;
            }}
            .btn {{ 
                padding: 10px 15px;
                font-size: 16px;
            }}
            .file-name {{ font-size: 16px; }}
            pre[class*="language-"], pre:not([class*="language-"]), .editor-textarea {{ 
                padding: 15px;
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="file-info-section">
            <div class="file-name">📄 {file_path.split('/')[-1]}</div>
            <div class="file-info">Project: {project_name} • Path: {file_path}</div>
        </div>
        <div class="toolbar">
            <button id="editBtn" class="btn primary" onclick="toggleEditMode()">
                <span id="editIcon">✏️</span> <span id="editText">Edit</span>
            </button>
            <button id="saveBtn" class="btn success" onclick="saveFile()" style="display: none;" disabled>
                💾 Save
            </button>
            <button id="downloadBtn" class="btn" onclick="downloadFile()">
                📥 Download
            </button>
            <button class="close-btn" onclick="closeWindow()" title="Close">×</button>
        </div>
    </div>
    
    <div class="content">
        <div class="editor-container">
            <!-- View Mode -->
            <div id="viewContent">
                {file_content}
            </div>
            
            <!-- Edit Mode -->
            <textarea id="editContent" class="editor-textarea" style="display: none;">{html.escape(content) if not is_binary else ""}</textarea>
            
            <!-- Loading Overlay -->
            <div id="loadingOverlay" class="loading-overlay">
                <div class="spinner"></div>
            </div>
        </div>
    </div>
    
    <!-- Status Message -->
    <div id="statusMessage" class="status-message"></div>
    
    <!-- Prism.js JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
    <script>
        // Configure Prism.js autoloader
        Prism.plugins.autoloader.languages_path = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/';
        
        // Application state - Using pre-generated JSON to avoid template conflicts
        var isEditMode = false;
        var isLoading = false;
        var originalContent = {original_content_json};
        var hasUnsavedChanges = false;
        var projectName = {project_name_json};
        var filePath = {file_path_json};
        
        // Check if this is an image file
        var isImageFile = {json.dumps(is_image)};
        
        // Initialize syntax highlighting and setup
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('=== FILE VIEWER INITIALIZATION ===');
            console.log('File viewer loading...', 'isImageFile:', isImageFile);
            
            // Add network debugging
            if (window.fetch) {{
                const originalFetch = window.fetch;
                window.fetch = function(...args) {{
                    console.log('=== FETCH REQUEST ===');
                    console.log('Fetch args:', args);
                    console.log('Request URL:', args[0]);
                    console.log('Request options:', args[1]);
                    
                    return originalFetch.apply(this, args)
                        .then(response => {{
                            console.log('=== FETCH RESPONSE ===');
                            console.log('Response URL:', response.url);
                            console.log('Response status:', response.status);
                            console.log('Response statusText:', response.statusText);
                            console.log('Response headers:');
                            for (let [key, value] of response.headers) {{
                                console.log('  ' + key + ':', value);
                            }}
                            return response;
                        }})
                        .catch(error => {{
                            console.error('=== FETCH ERROR ===');
                            console.error('Fetch error:', error);
                            console.error('Error for URL:', args[0]);
                            throw error;
                        }});
                }};
                console.log('Fetch interceptor installed');
            }}
            
            console.log('File viewer loading...', 'isImageFile:', isImageFile);
            
            if (!isImageFile) {{
                try {{
                    Prism.highlightAll();
                    console.log('Prism syntax highlighting applied');
                }} catch(e) {{
                    console.log('Prism highlighting failed:', e);
                }}
                
                // Set up change detection for text files only
                var editTextarea = document.getElementById('editContent');
                if (editTextarea) {{
                    editTextarea.addEventListener('input', function() {{
                        hasUnsavedChanges = editTextarea.value !== originalContent;
                        updateSaveButton();
                    }});
                    console.log('Change detection set up');
                }}
            }} else {{
                console.log('Image file detected - disabling edit functionality');
                // Hide edit controls for images
                var editBtn = document.getElementById('editBtn');
                var saveBtn = document.getElementById('saveBtn'); 
                var cancelBtn = document.getElementById('cancelBtn');
                if (editBtn) editBtn.style.display = 'none';
                if (saveBtn) saveBtn.style.display = 'none';
                if (cancelBtn) cancelBtn.style.display = 'none';
                
                // Log image URL for debugging (now using data URL)
                var mainImage = document.getElementById('main-image');
                if (mainImage) {{
                    console.log('Image source type:', mainImage.src.startsWith('data:') ? 'Data URL' : 'Regular URL');
                    if (mainImage.src.startsWith('data:')) {{
                        console.log('Data URL length:', mainImage.src.length, 'characters');
                    }}
                }}
            }}
            
            // Prevent accidental page close with unsaved changes
            window.addEventListener('beforeunload', function(e) {{
                if (hasUnsavedChanges) {{
                    e.preventDefault();
                    e.returnValue = '';
                    return '';
                }}
            }});
            
            console.log('File viewer initialized successfully');
        }});
        
        function toggleEditMode() {{
            console.log('toggleEditMode called, isLoading:', isLoading);
            
            if (isLoading) {{
                console.log('Cannot toggle edit mode while loading');
                return;
            }}
            
            var viewContent = document.getElementById('viewContent');
            var editContent = document.getElementById('editContent');
            var editBtn = document.getElementById('editBtn');
            var saveBtn = document.getElementById('saveBtn');
            var editIcon = document.getElementById('editIcon');
            var editText = document.getElementById('editText');
            
            if (!viewContent || !editContent || !editBtn || !saveBtn || !editIcon || !editText) {{
                console.error('Required elements not found for edit mode toggle');
                showStatusMessage('Error: Required elements not found', 'error');
                return;
            }}
            
            try {{
                if (!isEditMode) {{
                    // Switch to edit mode
                    console.log('Switching to edit mode');
                    viewContent.style.display = 'none';
                    editContent.style.display = 'block';
                    editContent.value = originalContent;
                    editBtn.classList.remove('primary');
                    editBtn.classList.add('danger');
                    editIcon.textContent = '👁️';
                    editText.textContent = 'View';
                    saveBtn.style.display = 'inline-flex';
                    isEditMode = true;
                    hasUnsavedChanges = false;
                    updateSaveButton();
                    editContent.focus();
                    console.log('Successfully switched to edit mode');
                }} else {{
                    // Switch to view mode
                    console.log('Switching to view mode');
                    if (hasUnsavedChanges) {{
                        if (!confirm('You have unsaved changes. Are you sure you want to discard them?')) {{
                            return;
                        }}
                    }}
                    viewContent.style.display = 'block';
                    editContent.style.display = 'none';
                    editBtn.classList.remove('danger');
                    editBtn.classList.add('primary');
                    editIcon.textContent = '✏️';
                    editText.textContent = 'Edit';
                    saveBtn.style.display = 'none';
                    isEditMode = false;
                    hasUnsavedChanges = false;
                    console.log('Successfully switched to view mode');
                }}
            }} catch(error) {{
                console.error('Error toggling edit mode:', error);
                showStatusMessage('Error toggling edit mode: ' + error.message, 'error');
            }}
        }}
        
        function updateSaveButton() {{
            var saveBtn = document.getElementById('saveBtn');
            if (saveBtn) {{
                saveBtn.disabled = !hasUnsavedChanges || isLoading;
                console.log('Save button updated: disabled =', saveBtn.disabled);
            }}
        }}
        
        function saveFile() {{
            console.log('saveFile called, isLoading:', isLoading, 'hasUnsavedChanges:', hasUnsavedChanges);
            
            if (isLoading || !hasUnsavedChanges) {{
                console.log('Cannot save: loading=' + isLoading + ', hasUnsavedChanges=' + hasUnsavedChanges);
                return;
            }}
            
            var editContent = document.getElementById('editContent');
            var loadingOverlay = document.getElementById('loadingOverlay');
            
            if (!editContent) {{
                console.error('Edit content element not found');
                showStatusMessage('Error: Edit content not found', 'error');
                return;
            }}
            
            var content = editContent.value;
            console.log('Saving file with content length:', content.length);
            
            isLoading = true;
            if (loadingOverlay) loadingOverlay.style.display = 'flex';
            updateSaveButton();
            
            var saveUrl = '/project/' + encodeURIComponent(projectName) + '/file/' + encodeURIComponent(filePath) + '/save';
            console.log('Save URL:', saveUrl);
            
            fetch(saveUrl, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ content: content }})
            }})
            .then(function(response) {{
                console.log('Save response status:', response.status);
                if (!response.ok) {{
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }}
                return response.text().then(text => {{
                    try {{
                        return JSON.parse(text);
                    }} catch (e) {{
                        console.error('Invalid JSON response:', text);
                        throw new Error('Server returned invalid JSON: ' + text.substring(0, 100));
                    }}
                }});
            }})
            .then(function(result) {{
                console.log('Save result:', result);
                if (result.success) {{
                    originalContent = content;
                    hasUnsavedChanges = false;
                    showStatusMessage('File saved successfully!', 'success');
                    updateSaveButton();
                    console.log('File saved successfully');
                }} else {{
                    showStatusMessage('Error saving file: ' + result.error, 'error');
                    console.error('Save failed:', result.error);
                }}
            }})
            .catch(function(error) {{
                showStatusMessage('Error saving file: ' + error.message, 'error');
                console.error('Save error:', error);
            }})
            .finally(function() {{
                isLoading = false;
                if (loadingOverlay) loadingOverlay.style.display = 'none';
                updateSaveButton();
            }});
        }}
        
        function showStatusMessage(message, type) {{
            console.log('showStatusMessage:', message, type);
            
            var statusMessage = document.getElementById('statusMessage');
            if (!statusMessage) {{
                console.error('Status message element not found');
                return;
            }}
            
            type = type || 'success';
            statusMessage.textContent = message;
            statusMessage.className = 'status-message ' + type;
            statusMessage.style.display = 'block';
            
            setTimeout(function() {{
                statusMessage.style.display = 'none';
            }}, 3000);
        }}
        
        function closeWindow() {{
            console.log('closeWindow called');
            
            if (hasUnsavedChanges) {{
                if (!confirm('You have unsaved changes. Are you sure you want to close?')) {{
                    console.log('Close cancelled due to unsaved changes');
                    return;
                }}
            }}
            
            // Multiple strategies to close/navigate away
            var closed = false;
            
            try {{
                // Strategy 1: Try window.close() - works if opened by script or popup
                console.log('Attempting window.close()');
                window.close();
                
                // Check if window actually closed (won't execute if it did)
                setTimeout(function() {{
                    if (!closed) {{
                        console.log('window.close() did not work, trying fallback');
                        closeWindowFallback();
                    }}
                }}, 100);
                
            }} catch(error) {{
                console.log('window.close() failed:', error);
                closeWindowFallback();
            }}
        }}
        
        function closeWindowFallback() {{
            console.log('Using close window fallback strategies');
            
            // Strategy 2: Go back in history if available
            if (window.history && window.history.length > 1) {{
                console.log('Going back in history');
                try {{
                    window.history.back();
                    return;
                }} catch(error) {{
                    console.log('History back failed:', error);
                }}
            }}
            
            // Strategy 3: Use document.referrer if available
            if (document.referrer && document.referrer !== window.location.href) {{
                console.log('Navigating to referrer:', document.referrer);
                try {{
                    window.location.href = document.referrer;
                    return;
                }} catch(error) {{
                    console.log('Referrer navigation failed:', error);
                }}
            }}
            
            // Strategy 4: Navigate to parent directory or root
            try {{
                var currentUrl = window.location.href;
                var pathParts = currentUrl.split('/');
                if (pathParts.length > 3) {{
                    // Go to parent path (remove file part)
                    pathParts.pop(); // remove file
                    pathParts.pop(); // remove 'file'
                    var parentUrl = pathParts.join('/');
                    console.log('Navigating to parent:', parentUrl);
                    window.location.href = parentUrl;
                    return;
                }}
            }} catch(error) {{
                console.log('Parent navigation failed:', error);
            }}
            
            // Strategy 5: Go to root
            try {{
                console.log('Navigating to root');
                window.location.href = '/';
                return;
            }} catch(error) {{
                console.log('Root navigation failed:', error);
            }}
            
            // Final fallback: Show message
            showStatusMessage('Cannot close window automatically. Please close the tab manually.', 'error');
        }}
        
        function downloadFile() {{
            console.log('=== MAIN DOWNLOAD DEBUG START ===');
            console.log('downloadFile called');
            console.log('isImageFile:', isImageFile);
            console.log('isEditMode:', isEditMode);
            console.log('Browser:', navigator.userAgent);
            console.log('Window location:', window.location.href);
            
            try {{
                // For text files in edit mode, download the current edited content
                if (!isImageFile && isEditMode) {{
                    console.log('Using blob download for edited text content');
                    var content = document.getElementById('editContent').value;
                    var fileName = filePath.split('/').pop();
                    console.log('Blob download - fileName:', fileName, 'content length:', content.length);
                    
                    var blob = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    
                    var link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = fileName;
                    document.body.appendChild(link);
                    
                    console.log('Blob link href:', link.href);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(link.href);
                    
                    showStatusMessage('File downloaded successfully!', 'success');
                    console.log('Blob download completed successfully');
                }} else {{
                    console.log('Using server API download for:', isImageFile ? 'image file' : 'text file in view mode');
                    // For all other cases (view mode, images, binary files), use server endpoint
                    downloadViaAPI();
                }}
            }} catch(error) {{
                console.error('Main download error:', error);
                console.error('Error stack:', error.stack);
                showStatusMessage('Error downloading file: ' + error.message, 'error');
            }}
            console.log('=== MAIN DOWNLOAD DEBUG END ===');
        }}
        
        function downloadViaAPI() {{
            console.log('=== DOWNLOAD DEBUG START ===');
            console.log('downloadViaAPI called');
            console.log('Current URL:', window.location.href);
            console.log('Current protocol:', window.location.protocol);
            console.log('Current host:', window.location.host);
            console.log('Current pathname:', window.location.pathname);
            console.log('Project name (raw):', projectName);
            console.log('File path (raw):', filePath);
            console.log('Project name type:', typeof projectName);
            console.log('File path type:', typeof filePath);
            
            // Use the dedicated download endpoint - properly encode the file path
            // Use the same apiBase logic as the main app to handle proxy paths
            var apiBase = '';
            const currentPath = window.location.pathname;
            if (currentPath.includes('/proxy/')) {{
                const proxyMatch = currentPath.match(/\/proxy\/\d+/);
                apiBase = proxyMatch ? proxyMatch[0] : '';
            }}
            
            var downloadUrl = apiBase + '/project/' + encodeURIComponent(projectName) + '/file/' + filePath + '/download';
            console.log('Download URL (relative):', downloadUrl);
            
            // Try absolute URL construction for external access
            var absoluteUrl = window.location.protocol + '//' + window.location.host + downloadUrl;
            console.log('Download URL (absolute):', absoluteUrl);
            
            // Create a temporary link to trigger download
            var link = document.createElement('a');
            link.href = downloadUrl; // Keep using relative for now
            link.download = filePath.split('/').pop();
            link.style.display = 'none';
            
            console.log('Link href before click:', link.href);
            console.log('Link download attribute:', link.download);
            
            document.body.appendChild(link);
            
            // Add error handling for the click
            link.addEventListener('error', function(e) {{
                console.error('Link click error:', e);
                showStatusMessage('Download link error: ' + e.message, 'error');
            }});
            
            try {{
                console.log('Attempting link click...');
                link.click();
                console.log('Link click completed');
            }} catch(error) {{
                console.error('Link click exception:', error);
                showStatusMessage('Download click error: ' + error.message, 'error');
            }}
            
            document.body.removeChild(link);
            
            // Test if we can fetch the URL directly
            console.log('Testing direct fetch to download URL...');
            fetch(downloadUrl, {{ method: 'HEAD' }})
                .then(response => {{
                    console.log('HEAD request status:', response.status);
                    console.log('HEAD request statusText:', response.statusText);
                    console.log('HEAD response headers:');
                    for (let [key, value] of response.headers) {{
                        console.log('  ' + key + ':', value);
                    }}
                    if (!response.ok) {{
                        console.error('HEAD request failed:', response.status, response.statusText);
                    }}
                }})
                .catch(error => {{
                    console.error('HEAD request error:', error);
                    showStatusMessage('Download URL test failed: ' + error.message, 'error');
                }});
            
            showStatusMessage('Download started...', 'success');
            console.log('=== DOWNLOAD DEBUG END ===');
        }}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            try {{
                // Ctrl+S or Cmd+S to save
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {{
                    e.preventDefault();
                    if (isEditMode && hasUnsavedChanges) {{
                        console.log('Keyboard shortcut: Save');
                        saveFile();
                    }}
                }}
                
                // Escape to toggle edit mode
                if (e.key === 'Escape') {{
                    console.log('Keyboard shortcut: Toggle edit mode');
                    toggleEditMode();
                }}
                
                // Ctrl+W or Cmd+W to close (with confirmation)
                if ((e.ctrlKey || e.metaKey) && e.key === 'w') {{
                    if (hasUnsavedChanges) {{
                        e.preventDefault();
                        closeWindow();
                    }}
                }}
            }} catch(error) {{
                console.error('Keyboard shortcut error:', error);
            }}
        }});
        
        // Add error handling for uncaught errors
        window.addEventListener('error', function(e) {{
            console.error('Uncaught error:', e.error);
            showStatusMessage('An error occurred: ' + e.message, 'error');
        }});
        
        console.log('File viewer script loaded successfully');
    </script>
</body>
</html>
"""
        
        # Return HTML response with explicit content type
        response = Response(html_content, mimetype='text/html')
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        # Prevent caching to avoid MIME type confusion
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        logger.error(f"Error serving file viewer for {project_name}/{file_path}: {e}")
        return f"""
<!DOCTYPE html>
<html>
<head><title>Error</title></head>
<body style="font-family: monospace; padding: 20px;">
    <h2>Error Loading File</h2>
    <p>Project: {project_name}</p>
    <p>File: {file_path}</p>
    <p>Error: {str(e)}</p>
</body>
</html>
""", 500

@app.route('/image/<project_name>/<path:file_path>', methods=['GET'])
def serve_image_file(project_name, file_path):
    """Serve raw image files directly."""
    try:
        project_dir = claude_wrapper.base_projects_dir / project_name
        if not project_dir.exists():
            return jsonify({"success": False, "error": "Project not found"}), 404
            
        full_file_path = project_dir / file_path
        
        # Security: prevent path traversal
        try:
            full_file_path.resolve().relative_to(project_dir.resolve())
        except ValueError:
            return jsonify({"success": False, "error": "Access denied"}), 403
        
        if not full_file_path.exists():
            return jsonify({"success": False, "error": "File not found"}), 404
            
        # Check if it's actually an image file
        file_extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
        if not is_image_file(file_extension):
            return jsonify({"success": False, "error": "Not an image file"}), 400
        
        return send_from_directory(str(project_dir), file_path)
        
    except Exception as e:
        logger.error(f"Error serving image {project_name}/{file_path}: {e}")
        return jsonify({"success": False, "error": "Failed to serve image"}), 500

@app.route('/')
def serve_web_app():
    """Serve the main web application."""
    try:
        response = send_from_directory('../web', 'index.html')
        
        # Enhanced headers for mobile compatibility
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Mobile-specific headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-UA-Compatible'] = 'IE=edge'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Force mobile browsers to use proper viewport
        response.headers['Viewport'] = 'width=device-width, initial-scale=1.0'
        
        # Prevent mobile browsers from transforming content
        response.headers['Cache-Control'] += ', no-transform'
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving main application: {e}")
        return jsonify({"success": False, "error": "Application not found"}), 404

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files (CSS, JS, etc.) from the web directory."""
    try:
        response = send_from_directory('../web', filename)
        
        # Enhanced MIME types and headers for mobile compatibility
        if filename.endswith('.css'):
            response.headers['Content-Type'] = 'text/css; charset=utf-8'
            response.headers['Cache-Control'] = 'public, max-age=3600'
            # Force no transform for mobile browsers
            response.headers['Cache-Control'] += ', no-transform'
            # Ensure mobile browsers don't compress CSS
            response.headers['Vary'] = 'Accept-Encoding'
        elif filename.endswith('.js'):
            response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            response.headers['Cache-Control'] = 'public, max-age=3600'
            response.headers['Vary'] = 'Accept-Encoding'
        elif filename.endswith('.html'):
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        # Add mobile-specific headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-UA-Compatible'] = 'IE=edge'
        
        # Force browsers to respect MIME types
        if filename.endswith(('.css', '.js')):
            response.headers['Content-Disposition'] = 'inline'
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({"success": False, "error": "File not found"}), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('../data/projects', exist_ok=True)
    
    # Run Flask app
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Claude Web API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)