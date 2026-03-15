#!/usr/bin/env python3
from pathlib import Path
import json, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'messages.json'
DOCS = ROOT / 'docs'
DOCS.mkdir(parents=True, exist_ok=True)
items = json.loads(DATA.read_text(encoding='utf-8'))
rows = []
for item in items[:20]:
    text = html.escape(item.get('text') or '').replace('\n', '<br>')
    url = item.get('url') or '#'
    post = html.escape(item.get('post') or '')
    dt = html.escape(item.get('datetime') or '')
    views = html.escape(item.get('views') or '')
    rows.append(f'<article class="card"><div class="meta"><a href="{url}" target="_blank">{post}</a> | {dt} | {views} views</div><div class="body">{text}</div></article>')
page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>财经慢报 Feed</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:860px;margin:40px auto;padding:0 16px;background:#f7f7f7;color:#222}}
.card{{background:#fff;border-radius:12px;padding:16px 18px;margin:14px 0;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.meta{{font-size:12px;color:#666;margin-bottom:10px}}
.body{{font-size:15px;line-height:1.6;word-break:break-word}}
a{{color:#0b57d0;text-decoration:none}} a:hover{{text-decoration:underline}}
small{{color:#777}}
</style>
</head>
<body>
<h1>财经慢报 Feed</h1>
<p>基于 Telegram 公开频道页生成的静态展示原型。</p>
<p><small>来源：<a href="https://t.me/Financial_Express" target="_blank">@Financial_Express</a></small></p>
{''.join(rows)}
</body>
</html>'''
(DOCS / 'index.html').write_text(page, encoding='utf-8')
print(f'wrote {DOCS / "index.html"}')
