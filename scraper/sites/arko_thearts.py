from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

SITE_KEY = "arko_thearts"
SITE_LABEL = "아르코 통합플랫폼"

LIST_URL = "https://thearts.arko.or.kr/thearts/news/contest"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def _item_id(href: str) -> str:
    qs = parse_qs(urlparse(href).query)
    docid = qs.get("docid", [None])[0]
    return docid or href


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for a in soup.select(".output-list-half.output-list ul > li > a.item"):
        href = a.get("href", "")
        if not href:
            continue

        title_el = a.select_one("h2.title")
        title = ""
        if title_el:
            title_spans = [
                s for s in title_el.select("span") if "fix" not in (s.get("class") or [])
            ]
            if title_spans:
                title = title_spans[-1].get_text(strip=True)
            else:
                title = title_el.get_text(strip=True)

        date_el = a.select_one("p.date")
        date = date_el.get_text(strip=True) if date_el else ""

        if not title:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": _item_id(href),
                "title": title,
                "url": href,
                "date": date,
                "image": None,
            }
        )
    return items
