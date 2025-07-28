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