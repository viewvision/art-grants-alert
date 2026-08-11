import html
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

MATCHED_ITEMS_PATH = Path(__file__).resolve().parent.parent / "data" / "matched_items.json"
DOCS_INDEX_PATH = Path(__file__).resolve().parent.parent / "docs" / "index.html"
MAX_ITEMS = 300
KST = timezone(timedelta(hours=9))


def load_matched_items(path: Path = MATCHED_ITEMS_PATH) -> list:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_matched_items(items: list, path: Path = MATCHED_ITEMS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def _normalize_title(title: str) -> str:
    return "".join((title or "").split())


def dedupe_by_title(items: list) -> list:
    """서로 다른 사이트가 같은 공고를 각자 긁어온 경우(예: 아르코 통합플랫폼이
    아트누리 글을 재게재) 제목이 같으면 하나만 남긴다."""
    seen_titles = set()
    deduped = []
    for item in items:
        key = _normalize_title(item.get("title", ""))
        if key in seen_titles:
            continue
        seen_titles.add(key)
        deduped.append(item)
    return deduped


def merge_matched_items(existing: list, new_items: list) -> list:
    by_key = {(i["site"], i["id"]): i for i in existing}
    for item in new_items:
        by_key[(item["site"], item["id"])] = item
    merged = list(by_key.values())
    # "date" 필드는 사이트마다 형식이 달라(게시일/마감일/"D-n" 등) 정렬 기준으로 쓸 수 없음.
    # 실제로 새로 수집된 시점(first_seen, ISO 형식)을 기준으로 최신순 정렬.
    merged.sort(key=lambda i: i.get("first_seen") or "", reverse=True)
    merged = dedupe_by_title(merged)
    return merged[:MAX_ITEMS]


def _card_html(item: dict) -> str:
    title = html.escape(item.get("title", ""))
    url = html.escape(item.get("url", "#"))
    date = html.escape(item.get("date") or "")
    site_label = html.escape(item.get("site_label", item.get("site", "")))
    image = item.get("image")

    image_html = ""
    if image:
        image_html = f'<img class="thumb" src="{html.escape(image)}" alt="" loading="lazy">'

    return f"""
    <a class="card" href="{url}" target="_blank" rel="noopener">
      {image_html}
      <div class="card-body">
        <span class="site-tag">{site_label}</span>
        <div class="card-title">{title}</div>
        <div class="card-date">{date}</div>
      </div>
    </a>
    """


def render_dashboard_html(items: list) -> str:
    updated_at = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    cards = "".join(_card_html(i) for i in items)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>공모/지원사업 알림 대시보드</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 900px; margin: 0 auto; padding: 24px 16px 64px; background: #fff; color: #111; }}
  @media (prefers-color-scheme: dark) {{ body {{ background: #111; color: #eee; }} }}
  h1 {{ font-size: 20px; }}
  .updated {{ color: #888; font-size: 13px; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }}
  .card {{ display: block; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; text-decoration: none; color: inherit; }}
  @media (prefers-color-scheme: dark) {{ .card {{ border-color: #333; }} }}
  .card:hover {{ border-color: #888; }}
  .thumb {{ width: 100%; height: 140px; object-fit: cover; display: block; }}
  .card-body {{ padding: 10px 12px; }}
  .site-tag {{ font-size: 11px; color: #666; }}
  .card-title {{ font-size: 14px; font-weight: 600; margin: 4px 0; line-height: 1.35; }}
  .card-date {{ font-size: 12px; color: #999; }}
</style>
</head>
<body>
  <h1>공모/지원사업/교육 알림 대시보드</h1>
  <div class="updated">마지막 업데이트: {updated_at} · 총 {len(items)}건</div>
  <div class="grid">
    {cards}
  </div>
</body>
</html>
"""


def write_dashboard(items: list, path: Path = DOCS_INDEX_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_dashboard_html(items))
