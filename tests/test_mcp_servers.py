"""
MCP 服务器测试。
由于 MCP 服务器通过 stdio 通信，这里主要测试工具逻辑。
"""

import pytest
import sys
sys.path.insert(0, ".")

# 测试 echo_server 的工具逻辑
# 注意: 完整测试需要启动 MCP 服务器进程，这里仅做导入验证


def test_import_echo_server():
    """验证 echo_server 可以正常导入"""
    from mcp import echo_server
    assert echo_server.server.name == "echo-server"


def test_import_calculator_server():
    """验证 calculator_server 可以正常导入"""
    from mcp import calculator_server
    assert calculator_server.server.name == "calculator-server"
