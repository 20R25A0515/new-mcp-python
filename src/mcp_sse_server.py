# src/mcp_sse_server.py
from flask import Flask, Response, request, jsonify
import json
import uuid
from datetime import datetime
import time
import os
import sys

# Fix imports
sys.path.append(os.path.dirname(__file__))

try:
    from hr_services import hr_db
except ImportError:
    # Fallback
    from .hr_services import hr_db

app = Flask(__name__)

# Add CORS headers manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

class MCPSseServer:
    def handle_mcp_connection(self):
        def generate_events():
            try:
                # Initialization response
                init_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "hr-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
                yield f"data: {json.dumps(init_message)}\n\n"
                
                # Tools list
                tools_message = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "result": {
                        "tools": [
                            {
                                "name": "get_employee_details",
                                "description": "Get employee details by ID",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "employee_id": {"type": "string"}
                                    },
                                    "required": ["employee_id"]
                                }
                            },
                            {
                                "name": "get_all_employees",
                                "description": "Get all employees",
                                "inputSchema": {"type": "object", "properties": {}}
                            }
                        ]
                    }
                }
                yield f"data: {json.dumps(tools_message)}\n\n"
                
                # Keep connection alive
                while True:
                    time.sleep(30)
                    heartbeat = {
                        "jsonrpc": "2.0",
                        "method": "notifications/heartbeat",
                        "params": {"timestamp": datetime.now().isoformat()}
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    
            except GeneratorExit:
                pass
    
        return Response(
            generate_events(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )

mcp_server = MCPSseServer()

# MCP SSE Endpoint for Copilot
@app.route('/mcp', methods=['GET', 'POST'])
def mcp_sse_endpoint():
    return mcp_server.handle_mcp_connection()

# REST API Endpoints
@app.route('/')
def root():
    return jsonify({
        "message": "HR MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "employees": "/employees",
            "leaves": "/leaves",
            "health": "/health",
            "mcp": "/mcp (SSE endpoint for Copilot)"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mcp_ready": True})

@app.route("/employees", methods=["GET"])
def get_all_employees():
    return jsonify(hr_db.get_all_employees())

@app.route("/employees/<employee_id>", methods=["GET"])
def get_employee(employee_id):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(employee)

@app.route("/employees/search/", methods=["GET"])
def search_employees():
    department = request.args.get('department')
    name = request.args.get('name')
    employees = hr_db.search_employees(department, name)
    return jsonify(employees)

@app.route("/leaves", methods=["GET"])
def get_all_leaves():
    status = request.args.get('status')
    leaves = hr_db.get_all_leaves(status)
    return jsonify(leaves)

@app.route("/leaves/employee/<employee_id>", methods=["GET"])
def get_employee_leaves(employee_id):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    leaves = hr_db.get_employee_leaves(employee_id)
    return jsonify(leaves)

@app.route("/leaves", methods=["POST"])
def create_leave_request():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ['employee_id', 'start_date', 'end_date', 'leave_type', 'reason']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    employee = hr_db.get_employee(data['employee_id'])
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    from datetime import date
    leave_data = {
        "employee_id": data['employee_id'],
        "start_date": data['start_date'],
        "end_date": data['end_date'],
        "leave_type": data['leave_type'],
        "reason": data['reason'],
        "status": "pending",
        "submitted_date": str(date.today())
    }
    
    leave = hr_db.create_leave_request(leave_data)
    return jsonify(leave)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)