# AI Testing Project

学习与测试 MCP (Model Context Protocol) 和 Claude Code Skills 的项目。

## 项目结构

```
├── mcp_servers/            # MCP 服务器示例
│   ├── echo_server.py      # 回显服务器
│   └── calculator_server.py # 计算器服务器
├── skills/         # 自定义 Skill 示例
├── config/         # Claude Code 配置示例
└── tests/          # 测试
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 MCP echo 服务器
python mcp_servers/echo_server.py
```

## MCP 服务器

MCP (Model Context Protocol) 是 AI 模型与外部工具/数据源之间的标准协议。

### 已实现的服务器

- **Echo Server** — 最简单的 MCP 服务器，回显输入
- **Calculator Server** — 提供计算工具，演示 tool use

## Skills

Skills 是 Claude Code 的自定义斜杠命令，定义在 `.claude/skills/` 目录下。

详见 `skills/` 目录中的示例。
