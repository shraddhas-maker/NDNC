// NDNC Automation Web UI - JavaScript
const socket = io();

let isRunning = false;

// Connect to WebSocket
socket.on('connect', () => {
    console.log('✅ Connected to server');
    updateConnectionStatus(true);
    refreshStatus();
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from server');
    updateConnectionStatus(false);
});

socket.on('connected', (data) => {
    console.log('Server message:', data.message);
    addConsoleMessage('System', data.message);
});

// Listen for log messages
socket.on('log', (data) => {
    addConsoleMessage('Log', data.message);
});

// Listen for status updates
socket.on('status', (data) => {
    isRunning = data.running;
    updateWorkflowStatus(data);
    addConsoleMessage('Status', data.message);
});

// Listen for file counts
socket.on('file_counts', (data) => {
    document.getElementById('reviewPendingCount').textContent = data.review_pending;
    document.getElementById('openCount').textContent = data.open;
});

// Listen for errors
socket.on('error', (data) => {
    addConsoleMessage('Error', `❌ ${data.message}`, 'error');
});

// Update connection status badge
function updateConnectionStatus(connected) {
    const badge = document.getElementById('connectionStatus');
    const dot = badge.querySelector('.status-dot');
    const text = badge.querySelector('.status-text');
    
    if (connected) {
        badge.classList.remove('disconnected');
        text.textContent = 'Connected';
    } else {
        badge.classList.add('disconnected');
        text.textContent = 'Disconnected';
    }
}

// Update workflow status
function updateWorkflowStatus(data) {
    const statusDiv = document.getElementById('workflowStatus');
    const indicator = statusDiv.querySelector('.status-indicator');
    const text = statusDiv.querySelector('span:last-child');
    
    if (data.running) {
        indicator.classList.remove('idle');
        indicator.classList.add('running');
        text.textContent = `Running: ${data.workflow}`;
        disableButtons(true);
    } else {
        indicator.classList.remove('running');
        indicator.classList.add('idle');
        text.textContent = 'Ready';
        disableButtons(false);
    }
}

// Disable/enable buttons
function disableButtons(disable) {
    const buttons = document.querySelectorAll('.control-buttons .btn');
    buttons.forEach(btn => {
        btn.disabled = disable;
    });
}

// Add message to console
function addConsoleMessage(type, message, level = 'info') {
    const console = document.getElementById('consoleOutput');
    const line = document.createElement('div');
    line.className = 'console-line';
    
    const timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    timestamp.textContent = `[${new Date().toLocaleTimeString()}]`;
    
    const msg = document.createElement('span');
    msg.className = 'message';
    msg.textContent = message;
    
    if (level === 'error') {
        msg.style.color = '#EF4444';
    } else if (level === 'success') {
        msg.style.color = '#10B981';
    } else if (level === 'warning') {
        msg.style.color = '#F59E0B';
    }
    
    line.appendChild(timestamp);
    line.appendChild(msg);
    console.appendChild(line);
    
    // Auto-scroll to bottom
    console.scrollTop = console.scrollHeight;
}

// Clear console
function clearConsole() {
    const console = document.getElementById('consoleOutput');
    console.innerHTML = '';
    addConsoleMessage('System', '🧹 Console cleared');
}

// Start workflow
async function startWorkflow(workflowType) {
    if (isRunning) {
        addConsoleMessage('Warning', '⚠️  Workflow already running', 'warning');
        return;
    }
    
    addConsoleMessage('System', `🚀 Starting ${workflowType} workflow...`, 'info');
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ workflow: workflowType })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start workflow');
        }
        
        const data = await response.json();
        addConsoleMessage('Success', `✅ ${data.message}`, 'success');
        
    } catch (error) {
        addConsoleMessage('Error', `❌ ${error.message}`, 'error');
    }
}

// Refresh status
async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update file counts
        document.getElementById('reviewPendingCount').textContent = data.file_counts.review_pending;
        document.getElementById('openCount').textContent = data.file_counts.open;
        document.getElementById('processedCount').textContent = data.stats.processed || 0;
        document.getElementById('failedCount').textContent = data.stats.failed || 0;
        
        // Update running status
        isRunning = data.running;
        if (data.running) {
            updateWorkflowStatus({
                running: true,
                workflow: data.workflow
            });
        }
        
    } catch (error) {
        console.error('Failed to refresh status:', error);
    }
}

// Auto-refresh status every 10 seconds
setInterval(refreshStatus, 10000);

// Initial load message
document.addEventListener('DOMContentLoaded', () => {
    addConsoleMessage('System', '🎯 Dashboard ready. Click a button to start automation.');
});

