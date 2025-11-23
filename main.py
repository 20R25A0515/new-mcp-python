# main.py
import uvicorn
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    try:
        # Try absolute import
        from src.mcp_sse_server import app
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ImportError as e:
        print(f"Import error: {e}")
        print("Trying alternative import...")
        # Alternative import
        import src.mcp_sse_server
        uvicorn.run(src.mcp_sse_server.app, host="0.0.0.0", port=port)