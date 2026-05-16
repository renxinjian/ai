"""
扩展引擎库 — 新增实用引擎
"""

import json, re, random, statistics, hashlib, time
from datetime import datetime


class TranslationEngine:
    """模拟翻译引擎（中英互译模拟）"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text = input_data.get("text", "")
        direction = input_data.get("direction", (config or {}).get("direction", "zh_to_en"))
        
        # 模拟翻译（实际可对接API）
        mock_translations = {
            "zh_to_en": {
                "你好": "Hello", "世界": "World", "谢谢": "Thank you",
                "早上好": "Good morning", "再见": "Goodbye", "中国": "China",
                "北京": "Beijing", "人工智能": "Artificial Intelligence",
                "技术": "Technology", "开发": "Development",
            },
            "en_to_zh": {
                "hello": "你好", "world": "世界", "thank you": "谢谢",
                "good morning": "早上好", "goodbye": "再见", "china": "中国",
                "technology": "技术", "development": "开发",
            }
        }
        
        tpl = mock_translations.get(direction, {})
        # 简单逐词翻译
        words = text.split()
        translated = []
        for w in words:
            w_clean = w.strip('.,!?;:')
            matched = tpl.get(w_clean.lower(), w_clean)
            if w_clean != w:
               # 保持标点
                punct = w[len(w_clean):]
                matched += punct
            translated.append(matched)
        
        result = " ".join(translated)
        return {
            "original": text,
            "translation": result,
            "direction": "中→英" if direction == "zh_to_en" else "英→中",
            "note": "此为模拟翻译，对接真实API可获得准确结果"
        }


class PasswordGeneratorEngine:
    """密码生成器"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        length = int(input_data.get("length", (config or {}).get("length", 12)))
        include_upper = input_data.get("upper", (config or {}).get("upper", True))
        include_lower = input_data.get("lower", (config or {}).get("lower", True))
        include_digits = input_data.get("digits", (config or {}).get("digits", True))
        include_symbols = input_data.get("symbols", (config or {}).get("symbols", False))
        count = int(input_data.get("count", (config or {}).get("count", 3)))
        
        chars = ""
        if include_upper: chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if include_lower: chars += "abcdefghijklmnopqrstuvwxyz"
        if include_digits: chars += "0123456789"
        if include_symbols: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not chars: chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        passwords = []
        for _ in range(count):
            pwd = "".join(random.choice(chars) for _ in range(length))
            # 保证至少包含每种选定类型
            if include_upper and not any(c.isupper() for c in pwd):
                pwd = pwd[:1] + random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + pwd[2:]
            if include_digits and not any(c.isdigit() for c in pwd):
                pwd = pwd[:-1] + random.choice("0123456789")
            passwords.append(pwd)
        
        return {
            "passwords": passwords,
            "length": length,
            "count": count,
            "strength": "强" if length >= 12 else ("中" if length >= 8 else "弱")
        }


class QRCodeEngine:
    """二维码生成引擎（返回模拟数据，实际可调用API）"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text = input_data.get("text", "")
        if not text: return {"error": "请输入要编码的内容"}
        
        # 模拟生成二维码链接
        encoded = hashlib.md5(text.encode()).hexdigest()[:8]
        return {
            "content": text,
            "qrcode_data": f"QR:{encoded}",
            "api_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}",
            "note": "可使用上方链接生成真实二维码"
        }


class TextDiffEngine:
    """文本对比引擎"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text_a = input_data.get("text_a", "")
        text_b = input_data.get("text_b", "")
        
        lines_a = text_a.splitlines()
        lines_b = text_b.splitlines()
        
        added = [l for l in lines_b if l not in lines_a]
        removed = [l for l in lines_a if l not in lines_b]
        common = [l for l in lines_a if l in lines_b]
        
        return {
            "added": added,
            "removed": removed,
            "common_count": len(common),
            "added_count": len(added),
            "removed_count": len(removed),
            "identical": text_a == text_b,
        }


