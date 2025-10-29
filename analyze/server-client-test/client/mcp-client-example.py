#!/usr/bin/env python3
"""
HTTP MCP Client for testing the filesystem usage server

This client uses the current MCP Python SDK to connect to the HTTP MCP server
with proper CORS support.
"""

import asyncio
import json
import httpx

async def test_http_mcp_server():
    """Test the HTTP MCP server with proper HTTP client"""
    
    print("Testing HTTP MCP Filesystem Usage Server...")
    print("Server URL: http://localhost:8000/mcp")
    
    try:
        # Create HTTP client for MCP server
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            print("\n1. Testing health endpoint...")
            health_response = await client.post(
                "http://localhost:8000/mcp/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "health",
                        "arguments": {}
                    }
                }
            )
            
            print(f"Health response status: {health_response.status_code}")
            if health_response.status_code == 200:
                print("✅ Health check successful!")
                print(f"Response: {health_response.text}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                print(f"Response: {health_response.text}")
            
            # Test get_disk_usage
            print("\n2. Testing get_disk_usage tool...")
            disk_response = await client.post(
                "http://localhost:8000/mcp/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "get_disk_usage",
                        "arguments": {}
                    }
                }
            )
            
            print(f"Disk usage response status: {disk_response.status_code}")
            if disk_response.status_code == 200:
                print("✅ Disk usage tool successful!")
                # Parse the response to extract the actual content
                try:
                    response_data = disk_response.json()
                    if 'result' in response_data and 'content' in response_data['result']:
                        content = response_data['result']['content']
                        if content and len(content) > 0 and 'text' in content[0]:
                            print(f"Disk usage info received ({len(content[0]['text'])} characters)")
                            # Show first few lines
                            lines = content[0]['text'].split('\n')[:10]
                            print("First 10 lines:")
                            for line in lines:
                                print(f"  {line}")
                        else:
                            print("No text content in response")
                    else:
                        print(f"Unexpected response structure: {response_data}")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Raw response: {disk_response.text}")
            else:
                print(f"❌ Disk usage tool failed: {disk_response.status_code}")
                print(f"Response: {disk_response.text}")
            
            # Test get_detailed_disk_info
            print("\n3. Testing get_detailed_disk_info tool...")
            detailed_response = await client.post(
                "http://localhost:8000/mcp/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "get_detailed_disk_info",
                        "arguments": {}
                    }
                }
            )
            
            print(f"Detailed disk info response status: {detailed_response.status_code}")
            if detailed_response.status_code == 200:
                print("✅ Detailed disk info tool successful!")
                try:
                    response_data = detailed_response.json()
                    if 'result' in response_data and 'content' in response_data['result']:
                        content = response_data['result']['content']
                        if content and len(content) > 0 and 'text' in content[0]:
                            text_length = len(content[0]['text'])
                            print(f"Detailed disk info received ({text_length} characters)")
                            # Show first few lines
                            lines = content[0]['text'].split('\n')[:15]
                            print("First 15 lines:")
                            for line in lines:
                                print(f"  {line}")
                        else:
                            print("No text content in response")
                    else:
                        print(f"Unexpected response structure: {response_data}")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Raw response: {detailed_response.text}")
            else:
                print(f"❌ Detailed disk info tool failed: {detailed_response.status_code}")
                print(f"Response: {detailed_response.text}")
            
            # Test list_tools
            print("\n4. Testing list_tools...")
            list_response = await client.post(
                "http://localhost:8000/mcp/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/list",
                    "params": {}
                }
            )
            
            print(f"List tools response status: {list_response.status_code}")
            if list_response.status_code == 200:
                print("✅ List tools successful!")
                try:
                    response_data = list_response.json()
                    if 'result' in response_data and 'tools' in response_data['result']:
                        tools = response_data['result']['tools']
                        print(f"Available tools ({len(tools)}):")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool['description']}")
                    else:
                        print(f"Unexpected response structure: {response_data}")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Raw response: {list_response.text}")
            else:
                print(f"❌ List tools failed: {list_response.status_code}")
                print(f"Response: {list_response.text}")
                
    except Exception as e:
        print(f"❌ Client test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("HTTP MCP Client Test")
    print("Make sure the server is running on http://localhost:8000/mcp")
    asyncio.run(test_http_mcp_server())
