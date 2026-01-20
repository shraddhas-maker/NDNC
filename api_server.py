#!/usr/bin/env python3
"""
Railway-Ready Flask API Server for NDNC Automation
Serves React frontend and provides REST API + WebSocket endpoints
"""
import os
import sys
import threading
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time

# Import the automation class
from complete_ndnc_automation import NDNCCompleteAutomation

# Initialize Flask app with static folder pointing to React build
app = Flask(
    __name__,
    static_folder="frontend/dist",
    static_url_path=""
)
app.config['SECRET_KEY'] = 'ndnc-automation-secret-key'

# Enable CORS for React frontend
CORS(app, origins=['*'])

# Initialize SocketIO
# Use 'threading' mode for local development (Python 3.14 compatible)
# Railway will use 'eventlet' via gunicorn worker
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# Global state
automation_state = {
    'running': False,
    'paused': False,
    'stop_requested': False,
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


def check_pause_and_stop():
    """Check if workflow should pause or stop - returns 'stop', 'pause', or 'continue'"""
    global automation_state
    
    # Check for stop request
    if automation_state.get('stop_requested', False):
        return 'stop'
    
    # Check for pause request
    if automation_state.get('paused', False):
        return 'pause'
    
    return 'continue'


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
        
        # Inject pause/stop checker
        automation.check_pause_stop = check_pause_and_stop
        
        # Start browser
        print("🌐 Starting browser...")
        
        # Check for pause/stop before browser start
        while check_pause_and_stop() == 'pause':
            time.sleep(0.5)
        if check_pause_and_stop() == 'stop':
            return
            
        automation.start_browser()
        
        # Login
        print("🔐 Logging in...")
        
        # Check for pause/stop before login
        while check_pause_and_stop() == 'pause':
            time.sleep(0.5)
        if check_pause_and_stop() == 'stop':
            return
            
        if not automation.login():
            print("✗ Login failed. Stopping automation.")
            socketio.emit('error', {'message': 'Login failed. Please check credentials.'})
            return
        
        print("✅ Login successful!")
        
        # Run appropriate workflow and collect results
        total_stats = {'processed': 0, 'failed': 0}
        
        if workflow_type in ['review_pending', 'both']:
            # Check for pause/stop before review pending
            while check_pause_and_stop() == 'pause':
                time.sleep(0.5)
            if check_pause_and_stop() == 'stop':
                return
                
            review_files = list(REVIEW_PENDING_DIR.glob('*.*')) if REVIEW_PENDING_DIR.exists() else []
            
            if not review_files and workflow_type == 'review_pending':
                print("⚠️  No files in 'review_pending' folder. Skipping.")
                socketio.emit('log', {'message': "⚠️  No files in 'review_pending' folder."})
            elif not review_files and workflow_type == 'both':
                print("⚠️  No files in 'review_pending' folder. Downloading...")
                socketio.emit('log', {'message': "⚠️  No files in 'review_pending'. Downloading from dashboard..."})
                results = automation.run_review_pending_workflow()
                if results:
                    total_stats['processed'] += results.get('success', 0)
                    total_stats['failed'] += results.get('failed', 0)
            else:
                print(f"📋 Processing {len(review_files)} Review Pending files...")
                results = automation.run_review_pending_workflow()
                if results:
                    total_stats['processed'] += results.get('success', 0)
                    total_stats['failed'] += results.get('failed', 0)
        
        if workflow_type in ['open', 'both']:
            # Check for pause/stop before open workflow
            while check_pause_and_stop() == 'pause':
                time.sleep(0.5)
            if check_pause_and_stop() == 'stop':
                return
                
            open_files = list(OPEN_DIR.glob('*.*')) if OPEN_DIR.exists() else []
            
            if not open_files:
                print("⚠️  No files in 'open' folder. Skipping.")
                socketio.emit('log', {'message': "⚠️  No files in 'open' folder."})
            else:
                print(f"📁 Processing {len(open_files)} Open files...")
                results = automation.run_open_workflow()
                if results:
                    total_stats['processed'] += results.get('success', 0)
                    total_stats['failed'] += results.get('failed', 0)
        
        # Success (only if not stopped)
        if not automation_state.get('stop_requested', False):
            print("✅ Workflow completed successfully!")
            
            # Update stats with actual file results
            automation_state['stats']['processed'] += total_stats.get('processed', 0)
            automation_state['stats']['failed'] += total_stats.get('failed', 0)
            
            # Emit updated status
            socketio.emit('status', {
                'running': False,
                'paused': False,
                'workflow': None,
                'message': f"✅ Completed! Processed: {total_stats['processed']}, Failed: {total_stats['failed']}"
            })
            
            # Emit updated stats
            socketio.emit('stats', automation_state['stats'])
            socketio.emit('file_counts', get_file_counts())
        
    except Exception as e:
        print(f"❌ Error during automation: {str(e)}")
        socketio.emit('error', {'message': f'Error: {str(e)}'})
        socketio.emit('status', {
            'running': False,
            'workflow': None,
            'message': f'❌ Workflow failed: {str(e)}'
        })
        # Stats already updated from file processing results
        socketio.emit('stats', automation_state['stats'])
        
    finally:
        # Cleanup
        automation_state['running'] = False
        automation_state['paused'] = False
        automation_state['stop_requested'] = False
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
        'paused': automation_state['paused'],
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
    
    # Reset stop flag
    automation_state['stop_requested'] = False
    automation_state['paused'] = False
    
    # Start workflow in background thread
    thread = threading.Thread(target=run_automation_workflow, args=(workflow,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': f'Started {workflow} workflow'})


@app.route('/api/pause', methods=['POST'])
def pause_workflow():
    """Pause current workflow"""
    if not automation_state['running']:
        return jsonify({'error': 'No workflow running'}), 400
    
    automation_state['paused'] = True
    socketio.emit('status', {
        'running': True,
        'paused': True,
        'workflow': automation_state['workflow'],
        'message': '⏸️ Workflow paused'
    })
    print("⏸️ Workflow paused by user")
    return jsonify({'message': 'Workflow paused'})


@app.route('/api/resume', methods=['POST'])
def resume_workflow():
    """Resume paused workflow"""
    if not automation_state['running']:
        return jsonify({'error': 'No workflow running'}), 400
    
    if not automation_state['paused']:
        return jsonify({'error': 'Workflow not paused'}), 400
    
    automation_state['paused'] = False
    socketio.emit('status', {
        'running': True,
        'paused': False,
        'workflow': automation_state['workflow'],
        'message': '▶️ Workflow resumed'
    })
    print("▶️ Workflow resumed by user")
    return jsonify({'message': 'Workflow resumed'})


@app.route('/api/stop', methods=['POST'])
def stop_workflow():
    """Stop current workflow and optionally shutdown server"""
    data = request.get_json() or {}
    shutdown_server = data.get('shutdown', False)
    
    if not automation_state['running'] and not shutdown_server:
        return jsonify({'error': 'No workflow running'}), 400
    
    automation_state['stop_requested'] = True
    automation_state['paused'] = False
    socketio.emit('status', {
        'running': False,
        'paused': False,
        'workflow': None,
        'message': '⏹️ Workflow stopped by user'
    })
    print("⏹️ Workflow stop requested by user")
    
    # Cleanup
    automation_state['running'] = False
    automation_state['workflow'] = None
    
    if automation_state['automation'] and automation_state['automation'].driver:
        try:
            automation_state['automation'].driver.quit()
        except:
            pass
    
    automation_state['automation'] = None
    
    # Shutdown server if requested
    if shutdown_server:
        print("🛑 Server shutdown requested...")
        socketio.emit('status', {
            'running': False,
            'paused': False,
            'workflow': None,
            'message': '🛑 Server shutting down...'
        })
        
        def shutdown():
            time.sleep(1)
            print("👋 Server stopped")
            os._exit(0)
        
        threading.Thread(target=shutdown, daemon=True).start()
        return jsonify({'message': 'Server shutting down'})
    
    return jsonify({'message': 'Workflow stopped'})


@app.route('/')
def serve_react():
    """Serve React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
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
    # Get port from environment variable (Railway) or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    print("=" * 60)
    print("🚀 NDNC Automation API Server (Railway Ready)")
    print("=" * 60)
    print(f"📧 Email: {EMAIL}")
    print(f"📂 Base Directory: {BASE_DIR}")
    print(f"🌐 Server: http://0.0.0.0:{port}")
    print(f"🔌 WebSocket: ws://0.0.0.0:{port}")
    print("=" * 60)
    print("✅ Server is ready! Serving React frontend + API.")
    print("=" * 60)
    
    # Run the server
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)

