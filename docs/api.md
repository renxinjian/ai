# API 文档

## MCP 工具接口

### calculator
- **名称**: `calculator`
- **描述**: 执行数学计算
- **参数**:
  - `expression` (string, 必填): 数学表达式
- **返回**: 计算结果

### echo
- **名称**: `echo`
- **描述**: 回显输入
- **参数**:
  - `message` (string, 必填): 要回显的消息
- **返回**: 回显内容

## Skills 接口

所有技能通过 Python import 使用:

```python
from skills.browser.agent import BrowserAgent
from skills.cloud.lighthouse import LighthouseManager
from skills.devtools.github import GitHubManager
from skills.search.tavily import TavilySearch
```
