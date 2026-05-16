# 系统架构

## 整体架构

```
┌─────────────────────────────────────────────┐
│               AI Testing Project              │
├─────────────────────────────────────────────┤
│  main.py              ┌──────────────────┐   │
│  (入口) ─────────────→│   MCP Server     │   │
│                       │  (Python/Node)   │   │
│                       └──────┬───────────┘   │
│                              │               │
│              ┌───────────────┼───────────┐   │
│              ▼               ▼           ▼   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│
│  │Browser │ │ Cloud  │ │DevTools│ │ Search ││
│  │ Skill  │ │ Skills │ │ Skills │ │ Skills ││
│  └────────┘ └────────┘ └────────┘ └────────┘│
└─────────────────────────────────────────────┘
```

## MCP 协议流程

```
AI Model ←→ MCP Client ←→ MCP Server ←→ Tools/Skills
```

## 技能模块

每个技能模块遵循以下接口：

```python
class BaseSkill:
    async def execute(self, **kwargs) -> Any: ...
    def get_metadata(self) -> dict: ...
```
