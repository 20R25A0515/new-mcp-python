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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

def handle_rpc_call(rpc_request):
    if rpc_request.get("jsonrpc") != "2.0" or "method" not in rpc_request:
        return {"jsonrpc": "2.0", "id": rpc_request.get("id"), "error": {"code": -32600, "message": "Invalid Request"}}
    method_name = rpc_request["method"]
    params = rpc_request.get("params", {})
    rpc_id = rpc_request.get("id")
    tool_method = hr_tool.tool_methods.get(method_name)
    if not tool_method:
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": f"Method not found: {method_name}"}}
    try:
        result = tool_method(**params)
        return {"jsonrpc": "2.0", "id": rpc_id, "result": result}
    except Exception as e:
        print(f"Error executing tool {method_name}: {e}")
        return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32000, "message": str(e)}}

def generate_events():
    # The first SSE message: initialization
    init_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": hr_tool.tool_schemas,
                "resources": {}
            },
            "serverInfo": {
                "name": "hr-mcp-server",
                "version": "1.0.0"
            }
        }
    }
    # Yield the initialization as the very first event
    yield f"data: {json.dumps(init_message)}\n\n"
    # Heartbeat
    while True:
        time.sleep(30)
        heartbeat = {
            "jsonrpc": "2.0",
            "method": "notifications/heartbeat",
            "params": {"timestamp": datetime.now().isoformat()}
        }
        yield f"data: {json.dumps(heartbeat)}\n\n"

# MCP endpoint for Copilot handshake and JSON-RPC
@app.route('/mcp', methods=['GET', 'POST'])
def mcp_endpoint():
    if request.method == 'GET':
        return Response(
            generate_events(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
    elif request.method == 'POST':
        rpc_request = request.get_json()
        if not rpc_request:
            return jsonify({"error": "Invalid JSON-RPC request"}), 400
        rpc_response = handle_rpc_call(rpc_request)
        return jsonify(rpc_response)

@app.route("/")
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

# ... (rest API endpoints as before, e.g. /employees, /leaves) ...

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)