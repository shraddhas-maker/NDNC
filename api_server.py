#!/usr/bin/env python3
"""
Simplified Flask API Server for NDNC Automation
This server provides REST API and WebSocket endpoints for the React frontend
"""
import os
import sys
import threading
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time

# Import the automation class
from complete_ndnc_automation import NDNCCompleteAutomation

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ndnc-automation-secret-key'

# Enable CORS for React frontend
CORS(app, origins=['*'])

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins='*')

# Global state
automation_state = {
    'running': False,
    'workflow': None,
    'automation': None,
    'stats': {
        'processed': 0,
        'failed': 0
    }
}

# Email configuration - Update this with your email
EMAIL = "shraddha.s@exotel.com"

# Folder paths
BASE_DIR = Path.home() / "Downloads" / "NDNC"
REVIEW_PENDING_DIR = BASE_DIR / "review_pending"
OPEN_DIR = BASE_DIR / "open"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_REVIEW_DIR = BASE_DIR / "processed_review"

# Custom logger class that emits to WebSocket
class SocketLogger:
    def __init__(self, original_stdout, socketio_instance):
        self.original_stdout = original_stdout
        self.socketio = socketio_instance
        
    def write(self, message):
        self.original_stdout.write(message)
        if message.strip():
            self.socketio.emit('log', {'message': message.strip()})
    
    def flush(self):
        self.original_stdout.flush()

# Redirect stdout to socket logger
original_stdout = sys.stdout
sys.stdout = SocketLogger(original_stdout, socketio)


def get_file_counts():
    """Get counts of files in each folder"""
    try:
        return {
            'review_pending': len(list(REVIEW_PENDING_DIR.glob('*.*'))) if REVIEW_PENDING_DIR.exists() else 0,
            'open': len(list(OPEN_DIR.glob('*.*'))) if OPEN_DIR.exists() else 0,
            'processed': len(list(PROCESSED_DIR.glob('*.*'))) if PROCESSED_DIR.exists() else 0,
            'processed_review': len(list(PROCESSED_REVIEW_DIR.glob('*.*'))) if PROCESSED_REVIEW_DIR.exists() else 0
        }
    except Exception as e:
        print(f"Error getting file counts: {e}")
        return {'review_pending': 0, 'open': 0, 'processed': 0, 'processed_review': 0}


def run_automation_workflow(workflow_type):
    """Run automation in a separate thread"""
    global automation_state
    
    try:
        # Update state
        automation_state['running'] = True
        automation_state['workflow'] = workflow_type
        
        socketio.emit('status', {
            'running': True,
            'workflow': workflow_type,
            'message': f'🚀 Starting {workflow_type} workflow...'
        })
        
        # Create automation instance
        automation = NDNCCompleteAutomation(email=EMAIL)
        automation_state['automation'] = automation
        
        # Start browser
        print("🌐 Starting browser...")
        automation.start_browser()
        
        # Login
        print("🔐 Logging in...")
        if not automation.login():
            print("✗ Login failed. Stopping automation.")
            socketio.emit('error', {'message': 'Login failed. Please check credentials.'})
            return
        
        print("✅ Login successful!")
        
        # Run appropriate workflow
        if workflow_type in ['review_pending', 'both']:
            review_files = list(REVIEW_PENDING_DIR.glob('*.*')) if REVIEW_PENDING_DIR.exists() else []
            
            if not review_files and workflow_type == 'review_pending':
                print("⚠️  No files in 'review_pending' folder. Skipping.")
                socketio.emit('log', {'message': "⚠️  No files in 'review_pending' folder."})
            elif not review_files and workflow_type == 'both':
                print("⚠️  No files in 'review_pending' folder. Downloading...")
                socketio.emit('log', {'message': "⚠️  No files in 'review_pending'. Downloading from dashboard..."})
                automation.run_review_pending_workflow()
            else:
                print(f"📋 Processing {len(review_files)} Review Pending files...")
                automation.run_review_pending_workflow()
        
        if workflow_type in ['open', 'both']:
            open_files = list(OPEN_DIR.glob('*.*')) if OPEN_DIR.exists() else []
            
            if not open_files:
                print("⚠️  No files in 'open' folder. Skipping.")
                socketio.emit('log', {'message': "⚠️  No files in 'open' folder."})
            else:
                print(f"📁 Processing {len(open_files)} Open files...")
                automation.run_open_workflow()
        
        # Success
        print("✅ Workflow completed successfully!")
        socketio.emit('status', {
            'running': False,
            'workflow': None,
            'message': '✅ Workflow completed successfully!'
        })
        
        # Update stats
        automation_state['stats']['processed'] += 1
        socketio.emit('file_counts', get_file_counts())
        
    except Exception as e:
        print(f"❌ Error during automation: {str(e)}")
        socketio.emit('error', {'message': f'Error: {str(e)}'})
        socketio.emit('status', {
            'running': False,
            'workflow': None,
            'message': f'❌ Workflow failed: {str(e)}'
        })
        automation_state['stats']['failed'] += 1
        
    finally:
        # Cleanup
        automation_state['running'] = False
        automation_state['workflow'] = None
        
        if automation_state['automation'] and automation_state['automation'].driver:
            try:
                automation_state['automation'].driver.quit()
            except:
                pass
        
        automation_state['automation'] = None


# REST API Endpoints

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current automation status and file counts"""
    return jsonify({
        'running': automation_state['running'],
        'workflow': automation_state['workflow'],
        'file_counts': get_file_counts(),
        'stats': automation_state['stats']
    })


@app.route('/api/start', methods=['POST'])
def start_workflow():
    """Start a workflow"""
    if automation_state['running']:
        return jsonify({'error': 'Workflow already running'}), 400
    
    data = request.get_json()
    workflow = data.get('workflow', 'both')
    
    if workflow not in ['both', 'review_pending', 'open']:
        return jsonify({'error': 'Invalid workflow type'}), 400
    
    # Start workflow in background thread
    thread = threading.Thread(target=run_automation_workflow, args=(workflow,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': f'Started {workflow} workflow'})


@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'NDNC Automation API',
        'version': '2.0.0'
    })


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('🔌 Client connected')
    emit('status', {
        'running': automation_state['running'],
        'workflow': automation_state['workflow'],
        'message': 'Connected to automation server'
    })
    emit('file_counts', get_file_counts())


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('🔌 Client disconnected')


@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    emit('status', {
        'running': automation_state['running'],
        'workflow': automation_state['workflow']
    })
    emit('file_counts', get_file_counts())


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NDNC Automation API Server")
    print("=" * 60)
    print(f"📧 Email: {EMAIL}")
    print(f"📂 Base Directory: {BASE_DIR}")
    print(f"🌐 Server: http://localhost:5000")
    print(f"🔌 WebSocket: ws://localhost:5000")
    print("=" * 60)
    print("✅ Server is ready! Connect your React frontend.")
    print("=" * 60)
    
    # Run the server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

