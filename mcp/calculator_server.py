"""
计算器 MCP 服务器 —— 演示 tool use。

提供工具:
- add, subtract, multiply, divide: 基本运算

运行方式:
    python mcp/calculator_server.py

在 Claude Code 中配置:
    {
        "mcpServers": {
            "calculator": {
                "command": "python",
                "args": ["mcp/calculator_server.py"]
            }
        }
    }
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server


server = Server("calculator-server")


@server.list_tools()
async def list_tools():
    return [
        {
            "name": "add",
            "description": "加法: 返回 a + b",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数"},
                    "b": {"type": "number", "description": "第二个数"},
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "subtract",
            "description": "减法: 返回 a - b",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "被减数"},
                    "b": {"type": "number", "description": "减数"},
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "multiply",
            "description": "乘法: 返回 a * b",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个因数"},
                    "b": {"type": "number", "description": "第二个因数"},
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "divide",
            "description": "除法: 返回 a / b",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "被除数"},
                    "b": {"type": "number", "description": "除数 (不能为 0)"},
                },
                "required": ["a", "b"],
            },
        },
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    a = float(arguments["a"])
    b = float(arguments["b"])

    operations = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b if b != 0 else "错误: 除数不能为 0",
    }

    if name not in operations:
        raise ValueError(f"Unknown tool: {name}")

    result = operations[name]()
    return [{"type": "text", "text": str(result)}]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
