"""
Skill 模板库 + 自然语言匹配引擎
用户说一句话，系统自动匹配最佳模板并生成完整代码
"""

import json
import re
from typing import Optional

# ═══════════════════════════════════════════
# 模板库（覆盖常见场景）
# ═══════════════════════════════════════════

TEMPLATES = [
    {
        "id": "text_summary",
        "name": "文本摘要",
        "category": "text",
        "icon": "📝",
        "description": "对一段文本生成摘要，提取关键信息",
        "keywords": ["摘要", "总结", "概括", "提炼", "压缩", "summary"],
        "parameters": [
            {"key": "text", "label": "输入文本", "type": "textarea", "default": "请输入需要摘要的文本内容...", "placeholder": "粘贴需要摘要的长文本"},
            {"key": "max_length", "label": "摘要长度", "type": "select", "default": "short", "options": [{"value":"short","label":"简短（1-2句）"}, {"value":"medium","label":"中等（3-5句）"}, {"value":"long","label":"详细"}], "optional": True},
        ],
        "code": """def main(input_data):
    text = input_data.get("text", "")
    max_len = input_data.get("max_length", "short")
    
    # 简单摘要算法：提取关键句
    sentences = [s.strip() for s in text.replace("！","。").replace("？","。").split("。") if s.strip()]
    
    if max_len == "short":
        limit = min(2, len(sentences))
    elif max_len == "medium":
        limit = min(5, len(sentences))
    else:
        limit = len(sentences)
    
    # 按长度排序，取较长的句子（通常信息更丰富）
    sentences.sort(key=len, reverse=True)
    summary = "。".join(sentences[:limit]) + "。"
    
    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": f"{len(summary)/len(text)*100:.1f}%" if text else "0%",
    }"""
    },
    {
        "id": "data_filter",
        "name": "数据筛选",
        "category": "data",
        "icon": "🔍",
        "description": "从数据列表中按条件筛选出符合要求的数据",
        "keywords": ["筛选", "过滤", "查找", "搜索", "匹配", "filter", "search"],
        "parameters": [
            {"key": "items", "label": "数据列表", "type": "textarea", "default": "[\"苹果\", \"香蕉\", \"橘子\", \"西瓜\", \"葡萄\"]", "placeholder": "JSON 数组格式，如 [\"a\", \"b\", \"c\"]"},
            {"key": "keyword", "label": "关键词", "type": "text", "default": "", "placeholder": "输入要搜索的关键词"},
            {"key": "mode", "label": "匹配方式", "type": "select", "default": "contains", "options": [{"value":"contains","label":"包含关键词"}, {"value":"startswith","label":"以关键词开头"}, {"value":"length_gt","label":"长度大于"}, {"value":"length_lt","label":"长度小于"}]},
            {"key": "threshold", "label": "阈值", "type": "number", "default": 3, "optional": True, "placeholder": "用于长度比较的阈值"},
        ],
        "code": """def main(input_data):
    items = input_data.get("items", [])
    keyword = input_data.get("keyword", "")
    mode = input_data.get("mode", "contains")
    threshold = int(input_data.get("threshold", 3))
    
    if isinstance(items, str):
        try: items = json.loads(items)
        except: items = [items]
    
    results = []
    for item in items:
        item_str = str(item)
        if mode == "contains":
            if keyword in item_str: results.append(item)
        elif mode == "startswith":
            if item_str.startswith(keyword): results.append(item)
        elif mode == "length_gt":
            if len(item_str) > threshold: results.append(item)
        elif mode == "length_lt":
            if len(item_str) < threshold: results.append(item)
    
    return {
        "total": len(items),
        "matched": len(results),
        "results": results,
    }"""
    },
    {
        "id": "calculator",
        "name": "数据计算器",
        "category": "data",
        "icon": "🧮",
        "description": "对一组数字进行求和、平均、最大/最小值等计算",
        "keywords": ["计算", "求和", "平均", "统计", "合计", "加总", "数字", "总数", "数学"],
        "parameters": [
            {"key": "numbers", "label": "数字列表", "type": "textarea", "default": "[10, 20, 30, 40, 50]", "placeholder": "JSON 数组，如 [1, 2, 3, 4, 5]"},
            {"key": "operations", "label": "计算类型", "type": "multiselect", "default": ["sum","avg","max","min"], "options": [{"value":"sum","label":"求和"}, {"value":"avg","label":"平均值"}, {"value":"max","label":"最大值"}, {"value":"min","label":"最小值"}, {"value":"count","label":"计数"}, {"value":"median","label":"中位数"}]},
        ],
        "code": """def main(input_data):
    import json, statistics
    
    numbers = input_data.get("numbers", [])
    if isinstance(numbers, str):
        try: numbers = json.loads(numbers)
        except: numbers = []
    
    if not numbers:
        return {"error": "请提供数字列表"}
    
    nums = [float(n) for n in numbers if isinstance(n, (int, float)) or str(n).replace('.','',1).isdigit()]
    ops = input_data.get("operations", ["sum","avg","max","min"])
    
    results = {}
    if "sum" in ops: results["sum"] = sum(nums)
    if "avg" in ops: results["average"] = round(sum(nums)/len(nums), 2)
    if "max" in ops: results["max"] = max(nums)
    if "min" in ops: results["min"] = min(nums)
    if "count" in ops: results["count"] = len(nums)
    if "median" in ops and len(nums) > 0:
        results["median"] = statistics.median(nums)
    
    return results"""
    },
    {
        "id": "text_transform",
        "name": "文本格式转换",
        "category": "text",
        "icon": "🔄",
        "description": "对文本进行大小写转换、去空格、分行等格式化处理",
        "keywords": ["转换", "格式化", "大小写", "去空格", "trim", "替换", "format"],
        "parameters": [
            {"key": "text", "label": "输入文本", "type": "textarea", "default": "Hello World! This is a Test.", "placeholder": "输入要处理的文本"},
            {"key": "transform_type", "label": "转换类型", "type": "select", "default": "upper", "options": [
                {"value":"upper","label":"全部大写"}, {"value":"lower","label":"全部小写"}, {"value":"title","label":"首字母大写"},
                {"value":"reverse","label":"反转文本"}, {"value":"trim","label":"去首尾空格"}, {"value":"lines","label":"按行拆分"},
                {"value":"no_space","label":"去所有空格"}
            ]},
        ],
        "code": """def main(input_data):
    text = input_data.get("text", "")
    ttype = input_data.get("transform_type", "upper")
    
    result = text
    if ttype == "upper": result = text.upper()
    elif ttype == "lower": result = text.lower()
    elif ttype == "title": result = text.title()
    elif ttype == "reverse": result = text[::-1]
    elif ttype == "trim": result = text.strip()
    elif ttype == "lines": result = text.splitlines()
    elif ttype == "no_space": result = text.replace(" ", "").replace("\\t", "")
    
    return {"original": text, "result": result, "transform": ttype, "length_changed": len(text) - len(str(result))}"""
    },
    {
        "id": "api_caller",
        "name": "API 调用器",
        "category": "api",
        "icon": "🌐",
        "description": "发送 HTTP 请求并处理返回数据，支持 GET 和 POST",
        "keywords": ["API", "接口", "请求", "HTTP", "GET", "POST", "调用", "数据获取", "爬虫"],
        "parameters": [
            {"key": "url", "label": "接口地址", "type": "text", "default": "", "placeholder": "https://api.example.com/data"},
            {"key": "method", "label": "请求方式", "type": "select", "default": "GET", "options": [{"value":"GET","label":"GET"}, {"value":"POST","label":"POST"}]},
            {"key": "headers", "label": "请求头 (JSON)", "type": "textarea", "default": "{}", "placeholder": '{"Authorization": "Bearer xxx"}', "optional": True},
            {"key": "body", "label": "请求体 (POST)", "type": "textarea", "default": "{}", "placeholder": '{"key": "value"}', "optional": True},
        ],
        "code": """def main(input_data):
    import json, urllib.request
    
    url = input_data.get("url", "")
    if not url: return {"error": "请提供 API 地址"}
    
    method = input_data.get("method", "GET")
    headers = input_data.get("headers", "{}")
    body = input_data.get("body", "{}")
    
    if isinstance(headers, str):
        try: headers = json.loads(headers)
        except: headers = {}
    if isinstance(body, str):
        try: body = json.loads(body)
        except: body = {}
    
    try:
        data = json.dumps(body).encode() if method == "POST" and body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode()
            try: content = json.loads(content)
            except: pass
            return {"status": resp.status, "data": content}
    except Exception as e:
        return {"error": str(e)}"""
    },
    {
        "id": "csv_json",
        "name": "CSV ↔ JSON 转换",
        "category": "data",
        "icon": "📊",
        "description": "在 CSV 和 JSON 格式之间互相转换",
        "keywords": ["CSV", "JSON", "转换", "表格", "数据格式", "导出", "导入"],
        "parameters": [
            {"key": "input_data_str", "label": "输入数据", "type": "textarea", "default": "name,age,city\n张三,28,北京\n李四,35,上海\n王五,22,广州", "placeholder": "CSV 或 JSON 格式"},
            {"key": "direction", "label": "转换方向", "type": "select", "default": "csv_to_json", "options": [
                {"value":"csv_to_json","label":"CSV → JSON"}, {"value":"json_to_csv","label":"JSON → CSV"}
            ]},
        ],
        "code": """def main(input_data):
    import json, csv, io
    
    data = input_data.get("input_data_str", "")
    direction = input_data.get("direction", "csv_to_json")
    
    if direction == "csv_to_json":
        reader = csv.DictReader(io.StringIO(data))
        rows = list(reader)
        return {"format": "JSON", "count": len(rows), "result": rows}
    else:
        try: rows = json.loads(data) if isinstance(data, str) else data
        except: return {"error": "JSON 格式错误"}
        if not rows: return {"error": "空数据"}
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return {"format": "CSV", "count": len(rows), "result": output.getvalue()}"""
    },
    {
        "id": "text_extract",
        "name": "信息提取器",
        "category": "text",
        "icon": "🔎",
        "description": "从文本中提取关键信息：邮箱、电话、网址、日期等",
        "keywords": ["提取", "抓取", "解析", "抽取", "邮箱", "电话", "网址", "日期", "信息"],
        "parameters": [
            {"key": "text", "label": "输入文本", "type": "textarea", "default": "请联系 support@example.com 或拨打 138-0000-0000，访问 https://example.com", "placeholder": "粘贴要提取信息的文本"},
            {"key": "extract_types", "label": "提取类型", "type": "multiselect", "default": ["email","phone","url"], "options": [
                {"value":"email","label":"邮箱地址"}, {"value":"phone","label":"电话号码"}, {"value":"url","label":"网址链接"},
                {"value":"date","label":"日期"}, {"value":"number","label":"数字"}
            ]},
        ],
        "code": """def main(input_data):
    import re
    
    text = input_data.get("text", "")
    types = input_data.get("extract_types", ["email", "phone", "url"])
    
    patterns = {
        "email": (r'[\\w.-]+@[\\w.-]+\\.\\w+', "邮箱地址"),
        "phone": (r'1[3-9]\\d{9}|\\d{3,4}-\\d{7,8}', "电话号码"),
        "url": (r'https?://[\\w./?#%&=-]+', "网址链接"),
        "date": (r'\\d{4}[-/年]\\d{1,2}[-/月]\\d{1,2}[日]?', "日期"),
        "number": (r'\\d+(\\.\\d+)?', "数字"),
    }
    
    results = {}
    for t in types:
        if t in patterns:
            pattern, label = patterns[t]
            found = re.findall(pattern, text)
            if found:
                results[t] = {"label": label, "matches": list(set(found)), "count": len(set(found))}
    
    return {
        "text_length": len(text),
        "extracted": results,
        "total_found": sum(v["count"] for v in results.values()),
    }"""
    },
    {
        "id": "sort_data",
        "name": "数据排序",
        "category": "data",
        "icon": "📋",
        "description": "对数据列表进行排序，支持正序/倒序",
        "keywords": ["排序", "排列", "顺序", "正序", "倒序", "sort", "order"],
        "parameters": [
            {"key": "items", "label": "数据列表", "type": "textarea", "default": "[5, 3, 8, 1, 9, 2, 7]", "placeholder": "JSON 数组"},
            {"key": "order", "label": "排序方式", "type": "select", "default": "asc", "options": [{"value":"asc","label":"正序（小→大）"}, {"value":"desc","label":"倒序（大→小）"}]},
        ],
        "code": """def main(input_data):
    import json
    
    items = input_data.get("items", [])
    if isinstance(items, str):
        try: items = json.loads(items)
        except: items = [items]
    
    order = input_data.get("order", "asc")
    
    try:
        sorted_items = sorted(items, reverse=(order == "desc"))
    except:
        sorted_items = sorted(items, key=str, reverse=(order == "desc"))
    
    return {"original": items, "sorted": sorted_items, "order": order, "count": len(items)}"""
    },
    {
        "id": "batch_process",
        "name": "批量处理",
        "category": "automation",
        "icon": "⚡",
        "description": "对列表中的每个元素执行统一操作，如加前缀、重复、截取等",
        "keywords": ["批量", "处理", "重复", "每个", "循环", "batch"],
        "parameters": [
            {"key": "items", "label": "数据列表", "type": "textarea", "default": "[\"a\", \"b\", \"c\", \"d\"]", "placeholder": "JSON 数组"},
            {"key": "action", "label": "操作类型", "type": "select", "default": "prefix", "options": [
                {"value":"prefix","label":"添加前缀"}, {"value":"suffix","label":"添加后缀"}, {"value":"repeat","label":"重复"},
                {"value":"truncate","label":"截取前N位"}, {"value":"upper_all","label":"转大写"}
            ]},
            {"key": "param", "label": "参数值", "type": "text", "default": "item_", "placeholder": "前缀/后缀/长度等参数"},
        ],
        "code": """def main(input_data):
    import json
    
    items = input_data.get("items", [])
    if isinstance(items, str):
        try: items = json.loads(items)
        except: return {"error": "数据格式错误"}
    
    action = input_data.get("action", "prefix")
    param = input_data.get("param", "")
    
    results = []
    for item in items:
        s = str(item)
        if action == "prefix": results.append(param + s)
        elif action == "suffix": results.append(s + param)
        elif action == "repeat": results.append(s * int(param) if param.isdigit() else s * 3)
        elif action == "truncate":
            n = int(param) if param.isdigit() else 3
            results.append(s[:n])
        elif action == "upper_all": results.append(s.upper())
    
    return {"original_count": len(items), "result_count": len(results), "results": results}"""
    },
    {
        "id": "hello",
        "name": "问候生成器",
        "category": "text",
        "icon": "👋",
        "description": "根据名字和场景生成个性化问候语",
        "keywords": ["问候", "你好", "欢迎", "打招呼", "greeting"],
        "parameters": [
            {"key": "name", "label": "名称/称呼", "type": "text", "default": "用户", "placeholder": "输入对方名称"},
            {"key": "style", "label": "风格", "type": "select", "default": "casual", "options": [
                {"value":"casual","label":"日常随意"}, {"value":"formal","label":"正式商务"}, {"value":"warm","label":"温暖亲切"}, {"value":"funny","label":"幽默风趣"}
            ]},
            {"key": "language", "label": "语言", "type": "select", "default": "zh", "options": [{"value":"zh","label":"中文"}, {"value":"en","label":"English"}]},
        ],
        "code": """def main(input_data):
    name = input_data.get("name", "用户")
    style = input_data.get("style", "casual")
    lang = input_data.get("language", "zh")
    
    templates = {
        "zh": {
            "casual": ["哈喽 {name}！今天过得怎么样？", "嘿 {name}，好久不见！", "你好呀，{name}~"],
            "formal": ["尊敬的 {name}，您好！", "{name} 先生/女士，非常荣幸与您联系。", "您好，{name}。祝您工作顺利！"],
            "warm": ["亲爱的 {name}，希望你今天心情棒棒的 ❤️", "{name}，一天的好心情从微笑开始 😊", "嗨 {name}，你是最棒的！加油 💪"],
            "funny": ["嘿 {name}！今天天气不错，适合摸鱼 🐟", "{name} 大侠驾到！", "叮！{name} 已上线 🛎️"],
        },
        "en": {
            "casual": ["Hey {name}! How's it going?", "Hi {name}, long time no see!", "What's up, {name}?"],
            "formal": ["Dear {name}, it's a pleasure to connect with you.", "Hello {name}, I hope this message finds you well."],
            "warm": ["Hi {name}, hope you're having a wonderful day! ❤️", "{name}, you're amazing! 💪"],
            "funny": ["Hey {name}! Coffee time! ☕", "{name} has entered the chat! 🎮"],
        }
    }
    
    lang_templates = templates.get(lang, templates["zh"])
    style_templates = lang_templates.get(style, lang_templates["casual"])
    
    import random
    greeting = random.choice(style_templates).format(name=name)
    
    return {"greeting": greeting, "style": style, "name": name}"""
    },
]

