import re

import requests
from bs4 import BeautifulSoup

SITE_KEY = "artnuri"
SITE_LABEL = "아트누리"

LIST_URL = "https://artnuri.or.kr/"
DETAIL_URL_TMPL = (
    "https://artnuri.or.kr/crawler/info/view.do"
    "?key=2301170002&docid={docid}&source={source}&seNo={se_no}"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ONCLICK_RE = re.compile(r"goView\('([^']*)','([^']*)','([^']*)'\)")


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for li in soup.select(".box-list-wrap.active ul.box-list > li"):
        a = li.select_one("a")
        if not a:
            continue
        m = ONCLICK_RE.search(a.get("onclick", ""))
        if not m:
            continue
        docid, source, se_no = m.groups()

        title_el = a.select_one("strong.list-tit")
        date_el = a.select_one("span.date")
        title = title_el.get_text(strip=True) if title_el else ""
        date = date_el.get_text(strip=True) if date_el else ""

        if not title:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": docid,
                "title": title,
                "url": DETAIL_URL_TMPL.format(docid=docid, source=source, se_no=se_no),
                "date": date,
                "image": None,
            }
        )
    return items
