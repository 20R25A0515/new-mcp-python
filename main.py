# main.py - Entry point
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.mcp_sse_server:app", host="0.0.0.0", port=port)