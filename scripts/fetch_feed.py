#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone, timedelta
import subprocess, re, html, json

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'tmp'
DATA = ROOT / 'data'
TMP.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
html_path = TMP / 'channel.html'
messages_path = DATA / 'messages.json'
meta_path = DATA / 'meta.json'

subprocess.run([
    'curl', '-L', '--max-time', '45', '-A', 'Mozilla/5.0',
    'https://t.me/s/Financial_Express',
    '-o', str(html_path)
], check=True)

src = html_path.read_text(encoding='utf-8')
items = []
for chunk in re.split(r'<div class="tgme_widget_message_wrap', src)[1:]:
    post = re.search(r'data-post="([^"]+)"', chunk)
    dt = re.search(r'<time datetime="([^"]+)"', chunk)
    views = re.search(r'<span class="tgme_widget_message_views">([^<]*)</span>', chunk)
    text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>([\s\S]*?)</div>\s*<div class="tgme_widget_message_footer', chunk)
    text = ''
    if text_match:
        text = text_match.group(1)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'</p\s*>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = html.unescape(text).strip()
    if post:
        items.append({
            'post': post.group(1),
            'datetime': dt.group(1) if dt else None,
            'views': views.group(1).strip() if views else None,
            'text': text,
            'url': f"https://t.me/{post.group(1)}"
        })

existing = []
if messages_path.exists():
    try:
        existing = json.loads(messages_path.read_text(encoding='utf-8'))
    except Exception:
        existing = []
by_post = {}
for item in existing + items:
    by_post[item['post']] = item
merged = list(by_post.values())
cutoff = datetime.now(timezone.utc) - timedelta(days=1)
recent = []
for item in merged:
    dt = item.get('datetime')
    try:
        parsed = datetime.fromisoformat(dt.replace('Z', '+00:00')) if dt else None
    except Exception:
        parsed = None
    if parsed is None or parsed >= cutoff:
        recent.append(item)
recent.sort(key=lambda x: x.get('datetime') or '', reverse=True)
messages_path.write_text(json.dumps(recent, ensure_ascii=False, indent=2), encoding='utf-8')
meta = {
    'updated_at': datetime.now(timezone.utc).isoformat(),
    'count': len(recent),
    'window': '1 day',
    'source': 'https://t.me/s/Financial_Express'
}
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'wrote {len(recent)} recent messages to {messages_path}')