# ═══════════════════════════════════════════
# 自然语言匹配引擎
# ═══════════════════════════════════════════

def match_templates(query: str, top_k: int = 3) -> list[dict]:
    """
    根据用户自然语言描述，匹配最合适的模板
    使用分词 + 关键词权重匹配
    """
    if not query:
        return [t.copy() for t in TEMPLATES[:top_k]]
    
    query = query.lower()
    
    # 提取关键词
    # 中文分词支持（简单切词）
    words = set()
    # 单字扫描（中文）
    for t in re.split(r'[\s,，。！？、；：""''（）\(\)\[\]【】]+', query):
        if t: words.add(t)
    # 二元字符组（中文词组匹配）
    for i in range(len(query) - 1):
        bigram = query[i:i+2]
        if '\u4e00' <= bigram[0] <= '\u9fff':
            words.add(bigram)
    
    scored = []
    for t in TEMPLATES:
        score = 0
        matched_kws = []
        
        for kw in t["keywords"]:
            kw_lower = kw.lower()
            if kw_lower in query:
                score += 10  # 完整关键词匹配权重高
                matched_kws.append(kw)
            # 部分匹配
            for w in words:
                if len(w) >= 2 and (kw_lower in w or w in kw_lower):
                    score += 3
                    if w not in matched_kws: matched_kws.append(w)
        
        # 模板名称匹配
        if t["name"].lower() in query:
            score += 15
        
        # 描述匹配
        desc_lower = t["description"].lower()
        for w in words:
            if len(w) >= 2 and w in desc_lower:
                score += 2
        
        if score > 0:
            scored.append((score, t, matched_kws))
    
    # 按分数排序
    scored.sort(key=lambda x: x[0], reverse=True)
    
    if not scored:
        return [t.copy() for t in TEMPLATES[:top_k]]
    
    result = []
    for score, t, kws in scored[:top_k]:
        r = t.copy()
        r["match_score"] = score
        r["matched_keywords"] = kws
        result.append(r)
    
    return result


def generate_skill_from_description(description: str) -> Optional[dict]:
    """
    从自然语言描述生成完整的 Skill
    返回包含 name, description, category, code, parameters 的字典
    """
    matches = match_templates(description, top_k=1)
    if not matches:
        return None
    
    template = matches[0]
    return {
        "name": template["name"],
        "description": template["description"],
        "category": template["category"],
        "code": template["code"],
        "parameters": template["parameters"],
    }


# ═══════════════════════════════════════════
# 快速模板列表（供前端选择）
# ═══════════════════════════════════════════

def get_template_list():
    """获取精简的模板列表（给前端展示用）"""
    return [{
        "id": t["id"],
        "name": t["name"],
        "category": t["category"],
        "icon": t["icon"],
        "description": t["description"],
    } for t in TEMPLATES]


def get_template_detail(template_id: str) -> Optional[dict]:
    """获取模板完整信息"""
    for t in TEMPLATES:
        if t["id"] == template_id:
            return t
    return None
