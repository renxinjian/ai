"""Tavily 搜索技能 - 网页搜索"""
from typing import Optional


class TavilySearch:
    """Tavily 搜索客户端"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com"
    
    def search(self, query: str, max_results: int = 5, include_answer: bool = False) -> dict:
        """执行搜索"""
        print(f"[Tavily] Searching: {query}")
        return {
            "query": query,
            "results": [
                {
                    "title": f"结果 {i+1}",
                    "url": f"https://example.com/{i}",
                    "content": f"关于 {query} 的第 {i+1} 条搜索结果",
                }
                for i in range(max_results)
            ],
            "answer": "这是一条模拟的搜索摘要。" if include_answer else None,
        }


class WebFetcher:
    """网页内容抓取技能"""
    
    def fetch(self, url: str, max_chars: int = 5000) -> str:
        """抓取网页内容"""
        print(f"[WebFetcher] Fetching: {url}")
        return f"模拟抓取的内容 - {url} (前{max_chars}字符)"
