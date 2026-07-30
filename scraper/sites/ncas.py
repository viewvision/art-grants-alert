import re

import requests
from bs4 import BeautifulSoup

SITE_KEY = "ncas"
SITE_LABEL = "국가문화예술지원시스템"

LIST_URL = "https://www.ncas.or.kr/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

WINDOW_OPEN_RE = re.compile(r"window\.open\('([^']+)'\)")


def _clean(el) -> str:
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for tr in soup.select("article.proj_list_box .tab__cont.on .scroll_box table.tbl_basic tbody > tr"):
        tds = tr.select("td")
        if len(tds) < 7:
            continue

        title = _clean(tds[1].select_one(".field"))
        deadline = _clean(tds[3].select_one(".field"))

        button = tds[6].select_one("button")
        m = WINDOW_OPEN_RE.search(button.get("onclick", "")) if button else None
        url = m.group(1) if m else None

        if not title or not url:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": url,
                "title": title,
                "url": url,
                "date": deadline,
                "image": None,
            }
        )
    return items
