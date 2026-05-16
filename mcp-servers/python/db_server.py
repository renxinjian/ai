"""
数据库 MCP Server - 与 MySQL 深度集成
直接连接 app 数据库，提供 SQL 查询和数据管理能力
"""

import asyncio
import json
import logging
from typing import Any
from contextlib import asynccontextmanager

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest, ListToolsRequest, ReadResourceRequest, 
    Resource, TextContent, Tool,
)
import pymysql
from pymysql.cursors import DictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db-mcp-server")


class DatabaseServer:
    """数据库 MCP 服务 - 提供数据库查询、表结构浏览等功能"""

    DB_CONFIG = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "app",
        "password": "NQ8azLqKGH9z4LqO",
        "database": "app",
        "charset": "utf8mb4",
    }

    def __init__(self):
        self.server = Server("db-mcp-server")
        self._register_handlers()

    def _get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(**self.DB_CONFIG, cursorclass=DictCursor)

    def _register_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="db_query",
                    description="执行 SQL 查询（SELECT 语句）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string", "description": "SELECT 查询语句"},
                            "limit": {"type": "integer", "description": "返回行数限制", "default": 100},
                        },
                        "required": ["sql"],
                    },
                ),
                Tool(
                    name="db_tables",
                    description="列出数据库中所有表",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="db_schema",
                    description="查看表结构",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table": {"type": "string", "description": "表名"},
                        },
                        "required": ["table"],
                    },
                ),
                Tool(
                    name="db_stats",
                    description="查看数据库统计信息",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="db_execute",
                    description="执行 INSERT/UPDATE/DELETE 语句",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string", "description": "SQL 语句"},
                        },
                        "required": ["sql"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> list[TextContent]:
            name = request.params.name
            args = request.params.arguments or {}
            logger.info(f"DB Tool called: {name}")

            try:
                conn = self._get_connection()

                if name == "db_tables":
                    with conn.cursor() as cursor:
                        cursor.execute("SHOW TABLES")
                        tables = [list(row.values())[0] for row in cursor.fetchall()]
                    return [TextContent(type="text", text=json.dumps({"tables": tables}, ensure_ascii=False, indent=2))]

                elif name == "db_schema":
                    table = args["table"]
                    with conn.cursor() as cursor:
                        cursor.execute(f"DESCRIBE `{table}`")
                        schema = cursor.fetchall()
                    return [TextContent(type="text", text=json.dumps(schema, ensure_ascii=False, indent=2))]

                elif name == "db_stats":
                    stats = {}
                    with conn.cursor() as cursor:
                        cursor.execute("SHOW TABLE STATUS")
                        tables_info = cursor.fetchall()
                        stats["tables"] = [
                            {
                                "name": t["Name"],
                                "rows": t["Rows"],
                                "engine": t["Engine"],
                                "size_mb": round((t["Data_length"] + t["Index_length"]) / 1024 / 1024, 2),
                            }
                            for t in tables_info
                        ]
                        cursor.execute("SELECT COUNT(*) as total FROM information_schema.TABLES WHERE TABLE_SCHEMA='app'")
                        stats["total_tables"] = cursor.fetchone()["total"]
                    return [TextContent(type="text", text=json.dumps(stats, ensure_ascii=False, indent=2))]

                elif name == "db_query":
                    sql = args["sql"].strip().upper()
                    if not sql.startswith("SELECT"):
                        return [TextContent(type="text", text="只允许 SELECT 查询")]
                    limit = args.get("limit", 100)
                    with conn.cursor() as cursor:
                        cursor.execute(args["sql"])
                        results = cursor.fetchmany(limit)
                    return [TextContent(type="text", text=json.dumps({
                        "rows": len(results),
                        "data": results,
                    }, ensure_ascii=False, indent=2, default=str))]

                elif name == "db_execute":
                    sql = args["sql"].strip().upper()
                    if not (sql.startswith("INSERT") or sql.startswith("UPDATE") or sql.startswith("DELETE")):
                        return [TextContent(type="text", text="只允许 INSERT/UPDATE/DELETE")]
                    with conn.cursor() as cursor:
                        affected = cursor.execute(args["sql"])
                        conn.commit()
                    return [TextContent(type="text", text=json.dumps({"affected_rows": affected}))]

            except Exception as e:
                logger.error(f"DB Error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
            finally:
                if conn:
                    conn.close()

    async def run(self):
        async with self.server.run(
            InitializationOptions(
                server_name="db-mcp-server",
                server_version="1.1.0",
                capabilities=self.server.get_capabilities(NotificationOptions(), experimental_capabilities={}),
            )
        ):
            logger.info("DB MCP Server running...")
            await asyncio.Event().wait()


if __name__ == "__main__":
    server = DatabaseServer()
    asyncio.run(server.run())
