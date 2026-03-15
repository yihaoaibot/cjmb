#!/usr/bin/env python3
from pathlib import Path
import json, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'messages.json'
META = ROOT / 'data' / 'meta.json'
DOCS = ROOT / 'docs'
DOCS.mkdir(parents=True, exist_ok=True)
items = json.loads(DATA.read_text(encoding='utf-8'))
meta = json.loads(META.read_text(encoding='utf-8')) if META.exists() else {}
rows = []
for item in items[:100]:
    full_text = item.get('text') or ''
    short_text = full_text if len(full_text) <= 220 else full_text[:220].rstrip() + '...'
    text = html.escape(short_text).replace('\n', '<br>')
    full = html.escape(full_text).replace('\n', '<br>')
    url = item.get('url') or '#'
    post = html.escape(item.get('post') or '')
    dt = html.escape(item.get('datetime') or '')
    views = html.escape(item.get('views') or '')
    button = ''
    if len(full_text) > 220:
        button = '<button class="toggle" onclick="toggleCard(this)">展开</button>'
    rows.append('<article class="card"><div class="meta"><a href="{url}" target="_blank">{post}</a> | {dt} | {views} views</div><div class="body" data-full="{full}" data-short="{text}">{text}</div><div class="actions">{button}<a class="linkbtn" href="{url}" target="_blank">查看原文</a></div></article>'.format(
        url=url, post=post, dt=dt, views=views, full=full, text=text, button=button
    ))
updated = html.escape(meta.get('updated_at', ''))
count = html.escape(str(meta.get('count', '')))
page = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>财经慢报 Feed</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:920px;margin:32px auto;padding:0 16px;background:#f6f7fb;color:#1f2328}
.header{margin-bottom:24px}
.header h1{margin:0 0 8px 0;font-size:30px}
.sub{color:#667085;font-size:14px;line-height:1.6}
.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:18px 0 24px 0}
.search{flex:1;min-width:220px;padding:12px 14px;border:1px solid #d0d7de;border-radius:10px;font-size:14px;background:#fff}
.badge{display:inline-block;background:#e8f0fe;color:#0b57d0;border-radius:999px;padding:6px 10px;font-size:12px}
.card{background:#fff;border-radius:14px;padding:16px 18px;margin:14px 0;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.meta{font-size:12px;color:#667085;margin-bottom:10px;word-break:break-all}
.body{font-size:15px;line-height:1.7;word-break:break-word}
.actions{display:flex;gap:10px;margin-top:12px;align-items:center}
.toggle,.linkbtn{border:none;border-radius:8px;padding:8px 12px;font-size:13px;cursor:pointer;text-decoration:none}
.toggle{background:#eef2ff;color:#334155}
.linkbtn{background:#0b57d0;color:#fff}
a{color:#0b57d0;text-decoration:none} a:hover{text-decoration:underline}
.empty{color:#667085;padding:30px 0}
</style>
<script>
function toggleCard(btn) {
  const body = btn.parentElement.previousElementSibling;
  const full = body.dataset.full;
  const shortv = body.dataset.short;
  if (btn.dataset.expanded === '1') {
    body.innerHTML = shortv;
    btn.dataset.expanded = '0';
    btn.textContent = '展开';
  } else {
    body.innerHTML = full;
    btn.dataset.expanded = '1';
    btn.textContent = '收起';
  }
}
function filterCards() {
  const q = document.getElementById('search').value.toLowerCase().trim();
  document.querySelectorAll('.card').forEach(card => {
    const txt = card.innerText.toLowerCase();
    card.style.display = !q || txt.includes(q) ? '' : 'none';
  });
}
</script>
</head>
<body>
<div class="header">
  <h1>财经慢报 Feed</h1>
  <div class="sub">最近 1 天消息流展示。来源：<a href="https://t.me/Financial_Express" target="_blank">@Financial_Express</a></div>
  <div class="sub">最近更新：__UPDATED__</div>
</div>
<div class="toolbar">
  <input id="search" class="search" placeholder="搜索关键词…" oninput="filterCards()">
  <span class="badge">最近 1 天：__COUNT__ 条</span>
</div>
__ROWS__
</body>
</html>'''
page = page.replace('__UPDATED__', updated).replace('__COUNT__', count).replace('__ROWS__', ''.join(rows) if rows else '<div class="empty">暂无最近 1 天的数据</div>')
(DOCS / 'index.html').write_text(page, encoding='utf-8')
print(f'wrote {DOCS / "index.html"}')
