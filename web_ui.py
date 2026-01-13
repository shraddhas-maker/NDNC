"""
NDNC Automation Web UI
Beautiful web interface for running NDNC automation workflows
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Import the automation
from complete_ndnc_automation import NDNCCompleteAutomation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ndnc-automation-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
automation_status = {
    'running': False,
    'workflow': None,
    'progress': [],
    'stats': {
        'review_pending_files': 0,
        'open_files': 0,
        'processed': 0,
        'failed': 0,
        'skipped': 0
    }
}

class WebUILogger:
    """Custom logger that sends output to web UI"""
    def __init__(self):
        self.buffer = []
    
    def write(self, message):
        if message.strip():
            self.buffer.append(message)
            socketio.emit('log', {'message': message}, namespace='/')
    
    def flush(self):
        pass


def count_files_in_folders():
    """Count files in review_pending and open folders"""
    ndnc_folder = Path.home() / "Downloads" / "NDNC"
    review_pending = ndnc_folder / "review_pending"
    open_folder = ndnc_folder / "open"
    
    review_count = 0
    open_count = 0
    
    if review_pending.exists():
        review_count = len(list(review_pending.glob("*.pdf")) + 
                          list(review_pending.glob("*.png")) +
                          list(review_pending.glob("*.jpg")) +
                          list(review_pending.glob("*.jpeg")))
    
    if open_folder.exists():
        open_count = len(list(open_folder.glob("*.pdf")) + 
                         list(open_folder.glob("*.png")) +
                         list(open_folder.glob("*.jpg")) +
                         list(open_folder.glob("*.jpeg")))
    
    return review_count, open_count


def run_automation_thread(workflow_type):
    """Run automation in background thread"""
    global automation_status
    
    try:
        automation_status['running'] = True
        automation_status['workflow'] = workflow_type
        automation_status['progress'] = []
        
        socketio.emit('status', {
            'running': True,
            'workflow': workflow_type,
            'message': f'Starting {workflow_type} workflow...'
        }, namespace='/')
        
        # Check file counts
        review_count, open_count = count_files_in_folders()
        automation_status['stats']['review_pending_files'] = review_count
        automation_status['stats']['open_files'] = open_count
        
        socketio.emit('file_counts', {
            'review_pending': review_count,
            'open': open_count
        }, namespace='/')
        
        # Check if we should skip
        skip_workflow = False
        skip_message = ""
        
        if workflow_type == 'review_pending' and review_count == 0:
            skip_workflow = True
            skip_message = "No files in review_pending folder. Skipping workflow."
        elif workflow_type == 'open' and open_count == 0:
            skip_workflow = True
            skip_message = "No files in open folder. Skipping workflow."
        elif workflow_type == 'both':
            if review_count == 0 and open_count == 0:
                skip_workflow = True
                skip_message = "No files in review_pending or open folders. Skipping all workflows."
        
        if skip_workflow:
            socketio.emit('log', {'message': f"\n⚠️  {skip_message}\n"}, namespace='/')
            socketio.emit('status', {
                'running': False,
                'workflow': None,
                'message': skip_message
            }, namespace='/')
            automation_status['running'] = False
            automation_status['stats']['skipped'] = 1
            return
        
        # Run automation
        EMAIL = "shraddha.s@exotel.com"
        automation = NDNCCompleteAutomation(email=EMAIL)
        
        # Redirect stdout to capture logs
        old_stdout = sys.stdout
        sys.stdout = WebUILogger()
        
        try:
            automation.run(workflow_type=workflow_type)
        finally:
            sys.stdout = old_stdout
        
        socketio.emit('status', {
            'running': False,
            'workflow': None,
            'message': 'Workflow completed successfully!'
        }, namespace='/')
        
    except Exception as e:
        socketio.emit('error', {'message': str(e)}, namespace='/')
        socketio.emit('status', {
            'running': False,
            'workflow': None,
            'message': f'Error: {str(e)}'
        }, namespace='/')
    finally:
        automation_status['running'] = False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current status"""
    review_count, open_count = count_files_in_folders()
    return jsonify({
        'running': automation_status['running'],
        'workflow': automation_status['workflow'],
        'stats': automation_status['stats'],
        'file_counts': {
            'review_pending': review_count,
            'open': open_count
        }
    })


@app.route('/api/start', methods=['POST'])
def start_automation():
    """Start automation workflow"""
    if automation_status['running']:
        return jsonify({'error': 'Automation already running'}), 400
    
    data = request.json
    workflow_type = data.get('workflow', 'both')
    
    # Start in background thread
    thread = threading.Thread(target=run_automation_thread, args=(workflow_type,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Automation started', 'workflow': workflow_type})


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to NDNC Automation Server'})
    
    # Send current status
    review_count, open_count = count_files_in_folders()
    emit('file_counts', {
        'review_pending': review_count,
        'open': open_count
    })


if __name__ == '__main__':
    print("🚀 Starting NDNC Automation Web UI...")
    print("📡 Server running at: http://localhost:5000")
    print("🔥 Press Ctrl+C to stop\n")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

