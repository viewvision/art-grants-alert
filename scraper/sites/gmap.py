from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

SITE_KEY = "gmap"
SITE_LABEL = "광주미디어아트플랫폼(G.MAP) 공지사항"

LIST_URL = "https://gmap.gwangju.go.kr/bbs/board.php?bo_table=notice"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for li in soup.select("div.gw_tb01 li.gw_tb_tr"):
        a = li.select_one("div.bo_tit a")
        if not a or not a.get("href"):
            continue

        href = a["href"]
        wr_id = parse_qs(urlparse(href).query).get("wr_id", [None])[0]
        title = a.get_text(strip=True)
        date_el = li.select_one("div.date")
        date = date_el.get_text(strip=True) if date_el else ""

        if not title or not wr_id:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": wr_id,
                "title": title,
                "url": href,
                "date": date,
                "image": None,
            }
        )
    return items
