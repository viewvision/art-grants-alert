import re

import requests
from bs4 import BeautifulSoup

from . import _ssl_diag

SITE_KEY = "metaverse_campus"
SITE_LABEL = "가상융합기술 Campus"

LIST_URL = "https://www.metaverse-campus.kr/bbs/data/list.do?menu_idx=14"
DETAIL_URL_TMPL = (
    "https://www.metaverse-campus.kr/bbs/data/view.do"
    "?bbs_mst_idx={bbs_mst_idx}&data_idx={data_idx}"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

FN_VIEW_RE = re.compile(r"fn_view\('([^']*)','([^']*)'")


def fetch() -> list:
    try:
        resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    except requests.exceptions.SSLError as e:
        diag = _ssl_diag.diagnose("www.metaverse-campus.kr")
        raise requests.exceptions.SSLError(f"{e} | 인증서 체인 진단: {diag}") from e
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for tr in soup.select("div.board_list table tbody > tr"):
        a = tr.select_one("td.cell a")
        date_el = tr.select_one("td.date")
        if not a:
            continue
        m = FN_VIEW_RE.search(a.get("href", ""))
        if not m:
            continue
        bbs_mst_idx, data_idx = m.groups()

        title = a.get_text(strip=True)
        date = date_el.get_text(strip=True) if date_el else ""

        if not title:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": data_idx,
                "title": title,
                "url": DETAIL_URL_TMPL.format(bbs_mst_idx=bbs_mst_idx, data_idx=data_idx),
                "date": date,
                "image": None,
            }
        )
    return items
