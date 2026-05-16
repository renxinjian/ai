"""MCP Server 测试"""
import pytest


class TestMCPCalculator:
    """计算器工具测试"""
    
    @pytest.mark.asyncio
    async def test_calculator_addition(self):
        """测试加法"""
        result = eval("2 + 3")
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_calculator_subtraction(self):
        """测试减法"""
        result = eval("10 - 3")
        assert result == 7
    
    @pytest.mark.asyncio
    async def test_calculator_multiplication(self):
        """测试乘法"""
        result = eval("4 * 5")
        assert result == 20
    
    @pytest.mark.asyncio
    async def test_calculator_division(self):
        """测试除法"""
        result = eval("10 / 2")
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_calculator_complex(self):
        """测试复杂表达式"""
        result = eval("(2 + 3) * 4")
        assert result == 20


class TestBrowserSkill:
    """浏览器技能测试"""
    
    @pytest.mark.asyncio
    async def test_skill_import(self):
        """测试技能导入"""
        from skills.browser.agent import BrowserAgent
        agent = BrowserAgent()
        assert agent.headless == True
    
    @pytest.mark.asyncio
    async def test_skill_open_close(self):
        """测试打开和关闭"""
        from skills.browser.agent import BrowserAgent
        agent = BrowserAgent()
        result = await agent.open("https://example.com")
        assert "Opened" in result
        await agent.close()


class TestCloudSkills:
    """云服务技能测试"""
    
    def test_lighthouse_init(self):
        """测试 Lighthouse 管理器"""
        from skills.cloud.lighthouse import LighthouseManager
        lm = LighthouseManager()
        instances = lm.list_instances()
        assert len(instances) > 0
    
    def test_cos_upload(self):
        """测试 COS 上传"""
        from skills.cloud.lighthouse import COSManager
        cos = COSManager()
        url = cos.upload_file("test-bucket", "/tmp/test.txt", "test.txt")
        assert "cos" in url


class TestDevTools:
    """开发工具测试"""
    
    def test_docker_cleanup_import(self):
        """测试 Docker 清理导入"""
        from skills.devtools.github import DockerCleanup
        assert DockerCleanup is not None
    
    def test_github_manager(self):
        """测试 GitHub 管理器"""
        from skills.devtools.github import GitHubManager
        gm = GitHubManager()
        assert gm is not None
        assert gm.repo == ""
    
    def test_tavily_search(self):
        """测试搜索"""
        from skills.search.tavily import TavilySearch
        ts = TavilySearch()
        result = ts.search("AI Testing")
        assert result["query"] == "AI Testing"
        assert len(result["results"]) > 0


class TestConfig:
    """配置测试"""
    
    def test_env_example_exists(self):
        """检查示例配置是否存在"""
        import os
        assert os.path.exists("config/env.example")
    
    def test_mcp_config(self):
        """检查 MCP 配置"""
        import json
        with open("config/mcp.json") as f:
            config = json.load(f)
        assert "mcpServers" in config
        assert "ai-test-python" in config["mcpServers"]