class FormatJSONEngine:
    """JSON 格式化和验证引擎"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text = input_data.get("text", "")
        action = input_data.get("action", (config or {}).get("action", "format"))
        
        try:
            parsed = json.loads(text)
            if action == "format":
                result = json.dumps(parsed, ensure_ascii=False, indent=2)
                return {"status": "valid", "result": result, "type": type(parsed).__name__}
            elif action == "minify":
                result = json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
                return {"status": "valid", "result": result, "type": type(parsed).__name__}
            elif action == "validate":
                return {"status": "valid", "type": type(parsed).__name__, "size": len(text)}
        except json.JSONDecodeError as e:
            return {"status": "invalid", "error": str(e), "position": e.pos}


class TimestampEngine:
    """时间戳转换引擎"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        ts = input_data.get("timestamp", "")
        direction = input_data.get("direction", (config or {}).get("direction", "ts_to_date"))
        
        import time as tmod
        
        if direction == "ts_to_date":
            try:
                ts_num = int(ts) if ts else int(tmod.time())
                if ts_num > 1e12: ts_num /= 1000  # 毫秒转秒
                dt = datetime.fromtimestamp(ts_num)
                return {
                    "timestamp": ts_num,
                    "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "weekday": ["一","二","三","四","五","六","日"][dt.weekday()],
                }
            except: return {"error": "无效时间戳"}
        else:
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                return {
                    "date": ts,
                    "timestamp": int(dt.timestamp()),
                    "timestamp_ms": int(dt.timestamp() * 1000),
                }
            except:
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%d")
                    return {"date": ts, "timestamp": int(dt.timestamp())}
                except: return {"error": "日期格式错误，请使用 YYYY-MM-DD HH:MM:SS"}


class ColorEngine:
    """颜色转换引擎"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        color = input_data.get("color", "#1a56d6")
        color = color.strip()
        
        # 识别输入格式
        if color.startswith("#"):
            hex_val = color[1:]
            if len(hex_val) == 3: hex_val = "".join(c*2 for c in hex_val)
            if len(hex_val) != 6: return {"error": "无效HEX颜色"}
            r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
            return {
                "hex": f"#{hex_val.upper()}",
                "rgb": f"rgb({r}, {g}, {b})",
                "rgba": f"rgba({r}, {g}, {b}, 1)",
                "hsl": f"hsl({int(hashlib.md5(f'{r},{g},{b}'.encode()).hexdigest()[:3],16) % 360}, 70%, 50%)",
                "values": {"r": r, "g": g, "b": b}
            }
        elif color.startswith("rgb"):
            import re as re_m
            nums = re_m.findall(r'\d+', color)
            if len(nums) >= 3:
                r, g, b = int(nums[0]), int(nums[1]), int(nums[2])
                return {
                    "hex": f"#{r:02X}{g:02X}{b:02X}",
                    "rgb": color,
                    "values": {"r": r, "g": g, "b": b}
                }
        return {"error": "支持 HEX(#xxx) 或 RGB(r,g,b) 格式"}


class RegexEngine:
    """正则表达式测试引擎"""
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        pattern = input_data.get("pattern", "")
        text = input_data.get("text", "")
        flags_str = input_data.get("flags", "")
        
        if not pattern: return {"error": "请输入正则表达式"}
        
        try:
            flags = 0
            if "i" in flags_str: flags |= re.IGNORECASE
            if "m" in flags_str: flags |= re.MULTILINE
            if "s" in flags_str: flags |= re.DOTALL
            
            compiled = re.compile(pattern, flags) if flags else re.compile(pattern)
            matches = compiled.findall(text)
            
            return {
                "pattern": pattern,
                "matches": matches[:20],
                "match_count": len(matches),
                "is_match": bool(matches),
            }
        except re.error as e:
            return {"error": f"正则语法错误: {e}"}


# ─── 引擎注册合并 ───
EXTRA_ENGINES = {
    "translator": TranslationEngine,
    "password_gen": PasswordGeneratorEngine,
    "qrcode": QRCodeEngine,
    "text_diff": TextDiffEngine,
    "json_tool": FormatJSONEngine,
    "timestamp": TimestampEngine,
    "color": ColorEngine,
    "regex": RegexEngine,
}

EXTRA_ENGINE_META = {
    "translator": {"name": "翻译助手", "icon": "🌐", "description": "中英文模拟翻译"},
    "password_gen": {"name": "密码生成器", "icon": "🔐", "description": "生成高强度随机密码"},
    "qrcode": {"name": "二维码生成", "icon": "📱", "description": "生成二维码数据"},
    "text_diff": {"name": "文本对比", "icon": "📑", "description": "对比两段文本差异"},
    "json_tool": {"name": "JSON 工具", "icon": "🔧", "description": "JSON 格式化/压缩/验证"},
    "timestamp": {"name": "时间戳转换", "icon": "⏰", "description": "时间戳与日期互转"},
    "color": {"name": "颜色转换", "icon": "🎨", "description": "HEX/RGB 颜色格式互转"},
    "regex": {"name": "正则测试器", "icon": "🔤", "description": "测试正则表达式匹配"},
}
