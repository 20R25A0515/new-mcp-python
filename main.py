# main.py - Entry point for the application
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Run the MCP SSE server for Render deployment
    uvicorn.run("src.mcp_sse_server:app", host="0.0.0.0", port=port, reload=True)