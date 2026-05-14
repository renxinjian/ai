"""
最简单的 MCP 服务器示例 —— 回显服务器。

提供两个工具:
- echo: 原样返回输入文本
- reverse_echo: 反转后返回输入文本

运行方式:
    python mcp/echo_server.py

在 Claude Code 中配置:
    {
        "mcpServers": {
            "echo": {
                "command": "python",
                "args": ["mcp/echo_server.py"]
            }
        }
    }
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server


server = Server("echo-server")


@server.list_tools()
async def list_tools():
    return [
        {
            "name": "echo",
            "description": "原样返回输入文本",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要回显的文本",
                    }
                },
                "required": ["text"],
            },
        },
        {
            "name": "reverse_echo",
            "description": "反转后返回输入文本",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要反转并回显的文本",
                    }
                },
                "required": ["text"],
            },
        },
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "echo":
        return [{"type": "text", "text": arguments["text"]}]
    elif name == "reverse_echo":
        return [{"type": "text", "text": arguments["text"][::-1]}]
    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
