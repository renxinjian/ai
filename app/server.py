from app.skill_pages import NEW_WIZARD_HTML, MARKET_INSTALLER_HTML
"""
AI Platform - 统一大系统
一个服务包含: API / MCP / Skill 编辑器 / 沙箱测试 / 数据库管理
"""

import json, sys, io, time, traceback, os
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional
from app.skill_engine import execute_skill, get_engine_input_schema, ENGINES, ENGINE_META, PRESET_SKILLS
from app.skill_templates import match_templates, generate_skill_from_description, get_template_list, get_template_detail

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from pymysql.cursors import DictCursor

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="AI Platform", version="3.0.0",
              description="AI 能力平台 - MCP / Skill IDE / 数据库管理 / 沙箱测试")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_CONFIG = {
    "host": "127.0.0.1", "port": 3306,
    "user": "app", "password": "NQ8azLqKGH9z4LqO",
    "database": "app", "charset": "utf8mb4",
}

def get_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)


# ═══════════════════════════════════════════════
# HTML 页面（内联模板）
# ═══════════════════════════════════════════════

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Platform</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;min-height:100vh}
.header{background:linear-gradient(135deg,#0a1628,#0f2b5b,#1a56d6);padding:48px 60px}
.header h1{font-size:40px;margin-bottom:6px}
.header .sub{color:#90b8f8;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:32px 60px}
.card{background:#0d1d3a;border:1px solid #1e3d70;border-radius:14px;padding:28px;transition:all .3s;cursor:pointer;text-decoration:none;color:#e0e8f0;display:block}
.card:hover{transform:translateY(-3px);border-color:#3b82f6;box-shadow:0 8px 30px rgba(26,86,214,.2)}
.card .icon{font-size:36px;margin-bottom:12px}
.card h3{font-size:18px;margin-bottom:6px}
.card p{color:#8098c0;font-size:13px;line-height:1.6}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:0 60px 32px}
.stat{background:#0d1d3a;border:1px solid #1e3d70;border-radius:10px;padding:20px}
.stat .num{font-size:28px;font-weight:700;color:#3b82f6}
.stat .lbl{color:#8098c0;font-size:12px;margin-top:4px}
.footer{text-align:center;padding:32px;color:#405880;font-size:12px}
.badge{padding:2px 10px;border-radius:12px;font-size:11px;background:#1a56d633;color:#60a5fa;display:inline-block;margin-top:8px}
</style>
</head>
<body>
<div class="header">
  <h1>🧠 AI Platform</h1>
  <div class="sub">MCP 服务 · Skill IDE · 沙箱测试 · 统一能力平台</div>
</div>
<div class="stats-row" id="statsRow">
  <div class="stat"><div class="num">-</div><div class="lbl">Skills</div></div>
  <div class="stat"><div class="num">-</div><div class="lbl">测试次数</div></div>
  <div class="stat"><div class="num">-</div><div class="lbl">通过率</div></div>
  <div class="stat"><div class="num">-</div><div class="lbl">MCP 工具</div></div>
</div>
<div class="grid">
  <a href="/editor" class="card"><div class="icon">✏️</div><h3>Skill 编辑器</h3><p>在线编写 Python 技能代码，语法高亮、一键保存、即时测试</p><span class="badge">CodeMirror</span></a>
  <a href="/playground" class="card"><div class="icon">🧪</div><h3>沙箱测试</h3><p>安全沙箱环境，任意代码运行验证，JSON 输入/输出，结果可视化</p><span class="badge">Sandbox</span></a>
  <a href="/docs" class="card"><div class="icon">📡</div><h3>API 文档</h3><p>RESTful API + MCP 协议接口，Swagger 交互式文档</p><span class="badge">FastAPI</span></a>
  <a href="/db" class="card"><div class="icon">🗄️</div><h3>数据库管理</h3><p>MySQL 表结构浏览、SQL 查询执行、数据统计看板</p><span class="badge">MySQL</span></a>
  <a href="/skills" class="card"><div class="icon">📦</div><h3>技能市场</h3><p>已发布的 Skills 列表，浏览、搜索、快速测试</p><span class="badge">Registry</span></a>
  <a href="http://101.34.214.120:3456" target="_blank" class="card"><div class="icon">🏪</div><h3>Skill Market</h3><p>全网 Skill 市场系统，ClawHub + SkillHub 双平台聚合</p><span class="badge">External</span></a>
</div>
<div class="footer">AI Platform v3.0 · 统一架构 · <span id="time"></span></div>
<script>
async function load(){try{
  const r=await fetch('/api/stats'),d=await r.json();
  if(d.total_skills!==undefined){
    const c=document.querySelectorAll('.stat .num');
    c[0].textContent=d.total_skills;c[1].textContent=d.total_tests;
    c[2].textContent=d.pass_rate+'%';c[3].textContent=d.mcp_tools||6;
  }
}catch(e){}
document.getElementById('time').textContent=new Date().toLocaleString('zh-CN');
}
load();
</script>
</body>
</html>"""

EDITOR_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill 编辑器 - AI Platform</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/theme/dracula.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/mode/python/python.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;height:100vh;display:flex;flex-direction:column}
.topbar{background:#0d1d3a;border-bottom:1px solid #1e3d70;padding:12px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.topbar a{color:#90b8f8;text-decoration:none;font-size:13px}
.topbar a:hover{color:#60a5fa}
.topbar .title{font-weight:700;font-size:16px;margin-right:16px}
.container{display:flex;flex:1;overflow:hidden}
.sidebar{width:280px;background:#0d1d3a;border-right:1px solid #1e3d70;padding:16px;overflow-y:auto;flex-shrink:0}
.sidebar h3{font-size:14px;margin-bottom:12px;color:#8098c0}
.skill-item{padding:10px 12px;border-radius:8px;cursor:pointer;margin-bottom:2px;font-size:13px;transition:all .2s}
.skill-item:hover{background:#122a55}
.skill-item.active{background:#1a56d6}
.main{flex:1;display:flex;flex-direction:column}
.toolbar{padding:12px 20px;background:#0d1d3a;border-bottom:1px solid #1e3d70;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.toolbar input,.toolbar select{background:#122a55;border:1px solid #1e3d70;color:#e0e8f0;padding:7px 12px;border-radius:6px;font-size:13px;outline:none}
.toolbar input:focus,.toolbar select:focus{border-color:#3b82f6}
.btn{padding:7px 18px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px;transition:all .2s}
.btn-primary{background:#1a56d6;color:#fff}.btn-primary:hover{background:#2563eb}
.btn-success{background:#059690;color:#fff}.btn-success:hover{background:#0dcea6}
.btn-outline{background:transparent;border:1px solid #1e3d70;color:#90a8c8}.btn-outline:hover{border-color:#3b82f6;color:#fff}
.CodeMirror{height:calc(100vh - 120px)!important;font-size:14px}
.panel{border-top:1px solid #1e3d70;background:#0d1d3a;overflow:hidden;transition:height .3s;height:0}
.panel.open{height:220px}
.panel .bar{display:flex;justify-content:space-between;padding:8px 16px;background:#122a55;font-size:12px}
.panel .body{padding:12px 16px;font-family:monospace;font-size:13px;white-space:pre-wrap;overflow-y:auto;height:155px;color:#b0c4e0}
</style>
</head>
<body>
<div class="topbar">
  <span class="title">✏️ Skill 编辑器</span>
  <a href="/">← 首页</a>
  <a href="/playground">🧪 沙箱</a>
  <a href="/docs">📡 API</a>
  <span style="flex:1"></span>
  <span id="saveStatus" style="font-size:12px;color:#8098c0"></span>
</div>
<div class="container">
  <div class="sidebar">
    <h3>📦 Skills</h3>
    <button class="btn btn-primary" onclick="newSkill()" style="width:100%;margin-bottom:12px">＋ 新建</button>
    <div id="skillList"></div>
  </div>
  <div class="main">
    <div class="toolbar">
      <input id="skillName" placeholder="Skill 名称" style="width:140px">
      <select id="skillCategory"><option value="custom">自定义</option><option value="data">数据处理</option><option value="api">API 调用</option><option value="ai">AI 能力</option><option value="automation">自动化</option></select>
      <select id="skillStatus"><option value="draft">草稿</option><option value="published">发布</option></select>
      <button class="btn btn-success" onclick="saveSkill()">💾 保存</button>
      <button class="btn btn-outline" onclick="runTest()">▶ 运行测试</button>
      <button class="btn btn-outline" onclick="deleteSkill()">🗑️ 删除</button>
    </div>
    <textarea id="codeEditor"># 定义 main(input_data) 函数作为入口\n\ndef main(input_data):\n    name = input_data.get("name", "World")\n    return {"message": f"你好, {name}!"}</textarea>
    <div class="panel" id="outputPanel">
      <div class="bar"><span id="testStatus">就绪</span><span id="testDuration"></span></div>
      <div class="body" id="testOutput"></div>
    </div>
  </div>
</div>
<script>
let currentId=null,editor=null;
function initEditor(){editor=CodeMirror.fromTextArea(document.getElementById('codeEditor'),{mode:'python',theme:'dracula',lineNumbers:true,indentUnit:4,tabSize:4})}
async function loadSkills(){const r=await fetch('/api/skills'),d=await r.json()
const list=document.getElementById('skillList')
list.innerHTML=d.skills.map(s=>'<div class="skill-item'+(s.id==currentId?' active':'')+'" onclick="loadSkill('+s.id+')"><b>'+s.name+'</b><br><small style="color:#8098c0">'+s.category+' · '+s.status+'</small></div>').join('')}
async function loadSkill(id){currentId=id;const r=await fetch('/api/skills/'+id),d=await r.json(),s=d.skill
document.getElementById('skillName').value=s.name
document.getElementById('skillCategory').value=s.category
document.getElementById('skillStatus').value=s.status
editor.setValue(s.code);loadSkills()}
function newSkill(){currentId=null
document.getElementById('skillName').value=''
document.getElementById('skillCategory').value='custom'
document.getElementById('skillStatus').value='draft'
editor.setValue('def main(input_data):\\n    return {"result": f"你好, {input_data.get(\\"name\\", \\"World\\")}!"}')
loadSkills();document.getElementById('saveStatus').textContent='新建中...'}
async function saveSkill(){const data={name:document.getElementById('skillName').value,description:'通过编辑器创建',category:document.getElementById('skillCategory').value,status:document.getElementById('skillStatus').value,code:editor.getValue()}
if(!data.name){alert('请输入名称');return}
document.getElementById('saveStatus').textContent='⏳ 保存中...'
if(currentId){await fetch('/api/skills/'+currentId,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
document.getElementById('saveStatus').textContent='✅ 已更新'}else{const r=await fetch('/api/skills',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const d=await r.json();currentId=d.id;document.getElementById('saveStatus').textContent='✅ 已创建'}
loadSkills()}
async function deleteSkill(){if(!currentId)return;if(!confirm('确定删除？'))return
await fetch('/api/skills/'+currentId,{method:'DELETE'});currentId=null;newSkill();document.getElementById('saveStatus').textContent='🗑️ 已删除'}
async function runTest(){const panel=document.getElementById('outputPanel');panel.classList.add('open')
document.getElementById('testStatus').textContent='⏳ 运行中...'
const input={name:'测试用户',value:42,items:[1,2,3]}
const r=await fetch('/api/test-run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:editor.getValue(),input_data:input})})
const result=await r.json()
document.getElementById('testStatus').textContent=result.status==='passed'?'✅ 通过':'❌ 失败'
document.getElementById('testDuration').textContent=result.duration_ms+'ms'
let out='📥 输入:\\n'+JSON.stringify(input,null,2)+'\\n\\n'
if(result.stdout)out+='📤 输出:\\n'+result.stdout+'\\n'
if(result.output!==undefined)out+='📦 返回:\\n'+JSON.stringify(result.output,null,2)+'\\n'
if(result.error)out+='❌ 错误:\\n'+result.error+'\\n'+result.traceback||''
document.getElementById('testOutput').textContent=out
if(currentId){await fetch('/api/skills/'+currentId+'/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({input_data:input,test_name:'编辑器测试'})})}}
const params=new URLSearchParams(location.search)
if(params.get('id'))currentId=parseInt(params.get('id'))
initEditor();loadSkills();if(currentId)loadSkill(currentId)
</script>
</body>
</html>"""

PLAYGROUND_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>沙箱测试 - AI Platform</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/theme/dracula.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/mode/python/python.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;height:100vh;display:flex;flex-direction:column}
.topbar{background:#0d1d3a;border-bottom:1px solid #1e3d70;padding:12px 24px;display:flex;align-items:center;gap:16px}
.topbar a{color:#90b8f8;text-decoration:none;font-size:13px}
.topbar .title{font-weight:700;font-size:16px}
.container{display:flex;flex:1;padding:12px;gap:12px}
.panel{background:#0d1d3a;border:1px solid #1e3d70;border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
.panel-left{flex:1.2}
.panel-right{flex:0.8}
.ph{padding:10px 14px;background:#122a55;font-weight:600;font-size:13px;display:flex;justify-content:space-between}
.CodeMirror{height:calc(100vh - 120px)!important}
.input-box{padding:10px;border-top:1px solid #1e3d70}
.input-box textarea{width:100%;background:#0a1628;border:1px solid #1e3d70;color:#e0e8f0;padding:8px;border-radius:6px;font-size:12px;min-height:80px;font-family:monospace;resize:vertical}
.ctrl{padding:10px 14px;display:flex;gap:10px;align-items:center}
.btn{padding:7px 18px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px;transition:all .2s}
.btn-success{background:#059690;color:#fff}.btn-success:hover{background:#0dcea6}
.btn-outline{background:transparent;border:1px solid #1e3d70;color:#90a8c8}.btn-outline:hover{border-color:#3b82f6;color:#fff}
.output-box{flex:1;padding:14px;font-family:monospace;font-size:13px;overflow-y:auto;white-space:pre-wrap;color:#b0c4e0}
select{background:#122a55;border:1px solid #1e3d70;color:#e0e8f0;padding:6px 10px;border-radius:6px;font-size:12px}
</style>
</head>
<body>
<div class="topbar">
  <span class="title">🧪 沙箱测试</span>
  <a href="/">← 首页</a>
  <a href="/editor">✏️ 编辑器</a>
  <a href="/docs">📡 API</a>
</div>
<div class="container">
  <div class="panel panel-left">
    <div class="ph"><span>📝 Python 代码</span>
      <select id="loadSelect" onchange="loadFromSkill()"><option value="">— 加载已有 Skill —</option></select>
    </div>
    <textarea id="codeInput"># 在沙箱中测试你的 Skill\n\ndef main(input_data):\n    text = input_data.get("text", "")\n    return {\n        "original": text,\n        "length": len(text),\n        "word_count": len(text.split()) if text else 0,\n        "reversed": text[::-1],\n    }</textarea>
  </div>
  <div class="panel panel-right">
    <div class="ph"><span>⚙️ 测试控制</span><span id="execStatus">就绪</span></div>
    <div class="input-box">
      <label style="font-size:11px;color:#8098c0;display:block;margin-bottom:4px">输入 (JSON):</label>
      <textarea id="inputJson">{"text": "Hello, this is a test for my AI Platform!"}</textarea>
    </div>
    <div class="ctrl">
      <button class="btn btn-success" onclick="run()">▶ 运行</button>
      <button class="btn btn-outline" onclick="clearOut()">清空</button>
    </div>
    <div class="output-box" id="outputBox">点击「运行」查看结果...</div>
  </div>
</div>
<script>
let codeEditor=null;
function init(){codeEditor=CodeMirror.fromTextArea(document.getElementById('codeInput'),{mode:'python',theme:'dracula',lineNumbers:true,indentUnit:4,tabSize:4})}
async function loadSelect(){const r=await fetch('/api/skills'),d=await r.json()
const sel=document.getElementById('loadSelect')
d.skills.forEach(s=>{const o=document.createElement('option');o.value=s.id;o.textContent=s.name;sel.appendChild(o)})}
async function loadFromSkill(){const id=document.getElementById('loadSelect').value;if(!id)return
const r=await fetch('/api/skills/'+id),d=await r.json();codeEditor.setValue(d.skill.code)
document.getElementById('inputJson').value='{"name":"test","value":42,"text":"Hello World!"}'}
async function run(){const out=document.getElementById('outputBox'),st=document.getElementById('execStatus')
st.textContent='⏳ 运行中...';out.textContent='执行中...\\n'
let inputData;try{inputData=JSON.parse(document.getElementById('inputJson').value)}catch(e){out.textContent='❌ JSON 错误: '+e.message;st.textContent='❌ 错误';return}
const r=await fetch('/api/test-run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:codeEditor.getValue(),input_data:inputData})})
const result=await r.json()
st.textContent=result.status==='passed'?'✅ 通过':'❌ 失败'
let o='📥 输入:\\n'+JSON.stringify(inputData,null,2)+'\\n\\n⏱ '+result.duration_ms+'ms\\n'
if(result.stdout)o+='\\n📤 stdout:\\n'+result.stdout
if(result.output!==undefined)o+='\\n📦 返回:\\n'+JSON.stringify(result.output,null,2)
if(result.error)o+='\\n\\n❌ '+result.error+(result.traceback?'\\n'+result.traceback:'')
out.textContent=o}
function clearOut(){document.getElementById('outputBox').textContent='就绪，等待测试...';document.getElementById('execStatus').textContent='就绪'}
init();loadSelect()
</script>
</body>
</html>"""

DB_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>数据库管理 - AI Platform</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;padding:32px 48px}
h1{font-size:28px;margin-bottom:8px}
.top a{color:#90b8f8;text-decoration:none;font-size:13px}
table{width:100%;border-collapse:collapse;margin-top:16px;font-size:13px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid #1e3d70}
th{background:#122a55;color:#8098c0;font-weight:600}
td{color:#e0e8f0}
tr:hover td{background:#0d1d3a}
.card{background:#0d1d3a;border:1px solid #1e3d70;border-radius:10px;padding:20px;margin-top:16px}
.sql-input{width:100%;background:#0a1628;border:1px solid #1e3d70;color:#e0e8f0;padding:10px;border-radius:6px;font-size:13px;font-family:monospace}
.btn{padding:8px 20px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px;background:#1a56d6;color:#fff;margin-top:8px}
.btn:hover{background:#2563eb}
pre{background:#0a1628;padding:16px;border-radius:8px;margin-top:12px;font-size:12px;overflow-x:auto;color:#b0c4e0}
</style>
</head>
<body>
<h1>🗄️ 数据库管理</h1>
<div class="top" style="margin-bottom:20px"><a href="/">← 首页</a> | <a href="/editor">编辑器</a> | <a href="/playground">沙箱</a></div>
<div class="card">
  <h3>📋 表结构</h3>
  <table id="tableInfo"><tr><td>加载中...</td></tr></table>
</div>
<div class="card">
  <h3>🔍 SQL 查询</h3>
  <textarea class="sql-input" id="sqlInput" rows="3">SELECT * FROM ai_skills ORDER BY category</textarea>
  <button class="btn" onclick="runQuery()">▶ 执行</button>
  <pre id="queryResult"></pre>
</div>
<script>
async function loadTables(){try{
  const r=await fetch('/api/db/tables'),d=await r.json()
  document.getElementById('tableInfo').innerHTML=d.tables.map(t=>'<tr><td>'+t.TABLE_NAME+'</td><td>'+t.ENGINE+'</td><td>'+t.TABLE_ROWS+' rows</td><td>'+t.SIZE_MB+' MB</td></tr>').join('')
}catch(e){}}
async function runQuery(){try{
  const sql=document.getElementById('sqlInput').value
  const r=await fetch('/api/db/query?sql='+encodeURIComponent(sql)),d=await r.json()
  document.getElementById('queryResult').textContent=JSON.stringify(d.rows||d,null,2).slice(0,5000)
}catch(e){document.getElementById('queryResult').textContent='错误: '+e}}
loadTables()
</script>
</body>
</html>"""

SKILLS_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>Skills 列表 - AI Platform</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;padding:32px 48px}
h1{font-size:28px;margin-bottom:4px}
.top{color:#8098c0;font-size:13px;margin-bottom:20px}
.top a{color:#90b8f8;text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:#0d1d3a;border:1px solid #1e3d70;border-radius:10px;padding:20px;transition:all .3s;cursor:pointer}
.card:hover{border-color:#3b82f6;transform:translateY(-2px)}
.card h3{font-size:16px;margin-bottom:4px}
.card .desc{color:#8098c0;font-size:12px;margin-bottom:10px}
.card .meta{display:flex;gap:12px;font-size:11px;color:#6080b0}
.badge{padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600}
.badge.published{background:#05969033;color:#0dcea6;border:1px solid #0dcea644}
.badge.draft{background:#d9770a33;color:#f59e0b;border:1px solid #f59e0b44}
</style>
</head>
<body>
<h1>📦 Skills 列表</h1>
<div class="top"><a href="/">← 首页</a> | <a href="/editor">✏️ 编辑器</a> | <a href="/playground">🧪 沙箱</a></div>
<div class="grid" id="skillGrid">加载中...</div>
<script>
async function load(){try{
  const r=await fetch('/api/skills'),d=await r.json()
  document.getElementById('skillGrid').innerHTML=d.skills.map(s=>
    '<div class="card" onclick="location.href=\'/editor?id='+s.id+'\'">'+
    '<h3>'+s.name+'</h3>'+
    '<div class="desc">'+(s.description||'暂无描述')+'</div>'+
    '<div class="meta">'+
    '<span>🏷️ '+s.category+'</span>'+
    '<span class="badge '+s.status+'">'+s.status+'</span>'+
    '<span>🧪 '+s.test_count+' 次</span>'+
    '<span>⏱ '+new Date(s.updated_at).toLocaleDateString('zh-CN')+'</span>'+
    '</div></div>'
  ).join('')
}catch(e){}}
load()
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════
# 路由: 页面
# ═══════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index(): return INDEX_HTML

@app.get("/editor", response_class=HTMLResponse)
async def editor(): return EDITOR_HTML

@app.get("/playground", response_class=HTMLResponse)
async def playground(): return PLAYGROUND_HTML

@app.get("/db", response_class=HTMLResponse)
async def db_page(): return DB_HTML

@app.get("/skills", response_class=HTMLResponse)
async def skills_page(): return SKILLS_HTML


# ═══════════════════════════════════════════════
# API: 系统状态
# ═══════════════════════════════════════════════

@app.get("/api/status")
async def status():
    return {"service": "AI Platform", "version": "3.0.0", "status": "running",
            "timestamp": datetime.now().isoformat()}

@app.get("/api/stats")
async def stats():
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS c FROM user_skills"); ts = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM skill_tests"); tt = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM skill_tests WHERE status='passed'"); tp = cursor.fetchone()["c"]
        return {"total_skills": ts, "total_tests": tt, "passed_tests": tp,
                "pass_rate": round(tp/tt*100,1) if tt>0 else 0, "mcp_tools": 6}
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# API: 数据库
# ═══════════════════════════════════════════════

@app.get("/api/db/tables")
async def db_tables():
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT TABLE_NAME, ENGINE, TABLE_ROWS, ROUND((DATA_LENGTH+INDEX_LENGTH)/1024/1024,2) AS SIZE_MB FROM information_schema.TABLES WHERE TABLE_SCHEMA='app' ORDER BY TABLE_NAME")
            return {"tables": cursor.fetchall()}
    finally:
        conn.close()

@app.get("/api/db/query")
async def db_query(sql: str = Query(...)):
    if not sql.strip().upper().startswith("SELECT"): raise HTTPException(400, "只允许 SELECT")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql); rows = cursor.fetchmany(500)
            cols = [d[0] for d in cursor.description] if cursor.description else []
        return {"columns": cols, "rows": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# API: Skills CRUD
# ═══════════════════════════════════════════════

@app.get("/api/skills")
async def list_skills():
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id,name,description,category,version,status,test_count,created_at,updated_at FROM user_skills ORDER BY updated_at DESC")
            return {"skills": cursor.fetchall()}
    finally:
        conn.close()

@app.get("/api/skills/{sid}")
async def get_skill(sid: int):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_skills WHERE id=%s", (sid,))
            skill = cursor.fetchone()
        if not skill: raise HTTPException(404, "不存在")
        return {"skill": skill}
    finally:
        conn.close()

@app.post("/api/skills")
async def create_skill(data: dict):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_skills (name,description,category,code,inputs_schema,outputs_schema) VALUES (%s,%s,%s,%s,%s,%s)",
                (data["name"], data.get("description",""), data.get("category","custom"),
                 data["code"], json.dumps(data.get("inputs_schema",{})), json.dumps(data.get("outputs_schema",{}))))
            conn.commit()
            return {"id": cursor.lastrowid, "message": "创建成功"}
    except pymysql.err.IntegrityError:
        raise HTTPException(400, "名称已存在")
    finally:
        conn.close()

@app.put("/api/skills/{sid}")
async def update_skill(sid: int, data: dict):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            fields, values = [], []
            for k in ["name","description","category","code","inputs_schema","outputs_schema","status"]:
                if k in data:
                    fields.append(f"{k}=%s")
                    values.append(json.dumps(data[k]) if k.endswith("schema") else data[k])
            values.append(sid)
            cursor.execute(f"UPDATE user_skills SET {','.join(fields)} WHERE id=%s", values)
            conn.commit()
        return {"message": "更新成功"}
    finally:
        conn.close()

@app.delete("/api/skills/{sid}")
async def delete_skill(sid: int):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM skill_tests WHERE skill_id=%s", (sid,))
            cursor.execute("DELETE FROM user_skills WHERE id=%s", (sid,))
            conn.commit()
        return {"message": "删除成功"}
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# API: 沙箱测试
# ═══════════════════════════════════════════════

BLOCKED = ["os.system", "subprocess", "shutil.rmtree", "open(", "__import__('os')"]

@app.post("/api/test-run")
async def test_run(data: dict):
    code = data.get("code", "")
    input_data = data.get("input_data", {})
    if not code.strip(): raise HTTPException(400, "代码为空")
    for b in BLOCKED:
        if b in code: return JSONResponse({"status":"error","error":f"安全限制: {b}","duration_ms":0})
    
    start = time.time()
    out_cap, err_cap = io.StringIO(), io.StringIO()
    result = {"status": "passed", "output": None, "error": None, "duration_ms": 0}
    try:
        compiled = compile(code, "<skill>", "exec")
        g = {"__builtins__": __builtins__, "input_data": input_data}
        with redirect_stdout(out_cap), redirect_stderr(err_cap):
            exec(compiled, g)
            if "main" in g and callable(g["main"]):
                result["output"] = g["main"](input_data)
            elif "execute" in g and callable(g["execute"]):
                result["output"] = g["execute"](input_data)
        s = out_cap.getvalue()
        if s: result["stdout"] = s
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()
    result["duration_ms"] = int((time.time()-start)*1000)
    return result

@app.post("/api/skills/{sid}/test")
async def test_skill(sid: int, data: dict = {}):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_skills WHERE id=%s", (sid,))
            skill = cursor.fetchone()
        if not skill: raise HTTPException(404, "技能不存在")
        
        input_data = data.get("input_data", {})
        result = await test_run({"code": skill["code"], "input_data": input_data})
        
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO skill_tests (skill_id,test_name,input_data,output_data,status,duration_ms,error_message) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (sid, data.get("test_name","manual"), json.dumps(input_data),
                 json.dumps(result.get("output")), result["status"], result["duration_ms"], result.get("error","")))
            cursor.execute("UPDATE user_skills SET test_count=test_count+1,last_test_at=NOW() WHERE id=%s", (sid,))
            conn.commit()
        return result
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# API: 测试记录
# ═══════════════════════════════════════════════

@app.get("/api/skills/{sid}/tests")
async def get_tests(sid: int, limit: int = 20):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM skill_tests WHERE skill_id=%s ORDER BY executed_at DESC LIMIT %s", (sid, limit))
            return {"tests": cursor.fetchall()}
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# MCP 工具模拟
# ═══════════════════════════════════════════════

@app.get("/api/mcp/tools")
async def mcp_tools():
    return {"tools": [
        {"name": "db_query", "description": "执行 SQL 查询"},
        {"name": "db_tables", "description": "列出数据库表"},
        {"name": "db_schema", "description": "查看表结构"},
        {"name": "calculator", "description": "数学计算"},
        {"name": "echo", "description": "回显测试"},
        {"name": "skill_test", "description": "测试技能运行"},
    ]}


# ═══════════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════════



# ═══════════════════════════════════════════════
# API: AI 辅助 & 模板系统
# ═══════════════════════════════════════════════

@app.get("/api/templates")
async def list_templates():
    """获取所有 Skill 模板（零代码使用）"""
    return {"templates": get_template_list(), "total": len(get_template_list())}

@app.get("/api/templates/{tid}")
async def template_detail(tid: str):
    """获取模板详情"""
    t = get_template_detail(tid)
    if not t:
        raise HTTPException(404, "模板不存在")
    return {"template": t}

@app.post("/api/skills/ai-generate")
async def ai_generate_skill(data: dict):
    """AI 根据自然语言描述生成 Skill"""
    description = data.get("description", "")
    if not description.strip():
        raise HTTPException(400, "请描述你想要的功能")
    
    # 使用模板匹配引擎
    matches = match_templates(description, top_k=3)
    
    # 如果已有同名 Skill，自动生成新名字
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            for t in matches:
                cursor.execute("SELECT COUNT(*) AS c FROM user_skills WHERE name=%s", (t["name"],))
                count = cursor.fetchone()["c"]
                if count > 0:
                    t["name"] = f"{t['name']}_{count+1}"
    finally:
        conn.close()
    
    return {"matches": matches, "total": len(matches)}

@app.post("/api/skills/from-template")
async def create_from_template(data: dict):
    """从模板创建 Skill（用户配置参数 → 生成完整 Skill 并保存）"""
    template_id = data.get("template_id", "")
    params = data.get("parameters", {})
    
    t = get_template_detail(template_id)
    if not t:
        raise HTTPException(404, "模板不存在")
    
    # 生成参数代码
    param_vars = "\n    ".join([f'{p["key"]} = input_data.get("{p["key"]}", {json.dumps(p.get("default", ""))})' for p in t["parameters"]])
    
    # 构建完整代码
    full_code = t["code"]
    
    # 保存到数据库
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 检查重名
            cursor.execute("SELECT COUNT(*) AS c FROM user_skills WHERE name=%s", (t["name"],))
            if cursor.fetchone()["c"] > 0:
                name = f"{t['name']}_{int(time.time())}"
            else:
                name = t["name"]
            
            cursor.execute(
                "INSERT INTO user_skills (name,description,category,code,inputs_schema,outputs_schema,status) VALUES (%s,%s,%s,%s,%s,%s,'published')",
                (name, t["description"], t["category"], full_code,
                 json.dumps(params), json.dumps({"result": "处理结果"})))
            conn.commit()
            return {"id": cursor.lastrowid, "name": name, "message": "创建成功"}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# 零代码页面
# ═══════════════════════════════════════════════

WIZARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Skill 工坊 - 零代码创建</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;min-height:100vh}
.topbar{background:#0d1d3a;border-bottom:1px solid #1e3d70;padding:14px 32px;display:flex;align-items:center;gap:20px}
.topbar .title{font-weight:700;font-size:18px}
.topbar a{color:#90b8f8;text-decoration:none;font-size:13px}
.topbar a:hover{color:#60a5fa}
.container{padding:32px;max-width:1200px;margin:0 auto}

/* 步骤指示器 */
.steps{display:flex;gap:8px;margin-bottom:32px}
.step{padding:10px 20px;border-radius:8px;font-size:13px;font-weight:600;background:#0d1d3a;border:1px solid #1e3d70;color:#8098c0;display:flex;align-items:center;gap:8px}
.step.active{background:#1a56d633;border-color:#3b82f6;color:#60a5fa}
.step.done{background:#05969033;border-color:#0dcea6;color:#0dcea6}

/* 输入区 */
.section{background:#0d1d3a;border:1px solid #1e3d70;border-radius:12px;padding:28px;margin-bottom:20px}
.section h2{font-size:20px;margin-bottom:4px}
.section .hint{color:#8098c0;font-size:13px;margin-bottom:20px}

/* 文本框 */
textarea, input[type="text"], select{width:100%;background:#0a1628;border:1px solid #1e3d70;color:#e0e8f0;padding:12px 16px;border-radius:8px;font-size:14px;outline:none;transition:border-color .3s}
textarea:focus, input:focus, select:focus{border-color:#3b82f6}
textarea{min-height:100px;resize:vertical;line-height:1.6}

/* 模板卡片 */
.tpl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:16px}
.tpl-card{background:#0a1628;border:1px solid #1e3d70;border-radius:10px;padding:16px;cursor:pointer;transition:all .3s}
.tpl-card:hover{border-color:#3b82f6;transform:translateY(-2px)}
.tpl-card.selected{border-color:#3b82f6;background:#1a56d622}
.tpl-card .icon{font-size:28px;margin-bottom:6px}
.tpl-card .name{font-size:14px;font-weight:600;margin-bottom:4px}
.tpl-card .desc{font-size:11px;color:#8098c0}

/* 参数表单 */
.param-group{margin-bottom:16px}
.param-group label{display:block;font-size:13px;font-weight:600;margin-bottom:6px;color:#b0c4e0}
.param-group .optional{color:#8098c0;font-size:11px;font-weight:400}
.param-group .help{color:#6080b0;font-size:11px;margin-top:4px}
select{appearance:auto;padding:10px 14px;font-size:13px}
.param-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}

/* 结果 */
.result-box{background:#0a1628;border:1px solid #1e3d70;border-radius:8px;padding:16px;font-family:monospace;font-size:13px;white-space:pre-wrap;min-height:60px;color:#b0c4e0;margin-top:12px}

/* 匹配结果 */
.match-item{background:#0a1628;border:1px solid #1e3d70;border-radius:8px;padding:16px;margin-bottom:8px;cursor:pointer;transition:all .3s}
.match-item:hover{border-color:#3b82f6}
.match-item .name{font-size:15px;font-weight:600}
.match-item .desc{color:#8098c0;font-size:12px;margin-top:2px}
.match-item .score{color:#059690;font-size:11px}

.btn{padding:10px 28px;border:none;border-radius:8px;cursor:pointer;font-weight:600;font-size:14px;transition:all .3s;display:inline-flex;align-items:center;gap:8px}
.btn-primary{background:linear-gradient(135deg,#1a56d6,#3b82f6);color:#fff}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(26,86,214,.3)}
.btn-success{background:linear-gradient(135deg,#059690,#0dcea6);color:#fff}
.btn-success:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(5,150,144,.3)}
.btn-outline{background:transparent;border:1px solid #1e3d70;color:#90a8c8}
.btn-outline:hover{border-color:#3b82f6;color:#fff}
.btn:disabled{opacity:.4;cursor:not-allowed;transform:none!important}

.toast{position:fixed;top:24px;right:24px;padding:14px 24px;border-radius:8px;font-size:14px;font-weight:600;z-index:999;animation:slideIn .3s}
.toast.success{background:#059690;color:#fff}
.toast.error{background:#dc3545;color:#fff}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}

.badge{padding:3px 10px;border-radius:12px;font-size:11px;background:#1a56d633;color:#60a5fa;display:inline-block}

/* 加载动画 */
.spinner{display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,.3);border-radius:50%;border-top-color:#fff;animation:spin .6s linear infinite;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}

.hidden{display:none!important}
</style>
</head>
<body>
<div class="topbar">
  <span class="title">🧠 AI Skill 工坊</span>
  <a href="/">← 首页</a>
  <span style="flex:1"></span>
  <span style="font-size:12px;color:#8098c0">三步创建 · 无需编程</span>
</div>
<div class="container">
  <!-- 步骤 -->
  <div class="steps">
    <div class="step active" id="step1Ind">① 描述需求</div>
    <div class="step" id="step2Ind">② 确认模板</div>
    <div class="step" id="step3Ind">③ 配置 & 测试</div>
  </div>

  <!-- 步骤1: 描述需求 -->
  <div class="section" id="step1">
    <h2>🎯 你想要什么功能？</h2>
    <div class="hint">用一句话描述你想做的事情，AI 会自动匹配最合适的模板</div>
    <textarea id="descInput" placeholder="例如：&#10;• 对一段文本生成摘要&#10;• 把 Excel 数据从 CSV 转成 JSON&#10;• 从文章中提取所有邮箱和电话&#10;• 给一组数字计算总和和平均值&#10;• 根据用户名字生成问候语" rows="4"></textarea>
    <div style="margin-top:12px;display:flex;gap:8px">
      <button class="btn btn-primary" onclick="aiMatch()">🤖 AI 匹配模板</button>
      <button class="btn btn-outline" onclick="showAllTemplates()">📋 浏览全部模板</button>
    </div>
    <div id="aiLoading" class="hidden" style="margin-top:16px;color:#8098c0"><span class="spinner"></span> 正在匹配...</div>
    <div id="aiResults" class="hidden" style="margin-top:16px">
      <h3 style="font-size:15px;margin-bottom:12px">🤖 推荐模板</h3>
      <div id="matchList"></div>
    </div>
    <div id="allTemplates" class="hidden" style="margin-top:16px">
      <h3 style="font-size:15px;margin-bottom:12px">📋 全部模板</h3>
      <div class="tpl-grid" id="tplGrid"></div>
    </div>
  </div>

  <!-- 步骤2: 确认模板 -->
  <div class="section hidden" id="step2">
    <h2>✅ 确认模板</h2>
    <div class="hint">我们已为你匹配到以下模板，确认或换一个</div>
    <div id="selectedTemplate"></div>
    <div style="margin-top:16px;display:flex;gap:8px">
      <button class="btn btn-success" onclick="goStep3()">确认，下一步 →</button>
      <button class="btn btn-outline" onclick="goStep1()">← 重新描述</button>
    </div>
  </div>

  <!-- 步骤3: 配置 & 测试 -->
  <div class="section hidden" id="step3">
    <h2>⚙️ 配置参数</h2>
    <div class="hint">调整参数后直接测试效果</div>
    <div id="paramForm"></div>
    <div style="margin-top:20px;display:flex;gap:8px;align-items:center">
      <button class="btn btn-success" onclick="testSkill()">▶ 立即测试</button>
      <button class="btn btn-primary" onclick="saveSkill()">💾 保存为 Skill</button>
      <span id="testStatus" style="font-size:13px;color:#8098c0"></span>
    </div>
    <div id="testResult" class="hidden result-box" style="margin-top:16px"></div>
    <div style="margin-top:12px;display:flex;gap:8px">
      <button class="btn btn-outline" onclick="goStep2()">← 返回选模板</button>
    </div>
  </div>
</div>

<script>
let selectedTemplate = null;
let selectedParams = {};

// ── 步骤控制 ──
function showStep(n) {
  document.getElementById('step1').classList.toggle('hidden', n!==1);
  document.getElementById('step2').classList.toggle('hidden', n!==2);
  document.getElementById('step3').classList.toggle('hidden', n!==3);
  for(let i=1;i<=3;i++){
    const el = document.getElementById('step'+i+'Ind');
    el.classList.toggle('active', i===n);
    el.classList.toggle('done', i<n);
  }
}

function goStep1(){showStep(1)}
function goStep2(){showStep(2)}
function goStep3(){renderParamForm();showStep(3)}

// ── AI 匹配 ──
async function aiMatch(){
  const desc = document.getElementById('descInput').value.trim();
  if(!desc){showToast('请先描述你想要的功能','error');return}
  
  document.getElementById('aiLoading').classList.remove('hidden');
  document.getElementById('aiResults').classList.add('hidden');
  document.getElementById('allTemplates').classList.add('hidden');
  
  try{
    const r = await fetch('/api/skills/ai-generate',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({description: desc})
    });
    const d = await r.json();
    
    document.getElementById('aiLoading').classList.add('hidden');
    
    if(d.matches && d.matches.length){
      document.getElementById('aiResults').classList.remove('hidden');
      document.getElementById('matchList').innerHTML = d.matches.map((m,i)=>`
        <div class="match-item" onclick="selectMatch(${i})">
          <div class="name">${m.icon||'🧩'} ${m.name}</div>
          <div class="desc">${m.description}</div>
          <div class="score">匹配度: ${m.match_score||'N/A'} · 分类: ${m.category||'通用'}</div>
        </div>
      `).join('');
      // 默认选中第一个
      selectMatch(0);
    }
  }catch(e){showToast('请求失败: '+e.message,'error');document.getElementById('aiLoading').classList.add('hidden')}
}

// ── 全模板浏览 ──
async function showAllTemplates(){
  document.getElementById('allTemplates').classList.toggle('hidden');
  if(!document.getElementById('allTemplates').classList.contains('hidden')){
    const r = await fetch('/api/templates');
    const d = await r.json();
    document.getElementById('tplGrid').innerHTML = d.templates.map(t=>`
      <div class="tpl-card" onclick="selectTemplateFromView('${t.id}')">
        <div class="icon">${t.icon||'🧩'}</div>
        <div class="name">${t.name}</div>
        <div class="desc">${t.description}</div>
      </div>
    `).join('');
  }
}

// ── 选择模板 ──
async function selectMatch(index){
  const r = await fetch('/api/skills/ai-generate',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({description: document.getElementById('descInput').value.trim()})
  });
  const d = await r.json();
  if(!d.matches || !d.matches[index]) return;
  
  const t = d.matches[index];
  
  // 获取完整模板
  const r2 = await fetch('/api/templates');
  const d2 = await r2.json();
  const full = d2.templates.find(tm => tm.id === t.id) || d2.templates[0];
  
  // 获取详情
  const r3 = await fetch('/api/templates/'+full.id);
  const d3 = await r3.json();
  
  selectedTemplate = d3.template;
  renderSelectedTemplate(d3.template);
}

async function selectTemplateFromView(tid){
  const r = await fetch('/api/templates/'+tid);
  const d = await r.json();
  selectedTemplate = d.template;
  renderSelectedTemplate(d.template);
}

function renderSelectedTemplate(t){
  document.getElementById('selectedTemplate').innerHTML = `
    <div style="background:#0a1628;border:1px solid #1e3d70;border-radius:10px;padding:20px">
      <div style="font-size:36px;margin-bottom:8px">${t.icon||'🧩'}</div>
      <h3 style="font-size:18px;margin-bottom:4px">${t.name}</h3>
      <p style="color:#8098c0;font-size:13px">${t.description}</p>
      <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
        <span class="badge">${t.category||'通用'}</span>
        ${(t.keywords||[]).slice(0,4).map(k=>'<span class="badge" style="background:#05969033;color:#0dcea6">'+k+'</span>').join('')}
      </div>
    </div>
  `;
  showStep(2);
}

// ── 参数配置 ──
function renderParamForm(){
  if(!selectedTemplate) return;
  const params = selectedTemplate.parameters || [];
  
  document.getElementById('paramForm').innerHTML = params.map((p,idx)=>{
    const id = 'param_'+p.key;
    let html = '<div class="param-group"><label>'+(p.optional?'':'* ')+p.label+(p.optional?' <span class="optional">(可选)</span>':'')+'</label>';
    
    if(p.type === 'textarea'){
      html += '<textarea id="'+id+'" placeholder="'+(p.placeholder||'')+'" rows="3">'+(p.default||'')+'</textarea>';
    } else if(p.type === 'text'){
      html += '<input type="text" id="'+id+'" placeholder="'+(p.placeholder||'')+'" value="'+(p.default||'')+'">';
    } else if(p.type === 'number'){
      html += '<input type="number" id="'+id+'" value="'+(p.default||'')+'" placeholder="'+(p.placeholder||'')+'">';
    } else if(p.type === 'select'){
      html += '<select id="'+id+'">';
      (p.options||[]).forEach(o => {
        html += '<option value="'+o.value+'"'+(o.value===p.default?' selected':'')+'>'+o.label+'</option>';
      });
      html += '</select>';
    } else if(p.type === 'multiselect'){
      html += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">';
      (p.options||[]).forEach(o => {
        const checked = (p.default||[]).includes(o.value);
        html += '<label style="display:flex;align-items:center;gap:6px;background:#0a1628;border:1px solid '+(checked?'#3b82f6':'#1e3d70')+';border-radius:6px;padding:6px 12px;cursor:pointer;font-size:12px">'+
          '<input type="checkbox" value="'+o.value+'" '+(checked?'checked':'')+' style="accent-color:#3b82f6" onchange="this.parentElement.style.borderColor=this.checked?'+"'"+'#3b82f6'+"'"+':'+"'"+'#1e3d70'+"'"+'"> '+o.label+'</label>';
      });
      html += '</div>';
    }
    
    if(p.placeholder) html += '<div class="help">例: '+p.placeholder+'</div>';
    html += '</div>';
    return html;
  }).join('');
}

// ── 测试 ──
async function testSkill(){
  if(!selectedTemplate) return;
  
  const inputData = {};
  (selectedTemplate.parameters||[]).forEach(p => {
    const el = document.getElementById('param_'+p.key);
    if(!el) return;
    if(p.type === 'multiselect'){
      inputData[p.key] = Array.from(el.querySelectorAll('input:checked')).map(cb => cb.value);
    } else if(p.type === 'number'){
      inputData[p.key] = parseFloat(el.value) || 0;
    } else if(p.type === 'textarea' || p.type === 'text'){
      inputData[p.key] = el.value;
    } else {
      inputData[p.key] = el.value;
    }
  });
  
  document.getElementById('testStatus').textContent = '⏳ 测试中...';
  document.getElementById('testResult').classList.add('hidden');
  
  try{
    const r = await fetch('/api/test-run',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({code: selectedTemplate.code, input_data: inputData})
    });
    const result = await r.json();
    
    document.getElementById('testResult').classList.remove('hidden');
    
    let out = '';
    if(result.status === 'passed'){
      out += '✅ 测试通过 ('+result.duration_ms+'ms)\\n\\n';
      if(result.output !== undefined){
        out += '📦 输出结果:\\n'+JSON.stringify(result.output, null, 2);
      }
    } else {
      out += '❌ 测试失败 ('+result.duration_ms+'ms)\\n';
      if(result.error) out += '\\n错误: '+result.error;
    }
    document.getElementById('testResult').textContent = out;
    document.getElementById('testStatus').textContent = '✅ 测试完成';
  } catch(e){
    document.getElementById('testResult').classList.remove('hidden');
    document.getElementById('testResult').textContent = '❌ 请求失败: '+e.message;
    document.getElementById('testStatus').textContent = '❌ 错误';
  }
}

// ── 保存 ──
async function saveSkill(){
  if(!selectedTemplate) return;
  
  const params = {};
  (selectedTemplate.parameters||[]).forEach(p => {
    const el = document.getElementById('param_'+p.key);
    if(!el) return;
    params[p.key] = el.value;
  });
  
  document.getElementById('testStatus').textContent = '⏳ 保存中...';
  
  try{
    const r = await fetch('/api/skills/from-template',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({template_id: selectedTemplate.id, parameters: params})
    });
    const d = await r.json();
    showToast('✅ Skill "'+d.name+'" 创建成功！','success');
    document.getElementById('testStatus').textContent = '✅ 已保存';
  } catch(e){
    showToast('❌ 保存失败: '+e.message,'error');
    document.getElementById('testStatus').textContent = '❌ 保存失败';
  }
}

// ── 提示消息 ──
function showToast(msg, type){
  const t = document.createElement('div');
  t.className = 'toast '+type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(()=>t.remove(), 3000);
}
</script>
</body>
</html>"""

@app.get("/wizard", response_class=HTMLResponse)
async def skill_wizard():
    return WIZARD_HTML



# ═══════════════════════════════════════════════
# API: 引擎执行 (声明式 .skill 模式)
# ═══════════════════════════════════════════════

@app.get("/api/engines")
async def list_engines():
    """列出所有可用引擎"""
    return {"engines": ENGINE_META, "total": len(ENGINE_META)}


@app.get("/api/engines/{ename}")
async def engine_detail(ename: str):
    """获取引擎详情（含参数定义）"""
    if ename not in ENGINES:
        raise HTTPException(404, "引擎不存在")
    inputs = get_engine_input_schema(ename)
    return {"engine": ename, "meta": ENGINE_META.get(ename, {}), "inputs": inputs}


@app.post("/api/skills/execute")
async def execute_skill_api(data: dict):
    """执行一个完整的 .skill 定义"""
    skill_def = data.get("skill", {})
    input_data = data.get("input_data", {})
    if not skill_def.get("engine"):
        raise HTTPException(400, "缺少 engine 字段")
    result = execute_skill(skill_def, input_data)
    return result


@app.get("/api/preset-skills")
async def list_preset_skills():
    """获取预设 .skill 列表（可直接下载安装）"""
    return {"skills": PRESET_SKILLS, "total": len(PRESET_SKILLS)}


@app.get("/api/preset-skills/{sid}")
async def get_preset_skill(sid: str):
    """获取单个预设 .skill（返回 .skill 格式）"""
    for s in PRESET_SKILLS:
        if s["id"] == sid:
            return {"skill": s}
    raise HTTPException(404, "不存在")


@app.get("/api/skills/{sid}/download")
async def download_skill(sid: int):
    """从数据库下载 Skill 为 .skill 文件"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_skills WHERE id=%s", (sid,))
            skill = cursor.fetchone()
        if not skill: raise HTTPException(404, "不存在")
        # 转换为 .skill 格式
        skill_file = {
            "id": str(skill["id"]),
            "name": skill["name"],
            "description": skill["description"],
            "engine": "calculator",
            "version": skill["version"],
            "category": skill["category"],
            "config": {},
            "inputs": [{"key": "input", "label": "输入", "type": "textarea"}],
            "outputs": [{"key": "output", "label": "结果", "type": "json"}],
        }
        return JSONResponse(content=skill_file, headers={"Content-Disposition": f"attachment; filename={skill['name']}.skill"})
    finally:
        conn.close()


@app.get("/wizard", response_class=HTMLResponse)
async def new_wizard():
    return NEW_WIZARD_HTML


@app.get("/market-installer", response_class=HTMLResponse)
async def market_installer():
    return MARKET_INSTALLER_HTML

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")