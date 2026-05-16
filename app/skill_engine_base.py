"""
Skill Engine — 声明式 Skill 执行引擎
.skill 文件 = JSON/YAML 配置，不是 Python 代码
"""

import json
import re
import statistics
from typing import Any, Optional
from datetime import datetime

# ═══════════════════════════════════════════════
# .skill 文件格式定义
# ═══════════════════════════════════════════════

SKILL_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "engine", "inputs", "outputs"],
    "properties": {
        "id": {"type": "string", "description": "唯一标识"},
        "name": {"type": "string", "description": "技能名称"},
        "description": {"type": "string", "description": "功能描述"},
        "icon": {"type": "string", "description": "图标 emoji"},
        "version": {"type": "string", "description": "版本号"},
        "author": {"type": "string", "description": "作者"},
        "engine": {"type": "string", "description": "执行引擎类型"},
        "category": {"type": "string", "description": "分类"},
        
        # 引擎配置
        "config": {
            "type": "object",
            "description": "引擎参数配置"
        },
        
        # 输入输出定义
        "inputs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["key", "label", "type"],
                "properties": {
                    "key": {"type": "string"},
                    "label": {"type": "string"},
                    "type": {"type": "string", "enum": ["text", "textarea", "number", "select", "multiselect", "json"]},
                    "default": {},
                    "required": {"type": "boolean"},
                    "options": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"value": {}, "label": {"type": "string"}}}
                    },
                    "placeholder": {"type": "string"}
                }
            }
        },
        "outputs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "label": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        }
    }
}

# ═══════════════════════════════════════════════
# 内置执行引擎
# ═══════════════════════════════════════════════

class TextSummaryEngine:
    """文本摘要引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text = input_data.get("text", "")
        max_len = (config or {}).get("max_length", "short")
        
        if not text:
            return {"error": "请输入文本", "summary": "", "compression_ratio": "0%"}
        
        sentences = [s.strip() for s in text.replace("！","。").replace("？","。").replace("\n","。").split("。") if s.strip()]
        
        limits = {"short": 2, "medium": 5, "long": 999}
        limit = limits.get(max_len, 2)
        
        # 按长度排序取关键句
        sentences.sort(key=len, reverse=True)
        summary = "。".join(sentences[:limit]) + "。"
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": f"{len(summary)/len(text)*100:.1f}%" if text else "0%"
        }


class CalculatorEngine:
    """数据计算引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        numbers = input_data.get("numbers", input_data.get("data", []))
        if isinstance(numbers, str):
            try: numbers = json.loads(numbers)
            except: numbers = [float(n) for n in numbers.split(",") if n.strip()]
        
        ops = (config or {}).get("operations", ["sum", "avg", "max", "min"])
        
        nums = []
        for n in numbers:
            try: nums.append(float(n))
            except: pass
        
        if not nums:
            return {"error": "请提供有效数字"}
        
        result = {}
        if "sum" in ops: result["sum"] = sum(nums)
        if "avg" in ops: result["average"] = round(sum(nums)/len(nums), 2)
        if "max" in ops: result["max"] = max(nums)
        if "min" in ops: result["min"] = min(nums)
        if "count" in ops: result["count"] = len(nums)
        if "median" in ops and nums:
            result["median"] = statistics.median(nums)
        
        result["input_count"] = len(nums)
        return result


class TextTransformEngine:
    """文本转换引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text = input_data.get("text", "")
        ttype = input_data.get("transform_type", (config or {}).get("type", "upper"))
        
        result = text
        if ttype == "upper": result = text.upper()
        elif ttype == "lower": result = text.lower()
        elif ttype == "title": result = text.title()
        elif ttype == "reverse": result = text[::-1]
        elif ttype == "trim": result = text.strip()
        elif ttype == "no_space": result = text.replace(" ", "").replace("\t", "")
        elif ttype == "lines": result = text.splitlines()
        
        return {"original": text, "result": result, "transform": ttype}


class DataFilterEngine:
    """数据筛选引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        items = input_data.get("items", input_data.get("data", []))
        keyword = input_data.get("keyword", (config or {}).get("keyword", ""))
        mode = input_data.get("mode", (config or {}).get("mode", "contains"))
        
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = items.split(",")
        
        threshold = int(input_data.get("threshold", (config or {}).get("threshold", 3)))
        
        results = []
        for item in items:
            s = str(item)
            if mode == "contains" and keyword in s: results.append(item)
            elif mode == "startswith" and s.startswith(keyword): results.append(item)
            elif mode == "endswith" and s.endswith(keyword): results.append(item)
            elif mode == "length_gt" and len(s) > threshold: results.append(item)
            elif mode == "length_lt" and len(s) < threshold: results.append(item)
            elif mode == "equals" and s == keyword: results.append(item)
        
        return {"total": len(items), "matched": len(results), "results": results}


