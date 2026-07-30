import requests

SITE_KEY = "artspoon"
SITE_LABEL = "아트스푼"

API_URL = "https://api-rakama.artra.gallery:8882/contest/public"
DETAIL_URL_TMPL = "https://artspoon.io/ko/contest/{slug}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "authorization": "QVG8W94EEM6",
    "version": "1.0",
    "referer": "https://artspoon.io/",
    "accept": "application/json, text/plain, */*",
}


def _fmt_date(iso_str: str) -> str:
    return iso_str[:10] if iso_str else ""


def fetch() -> list:
    resp = requests.get(API_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    items = []
    for c in payload.get("data", []):
        title = " ".join(c.get("translations", {}).get("ko", {}).get("title", "").split())
        slug = c.get("slug")
        cid = c.get("id")
        if not title or not slug:
            continue

        timeline = c.get("timeline", {})
        start = _fmt_date(timeline.get("applicationStart", ""))
        end = _fmt_date(timeline.get("applicationEnd", ""))
        date = f"{start} ~ {end}" if start or end else ""

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": str(cid),
                "title": title,
                "url": DETAIL_URL_TMPL.format(slug=slug),
                "date": date,
                "image": None,
            }
        )
    return items
