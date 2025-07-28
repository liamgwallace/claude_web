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
from claude_wrapper import ClaudeWrapper
import asyncio
from threading import Thread
import queue
import time

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
CORS(app)  # Enable CORS for all routes

# Configure proxy support for VS Code port forwarding
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize Claude wrapper
claude_wrapper = ClaudeWrapper()

# Add request logging middleware
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    logger.info(f"Headers: {dict(request.headers)}")

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

@app.route('/<project_name>/file/<path:file_path>')
def serve_file_viewer(project_name, file_path):
    """Serve the file viewer for a specific project file."""
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
        
        if is_binary:
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
        
        # Return lightweight HTML with Prism.js syntax highlighting
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{file_path.split('/')[-1]} - {project_name}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet" />
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
            line-height: 1.6;
        }}
        .header {{
            background: white;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
        .content {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            max-height: calc(100vh - 120px);
            overflow: auto;
        }}
        /* Custom Prism.js styling */
        pre[class*="language-"] {{
            margin: 0;
            padding: 0;
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
    </style>
</head>
<body>
    <div class="header">
        <div class="file-name">📄 {file_path.split('/')[-1]}</div>
        <div class="file-info">Project: {project_name} • Path: {file_path}</div>
    </div>
    
    <div class="content">
        {file_content}
    </div>
    
    <!-- Prism.js JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
    <script>
        // Configure Prism.js autoloader
        Prism.plugins.autoloader.languages_path = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/';
        
        // Initialize syntax highlighting
        document.addEventListener('DOMContentLoaded', function() {{
            Prism.highlightAll();
        }});
    </script>
</body>
</html>
"""
        
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

@app.route('/')
def serve_web_app():
    """Serve the main web application."""
    return send_from_directory('.', 'web_app.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data/projects', exist_ok=True)
    
    # Run Flask app
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Claude Web API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)