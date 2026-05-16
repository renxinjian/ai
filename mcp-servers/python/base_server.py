"""
MCP (Model Context Protocol) 基础服务端示例

MCP 是 AI 模型与大模型交互的标准协议，本示例展示如何创建 MCP 服务，
注册工具、资源和提示模板，供 AI 模型调用。

运行方式:
    python mcp-servers/python/base_server.py

依赖:
    pip install mcp httpx
"""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
    Resource,
    TextContent,
    Tool,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-mcp-server")


class AITestServer:
    """AI 测试 MCP 服务端"""

    def __init__(self, name: str = "ai-test-server"):
        self.server = Server(name)
        self._register_handlers()

    def _register_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(name="calculator", description="执行数学计算",
                     inputSchema={"type": "object", "properties": {
                         "expression": {"type": "string", "description": "数学表达式"}},
                         "required": ["expression"]}),
                Tool(name="echo", description="回显输入",
                     inputSchema={"type": "object", "properties": {
                         "message": {"type": "string", "description": "要回显的消息"}},
                         "required": ["message"]}),
            ]

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> list[TextContent]:
            name = request.params.name
            args = request.params.arguments or {}
            logger.info(f"Tool called: {name} with args: {args}")
            if name == "calculator":
                try:
                    result = eval(args["expression"], {"__builtins__": {}}, {})
                    return [TextContent(type="text", text=str(result))]
                except Exception as e:
                    return [TextContent(type="text", text=f"Error: {e}")]
            elif name == "echo":
                return [TextContent(type="text", text=f"Echo: {args.get('message', '')}")]
            raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        async with self.server.run(
            InitializationOptions(
                server_name="ai-test-server",
                server_version="1.0.0",
                capabilities=self.server.get_capabilities(
                    NotificationOptions(), experimental_capabilities={}),
            )
        ):
            logger.info("MCP Server running...")
            await asyncio.Event().wait()


if __name__ == "__main__":
    server = AITestServer()
    asyncio.run(server.run())
