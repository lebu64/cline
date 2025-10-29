# MCP Server Development Guide

## 📋 Overview

This guide provides comprehensive instructions for MCP (Model Context Protocol) server development with Cline AI assistant. It covers server setup, client development, configuration, and best practices to ensure smooth development workflow.

## 🎯 Target Audience

- **Developers**: Building MCP servers and clients
- **Cline AI Assistant**: Instructions for AI-assisted development
- **System Administrators**: Environment configuration

---

## 🔧 Development Environment Setup

### MCP Python SDK Reference

**⚠️ IMPORTANT FOR CLINE**: Always use the current MCP Python SDK located at:
```
analyze/server-client-test/mcp-python-sdk/
```

**Key SDK Files for Reference:**
- `examples/servers/simple-streamablehttp-stateless/` - Current HTTP implementation
- `examples/servers/` - Various server patterns
- `mcp/server/` - Core server implementation

### Virtual Environment Setup

```bash
# Server virtual environment
cd analyze/server-client-test/server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Client virtual environment  
cd analyze/server-client-test/client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Requirements Files

**Server requirements.txt:**
```
mcp>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
psutil>=5.9.0
starlette>=0.27.0
anyio>=4.0.0
```

**Client requirements.txt:**
```
httpx>=0.25.0
asyncio
```

---

## ⚙️ System Configuration for Cline

### .bashrc Configuration (Prevent Hanging Terminals)

Add these lines to `~/.bashrc` to prevent terminal hanging issues:

```bash
# Cline Terminal Configuration
export CLINE_TERMINAL_TIMEOUT=30
export PS1='\u@\h:\w\$ '  # Simple prompt without virtual env indicators
export PROMPT_COMMAND=''

# Python virtual environment handling
export VIRTUAL_ENV_DISABLE_PROMPT=1

# Terminal behavior
export TERM=xterm-256color
stty sane
```

### Cline Settings Configuration

In VSCode Cline settings (`settings.json`):

```json
{
  "cline.terminal.reuseTerminal": true,
  "cline.terminal.commandTimeout": 30000,
  "cline.terminal.maxBufferSize": 10000,
  "cline.autoApprove.tools": [
    "read_file",
    "list_files", 
    "search_files",
    "execute_command"
  ]
}
```

### Cline Rules for MCP Development

Create `.clinerules/mcp-development.md`:

```markdown
# MCP Development Rules for Cline

## SDK Reference
- ALWAYS reference: `analyze/server-client-test/mcp-python-sdk/`
- Use current examples, not simplified implementations
- Follow stateless Streamable HTTP patterns

## Virtual Environment Handling
- Always activate virtual environment before running Python scripts
- Use separate venvs for server and client
- Install dependencies from requirements.txt

## Testing Workflow
1. Start server first: `cd server && source .venv/bin/activate && python server.py`
2. Test with client: `cd client && source .venv/bin/activate && python client.py`
3. Use MCP Inspector for browser testing

## Error Prevention
- Check CORS configuration for browser clients
- Validate URL paths (use trailing slash: `/mcp/`)
- Handle both Accept headers: `application/json, text/event-stream`
```

---

## 🚀 MCP Server Development

### Server Implementation Template

**File: `server/mcp-server-example.py`**

```python
#!/usr/bin/env python3
import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

# Create server
app = Server("your-server-name")

# Tool implementation
@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    # Your tool logic here
    pass

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    # List available tools
    pass

# CORS Configuration (CRITICAL for browser clients)
starlette_app = CORSMiddleware(
    Starlette(routes=[Mount("/mcp", app=handle_streamable_http)]),
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
```

### Key Server Development Points

1. **Use Streamable HTTP Transport**: Current standard, not deprecated SSE
2. **Implement CORS**: Required for browser-based clients (MCP Inspector)
3. **Stateless Design**: Recommended for HTTP servers
4. **Proper Tool Definitions**: Include name, description, and inputSchema

---

## 🔗 MCP Client Development

### Client Implementation Template

**File: `client/mcp-client-example.py`**

```python
#!/usr/bin/env python3
import asyncio
import httpx

async def test_mcp_server():
    async with httpx.AsyncClient() as client:
        # Use correct URL with trailing slash
        response = await client.post(
            "http://localhost:8000/mcp/",  # ⚠️ Note trailing slash
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"  # ⚠️ Both required
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "tool_name", "arguments": {}}
            }
        )
