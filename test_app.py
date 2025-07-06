#!/usr/bin/env python3
"""
FastAPI Test Runner Web Interface
A simple web application that runs pytest tests with configurable timing.
"""

import asyncio
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(
    title="PyTest Runner",
    description="Web interface for running pytest with live updates"
)

# Global state
current_test_state = {
    "running": False,
    "wait_time": 30,
    "timeout": 20,
    "last_run": None,
    "last_results": None,
    "progress": 0,
    "next_run_in": 0
}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Remove dead connections
                self.active_connections.remove(connection)


manager = ConnectionManager()


async def run_pytest(timeout: int = 20) -> Dict[str, Any]:
    """Run pytest and return results"""
    try:
        cmd = [
            "python", "-m", "pytest", f"--timeout={timeout}",
            "-v", "--tb=short", "--json-report",
            "--json-report-file=/tmp/pytest_report.json"
        ]
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/app"
        )
        end_time = time.time()
        
        # Try to read JSON report if available
        json_report = None
        try:
            with open("/tmp/pytest_report.json", "r") as f:
                json_report = json.load(f)
        except Exception:
            pass
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": round(end_time - start_time, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "json_report": json_report
        }
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "json_report": None
        }


async def test_runner_loop():
    """Main test runner loop"""
    while current_test_state["running"]:
        # Run tests
        await manager.broadcast({
            "type": "test_start",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        results = await run_pytest(current_test_state["timeout"])
        current_test_state["last_run"] = results["timestamp"]
        current_test_state["last_results"] = results
        
        await manager.broadcast({
            "type": "test_complete",
            "results": results
        })
        
        # Wait with progress updates
        wait_time = current_test_state["wait_time"]
        for i in range(wait_time):
            if not current_test_state["running"]:
                break
                
            progress = ((i + 1) * 100) // wait_time
            remaining = wait_time - i - 1
            current_test_state["progress"] = progress
            current_test_state["next_run_in"] = remaining
            
            await manager.broadcast({
                "type": "progress",
                "progress": progress,
                "remaining": remaining
            })
            
            await asyncio.sleep(1)


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Main dashboard page"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyTest Runner Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2d3748, #4a5568); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.8; font-size: 1.1em; }
        .controls { 
            padding: 30px; 
            background: #f8f9fa; 
            border-bottom: 1px solid #e9ecef; 
        }
        .control-group { 
            display: flex; 
            gap: 20px; 
            align-items: center; 
            margin-bottom: 20px; 
            flex-wrap: wrap;
        }
        .control-group label { 
            font-weight: 600; 
            color: #495057;
            min-width: 120px;
        }
        .control-group input { 
            padding: 10px 15px; 
            border: 2px solid #dee2e6; 
            border-radius: 8px; 
            font-size: 16px;
            width: 100px;
        }
        .control-group input:focus { 
            outline: none; 
            border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn { 
            padding: 12px 25px; 
            border: none; 
            border-radius: 8px; 
            font-size: 16px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.2s;
            margin-right: 10px;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
        }
        .btn-primary:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-danger { 
            background: linear-gradient(135deg, #ff6b6b, #ee5a52); 
            color: white; 
        }
        .btn-danger:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
        .status { 
            padding: 30px; 
        }
        .status-card { 
            background: #f8f9fa; 
            border-radius: 12px; 
            padding: 25px; 
            margin-bottom: 20px; 
            border-left: 5px solid #667eea;
        }
        .status-running { border-left-color: #28a745; }
        .status-stopped { border-left-color: #dc3545; }
        .status-waiting { border-left-color: #ffc107; }
        .progress-container { 
            background: #e9ecef; 
            border-radius: 10px; 
            height: 20px; 
            margin: 15px 0; 
            overflow: hidden;
        }
        .progress-bar { 
            height: 100%; 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            transition: width 0.3s ease; 
            border-radius: 10px;
        }
        .results { 
            padding: 30px; 
            background: #f8f9fa; 
        }
        .results pre { 
            background: #2d3748; 
            color: #e2e8f0; 
            padding: 20px; 
            border-radius: 8px; 
            overflow-x: auto; 
            font-family: 'Monaco', 'Menlo', monospace; 
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .timestamp { 
            color: #6c757d; 
            font-size: 0.9em; 
            margin-top: 10px; 
        }
        .success { color: #28a745; font-weight: 600; }
        .error { color: #dc3545; font-weight: 600; }
        .info { color: #17a2b8; font-weight: 600; }
        @media (max-width: 768px) {
            .control-group { flex-direction: column; align-items: flex-start; }
            .control-group label { min-width: auto; }
            .control-group input { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 PyTest Runner</h1>
            <p>Continuous testing with live updates and beautiful progress tracking</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="waitTime">Wait Time (seconds):</label>
                <input type="number" id="waitTime" value="30" min="1" max="3600">
                
                <label for="timeout">Test Timeout (seconds):</label>
                <input type="number" id="timeout" value="20" min="1" max="300">
            </div>
            
            <div class="control-group">
                <button class="btn btn-primary" onclick="startTests()">▶️ Start Continuous Testing</button>
                <button class="btn btn-danger" onclick="stopTests()">⏹️ Stop Testing</button>
                <button class="btn btn-primary" onclick="runOnce()">🔄 Run Once</button>
            </div>
        </div>
        
        <div class="status">
            <div class="status-card" id="statusCard">
                <h3 id="statusTitle">⏸️ Ready to Start</h3>
                <p id="statusText">Configure your settings above and click "Start Continuous Testing"</p>
                <div class="progress-container" id="progressContainer" style="display: none;">
                    <div class="progress-bar" id="progressBar" style="width: 0%;"></div>
                </div>
                <div class="timestamp" id="statusTime"></div>
            </div>
        </div>
        
        <div class="results">
            <h3>📊 Latest Test Results</h3>
            <pre id="testOutput">No tests run yet. Click "Start Continuous Testing" or "Run Once" to begin.</pre>
            <div class="timestamp" id="lastRun"></div>
        </div>
    </div>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        let isRunning = false;
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        function handleWebSocketMessage(data) {
            const statusCard = document.getElementById('statusCard');
            const statusTitle = document.getElementById('statusTitle');
            const statusText = document.getElementById('statusText');
            const statusTime = document.getElementById('statusTime');
            const progressContainer = document.getElementById('progressContainer');
            const progressBar = document.getElementById('progressBar');
            const testOutput = document.getElementById('testOutput');
            const lastRun = document.getElementById('lastRun');
            
            switch(data.type) {
                case 'test_start':
                    statusCard.className = 'status-card status-running';
                    statusTitle.innerHTML = '🏃‍♂️ Running Tests...';
                    statusText.innerHTML = 'Executing pytest with current configuration';
                    statusTime.innerHTML = `Started at ${data.timestamp}`;
                    progressContainer.style.display = 'none';
                    break;
                    
                case 'test_complete':
                    const results = data.results;
                    const success = results.returncode === 0;
                    
                    statusCard.className = 'status-card status-waiting';
                    statusTitle.innerHTML = success ? '✅ Tests Completed Successfully' : '❌ Tests Failed';
                    statusText.innerHTML = `Duration: ${results.duration}s | Return code: ${results.returncode}`;
                    statusTime.innerHTML = `Completed at ${results.timestamp}`;
                    
                    // Show results
                    let output = `=== PyTest Results (${results.timestamp}) ===\n`;
                    output += `Duration: ${results.duration} seconds\n`;
                    output += `Return Code: ${results.returncode}\n\n`;
                    
                    if (results.stdout) {
                        output += "STDOUT:\n" + results.stdout + "\n\n";
                    }
                    if (results.stderr) {
                        output += "STDERR:\n" + results.stderr + "\n\n";
                    }
                    
                    testOutput.textContent = output;
                    lastRun.innerHTML = `Last run: ${results.timestamp}`;
                    
                    if (isRunning) {
                        progressContainer.style.display = 'block';
                    }
                    break;
                    
                case 'progress':
                    if (isRunning) {
                        statusCard.className = 'status-card status-waiting';
                        statusTitle.innerHTML = '⏳ Waiting for Next Run';
                        statusText.innerHTML = `Next test run in ${data.remaining} seconds`;
                        progressBar.style.width = `${data.progress}%`;
                    }
                    break;
                    
                case 'status':
                    isRunning = data.running;
                    if (!isRunning) {
                        statusCard.className = 'status-card status-stopped';
                        statusTitle.innerHTML = '⏹️ Testing Stopped';
                        statusText.innerHTML = 'Click "Start Continuous Testing" to resume';
                        progressContainer.style.display = 'none';
                    }
                    break;
            }
        }
        
        async function startTests() {
            console.log('🚀 startTests() called');
            const waitTime = document.getElementById('waitTime').value;
            const timeout = document.getElementById('timeout').value;
            console.log(`Parameters: waitTime=${waitTime}, timeout=${timeout}`);
            
            try {
                console.log('Sending POST request to /start...');
                const response = await fetch('/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `wait_time=${waitTime}&timeout=${timeout}`
                });
                
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                
                const result = await response.json();
                console.log('Server response:', result);
                
                if (response.ok) {
                    isRunning = true;
                    document.getElementById('statusCard').className = 'status-card status-running';
                    document.getElementById('statusTitle').innerHTML = '🚀 Starting Continuous Testing...';
                    document.getElementById('statusText').innerHTML = 'Initializing test runner';
                    console.log('✅ Tests started successfully');
                } else {
                    console.error('❌ Failed to start tests:', result);
                    alert('Failed to start tests: ' + JSON.stringify(result));
                }
            } catch (error) {
                console.error('❌ Error starting tests:', error);
                alert('Error starting tests: ' + error.message);
            }
        }
        
        async function stopTests() {
            const response = await fetch('/stop', {method: 'POST'});
            if (response.ok) {
                isRunning = false;
            }
        }
        
        async function runOnce() {
            const timeout = document.getElementById('timeout').value;
            
            const response = await fetch('/run-once', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `timeout=${timeout}`
            });
        }
        
        // Initialize connection
        ws.onopen = function() {
            console.log('✅ Connected to test runner WebSocket');
        };
        
        ws.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
        };
        
        ws.onclose = function() {
            console.log('🔌 Disconnected from test runner');
            setTimeout(() => window.location.reload(), 2000);
        };
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Send current status
    await websocket.send_text(json.dumps({
        "type": "status",
        "running": current_test_state["running"],
        "wait_time": current_test_state["wait_time"],
        "timeout": current_test_state["timeout"]
    }))
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/start")
async def start_tests(wait_time: int = Form(30), timeout: int = Form(20)):
    """Start continuous testing"""
    print(f"🚀 Start request received: wait_time={wait_time}, timeout={timeout}")
    print(f"Current state before: {current_test_state}")
    
    if current_test_state["running"]:
        print("⚠️  Tests already running")
        return {"status": "already_running"}
    
    try:
        current_test_state["running"] = True
        current_test_state["wait_time"] = wait_time
        current_test_state["timeout"] = timeout
        
        # Start the test runner loop
        task = asyncio.create_task(test_runner_loop())
        print(f"✅ Test runner loop started, task: {task}")
        
        await manager.broadcast({
            "type": "status",
            "running": True,
            "wait_time": wait_time,
            "timeout": timeout
        })
        print("📡 Broadcasted status update")
        
        return {"status": "started", "wait_time": wait_time, "timeout": timeout}
    except Exception as e:
        print(f"❌ Error starting tests: {e}")
        import traceback
        traceback.print_exc()
        current_test_state["running"] = False
        return {"status": "error", "message": str(e)}

@app.post("/stop")
async def stop_tests():
    """Stop continuous testing"""
    current_test_state["running"] = False
    
    await manager.broadcast({
        "type": "status",
        "running": False
    })
    
    return {"status": "stopped"}

@app.post("/run-once")
async def run_once(timeout: int = Form(20)):
    """Run tests once without continuous loop"""
    await manager.broadcast({
        "type": "test_start",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    results = await run_pytest(timeout)
    current_test_state["last_run"] = results["timestamp"]
    current_test_state["last_results"] = results
    
    await manager.broadcast({
        "type": "test_complete",
        "results": results
    })
    
    return {"status": "completed", "results": results}

@app.get("/status")
async def get_status():
    """Get current status"""
    return current_test_state

if __name__ == "__main__":
    print("🧪 Starting PyTest Runner Web Interface...")
    print("📊 Dashboard will be available at: http://localhost:8001")
    print("⚙️  Default settings: 30s wait time, 20s timeout")
    print("🔄 Use Ctrl+C to stop the server")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001, 
        log_level="info",
        access_log=False
    )
