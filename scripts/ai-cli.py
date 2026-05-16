#!/usr/bin/env python3
"""
AI Testing CLI - 项目命令行管理工具

用法:
    python ai-cli.py status          # 系统状态
    python ai-cli.py db check        # 数据库检查
    python ai-cli.py api start       # 启动 API 服务
    python ai-cli.py skill list      # 列出技能
    python ai-cli.py test run        # 运行测试
    python ai-cli.py logs            # 查看日志
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 添加项目根到路径
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    import pymysql
    from pymysql.cursors import DictCursor
    HAS_DB = True
except ImportError:
    HAS_DB = False

DB_CONFIG = {
    "host": "127.0.0.1", "port": 3306,
    "user": "app", "password": "NQ8azLqKGH9z4LqO",
    "database": "app", "charset": "utf8mb4",
}


def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def cmd_status():
    """系统状态"""
    print_header("📊 AI Testing - 系统状态")
    
    # 数据库
    if HAS_DB:
        try:
            conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS cnt FROM ai_skills")
                skills = cursor.fetchone()["cnt"]
                cursor.execute("SELECT COUNT(*) AS cnt FROM ai_tests")
                tests = cursor.fetchone()["cnt"]
            conn.close()
            print(f"  ✅ MySQL: 连接正常 (技能: {skills}, 测试: {tests})")
        except Exception as e:
            print(f"  ❌ MySQL: {e}")
    else:
        print("  ⚠️  pymysql 未安装")
    
    # 服务
    services = [
        ("MySQL", ["docker", "ps", "--filter", "name=mysql84", "--format", "{{.Status}}"]),
        ("Skill Market", ["systemctl", "is-active", "skill-market"]),
    ]
    for name, cmd in services:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            status = result.stdout.strip()
            print(f"  {'✅' if 'Up' in status or 'active' in status else '❌'} {name}: {status}")
        except:
            print(f"  ⚠️  {name}: 无法检测")


def cmd_db_check():
    """数据库详细检查"""
    print_header("🗄️  MySQL 数据库检查")
    
    conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
    try:
        with conn.cursor() as cursor:
            # 表
            cursor.execute("SHOW TABLE STATUS FROM app")
            print(f"\n📋 表信息:")
            for t in cursor.fetchall():
                print(f"  • {t['Name']:20s} {t['Engine']:8s} 行数:{t['Rows']:>8}  大小:{round((t['Data_length']+t['Index_length'])/1024/1024,2):>8} MB")
            
            # 种子数据
            cursor.execute("SELECT name, category, enabled FROM ai_skills ORDER BY category")
            print(f"\n📦 技能列表:")
            for s in cursor.fetchall():
                status = '🟢' if s['enabled'] else '🔴'
                print(f"  {status} {s['name']:20s} [{s['category']}]")
            
            cursor.execute("SELECT * FROM ai_config")
            print(f"\n⚙️  配置:")
            for c in cursor.fetchall():
                print(f"  {c['config_key']:20s} = {c['config_value']}")
    finally:
        conn.close()


def cmd_skill_list():
    """列出所有技能"""
    print_header("🛠️  AI 技能列表")
    print(f"\n{'技能名称':25s} {'分类':15s} {'描述'}")
    print("-" * 90)
    
    skills_dir = ROOT / "skills"
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
            py_files = list(skill_dir.glob("*.py"))
            if py_files:
                for pf in py_files:
                    if pf.name != "__init__.py":
                        print(f"  {pf.stem:25s} {skill_dir.name:15s} {pf.read_text().split(chr(10))[1] if pf.read_text() else ''}")
    
    print(f"\n  MCP Servers:")
    mcp_dir = ROOT / "mcp-servers"
    for d in sorted(mcp_dir.iterdir()):
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix in ('.py', '.ts'):
                    print(f"  • {d.name}/{f.name}")


def cmd_start_api():
    """启动 API 服务"""
    print_header("🚀 启动 API 服务")
    print("  http://0.0.0.0:8080")
    print("  http://localhost:8080/docs (Swagger)")
    print("\n  按 Ctrl+C 停止\n")
    
    # 先测试数据库
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        conn.close()
        print("  ✅ MySQL 连接测试通过\n")
    except Exception as e:
        print(f"  ⚠️  MySQL 连接失败: {e}")
    
    import uvicorn
    sys.path.insert(0, str(ROOT / "mcp-servers" / "python"))
    from web_api import app
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


def cmd_run_tests():
    """运行测试"""
    print_header("🧪 运行测试")
    os.chdir(ROOT)
    
    import pytest
    result = pytest.main(["tests/", "-v", "--tb=short"])
    
    # 记录到数据库
    if HAS_DB:
        try:
            conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ai_tests (skill_name, test_name, status) VALUES (%s, %s, %s)",
                    ("system", f"pytest_run_{datetime.now():%Y%m%d_%H%M%S}",
                     "passed" if result == 0 else "failed")
                )
                conn.commit()
            conn.close()
        except:
            pass
    
    sys.exit(result)


def cmd_logs(level: str = "INFO", limit: int = 50):
    """查看日志"""
    print_header(f"📝 日志 (级别: {level}, 最近 {limit} 条)")
    
    if HAS_DB:
        try:
            conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM ai_logs WHERE level >= %s ORDER BY created_at DESC LIMIT %s",
                    (level, limit)
                )
                logs = cursor.fetchall()
                for log in logs:
                    print(f"  [{log['created_at']}] {log['level']:7s} {log['source'] or '':15s} {log['message']}")
            conn.close()
        except Exception as e:
            print(f"  数据库查询失败: {e}")
            print("  (无日志数据，系统刚初始化)")


def main():
    import os
    
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        cmd_status()
    elif cmd == "db" and len(sys.argv) > 2:
        {"check": cmd_db_check}.get(sys.argv[2], lambda: print("未知命令"))()
    elif cmd == "skill" and len(sys.argv) > 2:
        {"list": cmd_skill_list}.get(sys.argv[2], lambda: print("未知命令"))()
    elif cmd == "api" and len(sys.argv) > 2:
        {"start": cmd_start_api}.get(sys.argv[2], lambda: print("未知命令"))()
    elif cmd == "test" and len(sys.argv) > 2:
        {"run": cmd_run_tests}.get(sys.argv[2], lambda: print("未知命令"))()
    elif cmd == "logs":
        cmd_logs()
    else:
        print(f"未知命令: {' '.join(sys.argv[1:])}")
        print(__doc__)


if __name__ == "__main__":
    main()
