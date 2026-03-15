#!/usr/bin/env python3
from pathlib import Path
import subprocess, re, html, json

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'tmp'
DATA = ROOT / 'data'
TMP.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
html_path = TMP / 'channel.html'

subprocess.run([
    'curl','-L','--max-time','45','-A','Mozilla/5.0',
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

(DATA / 'messages.json').write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'wrote {len(items)} messages to {DATA / "messages.json"}')
