"""零代码前端页面 — 引擎模式，用户不用写代码"""

NEW_WIZARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 技能工坊 - 零代码</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;min-height:100vh}
.topbar{background:#0d1d3a;border-bottom:1px solid #1e3d70;padding:14px 32px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.topbar .title{font-weight:700;font-size:18px}
.topbar a{color:#90b8f8;text-decoration:none;font-size:13px}
.topbar a:hover{color:#60a5fa}
.container{padding:32px;max-width:1200px;margin:0 auto}
h2{font-size:18px;margin-bottom:4px}.hint{color:#8098c0;font-size:13px;margin-bottom:20px}

.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-bottom:24px}
.card{background:#0d1d3a;border:1px solid #1e3d70;border-radius:12px;padding:20px;cursor:pointer;transition:all .3s;text-decoration:none;color:#e0e8f0}
.card:hover{border-color:#3b82f6;transform:translateY(-2px);box-shadow:0 4px 20px rgba(26,86,214,.2)}
.card .icon{font-size:36px;margin-bottom:8px}
.card .name{font-size:15px;font-weight:600;margin-bottom:4px}
.card .desc{font-size:11px;color:#8098c0}
.card .tag{display:inline-block;padding:2px 8px;border-radius:4px;background:#1a56d633;color:#60a5fa;font-size:10px;margin-top:6px}

.steps{display:flex;gap:8px;margin-bottom:24px}
.step{padding:8px 16px;border-radius:6px;font-size:12px;font-weight:600;background:#0d1d3a;border:1px solid #1e3d70;color:#8098c0}
.step.active{background:#1a56d633;border-color:#3b82f6;color:#60a5fa}
.step.done{background:#05969033;border-color:#0dcea6;color:#0dcea6}

.section{background:#0d1d3a;border:1px solid #1e3d70;border-radius:12px;padding:28px;margin-bottom:20px}
.param-group{margin-bottom:16px}
.param-group label{display:block;font-size:13px;font-weight:600;margin-bottom:6px;color:#b0c4e0}
textarea,input[type="text"]{width:100%;background:#0a1628;border:1px solid #1e3d70;color:#e0e8f0;padding:10px 14px;border-radius:6px;font-size:13px;outline:none}
textarea:focus,input:focus{border-color:#3b82f6}
textarea{min-height:80px;resize:vertical}
select{background:#0a1628;border:1px solid #1e3d70;color:#e0e8f0;padding:8px 12px;border-radius:6px;font-size:13px;width:100%}
.checkbox-group{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.checkbox-group label{display:flex;align-items:center;gap:6px;background:#0a1628;border:1px solid #1e3d70;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:12px;font-weight:400}
.checkbox-group input:checked+span{color:#60a5fa}

.btn{padding:10px 24px;border:none;border-radius:8px;cursor:pointer;font-weight:600;font-size:14px;transition:all .3s;display:inline-flex;align-items:center;gap:8px}
.btn-primary{background:linear-gradient(135deg,#1a56d6,#3b82f6);color:#fff}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(26,86,214,.3)}
.btn-success{background:linear-gradient(135deg,#059690,#0dcea6);color:#fff}
.btn-success:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(5,150,144,.3)}
.btn-outline{background:transparent;border:1px solid #1e3d70;color:#90a8c8}
.btn-outline:hover{border-color:#3b82f6;color:#fff}

.result-box{background:#0a1628;border:1px solid #1e3d70;border-radius:8px;padding:16px;font-family:monospace;font-size:13px;white-space:pre-wrap;min-height:60px;color:#b0c4e0;margin-top:12px;max-height:300px;overflow:auto}

.toast{position:fixed;top:24px;right:24px;padding:14px 24px;border-radius:8px;font-size:14px;font-weight:600;z-index:999;animation:slideIn .3s}
.toast.success{background:#059690;color:#fff}
.toast.error{background:#dc3545;color:#fff}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}

.hidden{display:none!important}
.badge{padding:2px 10px;border-radius:12px;font-size:11px;background:#1a56d633;color:#60a5fa;display:inline-block}
.code-block{background:#0a1628;border:1px solid #2a2a4a;border-radius:6px;padding:10px 14px;font-family:monospace;font-size:12px;white-space:pre-wrap;color:#b0c4e0;margin-top:8px;max-height:200px;overflow:auto}
</style>
</head>
<body>
<div class="topbar">
  <span class="title">🧩 AI 技能工坊</span>
  <a href="/">← 首页</a>
  <a href="/playground">沙箱</a>
  <a href="/market-installer" style="background:#05969033;padding:6px 14px;border-radius:20px">🏪 安装 Market 技能</a>
  <span style="flex:1"></span>
  <span style="font-size:12px;color:#8098c0">无需编程 · 即装即用</span>
</div>
<div class="container">
  <!-- 步骤指示器 -->
  <div class="steps">
    <div class="step active" id="s1">① 选技能</div>
    <div class="step" id="s2">② 填参数</div>
    <div class="step" id="s3">③ 看结果</div>
  </div>

  <!-- 步骤1: 选择技能 -->
  <div class="section" id="step1">
    <h2>🎯 选择你要用的技能</h2>
    <div class="hint">点一下就能用，不需要写任何代码</div>
    <div class="card-grid" id="skillGrid"></div>
  </div>

  <!-- 步骤2: 配置参数 -->
  <div class="section hidden" id="step2">
    <h2>⚙️ 配置参数</h2>
    <div class="hint">填写或选择参数后，一键执行</div>
    <div id="paramForm"></div>
    <div style="margin-top:20px;display:flex;gap:10px;flex-wrap:wrap">
      <button class="btn btn-success" onclick="runSkill()">▶ 立即执行</button>
      <button class="btn btn-outline" onclick="saveAsSkill()">💾 保存到我的技能</button>
      <button class="btn btn-outline" onclick="downloadSkill()">⬇️ 下载 .skill 文件</button>
      <button class="btn btn-outline" onclick="showStep(1)">← 换一个</button>
    </div>
    <div id="runStatus" style="margin-top:12px;font-size:13px;color:#8098c0"></div>
  </div>

  <!-- 步骤3: 结果 -->
  <div class="section hidden" id="step3">
    <h2>📊 执行结果</h2>
    <div class="result-box" id="resultBox"></div>
    <div style="margin-top:16px;display:flex;gap:10px">
      <button class="btn btn-primary" onclick="showStep(2)">← 重新配置</button>
      <button class="btn btn-outline" onclick="showStep(1)">🔄 换一个技能</button>
    </div>
  </div>

  <!-- 当前技能信息 -->
  <div id="skillInfo" class="hidden" style="margin-bottom:16px;display:flex;align-items:center;gap:12px;padding:12px 20px;background:#0d1d3a;border:1px solid #1e3d70;border-radius:8px">
    <span id="skillIcon" style="font-size:28px"></span>
    <div><b id="skillName"></b><br><span id="skillDesc" style="font-size:12px;color:#8098c0"></span></div>
  </div>
</div>

<script>
let currentSkill = null;

// ── 加载预设技能列表 ──
async function loadSkills(){
  try{
    const r = await fetch('/api/preset-skills');
    const d = await r.json();
    const grid = document.getElementById('skillGrid');
    grid.innerHTML = d.skills.map(s => 
      `<div class="card" onclick="selectSkill('${s.id}')">
        <div class="icon">${s.icon||'🧩'}</div>
        <div class="name">${s.name}</div>
        <div class="desc">${s.description}</div>
        <div class="tag">${s.engine} · v${s.version||'1.0'}</div>
      </div>`
    ).join('');
  }catch(e){document.getElementById('skillGrid').innerHTML='<div style="color:#8098c0">加载失败</div>'}
}

// ── 选择技能 ──
async function selectSkill(sid){
  try{
    const r = await fetch('/api/preset-skills/'+sid);
    const d = await r.json();
    currentSkill = d.skill;
    
    document.getElementById('skillIcon').textContent = currentSkill.icon||'🧩';
    document.getElementById('skillName').textContent = currentSkill.name;
    document.getElementById('skillDesc').textContent = currentSkill.description;
    document.getElementById('skillInfo').classList.remove('hidden');
    
    renderParams();
    showStep(2);
  }catch(e){showToast('加载失败','error')}
}

// ── 渲染参数表单 ──
function renderParams(){
  if(!currentSkill) return;
  const inputs = currentSkill.inputs || [];
  
  document.getElementById('paramForm').innerHTML = inputs.map(p => {
    const id = 'param_'+p.key;
    let html = '<div class="param-group"><label>'+p.label+'</label>';
    
    if(p.type === 'textarea'){
      html += '<textarea id="'+id+'" placeholder="'+(p.placeholder||'')+'">'+(p.default||'')+'</textarea>';
    } else if(p.type === 'text'){
      html += '<input type="text" id="'+id+'" value="'+(p.default||'')+'" placeholder="'+(p.placeholder||'')+'">';
    } else if(p.type === 'number'){
      html += '<input type="text" id="'+id+'" value="'+(p.default||'')+'" placeholder="'+(p.placeholder||'')+'">';
    } else if(p.type === 'select'){
      html += '<select id="'+id+'">';
      (p.options||[]).forEach(o => {
        html += '<option value="'+o.value+'"'+(o.value===p.default?' selected':'')+'>'+o.label+'</option>';
      });
      html += '</select>';
    } else if(p.type === 'multiselect'){
      html += '<div class="checkbox-group">';
      (p.options||[]).forEach(o => {
        const checked = (p.default||[]).includes(o.value);
        html += '<label style="border-color:'+(checked?'#3b82f6':'#1e3d70')+'">'+
          '<input type="checkbox" value="'+o.value+'" '+(checked?'checked':'')+' style="accent-color:#3b82f6">'+
          '<span>'+o.label+'</span></label>';
      });
      html += '</div>';
    }
    html += '</div>';
    return html;
  }).join('');
}

// ── 执行技能 ──
async function runSkill(){
  if(!currentSkill) return;
  
  document.getElementById('runStatus').textContent = '⏳ 执行中...';
  
  // 收集参数
  const inputData = {};
  (currentSkill.inputs||[]).forEach(p => {
    const el = document.getElementById('param_'+p.key);
    if(!el) return;
    if(p.type === 'multiselect'){
      inputData[p.key] = Array.from(el.querySelectorAll('input:checked')).map(cb => cb.value);
    } else {
      inputData[p.key] = el.value;
    }
  });
  
  try{
    const r = await fetch('/api/skills/execute', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({skill: currentSkill, input_data: inputData})
    });
    const result = await r.json();
    
    showStep(3);
    const box = document.getElementById('resultBox');
    
    if(result.status === 'passed'){
      let out = '✅ 执行成功 ('+result.engine+' 引擎)\\n\\n';
      if(result.output){
        out += JSON.stringify(result.output, null, 2);
      }
      box.textContent = out;
    } else {
      box.textContent = '❌ 执行失败\\n\\n'+result.error;
    }
    document.getElementById('runStatus').textContent = '✅ 完成';
  }catch(e){
    document.getElementById('runStatus').textContent = '❌ 失败';
    showToast('执行失败: '+e.message,'error');
  }
}

// ── 保存到我的技能 ──
async function saveAsSkill(){
  if(!currentSkill) return;
  try{
    const r = await fetch('/api/skills', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        name: currentSkill.name,
        description: currentSkill.description,
        category: currentSkill.category||'engine',
        code: '# 引擎模式: '+currentSkill.engine,
        status: 'published'
      })
    });
    const d = await r.json();
    showToast('✅ 已保存到我的技能','success');
  }catch(e){showToast('保存失败','error')}
}

// ── 下载 .skill 文件 ──
function downloadSkill(){
  if(!currentSkill) return;
  const blob = new Blob([JSON.stringify(currentSkill, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = currentSkill.id+'.skill';
  a.click();
  showToast('✅ 已下载 '+currentSkill.id+'.skill','success');
}

function showStep(n){
  ['step1','step2','step3'].forEach((id,i)=>{
    document.getElementById(id).classList.toggle('hidden', i+1!==n);
    document.getElementById('s'+(i+1)).classList.toggle('active', i+1===n);
    document.getElementById('s'+(i+1)).classList.toggle('done', i+1<n);
  });
}

function showToast(msg, type){
  const t = document.createElement('div');
  t.className = 'toast '+type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(()=>t.remove(), 3000);
}

loadSkills();
</script>
</body>
</html>"""


MARKET_INSTALLER_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Market 技能安装器</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#0a1628;color:#e0e8f0;min-height:100vh;padding:32px}
.topbar{margin-bottom:24px}
.topbar h1{font-size:24px}
.topbar p{color:#8098c0;font-size:13px}
.topbar a{color:#90b8f8;text-decoration:none;font-size:13px}
.upload-zone{border:2px dashed #1e3d70;border-radius:16px;padding:60px;text-align:center;cursor:pointer;transition:all .3s;margin-bottom:24px}
.upload-zone:hover{border-color:#3b82f6;background:#1a56d611}
.upload-zone .icon{font-size:48px;margin-bottom:12px}
.upload-zone p{color:#8098c0;font-size:14px}
.import-section{background:#0d1d3a;border:1px solid #1e3d70;border-radius:12px;padding:24px;margin-bottom:20px}
.import-section textarea{width:100%;background:#0a1628;border:1px solid #1e3d70;color:#e0e8f0;padding:12px;border-radius:8px;font-size:12px;min-height:180px;font-family:monospace;resize:vertical}
.import-section .hint{color:#8098c0;font-size:12px;margin-bottom:8px}
.btn{padding:10px 24px;border:none;border-radius:8px;cursor:pointer;font-weight:600;font-size:14px;background:linear-gradient(135deg,#059690,#0dcea6);color:#fff}
.btn:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(5,150,144,.3)}
.installed-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.installed-item{background:#0d1d3a;border:1px solid #1e3d70;border-radius:10px;padding:16px}
.installed-item .name{font-weight:600;font-size:14px}
.installed-item .meta{color:#8098c0;font-size:11px;margin-top:4px}
.installed-item .actions{margin-top:10px;display:flex;gap:8px}
.btn-sm{padding:5px 12px;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600}
.btn-sm.primary{background:#1a56d6;color:#fff}
.btn-sm.success{background:#059690;color:#fff}
.code-block{background:#0a1628;border:1px solid #2a2a4a;border-radius:6px;padding:10px;font-family:monospace;font-size:11px;white-space:pre-wrap;max-height:150px;overflow:auto;margin-top:8px;color:#b0c4e0}
</style>
</head>
<body>
<div class="topbar">
  <h1>🏪 Market 技能安装器</h1>
  <p>从 Skill Market 下载的 .skill 文件，直接拖放或粘贴即可安装使用</p>
  <a href="/">← 首页</a> | <a href="/wizard">🧩 技能工坊</a>
</div>

<div class="upload-zone" id="dropZone" ondragover="event.preventDefault()" ondrop="handleDrop(event)">
  <div class="icon">📂</div>
  <p><b>拖放 .skill 文件到此处</b></p>
  <p style="font-size:12px;margin-top:4px">或点击下方按钮粘贴 JSON</p>
</div>

<div class="import-section">
  <div class="hint">📋 也可以直接粘贴 .skill JSON 内容：</div>
  <textarea id="skillJsonInput" placeholder='{\n  "id": "my_skill",\n  "name": "我的技能",\n  "engine": "text_summary",\n  ...}'></textarea>
  <div style="margin-top:10px">
    <button class="btn" onclick="installFromJson()">📦 安装此技能</button>
  </div>
</div>

<div id="previewArea" class="hidden import-section">
  <h3 style="margin-bottom:12px">🔍 技能预览</h3>
  <div id="previewContent"></div>
  <div style="margin-top:12px">
    <button class="btn" onclick="confirmInstall()">✅ 确认安装</button>
    <button class="btn" style="background:#dc3545" onclick="clearPreview()">取消</button>
  </div>
</div>

<h2 style="margin-top:24px;margin-bottom:12px">📦 已安装的技能</h2>
<div class="installed-list" id="installedList">加载中...</div>

<script>
let pendingSkill = null;

// ── 拖放处理 ──
function handleDrop(e){
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if(!file || !file.name.endsWith('.skill')) return showToast('请拖入 .skill 文件','error');
  
  const reader = new FileReader();
  reader.onload = function(ev){
    try{
      pendingSkill = JSON.parse(ev.target.result);
      showPreview(pendingSkill);
    }catch(e){showToast('文件格式错误: '+e.message,'error')}
  };
  reader.readAsText(file);
}

// ── 粘贴安装 ──
function installFromJson(){
  try{
    pendingSkill = JSON.parse(document.getElementById('skillJsonInput').value);
    showPreview(pendingSkill);
  }catch(e){showToast('JSON 格式错误: '+e.message,'error')}
}

// ── 显示预览 ──
function showPreview(skill){
  document.getElementById('previewArea').classList.remove('hidden');
  document.getElementById('previewContent').innerHTML = 
    '<div style="display:flex;gap:20px;align-items:start;flex-wrap:wrap">'+
    '<div><div style="font-size:36px">'+(skill.icon||'🧩')+'</div></div>'+
    '<div><b style="font-size:18px">'+skill.name+'</b>'+
    '<div style="color:#8098c0;font-size:13px;margin-top:4px">'+(skill.description||'')+'</div>'+
    '<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">'+
    '<span class="badge">引擎: '+skill.engine+'</span>'+
    '<span class="badge">v'+skill.version+'</span>'+
    (skill.author?'<span class="badge">作者: '+skill.author+'</span>':'')+
    '</div></div></div>'+
    '<div class="code-block">'+JSON.stringify(skill, null, 2)+'</div>';
}

// ── 确认安装 ──
async function confirmInstall(){
  if(!pendingSkill) return;
  try{
    const r = await fetch('/api/skills', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        name: pendingSkill.name,
        description: pendingSkill.description||'从 Market 安装',
        category: pendingSkill.category||'market',
        code: '# .skill 引擎模式: '+pendingSkill.engine+'\n# 配置: '+JSON.stringify(pendingSkill.config||{}),
        status: 'published'
      })
    });
    const d = await r.json();
    showToast('✅ "'+pendingSkill.name+'" 安装成功！','success');
    clearPreview();
    loadInstalled();
  }catch(e){showToast('安装失败: '+e.message,'error')}
}

function clearPreview(){
  document.getElementById('previewArea').classList.add('hidden');
  pendingSkill = null;
}

// ── 加载已安装的技能 ──
async function loadInstalled(){
  try{
    const r = await fetch('/api/skills');
    const d = await r.json();
    document.getElementById('installedList').innerHTML = d.skills.length 
      ? d.skills.map(s => `
        <div class="installed-item">
          <div class="name">${s.name}</div>
          <div class="meta">${s.category} · ${s.status} · 🧪${s.test_count}次测试</div>
          <div class="code-block" style="max-height:80px">${s.description||'无描述'}</div>
          <div class="actions">
            <button class="btn-sm primary" onclick="location.href='/editor?id=${s.id}'">编辑</button>
            <button class="btn-sm success" onclick="location.href='/playground'">测试</button>
          </div>
        </div>
      `).join('')
      : '<div style="color:#8098c0">还没有安装任何技能</div>';
  }catch(e){}
}

function showToast(msg, type){
  const t = document.createElement('div');
  t.className = 'toast '+(type||'success');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;top:24px;right:24px;padding:14px 24px;border-radius:8px;font-size:14px;font-weight:600;z-index:999;animation:slideIn .3s;'+(type==='error'?'background:#dc3545;color:#fff':'background:#059690;color:#fff');
  document.body.appendChild(t);
  setTimeout(()=>t.remove(), 3000);
}

loadInstalled();
</script>
</body>
</html>"""
