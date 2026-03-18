#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin
import subprocess, re, html, json

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'tmp'
DATA = ROOT / 'data'
TMP.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

WINDOW_DAYS = 1
CUT_OFF = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
MAX_PAGES = 1
BASE = 'https://t.me'

SOURCES = [
    {
        'name': 'financial_express',
        'url': 'https://t.me/s/Financial_Express',
        'html_path': TMP / 'channel.html',
        'messages_path': DATA / 'messages.json',
        'meta_path': DATA / 'meta.json',
    },
    {
        'name': 'clsvip',
        'url': 'https://t.me/s/clsvip',
        'html_path': TMP / 'clsvip.html',
        'messages_path': DATA / 'clsvip_messages.json',
        'meta_path': DATA / 'clsvip_meta.json',
    },
]


def fetch_url(url: str, html_path: Path) -> str:
    subprocess.run([
        'curl', '-L', '--max-time', '45', '-A', 'Mozilla/5.0',
        url,
        '-o', str(html_path)
    ], check=True)
    return html_path.read_text(encoding='utf-8')


def clean_html_text(raw: str) -> str:
    text = re.sub(r'<br\s*/?>', '\n', raw)
    text = re.sub(r'</p\s*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def parse_message_chunk(chunk: str) -> dict | None:
    post = re.search(r'data-post="([^"]+)"', chunk)
    if not post:
        return None
    dt = re.search(r'<time datetime="([^"]+)"', chunk)
    views = re.search(r'<span class="tgme_widget_message_views">([^<]*)</span>', chunk)
    text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>([\s\S]*?)</div>\s*<div class="tgme_widget_message_footer', chunk)
    text = ''
    media_only = False
    if text_match:
        text = clean_html_text(text_match.group(1))
    else:
        media_only = 'text_not_supported_wrap' in chunk or 'tgme_widget_message_photo_wrap' in chunk or 'tgme_widget_message_video_player' in chunk
    return {
        'post': post.group(1),
        'datetime': dt.group(1) if dt else None,
        'views': views.group(1).strip() if views else None,
        'text': text,
        'media_only': media_only,
        'url': f"https://t.me/{post.group(1)}",
    }


def parse_page(src: str) -> tuple[list, str | None]:
    items = []
    for chunk in re.split(r'<div class="tgme_widget_message_wrap', src)[1:]:
        parsed = parse_message_chunk(chunk)
        if parsed:
            items.append(parsed)
    more = None
    m = re.search(r'href="([^"]*before=[^"]+)"', src)
    if m:
        more = urljoin(BASE, m.group(1).replace('&amp;', '&'))
    return items, more


def load_existing(path: Path) -> list:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []


def filter_recent(items: list) -> list:
    recent = []
    for item in items:
        dt = item.get('datetime')
        try:
            parsed = datetime.fromisoformat(dt.replace('Z', '+00:00')) if dt else None
        except Exception:
            parsed = None
        if parsed is None or parsed >= CUT_OFF:
            recent.append(item)
    recent.sort(key=lambda x: x.get('datetime') or '', reverse=True)
    return recent


def fetch_source(cfg: dict) -> None:
    collected = []
    next_url = cfg['url']
    for page_num in range(MAX_PAGES):
        html_file = cfg['html_path'] if page_num == 0 else cfg['html_path'].with_name(f"{cfg['html_path'].stem}-{page_num}.html")
        src = fetch_url(next_url, html_file)
        items, more_url = parse_page(src)
        collected.extend(items)
        if not more_url:
            break
        if any((it.get('datetime') and datetime.fromisoformat(it['datetime'].replace('Z', '+00:00')) < CUT_OFF) for it in items if it.get('datetime')):
            break
        next_url = more_url

    existing = load_existing(cfg['messages_path'])
    by_post = {}
    for item in existing + collected:
        by_post[item['post']] = item
    recent = filter_recent(list(by_post.values()))

    cfg['messages_path'].write_text(json.dumps(recent, ensure_ascii=False, indent=2), encoding='utf-8')
    cfg['meta_path'].write_text(json.dumps({
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'count': len(recent),
        'window': f'{WINDOW_DAYS} day',
        'source': cfg['url'],
        'channel': cfg['name'],
        'pagesFetched': 1,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"wrote {len(recent)} recent messages to {cfg['messages_path']}")


for source in SOURCES:
    fetch_source(source)
