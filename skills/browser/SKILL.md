# Browser Automation Skill

浏览器自动化技能，基于 Playwright 实现网页操控。

## 能力

- 打开/关闭网页
- 页面截图与内容提取
- 表单填写与交互
- 元素点击与导航

## 使用

```python
from skills.browser import BrowserAgent

agent = BrowserAgent()
page = await agent.open("https://example.com")
content = await agent.extract_text()
await agent.close()
```

## 配置

| 参数 | 说明 |
|------|------|
| `headless` | 是否无头模式 (默认: true) |
| `timeout` | 超时时间 (默认: 30000ms) |
