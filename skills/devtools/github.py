"""GitHub 操作技能 - 基于 gh CLI"""
import subprocess
import json
from typing import Optional


class GitHubManager:
    """GitHub 仓库管理器"""
    
    def __init__(self, repo: str = ""):
        self.repo = repo
    
    def _run(self, cmd: list[str]) -> str:
        """执行 gh 命令"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def list_issues(self, state: str = "open", limit: int = 10) -> list[dict]:
        """列出 issues"""
        output = self._run(["gh", "issue", "list", "--state", state, "--json", "number,title,state", "--limit", str(limit)])
        try:
            return json.loads(output) if output else []
        except json.JSONDecodeError:
            return []
    
    def create_issue(self, title: str, body: str = "", labels: list[str] = None) -> dict:
        """创建 issue"""
        cmd = ["gh", "issue", "create", "--title", title, "--body", body]
        if labels:
            cmd.extend(["--label", ",".join(labels)])
        output = self._run(cmd)
        return {"url": output}
    
    def list_prs(self, state: str = "open") -> list[dict]:
        """列出 PR"""
        return self._run(["gh", "pr", "list", "--state", state, "--json", "number,title,headRefName"])
    
    def list_runs(self, branch: str = "main", limit: int = 5) -> list[dict]:
        """列出 CI 运行"""
        output = self._run(["gh", "run", "list", "--branch", branch, "--limit", str(limit), "--json", "databaseId,conclusion,displayTitle"])
        try:
            return json.loads(output) if output else []
        except json.JSONDecodeError:
            return []


# ─── Docker Cleanup Skill ───
class DockerCleanup:
    """Docker 清理工具"""
    
    @staticmethod
    def prune_images() -> str:
        """清理未使用的镜像"""
        result = subprocess.run(["docker", "image", "prune", "-f"], capture_output=True, text=True)
        return result.stdout
    
    @staticmethod
    def prune_volumes() -> str:
        """清理未使用的卷"""
        result = subprocess.run(["docker", "volume", "prune", "-f"], capture_output=True, text=True)
        return result.stdout
    
    @staticmethod
    def disk_usage() -> dict:
        """查看磁盘使用"""
        result = subprocess.run(["docker", "system", "df"], capture_output=True, text=True)
        return {"raw": result.stdout}
    
    @staticmethod
    def clean_all() -> str:
        """全面清理"""
        report = []
        for cmd in [
            ["docker", "image", "prune", "-f"],
            ["docker", "container", "prune", "-f"],
            ["docker", "builder", "prune", "-f"],
        ]:
            result = subprocess.run(cmd, capture_output=True, text=True)
            report.append(result.stdout.strip())
        return "\n".join(report)
