from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup

SITE_KEY = "gokams"
SITE_LABEL = "예술경영지원센터"

LIST_URL = "https://www.gokams.or.kr/01_news/notice_list.aspx"
BASE_URL = "https://www.gokams.or.kr/01_news/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for tr in soup.select("table.boardList tr"):
        a = tr.select_one("td.left a")
        if not a or not a.get("href"):
            continue

        title = a.get_text(strip=True)
        url = urljoin(BASE_URL, a["href"])
        idx = parse_qs(urlparse(url).query).get("Idx", [None])[0]

        tds = tr.select("td")
        date = tds[3].get_text(strip=True) if len(tds) > 3 else ""

        if not title or not idx:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": idx,
                "title": title,
                "url": url,
                "date": date,
                "image": None,
            }
        )
    return items
