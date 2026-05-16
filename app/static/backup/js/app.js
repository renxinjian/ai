// AI Platform - 全局工具函数
const API = '/api';

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

async function apiFetch(path, options = {}) {
  const url = API + path;
  const opts = { headers: { 'Content-Type': 'application/json' }, ...options };
  if (options.body) opts.body = JSON.stringify(options.body);
  const r = await fetch(url, opts);
  return r.json();
}

function showLoading(el, msg = '加载中...') {
  el.innerHTML = `<div style="color:var(--text-muted);padding:20px;text-align:center">⏳ ${msg}</div>`;
}
