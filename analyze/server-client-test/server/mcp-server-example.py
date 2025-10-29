#!/usr/bin/env python3
"""
HTTP MCP Server with CORS support for browser-based clients

This server follows the current MCP Python SDK examples and includes proper CORS support
for browser-based clients like the MCP Inspector.
"""

import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import anyio
import mcp.types as types
import psutil
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

def main() -> int:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("filesystem-usage-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """Handle tool calls for filesystem usage information"""
        if name == "get_disk_usage":
            return await get_disk_usage()
        elif name == "get_detailed_disk_info":
            return await get_detailed_disk_info()
        elif name == "health":
            return [types.TextContent(type="text", text="Server is healthy and running")]
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def get_disk_usage() -> list[types.ContentBlock]:
        """Get disk usage information for all mounted filesystems"""
        disk_info = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(
                    f"Device: {partition.device}\n"
                    f"Mountpoint: {partition.mountpoint}\n"
                    f"Filesystem: {partition.fstype}\n"
                    f"Total: {usage.total / (1024**3):.2f} GB\n"
                    f"Used: {usage.used / (1024**3):.2f} GB\n"
                    f"Free: {usage.free / (1024**3):.2f} GB\n"
                    f"Usage: {usage.percent:.1f}%\n"
                    f"{'-'*40}"
                )
            except PermissionError:
                # Some filesystems may not be accessible
                disk_info.append(
                    f"Device: {partition.device}\n"
                    f"Mountpoint: {partition.mountpoint}\n"
                    f"Filesystem: {partition.fstype}\n"
                    f"Status: Permission denied\n"
                    f"{'-'*40}"
                )
        
        result_text = "Disk Usage Information:\n\n" + "\n".join(disk_info)
        return [types.TextContent(type="text", text=result_text)]

    async def get_detailed_disk_info() -> list[types.ContentBlock]:
        """Get detailed disk information including partitions and usage statistics"""
        disk_info = []
        
        # Get disk partitions
        disk_info.append("=== Disk Partitions ===")
        for partition in psutil.disk_partitions():
            disk_info.append(
                f"Device: {partition.device}\n"
                f"Mountpoint: {partition.mountpoint}\n"
                f"Filesystem: {partition.fstype}\n"
                f"Options: {partition.opts}"
            )
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(
                    f"  Total: {usage.total / (1024**3):.2f} GB\n"
                    f"  Used: {usage.used / (1024**3):.2f} GB ({usage.percent:.1f}%)\n"
                    f"  Free: {usage.free / (1024**3):.2f} GB\n"
                )
            except PermissionError:
                disk_info.append("  Status: Permission denied")
            disk_info.append("")
        
        # Get disk I/O statistics
        disk_info.append("=== Disk I/O Statistics ===")
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_info.append(
                    f"Read Count: {disk_io.read_count}\n"
                    f"Write Count: {disk_io.write_count}\n"
                    f"Read Bytes: {disk_io.read_bytes / (1024**2):.2f} MB\n"
                    f"Write Bytes: {disk_io.write_bytes / (1024**2):.2f} MB\n"
                    f"Read Time: {disk_io.read_time} ms\n"
                    f"Write Time: {disk_io.write_time} ms"
                )
            else:
                disk_info.append("No disk I/O statistics available")
        except Exception as e:
            disk_info.append(f"Error getting disk I/O statistics: {e}")
        
        result_text = "\n".join(disk_info)
        return [types.TextContent(type="text", text=result_text)]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools for filesystem usage"""
        return [
            types.Tool(
                name="health",
                description="Health check endpoint",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="get_disk_usage",
                description="Get disk usage information for all mounted filesystems",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="get_detailed_disk_info",
                description="Get detailed disk information including partitions and usage statistics",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]

    # Create the session manager with stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=False,
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Filesystem Usage MCP Server started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Filesystem Usage MCP Server shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Wrap ASGI application with CORS middleware to expose Mcp-Session-Id header
    # for browser-based clients (ensures 500 errors get proper CORS headers)
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],  # Allow all origins - adjust as needed for production
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # MCP streamable HTTP methods + OPTIONS for preflight
        allow_headers=["*"],  # Allow all headers for preflight requests
        expose_headers=["Mcp-Session-Id"],
    )

    import uvicorn

    print("Starting HTTP MCP Filesystem Usage Server with CORS support...")
    print("Available tools:")
    print("  - health: Health check endpoint")
    print("  - get_disk_usage: Get disk usage information")
    print("  - get_detailed_disk_info: Get detailed disk information")
    print("Server will run on http://localhost:8000 with Streamable HTTP transport")
    print("MCP endpoint: http://localhost:8000/mcp")
    print("CORS enabled for browser-based clients")
    
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)

    return 0

if __name__ == "__main__":
    main()
