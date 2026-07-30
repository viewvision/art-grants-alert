import re

import requests
from bs4 import BeautifulSoup

SITE_KEY = "artskorealab"
SITE_LABEL = "아트코리아랩"

LIST_URL = "https://www.artskorealab.kr/bbs/list.do?key=2303300002"
DETAIL_URL_TMPL = "https://www.artskorealab.kr/bbs/view.do?key=2303300002&pstSn={pst_sn}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for a in soup.select("ul.notice-list li a.box"):
        onclick = a.get("onclick", "")
        m = re.search(r"goView\('(\d+)'\)", onclick)
        if not m:
            continue
        pst_sn = m.group(1)

        title_el = a.select_one("strong.ti")
        date_el = a.select_one("span.date")
        title = title_el.get_text(strip=True) if title_el else ""
        date = date_el.get_text(strip=True) if date_el else ""

        if not title:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": pst_sn,
                "title": title,
                "url": DETAIL_URL_TMPL.format(pst_sn=pst_sn),
                "date": date,
                "image": None,
            }
        )
    return items
