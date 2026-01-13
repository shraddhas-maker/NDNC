import { useState, useEffect, useRef } from 'react'
import io from 'socket.io-client'
import './index.css'

// Configure API URL - Change this for deployment
const API_URL = import.meta.env.PROD 
  ? 'http://localhost:5000'  // For production build
  : 'http://localhost:5000'  // For development

function App() {
  const [connected, setConnected] = useState(false)
  const [running, setRunning] = useState(false)
  const [paused, setPaused] = useState(false)
  const [workflow, setWorkflow] = useState(null)
  const [stats, setStats] = useState({
    reviewPending: '-',
    open: '-',
    processed: 0,
    failed: 0
  })
  const [logs, setLogs] = useState([
    { time: new Date(), message: '🚀 NDNC Automation Dashboard loaded. Select a workflow to begin.' }
  ])
  
  const socketRef = useRef(null)
  const consoleRef = useRef(null)

  useEffect(() => {
    // Connect to WebSocket
    const socket = io(API_URL)
    socketRef.current = socket

    socket.on('connect', () => {
      console.log('✅ Connected to server')
      setConnected(true)
      addLog('System', '✅ Connected to NDNC Automation Server')
      refreshStatus()
    })

    socket.on('disconnect', () => {
      console.log('❌ Disconnected from server')
      setConnected(false)
      addLog('System', '❌ Disconnected from server')
    })

    socket.on('log', (data) => {
      addLog('Log', data.message)
    })

    socket.on('status', (data) => {
      setRunning(data.running)
      setPaused(data.paused || false)
      setWorkflow(data.workflow)
      if (data.message) {
        addLog('Status', data.message)
      }
    })

    socket.on('file_counts', (data) => {
      setStats(prev => ({
        ...prev,
        reviewPending: data.review_pending,
        open: data.open
      }))
    })

    socket.on('error', (data) => {
      addLog('Error', `❌ ${data.message}`)
    })

    // Refresh status every 10 seconds
    const interval = setInterval(refreshStatus, 10000)

    return () => {
      socket.disconnect()
      clearInterval(interval)
    }
  }, [])

  // Auto-scroll console
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight
    }
  }, [logs])

  const addLog = (type, message) => {
    setLogs(prev => [...prev, { time: new Date(), message, type }])
  }

  const refreshStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/status`)
      const data = await response.json()
      
      setStats(prev => ({
        ...prev,
        reviewPending: data.file_counts.review_pending,
        open: data.file_counts.open,
        processed: data.stats.processed || 0,
        failed: data.stats.failed || 0
      }))
      
      setRunning(data.running)
      setPaused(data.paused || false)
      setWorkflow(data.workflow)
    } catch (error) {
      console.error('Failed to refresh status:', error)
    }
  }

  const startWorkflow = async (workflowType) => {
    if (running) {
      addLog('Warning', '⚠️  Workflow already running')
      return
    }

    addLog('System', `🚀 Starting ${workflowType} workflow...`)

    try {
      const response = await fetch(`${API_URL}/api/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ workflow: workflowType })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to start workflow')
      }

      const data = await response.json()
      addLog('Success', `✅ ${data.message}`)
    } catch (error) {
      addLog('Error', `❌ ${error.message}`)
    }
  }

  const pauseWorkflow = async () => {
    try {
      const response = await fetch(`${API_URL}/api/pause`, {
        method: 'POST'
      })
      if (response.ok) {
        setPaused(true)
        addLog('System', '⏸️ Workflow paused')
      }
    } catch (error) {
      addLog('Error', `❌ Failed to pause: ${error.message}`)
    }
  }

  const resumeWorkflow = async () => {
    try {
      const response = await fetch(`${API_URL}/api/resume`, {
        method: 'POST'
      })
      if (response.ok) {
        setPaused(false)
        addLog('System', '▶️ Workflow resumed')
      }
    } catch (error) {
      addLog('Error', `❌ Failed to resume: ${error.message}`)
    }
  }

  const stopWorkflow = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stop`, {
        method: 'POST'
      })
      if (response.ok) {
        setRunning(false)
        setPaused(false)
        addLog('System', '⏹️ Workflow stopped')
      }
    } catch (error) {
      addLog('Error', `❌ Failed to stop: ${error.message}`)
    }
  }

  const clearConsole = () => {
    setLogs([{ time: new Date(), message: '🧹 Console cleared' }])
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour12: false })
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <h1>🚀 NDNC Automation</h1>
        </div>
        <div className={`status-badge ${!connected ? 'disconnected' : ''}`}>
          <span className="status-dot"></span>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      {/* Statistics */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon review-pending">
            <span>📋</span>
          </div>
          <div className="stat-info">
            <h3>Review Pending</h3>
            <p className="stat-number">{stats.reviewPending}</p>
            <span className="stat-label">files ready</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon open">
            <span>📁</span>
          </div>
          <div className="stat-info">
            <h3>Open Complaints</h3>
            <p className="stat-number">{stats.open}</p>
            <span className="stat-label">files ready</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon processed">
            <span>✅</span>
          </div>
          <div className="stat-info">
            <h3>Processed</h3>
            <p className="stat-number">{stats.processed}</p>
            <span className="stat-label">files completed</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon failed">
            <span>❌</span>
          </div>
          <div className="stat-info">
            <h3>Failed</h3>
            <p className="stat-number">{stats.failed}</p>
            <span className="stat-label">files failed</span>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="control-panel">
        <div className="control-header">
          <h2>Workflow Control</h2>
          <div className="workflow-status">
            <span className={`status-indicator ${running ? 'running' : ''}`}></span>
            <span>{running ? (paused ? `Paused: ${workflow}` : `Running: ${workflow}`) : 'Ready'}</span>
          </div>
        </div>

        <div className="control-buttons">
          <button 
            className="btn btn-primary" 
            onClick={() => startWorkflow('both')}
            disabled={running}
          >
            <span>▶️ Run Both Workflows</span>
            <span className="btn-subtitle">Review Pending + Open</span>
          </button>

          <button 
            className="btn btn-secondary" 
            onClick={() => startWorkflow('review_pending')}
            disabled={running}
          >
            <span>📋 Review Pending Only</span>
          </button>

          <button 
            className="btn btn-secondary" 
            onClick={() => startWorkflow('open')}
            disabled={running}
          >
            <span>📁 Open Complaints Only</span>
          </button>

          {/* Control buttons when workflow is running */}
          {running && (
            <div style={{ display: 'flex', gap: '15px', marginTop: '20px' }}>
              {!paused ? (
                <button 
                  className="btn btn-secondary" 
                  onClick={pauseWorkflow}
                  style={{ backgroundColor: '#F59E0B', borderColor: '#F59E0B' }}
                >
                  <span>⏸️ Pause</span>
                </button>
              ) : (
                <button 
                  className="btn btn-secondary" 
                  onClick={resumeWorkflow}
                  style={{ backgroundColor: '#10B981', borderColor: '#10B981' }}
                >
                  <span>▶️ Resume</span>
                </button>
              )}
              <button 
                className="btn btn-secondary" 
                onClick={stopWorkflow}
                style={{ backgroundColor: '#EF4444', borderColor: '#EF4444' }}
              >
                <span>⏹️ Stop</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Console */}
      <div className="console-panel">
        <div className="console-header">
          <h3>
            <span>💻</span>
            Live Console Output
          </h3>
          <button className="btn btn-secondary" onClick={clearConsole} style={{padding: '8px 16px', fontSize: '14px'}}>
            🔄 Clear
          </button>
        </div>
        <div className="console-output" ref={consoleRef}>
          {logs.map((log, index) => (
            <div key={index} className="console-line">
              <span className="timestamp">[{formatTime(log.time)}]</span>
              <span className="message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>© 2026 NDNC Automation | Powered by Exotel</p>
      </footer>
    </div>
  )
}

export default App

