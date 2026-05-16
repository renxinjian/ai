"""
AI Platform - 统一大系统
一个服务包含: API / MCP / Skill 编辑器 / 沙箱测试 / 数据库管理
"""

import json, sys, io, time, traceback, os
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
