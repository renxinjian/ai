"""
AI Testing Project - 主入口

用法:
    python main.py          # 运行 MCP 服务器
    python main.py --test   # 运行测试
    python main.py --list   # 列出可用技能
"""

import asyncio
import sys
import importlib
import pkgutil
from pathlib import Path


def list_skills():
    """列出所有可用技能模块"""
    skills_dir = Path(__file__).parent / "skills"
    print("📦 可用技能模块:")
    print("=" * 40)
    
    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            py_files = list(item.glob("*.py"))
            if py_files:
                print(f"\n  📁 {item.name}/")
                for pf in py_files:
                    if pf.name != "__init__.py":
                        print(f"     📄 {pf.stem}")


def list_mcp_servers():
    """列出 MCP 服务器"""
    mcp_dir = Path(__file__).parent / "mcp-servers"
    print("\n🧩 MCP 服务器:")
    print("=" * 40)
    
    for item in mcp_dir.iterdir():
        if item.is_dir():
            print(f"  • {item.name}/")
            for f in item.iterdir():
                if f.suffix in (".py", ".ts", ".js"):
                    print(f"     └ {f.name}")


async def run_mcp_server():
    """运行 MCP Python 服务器"""
    sys.path.insert(0, str(Path(__file__).parent))
    from mcp_servers.python.base_server import AITestServer
    server = AITestServer()
    print("🚀 启动 MCP Server...")
    await server.run()


def main():
    if "--list" in sys.argv or "-l" in sys.argv:
        list_skills()
        list_mcp_servers()
    elif "--test" in sys.argv or "-t" in sys.argv:
        import pytest
        sys.exit(pytest.main(["tests/", "-v"]))
    else:
        asyncio.run(run_mcp_server())


if __name__ == "__main__":
    main()
