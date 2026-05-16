"""
数据库初始化脚本
创建项目所需的表结构和种子数据
"""

import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "app",
    "password": "NQ8azLqKGH9z4LqO",
    "database": "app",
    "charset": "utf8mb4",
}

INIT_SQL = """
CREATE TABLE IF NOT EXISTS ai_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50),
    version VARCHAR(20) DEFAULT '1.0.0',
    enabled TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ai_tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL,
    test_name VARCHAR(200) NOT NULL,
    status ENUM('passed', 'failed', 'skipped') DEFAULT 'passed',
    duration_ms INT DEFAULT 0,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ai_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ai_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level ENUM('DEBUG','INFO','WARNING','ERROR') DEFAULT 'INFO',
    source VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

SEED_SQL = """
INSERT IGNORE INTO ai_skills (name, description, category) VALUES
('browser', '浏览器自动化 - 基于 Playwright 的网页操控', 'automation'),
('lighthouse', '腾讯云 Lighthouse 轻量服务器管理', 'cloud'),
('cos', '腾讯云 COS 对象存储管理', 'cloud'),
('tencent_docs', '腾讯文档创建与管理', 'cloud'),
('github', 'GitHub 仓库与 Issue 管理', 'devtools'),
('docker_cleanup', 'Docker 资源清理与磁盘分析', 'devtools'),
('tavily_search', 'Tavily 网页搜索', 'search'),
('memory_hygiene', '向量记忆库维护与优化', 'ai'),
('mcp_server', 'MCP 协议服务端', 'ai'),
('web_tools', '网页工具链（搜索/抓取）', 'tools');

INSERT IGNORE INTO ai_config (config_key, config_value, description) VALUES
('project_version', '2.0.0', '项目版本号'),
('db_host', '127.0.0.1', '数据库主机'),
('db_port', '3306', '数据库端口'),
('db_name', 'app', '数据库名'),
('server_port', '8080', 'API 服务端口'),
('mcp_enabled', 'true', 'MCP 服务是否启用');
"""


def run():
    conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
    try:
        with conn.cursor() as cursor:
            for stmt in INIT_SQL.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt + ";")
                    
            for stmt in SEED_SQL.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt + ";")
        conn.commit()
        print("✅ 数据库初始化完成")
        
        # 验证
        with conn.cursor() as cursor:
            cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='app'")
            print(f"📊 已创建表: {[r['TABLE_NAME'] for r in cursor.fetchall()]}")
            cursor.execute("SELECT COUNT(*) AS cnt FROM ai_skills")
            print(f"📦 种子数据: {cursor.fetchone()['cnt']} 个技能")
    except Exception as e:
        print(f"❌ 错误: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run()