class InfoExtractEngine:
    """信息提取引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        text = input_data.get("text", "")
        types = input_data.get("extract_types", (config or {}).get("types", ["email", "phone"]))
        
        patterns = {
            "email": (r'[\w.-]+@[\w.-]+\.\w+', "邮箱"),
            "phone": (r'1[3-9]\d{9}|\d{3,4}-\d{7,8}', "电话"),
            "url": (r'https?://[./\w?#%&=-]+', "网址"),
            "date": (r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?', "日期"),
            "number": (r'\d+(\.\d+)?', "数字"),
            "id_card": (r'\d{17}[\dXx]', "身份证"),
        }
        
        results = {}
        for t in types:
            if t in patterns:
                pat, label = patterns[t]
                found = re.findall(pat, text)
                if found:
                    results[t] = {"label": label, "matches": list(set(found)), "count": len(set(found))}
        
        return {"text_length": len(text), "extracted": results, "total_found": sum(v["count"] for v in results.values())}


class ConverterEngine:
    """格式转换引擎（CSV↔JSON）"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        import csv, io
        
        data = input_data.get("data", input_data.get("input", ""))
        direction = input_data.get("direction", (config or {}).get("direction", "csv_to_json"))
        
        if direction == "csv_to_json":
            reader = csv.DictReader(io.StringIO(data))
            rows = list(reader)
            return {"format": "JSON", "count": len(rows), "result": rows}
        else:
            try: rows = json.loads(data) if isinstance(data, str) else data
            except: return {"error": "JSON 格式错误"}
            if not rows: return {"error": "空数据"}
            output = io.StringIO()
            w = csv.DictWriter(output, fieldnames=rows[0].keys())
            w.writeheader(); w.writerows(rows)
            return {"format": "CSV", "count": len(rows), "result": output.getvalue()}


