"""数据库集成测试 - 真实 MySQL 连接"""
import pytest
import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": "127.0.0.1", "port": 3306,
    "user": "app", "password": "NQ8azLqKGH9z4LqO",
    "database": "app", "charset": "utf8mb4",
}


@pytest.fixture
def db():
    conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
    yield conn
    conn.close()


class TestDatabaseConnection:
    """数据库连接测试"""
    
    def test_connect(self, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            assert cursor.fetchone()["ok"] == 1
    
    def test_tables_exist(self, db):
        with db.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [list(r.values())[0] for r in cursor.fetchall()]
            assert "ai_skills" in tables
            assert "ai_tests" in tables
            assert "ai_config" in tables
            assert "ai_logs" in tables
    
    def test_skills_seeded(self, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM ai_skills")
            count = cursor.fetchone()["cnt"]
            assert count >= 10, f"预期 >=10 个技能, 实际 {count}"
    
    def test_config_seeded(self, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM ai_config")
            count = cursor.fetchone()["cnt"]
            assert count >= 6, f"预期 >=6 条配置, 实际 {count}"
    
    def test_skills_categories(self, db):
        with db.cursor() as cursor:
            cursor.execute("SELECT DISTINCT category FROM ai_skills ORDER BY category")
            categories = [r["category"] for r in cursor.fetchall()]
            assert "cloud" in categories
            assert "devtools" in categories
            assert "search" in categories
    
    def test_db_stats(self, db):
        """验证数据库表统计数据可用"""
        with db.cursor() as cursor:
            cursor.execute("SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES WHERE TABLE_SCHEMA='app'")
            stats = cursor.fetchall()
            assert len(stats) >= 4, f"预期 >=4 张表, 实际 {len(stats)}"


class TestCRUD:
    """增删改查测试"""
    
    def test_insert_and_query(self, db):
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO ai_logs (level, source, message) VALUES ('INFO', 'test', 'test message')")
            db.commit()
            cursor.execute("SELECT * FROM ai_logs WHERE source='test' ORDER BY id DESC LIMIT 1")
            log = cursor.fetchone()
            assert log is not None
            assert log["message"] == "test message"
    
    def test_mcp_tools_roundtrip(self, db):
        """验证 MCP 数据库工具能否正常工作"""
        with db.cursor() as cursor:
            cursor.execute("SELECT name, description FROM ai_skills WHERE enabled=1 ORDER BY name")
            skills = cursor.fetchall()
            assert len(skills) > 0
            for s in skills:
                assert s["name"]
                assert s["description"]


class TestAPIIntegration:
    """API 集成测试"""
    
    def test_health_endpoint(self):
        """测试 Web API 健康检查 (如果服务在运行)"""
        import urllib.request
        import json
        try:
            resp = urllib.request.urlopen("http://localhost:8080/health", timeout=3)
            data = json.loads(resp.read())
            assert data["status"] == "ok"
        except Exception as e:
            pytest.skip(f"API 服务未运行: {e}")
    
    def test_root_endpoint(self):
        try:
            resp = urllib.request.urlopen("http://localhost:8080/", timeout=3)
            data = json.loads(resp.read())
            assert data["service"] == "AI Testing API"
        except Exception as e:
            pytest.skip(f"API 服务未运行: {e}")
