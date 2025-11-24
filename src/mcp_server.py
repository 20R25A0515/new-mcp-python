from flask import Flask, Response, request, jsonify
import json
from datetime import datetime
import time
import os
import sys

# Fix imports path
sys.path.append(os.path.dirname(__file__))

try:
    from hr_services import hr_db, hr_tool
except ImportError:
    # Fallback for local execution
    from .hr_services import hr_db, hr_tool

app = Flask(__name__)

# Add CORS headers manually (Crucial for Copilot communication)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# --- MCP Tool Invocation Logic (Handles POST /mcp) ---

def handle_rpc_call(rpc_request):
    """Executes an RPC method based on the request body."""
    # RPC must have jsonrpc, method, and id
    if rpc_request.get("jsonrpc") != "2.0" or "method" not in rpc_request:
        return {"jsonrpc": "2.0", "id": rpc_request.get("id"), "error": {"code": -32600, "message": "Invalid Request"}}

    method_name = rpc_request["method"]
    params = rpc_request.get("params", {})
    rpc_id = rpc_request.get("id")

    tool_method = hr_tool.tool_methods.get(method_name)

    if not tool_method:
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Method not found: {method_name}"}}

    try:
        # Execute the function, passing parameters from the RPC request
        result = tool_method(**params)
        
        # Return a standard JSON-RPC success response
        return {"jsonrpc": "2.0", "id": rpc_id, "result": result}
        
    except Exception as e:
        # Return a standard JSON-RPC error response
        print(f"Error executing tool {method_name}: {e}")
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32000, "message": str(e)}}

# --- MCP SSE Endpoint (Handles GET /mcp for Handshake) ---

# --- MCP SSE Endpoint (Handles GET /mcp for Handshake) ---

def generate_events():
    """Generates the initial capability message and heartbeats for the SSE stream."""
    
    # 1. Initialization Response (Protocol/Server Info)
    init_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                # This is the line that defines the visible tools
                "tools": hr_tool.tool_schemas, 
                "resources": {}
            },
            "serverInfo": {
                "name": "hr-mcp-server",
                "version": "1.0.0"
            }
        }
    }
    yield f"data: {json.dumps(init_message)}\n\n"
    # 2. Keep connection alive with heartbeats
    while True:
        time.sleep(30)
        heartbeat = {
            "jsonrpc": "2.0",
            "method": "notifications/heartbeat",
            "params": {"timestamp": datetime.now().isoformat()}
        }
        yield f"data: {json.dumps(heartbeat)}\n\n"
            
# MCP SSE Endpoint for Copilot
@app.route('/', methods=['GET', 'POST'])
def mcp_endpoint():
    if request.method == 'GET':
        # Handle SSE Handshake and Capabilities
        return Response(
            generate_events(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
    elif request.method == 'POST':
        # Handle Tool Invocation (JSON-RPC Call)
        rpc_request = request.get_json()
        if not rpc_request:
            return jsonify({"error": "Invalid JSON-RPC request"}), 400
            
        rpc_response = handle_rpc_call(rpc_request)
        return jsonify(rpc_response)

# --- Standard REST API Endpoints (Kept for frontend/external usage) ---

@app.route('/')
def root():
    return jsonify({
        "message": "HR MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "employees": "/employees",
            "leaves": "/leaves",
            "mcp_sse": "/mcp (GET for Copilot handshake)",
            "mcp_rpc": "/mcp (POST for Copilot tool invocation)"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mcp_ready": True})

@app.route("/employees", methods=["GET"])
def get_all_employees_rest():
    # REST endpoint implementation, leveraging HRDatabase directly
    return jsonify(hr_db.get_all_employees())

@app.route("/employees/<employee_id>", methods=["GET"])
def get_employee_rest(employee_id):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(employee)

@app.route("/employees/search", methods=["GET"])
def search_employees_rest():
    department = request.args.get('department')
    name = request.args.get('name')
    employees = hr_db.search_employees(department, name)
    return jsonify(employees)

@app.route("/leaves", methods=["GET"])
def get_all_leaves_rest():
    status = request.args.get('status')
    leaves = hr_db.get_all_leaves(status)
    return jsonify(leaves)

@app.route("/leaves/employee/<employee_id>", methods=["GET"])
def get_employee_leaves_rest(employee_id):
    employee = hr_db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    leaves = hr_db.get_employee_leaves(employee_id)
    return jsonify(leaves)

@app.route("/leaves", methods=["POST"])
def create_leave_request_rest():
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
    
    # Use datetime.date from the import in hr_services.py
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