class GreetingEngine:
    """问候生成引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        name = input_data.get("name", "用户")
        style = input_data.get("style", (config or {}).get("style", "casual"))
        lang = input_data.get("language", (config or {}).get("language", "zh"))
        
        import random
        
        templates = {
            "zh": {
                "casual": ["哈喽 {name}！", "嘿 {name}~", "你好呀，{name}！"],
                "formal": ["尊敬的 {name}，您好！", "{name} 先生/女士，幸会。"],
                "warm": ["亲爱的 {name} ❤️", "{name}，给你一个大大的拥抱 🤗"],
                "funny": ["嘿 {name}！摸鱼时间到 🐟", "{name} 大佬驾到！🎉"],
            },
            "en": {
                "casual": ["Hey {name}! 😎", "Hi {name}!"],
                "formal": ["Dear {name},", "Hello {name},"],
                "warm": ["{name}, you're amazing! ⭐", "Hi {name}, have a great day! 🌟"],
                "funny": ["{name}! Coffee's ready! ☕"],
            }
        }
        
        lang_tpl = templates.get(lang, templates["zh"])
        style_tpl = lang_tpl.get(style, lang_tpl["casual"])
        greeting = random.choice(style_tpl).format(name=name)
        
        return {"greeting": greeting, "style": style, "name": name}


class SortEngine:
    """数据排序引擎"""
    
    @staticmethod
    def execute(input_data: dict, config: dict = None) -> dict:
        items = input_data.get("items", input_data.get("data", []))
        if isinstance(items, str):
            try: items = json.loads(items)
            except: items = items.split(",")
        
        order = input_data.get("order", (config or {}).get("order", "asc"))
        
        try: sorted_items = sorted(items, reverse=(order == "desc"))
        except: sorted_items = sorted(items, key=str, reverse=(order == "desc"))
        
        return {"original": items, "sorted": sorted_items, "order": order, "count": len(items)}

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



# ═══════════════════════════════════════════════
# 引擎注册表
# ═══════════════════════════════════════════════

ENGINES = {"text_summary": TextSummaryEngine,
    "calculator": CalculatorEngine,
    "text_transform": TextTransformEngine,
    "data_filter": DataFilterEngine,
    "info_extract": InfoExtractEngine,
    "converter": ConverterEngine,
    "greeting": GreetingEngine,
    "sort": SortEngine,
,
{
    "translator": TranslationEngine,
    "password_gen": PasswordGeneratorEngine,
    "qrcode": QRCodeEngine,
    "text_diff": TextDiffEngine,
    "json_tool": FormatJSONEngine,
    "timestamp": TimestampEngine,
    "color": ColorEngine,
    "regex": RegexEngine,
},
{
    "translator": TranslationEngine,
    "password_gen": PasswordGeneratorEngine,
    "qrcode": QRCodeEngine,
    "text_diff": TextDiffEngine,
    "json_tool": FormatJSONEngine,
    "timestamp": TimestampEngine,
    "color": ColorEngine,
    "regex": RegexEngine,
},
{
    "translator": TranslationEngine,
    "password_gen": PasswordGeneratorEngine,
    "qrcode": QRCodeEngine,
    "text_diff": TextDiffEngine,
    "json_tool": FormatJSONEngine,
    "timestamp": TimestampEngine,
    "color": ColorEngine,
    "regex": RegexEngine,
}

ENGINE_META = {"text_summary": {"name": "文本摘要", "icon": "📝", "description": "自动提取文本关键信息，生成摘要",
{
    "translator": {"name": "翻译助手", "icon": "🌐", "description": "中英文模拟翻译"},
    "password_gen": {"name": "密码生成器", "icon": "🔐", "description": "生成高强度随机密码"},
    "qrcode": {"name": "二维码生成", "icon": "📱", "description": "生成二维码数据"},
    "text_diff": {"name": "文本对比", "icon": "📑", "description": "对比两段文本差异"},
    "json_tool": {"name": "JSON 工具", "icon": "🔧", "description": "JSON 格式化/压缩/验证"},
    "timestamp": {"name": "时间戳转换", "icon": "⏰", "description": "时间戳与日期互转"},
    "color": {"name": "颜色转换", "icon": "🎨", "description": "HEX/RGB 颜色格式互转"},
    "regex": {"name": "正则测试器", "icon": "🔤", "description": "测试正则表达式匹配"},
}
},
    "calculator": {"name": "数据计算器", "icon": "🧮", "description": "对数字列表进行求和、平均、最大/最小值等计算"},
    "text_transform": {"name": "文本转换", "icon": "🔄", "description": "大小写转换、反转、去空格等格式化"},
    "data_filter": {"name": "数据筛选", "icon": "🔍", "description": "按关键词或条件筛选数据"},
    "info_extract": {"name": "信息提取器", "icon": "🔎", "description": "提取邮箱、电话、网址、日期等信息"},
    "converter": {"name": "格式转换", "icon": "📊", "description": "CSV↔JSON 格式互转"},
    "greeting": {"name": "问候生成器", "icon": "👋", "description": "生成个性化问候语"},
    "sort": {"name": "数据排序", "icon": "📋", "description": "正序/倒序排列数据"},
{
    "translator": {"name": "翻译助手", "icon": "🌐", "description": "中英文模拟翻译"},
    "password_gen": {"name": "密码生成器", "icon": "🔐", "description": "生成高强度随机密码"},
    "qrcode": {"name": "二维码生成", "icon": "📱", "description": "生成二维码数据"},
    "text_diff": {"name": "文本对比", "icon": "📑", "description": "对比两段文本差异"},
    "json_tool": {"name": "JSON 工具", "icon": "🔧", "description": "JSON 格式化/压缩/验证"},
    "timestamp": {"name": "时间戳转换", "icon": "⏰", "description": "时间戳与日期互转"},
    "color": {"name": "颜色转换", "icon": "🎨", "description": "HEX/RGB 颜色格式互转"},
    "regex": {"name": "正则测试器", "icon": "🔤", "description": "测试正则表达式匹配"},
},
{
    "translator": {"name": "翻译助手", "icon": "🌐", "description": "中英文模拟翻译"},
    "password_gen": {"name": "密码生成器", "icon": "🔐", "description": "生成高强度随机密码"},
    "qrcode": {"name": "二维码生成", "icon": "📱", "description": "生成二维码数据"},
    "text_diff": {"name": "文本对比", "icon": "📑", "description": "对比两段文本差异"},
    "json_tool": {"name": "JSON 工具", "icon": "🔧", "description": "JSON 格式化/压缩/验证"},
    "timestamp": {"name": "时间戳转换", "icon": "⏰", "description": "时间戳与日期互转"},
    "color": {"name": "颜色转换", "icon": "🎨", "description": "HEX/RGB 颜色格式互转"},
    "regex": {"name": "正则测试器", "icon": "🔤", "description": "测试正则表达式匹配"},
}


def execute_skill(skill_def: dict, input_data: dict) -> dict:
    """执行一个 .skill 定义"""
    engine_name = skill_def.get("engine", "")
    config = skill_def.get("config", {})
    
    if engine_name not in ENGINES:
        return {"status": "error", "error": f"未知引擎: {engine_name}"}
    
    engine = ENGINES[engine_name]
    # 合并配置：input_data 覆盖 config 中的默认值
    merged = {}
    merged.update(config)
    merged.update(input_data)
    
    try:
        result = engine.execute(input_data, config)
        return {"status": "passed", "output": result, "engine": engine_name}
    except Exception as e:
        return {"status": "error", "error": str(e), "engine": engine_name}


def get_engine_input_schema(engine_name: str, config: dict = None) -> list:
    """获取引擎的输入参数定义（用于生成表单）"""
    schemas = {
        "text_summary": [
            {"key": "text", "label": "输入文本", "type": "textarea", "placeholder": "粘贴需要摘要的长文本"},
            {"key": "max_length", "label": "摘要长度", "type": "select", "default": "short",
             "options": [{"value":"short","label":"简短"}, {"value":"medium","label":"中等"}, {"value":"long","label":"详细"}]},
        ],
        "calculator": [
            {"key": "numbers", "label": "数字列表", "type": "textarea", "default": "[10, 20, 30, 40, 50]",
             "placeholder": "JSON 数组，如 [1,2,3] 或逗号分隔 1,2,3"},
            {"key": "operations", "label": "计算类型", "type": "multiselect", "default": ["sum","avg"],
             "options": [
                 {"value":"sum","label":"求和"}, {"value":"avg","label":"平均"},
                 {"value":"max","label":"最大"}, {"value":"min","label":"最小"},
                 {"value":"median","label":"中位数"}, {"value":"count","label":"计数"}
             ]},
        ],
        "text_transform": [
            {"key": "text", "label": "输入文本", "type": "textarea", "default": "Hello World"},
            {"key": "transform_type", "label": "转换类型", "type": "select", "default": "upper",
             "options": [
                 {"value":"upper","label":"全部大写"}, {"value":"lower","label":"全部小写"},
                 {"value":"title","label":"首字母大写"}, {"value":"reverse","label":"反转"},
                 {"value":"trim","label":"去首尾空格"}, {"value":"no_space","label":"去所有空格"},
             ]},
        ],
        "data_filter": [
            {"key": "items", "label": "数据列表", "type": "textarea", "default": '["苹果","香蕉","橘子","西瓜","葡萄"]'},
            {"key": "keyword", "label": "关键词", "type": "text", "placeholder": "输入搜索关键词"},
            {"key": "mode", "label": "匹配方式", "type": "select", "default": "contains",
             "options": [
                 {"value":"contains","label":"包含"}, {"value":"startswith","label":"开头匹配"},
                 {"value":"endswith","label":"结尾匹配"}, {"value":"length_gt","label":"长度大于"},
                 {"value":"equals","label":"完全相等"},
             ]},
        ],
        "info_extract": [
            {"key": "text", "label": "输入文本", "type": "textarea",
             "default": "请联系 support@example.com 或 13800000000，访问 https://example.com"},
            {"key": "extract_types", "label": "提取类型", "type": "multiselect", "default": ["email","phone"],
             "options": [
                 {"value":"email","label":"邮箱"}, {"value":"phone","label":"电话"},
                 {"value":"url","label":"网址"}, {"value":"date","label":"日期"},
                 {"value":"number","label":"数字"}, {"value":"id_card","label":"身份证"},
             ]},
        ],
        "converter": [
            {"key": "data", "label": "输入数据", "type": "textarea",
             "default": "name,age,city\n张三,28,北京\n李四,35,上海"},
            {"key": "direction", "label": "转换方向", "type": "select", "default": "csv_to_json",
             "options": [{"value":"csv_to_json","label":"CSV → JSON"}, {"value":"json_to_csv","label":"JSON → CSV"}]},
        ],
        "greeting": [
            {"key": "name", "label": "称呼/名称", "type": "text", "default": "朋友"},
            {"key": "style", "label": "风格", "type": "select", "default": "casual",
             "options": [{"value":"casual","label":"日常随意"}, {"value":"formal","label":"正式商务"},
                         {"value":"warm","label":"温暖亲切"}, {"value":"funny","label":"幽默风趣"}]},
            {"key": "language", "label": "语言", "type": "select", "default": "zh",
             "options": [{"value":"zh","label":"中文"}, {"value":"en","label":"English"}]},
        ],
        "sort": [
            {"key": "items", "label": "数据列表", "type": "textarea", "default": "[5, 3, 8, 1, 9, 2, 7]"},
            {"key": "order", "label": "排序方式", "type": "select", "default": "asc",
             "options": [{"value":"asc","label":"正序（小→大）"}, {"value":"desc","label":"倒序（大→小）"}]},
        ],
    }
    return schemas.get(engine_name, [])


# ═══════════════════════════════════════════════
# 预设 .skill 定义（可直接下载使用）
# ═══════════════════════════════════════════════

PRESET_SKILLS = [
    {
        "id": "text_summary",
        "name": "文本摘要",
        "description": "自动提取文本关键信息，生成简洁摘要",
        "icon": "📝", "version": "1.0.0", "author": "AI Platform",
        "engine": "text_summary", "category": "文本处理",
        "config": {"max_length": "short"},
        "inputs": [
            {"key": "text", "label": "输入文本", "type": "textarea"},
            {"key": "max_length", "label": "摘要长度", "type": "select", "default": "short",
             "options": [{"value":"short","label":"简短"}, {"value":"medium","label":"中等"}, {"value":"long","label":"详细"}]},
        ],
        "outputs": [{"key":"summary","label":"摘要结果","type":"text"}, {"key":"compression_ratio","label":"压缩比","type":"text"}]
    },
    {
        "id": "calculator",
        "name": "数据计算器",
        "description": "对数字列表进行求和、平均、最大/最小等统计计算",
        "icon": "🧮", "version": "1.0.0", "author": "AI Platform",
        "engine": "calculator", "category": "数据处理",
        "config": {"operations": ["sum","avg","max","min"]},
        "inputs": [
            {"key": "numbers", "label": "数字列表", "type": "textarea"},
            {"key": "operations", "label": "计算类型", "type": "multiselect", "default": ["sum","avg"],
             "options": [
                 {"value":"sum","label":"求和"}, {"value":"avg","label":"平均"},
                 {"value":"max","label":"最大"}, {"value":"min","label":"最小"},
                 {"value":"median","label":"中位数"},
             ]},
        ],
        "outputs": [{"key":"sum","label":"总和","type":"number"}, {"key":"average","label":"平均","type":"number"}]
    },
    {
        "id": "info_extract",
        "name": "信息提取器",
        "description": "从文本中自动提取邮箱、电话、网址等关键信息",
        "icon": "🔎", "version": "1.0.0", "author": "AI Platform",
        "engine": "info_extract", "category": "文本处理",
        "config": {"types": ["email","phone","url"]},
        "inputs": [
            {"key": "text", "label": "输入文本", "type": "textarea"},
            {"key": "extract_types", "label": "提取类型", "type": "multiselect", "default": ["email","phone"],
             "options": [
                 {"value":"email","label":"邮箱"}, {"value":"phone","label":"电话"},
                 {"value":"url","label":"网址"}, {"value":"date","label":"日期"},
                 {"value":"number","label":"数字"},
             ]},
        ],
        "outputs": [{"key":"extracted","label":"提取结果","type":"json"}]
    },
    {
        "id": "greeting",
        "name": "问候生成器",
        "description": "根据名称和风格生成个性化问候语",
        "icon": "👋", "version": "1.0.0", "author": "AI Platform",
        "engine": "greeting", "category": "文本处理",
        "inputs": [
            {"key": "name", "label": "称呼", "type": "text"},
            {"key": "style", "label": "风格", "type": "select", "default": "casual",
             "options": [{"value":"casual","label":"日常随意"}, {"value":"formal","label":"正式商务"}, {"value":"warm","label":"温暖亲切"}]},
            {"key": "language", "label": "语言", "type": "select", "default": "zh",
             "options": [{"value":"zh","label":"中文"}, {"value":"en","label":"English"}]},
        ],
        "outputs": [{"key":"greeting","label":"问候语","type":"text"}]
    },
]
