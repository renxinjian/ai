# Claude Code 配置

## MCP 服务器配置

将 `mcp-servers.json` 的内容合并到你的 Claude Code 配置文件中:

- **项目级配置**: `.claude/mcp.json`（仅当前项目）
- **用户级配置**: `~/.claude/mcp.json`（所有项目）

### 配置示例 (`.claude/mcp.json`)

```json
{
    "mcpServers": {
        "echo": {
            "command": "python",
            "args": ["mcp_servers/echo_server.py"]
        },
        "calculator": {
            "command": "python",
            "args": ["mcp_servers/calculator_server.py"]
        }
    }
}
```

配置后重启 Claude Code，MCP 服务器的工具就会自动可用。

## Skill 配置

将 `skills/` 目录下的 `.md` 文件复制到 `.claude/skills/` 目录中:

```bash
mkdir -p .claude/skills
cp skills/*.md .claude/skills/
```

然后这些 skill 就可以通过 `/skill-name` 在 Claude Code 中调用了。
