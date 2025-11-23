import uvicorn
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    from mcp_sse_server import app
    uvicorn.run(app, host="0.0.0.0", port=port)