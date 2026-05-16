# AI Testing Project

<<<<<<< HEAD
> 一个测试 AI 能力的综合项目，包含 MCP Servers、Skills 示例和完整的数据库集成

## 📋 快速概览

| 组件 | 说明 | 访问 |
|------|------|------|
| 🧩 MCP Server | Model Context Protocol 服务 | Python / Node.js |
| 🌐 Web API | FastAPI RESTful 接口 | `:8080/docs` |
| 🛠️ CLI | 命令行管理工具 | `ai-cli.py` |
| 🗄️ MySQL | 持久化存储 | `app@localhost:3306` |
| 🐳 Docker | 容器化部署 | `docker-compose up` |

## 🚀 快速开始

```bash
# 1. 查看状态
python scripts/ai-cli.py status

# 2. 初始化数据库
python scripts/init_db.py

# 3. 启动 API 服务
python scripts/ai-cli.py api start

# 4. 运行测试
python scripts/ai-cli.py test run
```

## 🏗️ 项目结构

```
ai/
├── mcp-servers/          # MCP 协议服务端
│   └── python/
│       ├── base_server.py   # 基础 MCP 示例
│       ├── db_server.py     # 数据库 MCP (真实 MySQL)
│       └── web_api.py       # FastAPI RESTful API
├── skills/               # AI 技能模块
│   ├── browser/          # 浏览器自动化
│   ├── cloud/            # 腾讯云 (Lighthouse/COS/Docs)
│   ├── devtools/         # GitHub + Docker
│   └── search/           # Tavily 搜索
├── config/               # 配置文件
├── scripts/              # 工具脚本
│   ├── ai-cli.py         # CLI 管理工具
│   └── init_db.py        # 数据库初始化
├── tests/                # 测试用例
├── docs/                 # 文档
├── docker-compose.yml    # Docker 部署
└── Dockerfile            # 容器镜像
```

## 🔧 配置

```bash
cp config/env.example .env
# 编辑 .env 填写密钥
```

## 🧪 测试

```bash
pytest tests/ -v
```

## 🗄️ 数据库

MySQL 数据库 `app`，已自动创建 4 张表和 10 条种子数据：

| 表 | 说明 |
|----|------|
| `ai_skills` | 技能注册表 |
| `ai_tests` | 测试执行记录 |
| `ai_config` | 项目配置 |
| `ai_logs` | 日志记录 |

## 📊 API 文档

启动服务后访问:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- 健康检查: http://localhost:8080/health

## 📄 License

MIT
=======
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
>>>>>>> 40dbc284c9d6adcf4f26d6fa6398acf074adad6f
