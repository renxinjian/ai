"""腾讯云 Lighthouse 轻量服务器管理技能"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LighthouseInstance:
    """轻量服务器实例"""
    instance_id: str
    name: str
    public_ip: str
    status: str
    region: str


class LighthouseManager:
    """Lighthouse 实例管理器"""
    
    def __init__(self, secret_id: str = "", secret_key: str = ""):
        self.secret_id = secret_id
        self.secret_key = secret_key
    
    def list_instances(self, region: str = "ap-guangzhou") -> list[LighthouseInstance]:
        """获取实例列表"""
        return [
            LighthouseInstance(
                instance_id="lhins-xxxxx",
                name="example-server",
                public_ip="1.2.3.4",
                status="RUNNING",
                region=region,
            )
        ]
    
    def get_traffic_package(self, instance_id: str) -> dict:
        """获取流量包使用情况"""
        return {"used": 10.5, "total": 200, "unit": "GB", "percentage": 5.25}
    
    def reboot(self, instance_id: str) -> bool:
        """重启实例"""
        print(f"[Lighthouse] Rebooting: {instance_id}")
        return True


# ─── COS 对象存储技能 ───
class COSManager:
    """腾讯云 COS 对象存储管理器"""
    
    def upload_file(self, bucket: str, local_path: str, key: str) -> str:
        """上传文件"""
        url = f"https://{bucket}.cos.ap-guangzhou.myqcloud.com/{key}"
        print(f"[COS] Uploaded: {local_path} → {url}")
        return url
    
    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        """列出对象"""
        return [f"{prefix}file1.txt", f"{prefix}file2.txt"]
    
    def delete_object(self, bucket: str, key: str) -> bool:
        """删除对象"""
        print(f"[COS] Deleted: {bucket}/{key}")
        return True


# ─── 腾讯文档技能 ───
class TencentDocsManager:
    """腾讯文档管理器"""
    
    def create_doc(self, title: str, doc_type: str = "doc") -> dict:
        """创建文档"""
        return {"doc_id": "xxxxx", "title": title, "url": f"https://docs.qq.com/doc/xxxxx"}
    
    def search_docs(self, keyword: str) -> list[dict]:
        """搜索文档"""
        return [{"title": f"结果_{keyword}", "url": "https://docs.qq.com/doc/xxx"}]
