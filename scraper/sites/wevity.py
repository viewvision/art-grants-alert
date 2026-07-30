from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup

SITE_KEY = "wevity"
SITE_LABEL = "위비티"

LIST_URL = "https://www.wevity.com/?c=find&s=1&gbn=list"
BASE_URL = "https://www.wevity.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for li in soup.select("ul.list li"):
        a = li.select_one("div.tit a")
        if not a or not a.get("href"):
            continue

        stat_el = a.select_one("span.stat")
        if stat_el:
            stat_el.extract()
        title = a.get_text(strip=True)

        href = a["href"]
        url = urljoin(BASE_URL, href)
        ix = parse_qs(urlparse(url).query).get("ix", [None])[0]

        day_el = li.select_one("div.day")
        date = day_el.get_text(" ", strip=True) if day_el else ""

        if not title or not ix:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": ix,
                "title": title,
                "url": url,
                "date": date,
                "image": None,
            }
        )
    return items
