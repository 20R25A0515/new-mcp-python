# check_mcp.py
import mcp
print("MCP version:", getattr(mcp, '__version__', 'unknown'))
print("MCP attributes:", [attr for attr in dir(mcp) if not attr.startswith('_')])

import mcp.server
print("MCP server attributes:", [attr for attr in dir(mcp.server) if not attr.startswith('_')])

import mcp.types
print("MCP types attributes:", [attr for attr in dir(mcp.types) if not attr.startswith('_')])