```

### Client Development Workflow

1. **Start Server First**
   ```bash
   cd analyze/server-client-test/server
   source .venv/bin/activate
   python mcp-server-example.py
   ```

2. **Test with Client**
   ```bash
   cd analyze/server-client-test/client  
   source .venv/bin/activate
   python mcp-client-example.py
   ```

3. **Browser Testing with MCP Inspector**
   - Open MCP Inspector in browser
   - Connect to: `http://localhost:8000/mcp/`
   - Test all tools

---

## 🛠️ Development Workflow with Cline

### Instructions for Cline AI Assistant

**⚠️ CRITICAL: Always follow these patterns**

1. **Reference Current SDK**
   ```
   ALWAYS check: analyze/server-client-test/mcp-python-sdk/examples/servers/
   DO NOT simplify - use current implementation patterns
   ```

2. **Virtual Environment Handling**
   ```
   BEFORE executing Python commands:
   - cd to correct directory (server/client)
   - source .venv/bin/activate
   - THEN run Python script
   ```

3. **Testing Sequence**
   ```
   1. Start server in terminal
   2. Wait for "Application startup complete"
   3. Run client tests
   4. Use MCP Inspector for browser validation
   ```

4. **Error Prevention**
   ```
   - Check CORS configuration for 406 errors
   - Use trailing slash in URLs to avoid 307 redirects
   - Include both Accept headers
   - Handle Server-Sent Events format in responses
   ```

### Common Issues and Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| CORS Error | "CORS Missing Allow Origin" | Add proper CORS middleware |
| 307 Redirect | Client gets redirect responses | Use `/mcp/` with trailing slash |
| 406 Not Acceptable | Wrong Accept header | Use `application/json, text/event-stream` |
| Virtual Env Hanging | Terminal freezes | Use simple PS1, disable prompt modification |

---

## 📊 Testing and Validation

### Server Health Check

```bash
# Test server directly
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"health","arguments":{}}}'
```

### MCP Inspector Testing

1. Open MCP Inspector web interface
2. Enter server URL: `http://localhost:8000/mcp/`
3. Click "Connect"
4. Test all available tools

### Automated Testing

Create test scripts in `analyze/server-client-test/scripts/`:
- `test-server-start.sh` - Server startup validation
- `test-client-connection.sh` - Client connectivity tests  
- `test-tools-functionality.sh` - Individual tool testing

---

## 🔍 Debugging and Troubleshooting

### Server Log Analysis

Monitor server logs for:
- `"Processing request of type"` - Successful request handling
- `"Terminating session"` - Normal session cleanup
- HTTP status codes: 200 (OK), 406 (Accept error), 307 (Redirect)

### Client Debugging

Enable debug output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Error Patterns

1. **Session Issues**: Check `Mcp-Session-Id` header exposure
2. **Streaming Problems**: Verify Server-Sent Events format
3. **Tool Execution**: Validate inputSchema and parameter types
4. **Connection Timeouts**: Check terminal configuration and timeouts

---

## 📈 Best Practices

### For Developers
- Use type hints and proper error handling
- Implement comprehensive logging
- Follow MCP protocol specifications
- Test with multiple client types

### For Cline AI Assistant  
- Reference current SDK examples directly
- Follow established patterns in this guide
- Validate configurations before implementation
- Test thoroughly at each development step

### Performance Optimization
- Use stateless design for scalability
- Implement proper resource cleanup
- Monitor memory usage in long-running sessions
- Use connection pooling for clients

---

## 🎯 Conclusion

This guide provides a complete framework for MCP server development with Cline AI assistance. By following these patterns and configurations, developers can create robust MCP servers while avoiding common pitfalls like terminal hanging and CORS issues.

**Key Success Factors:**
- ✅ Proper environment configuration
- ✅ Current SDK reference usage  
- ✅ Comprehensive testing workflow
- ✅ Cline-specific development rules
- ✅ Error prevention strategies

Use this guide as the primary reference for all MCP server development activities with Cline.
