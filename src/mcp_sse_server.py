# src/mcp_sse_server.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uuid
from datetime import datetime
import uvicorn
import os

# Import your existing modules
from .hr_services import hr_db

app = FastAPI(title="HR MCP SSE Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MCPSseServer:
    def __init__(self):
        self.clients = {}
    
    async def handle_mcp_connection(self, request: Request):
        client_id = str(uuid.uuid4())
        
        async def mcp_event_stream():
            try:
                # Initialization response (MCP protocol format)
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
                            },
                            {
                                "name": "search_employees", 
                                "description": "Search employees by department or name",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "department": {"type": "string"},
                                        "name": {"type": "string"}
                                    }
                                }
                            },
                            {
                                "name": "get_employee_leave_requests",
                                "description": "Get employee leave requests",
                                "inputSchema": {
                                    "type": "object", 
                                    "properties": {
                                        "employee_id": {"type": "string"}
                                    },
                                    "required": ["employee_id"]
                                }
                            }
                        ]
                    }
                }
                yield f"data: {json.dumps(tools_message)}\n\n"
                
                # Keep connection alive with heartbeats
                while True:
                    await asyncio.sleep(30)
                    heartbeat = {
                        "jsonrpc": "2.0",
                        "method": "notifications/heartbeat",
                        "params": {"timestamp": datetime.now().isoformat()}
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    
            except asyncio.CancelledError:
                pass
    
        return StreamingResponse(
            mcp_event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

mcp_server = MCPSseServer()

@app.post("/mcp")
async def mcp_sse_endpoint(request: Request):
    return await mcp_server.handle_mcp_connection(request)

@app.get("/mcp")
async def mcp_sse_get_endpoint(request: Request):
    return await mcp_server.handle_mcp_connection(request)

@app.get("/")
async def root():
    return {"message": "HR MCP SSE Server", "mcp_endpoint": "/mcp"}

@app.get("/health")
async def health():
    return {"status": "healthy", "mcp_ready": True}

# Add a simple tool testing endpoint
@app.post("/test-tool")
async def test_tool(request: Request):
    data = await request.json()
    tool_name = data.get("name")
    arguments = data.get("arguments", {})
    
    if tool_name == "get_employee_details":
        employee_id = arguments.get("employee_id")
        employee = hr_db.get_employee(employee_id)
        if employee:
            return {"result": f"Employee: {employee.name}, Dept: {employee.department}"}
        else:
            return {"result": f"Employee {employee_id} not found"}
    
    return {"result": f"Tool {tool_name} not found"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)