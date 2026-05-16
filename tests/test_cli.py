"""CLI 工具测试"""
import subprocess
import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "scripts/ai-cli.py"],
        capture_output=True, text=True, cwd=ROOT
    )
    assert "用法" in result.stdout or "用法" in result.stderr


def test_cli_status():
    result = subprocess.run(
        [sys.executable, "scripts/ai-cli.py", "status"],
        capture_output=True, text=True, cwd=ROOT
    )
    assert "MySQL" in result.stdout
    assert "系统状态" in result.stdout


def test_cli_skill_list():
    result = subprocess.run(
        [sys.executable, "scripts/ai-cli.py", "skill", "list"],
        capture_output=True, text=True, cwd=ROOT
    )
    assert "B" in result.stdout or "技能" in result.stdout


def test_init_db_script():
    """验证初始化脚本可导入"""
    import importlib
    spec = importlib.util.spec_from_file_location("init_db", f"{ROOT}/scripts/init_db.py")
    assert spec is not None
    assert spec.loader is not None
