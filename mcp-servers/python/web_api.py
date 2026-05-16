"""
Web API Server - 提供 RESTful API 接口
基于 FastAPI，提供对 AI 测试项目的完整管理能力
"""

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pymysql
from pymysql.cursors import DictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web-api")

app = FastAPI(
    title="AI Testing API",
    description="AI 测试项目的 RESTful API 接口",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "app",
    "password": "NQ8azLqKGH9z4LqO",
    "database": "app",
    "charset": "utf8mb4",
}


def get_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)


# ── 系统状态 ──
@app.get("/")
async def root():
    return {
        "service": "AI Testing API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    """完整健康检查"""
    checks = {"status": "ok", "timestamp": datetime.now().isoformat()}
    
    # MySQL 检查
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            checks["mysql"] = "connected"
        conn.close()
    except Exception as e:
        checks["mysql"] = f"error: {e}"
        checks["status"] = "degraded"
    
    return checks


# ── 数据库操作 ──
@app.get("/db/tables")
async def list_tables():
    """列出所有表"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT TABLE_NAME, TABLE_ROWS, ENGINE, "
                           "ROUND((DATA_LENGTH + INDEX_LENGTH)/1024/1024, 2) AS SIZE_MB "
                           "FROM information_schema.TABLES "
                           "WHERE TABLE_SCHEMA = 'app' "
                           "ORDER BY TABLE_NAME")
            tables = cursor.fetchall()
        return {"tables": tables, "total": len(tables)}
    finally:
        conn.close()


@app.get("/db/query")
async def query(sql: str = Query(..., description="SELECT 语句"),
                limit: int = Query(100, ge=1, le=1000)):
    """执行 SQL 查询"""
    if not sql.strip().upper().startswith("SELECT"):
        raise HTTPException(400, "只允许 SELECT 语句")
    
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchmany(limit)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return {"columns": columns, "rows": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@app.get("/db/schema/{table}")
async def table_schema(table: str):
    """查看表结构"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table}`")
            return {"table": table, "columns": cursor.fetchall()}
    except Exception as e:
        raise HTTPException(404, f"表 {table} 不存在: {e}")
    finally:
        conn.close()


# ── MCP 工具模拟 ──
@app.post("/mcp/calculator")
async def mcp_calculator(expression: str):
    """MCP 计算器工具 (RESTful 版)"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"tool": "calculator", "input": expression, "result": result}
    except Exception as e:
        raise HTTPException(400, f"计算错误: {e}")


@app.get("/mcp/tools")
async def list_mcp_tools():
    """列出所有 MCP 工具"""
    return {
        "tools": [
            {"name": "db_query", "description": "执行 SQL 查询"},
            {"name": "db_tables", "description": "列出数据库表"},
            {"name": "db_schema", "description": "查看表结构"},
            {"name": "calculator", "description": "数学计算"},
            {"name": "echo", "description": "回显测试"},
        ]
    }


# ── 启动入口 ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
