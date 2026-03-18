#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone, timedelta
import subprocess, re, html, json, shutil

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'tmp'
DATA = ROOT / 'data'
DOCS = ROOT / 'docs'
TMP.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
VIP_MEDIA_TMP = TMP / 'vip-media'
VIP_MEDIA_PUBLIC = ROOT / 'astro' / 'public' / 'vip-media'
VIP_MEDIA_DOCS = DOCS / 'vip-media'
VIP_MEDIA_TMP.mkdir(parents=True, exist_ok=True)
VIP_MEDIA_PUBLIC.mkdir(parents=True, exist_ok=True)
VIP_MEDIA_DOCS.mkdir(parents=True, exist_ok=True)

WINDOW_DAYS = 2
CUT_OFF = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
MAX_PAGES = 1
VIP_IMAGE_LIMIT = 20

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


def fetch_url(url: str, out_path: Path) -> str:
    subprocess.run(['curl', '-L', '--max-time', '45', '-A', 'Mozilla/5.0', url, '-o', str(out_path)], check=True)
    return out_path.read_text(encoding='utf-8')


def clean_html_text(raw: str) -> str:
    text = re.sub(r'<br\s*/?>', '\n', raw)
    text = re.sub(r'</p\s*>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()

def strip_telegram_promo_lines(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lower = line.lower().strip()
        if not lower:
            lines.append(line)
            continue
        if ('t.me/' in lower or 'https://t.me/' in lower or 'http://t.me/' in lower) and any(k in lower for k in ['关注频道', 'telegram必备', 'jisou', 'start=']):
            continue
        lines.append(line)
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    promo_keywords = ['telegram必备的搜索引擎', '关注频道', 'jisou', '每日分享b站各类课程']
    low = cleaned.lower()
    if any(k in low for k in promo_keywords):
        return ''
    return cleaned


def parse_message_chunk(chunk: str, channel: str) -> dict | None:
    post = re.search(r'data-post="([^"]+)"', chunk)
    if not post:
        return None
    dt = re.search(r'<time datetime="([^"]+)"', chunk)
    views = re.search(r'<span class="tgme_widget_message_views">([^<]*)</span>', chunk)
    text_match = re.search(r'<div class="tgme_widget_message_text[^>]*>([\s\S]*?)</div>\s*<div class="tgme_widget_message_footer', chunk)
    photo_bg = re.search(r'background-image:url\(\'([^\']+)\'\)', chunk)

    text = ''
    media_only = False
    if text_match:
        text = strip_telegram_promo_lines(clean_html_text(text_match.group(1)))
    else:
        media_only = 'text_not_supported_wrap' in chunk or 'tgme_widget_message_photo_wrap' in chunk or 'tgme_widget_message_video_player' in chunk

    image_url = None
    if photo_bg:
        image_url = photo_bg.group(1)
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        if 'telegram.org/img/emoji/' in image_url:
            image_url = None

    return {
        'post': post.group(1),
        'datetime': dt.group(1) if dt else None,
        'views': views.group(1).strip() if views else None,
        'text': text,
        'media_only': media_only,
        'image_url': image_url if channel == 'clsvip' else None,
        'url': f"https://t.me/{post.group(1)}",
    }


def parse_page(src: str, channel: str) -> list:
    items = []
    for chunk in re.split(r'<div class="tgme_widget_message_wrap', src)[1:]:
        parsed = parse_message_chunk(chunk, channel)
        if parsed:
            items.append(parsed)
    return items


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


def sync_vip_images(items: list) -> None:
    for d in [VIP_MEDIA_DOCS, VIP_MEDIA_PUBLIC]:
        for old in d.glob('*'):
            old.unlink()
    downloaded = 0
    for item in items:
        item['image'] = None
        if downloaded >= VIP_IMAGE_LIMIT:
            continue
        url = item.get('image_url')
        if not url:
            continue
        post_id = item['post'].split('/')[-1]
        ext = '.jpg'
        out = VIP_MEDIA_DOCS / f'{post_id}{ext}'
        public_out = VIP_MEDIA_PUBLIC / f'{post_id}{ext}'
        try:
            subprocess.run(['curl', '-L', '--max-time', '45', '-A', 'Mozilla/5.0', url, '-o', str(out)], check=True)
            if out.exists() and out.stat().st_size > 1000:
                shutil.copy2(out, public_out)
                item['image'] = f'./vip-media/{out.name}'
                downloaded += 1
        except Exception:
            for path in [out, public_out]:
                if path.exists():
                    path.unlink()


def fetch_source(cfg: dict) -> None:
    src = fetch_url(cfg['url'], cfg['html_path'])
    collected = parse_page(src, cfg['name'])
    existing = load_existing(cfg['messages_path'])
    by_post = {}
    for item in existing + collected:
        by_post[item['post']] = item
    recent = filter_recent(list(by_post.values()))

    if cfg['name'] == 'clsvip':
        sync_vip_images(recent)

    cfg['messages_path'].write_text(json.dumps(recent, ensure_ascii=False, indent=2), encoding='utf-8')
    cfg['meta_path'].write_text(json.dumps({
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'count': len(recent),
        'window': f'{WINDOW_DAYS} days',
        'source': cfg['url'],
        'channel': cfg['name'],
        'pagesFetched': 1,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"wrote {len(recent)} recent messages to {cfg['messages_path']}")


for source in SOURCES:
    fetch_source(source)
