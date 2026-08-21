import re

import requests
from bs4 import BeautifulSoup

from . import _ssl_diag

SITE_KEY = "metaverse_campus_lecture"
SITE_LABEL = "가상융합기술 Campus (제작역량강화 교육)"

LIST_URL = "https://www.metaverse-campus.kr/lecture/listAll.do?menu_idx=50&lecIdx=17"
DETAIL_URL_TMPL = (
    "https://www.metaverse-campus.kr/lecture/viewAll.do"
    "?menu_idx=50&lecIdx=17&proIdx={pro_idx}"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

FN_INFO_DTL_RE = re.compile(r"fn_infoDtl\('(\d+)'\)")


def fetch() -> list:
    try:
        resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    except requests.exceptions.SSLError as e:
        diag = _ssl_diag.diagnose("www.metaverse-campus.kr")
        raise requests.exceptions.SSLError(f"{e} | 인증서 체인 진단: {diag}") from e
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for tr in soup.select("div.board_list table tbody tr"):
        a = tr.select_one("td.cell a")
        if not a:
            continue
        m = FN_INFO_DTL_RE.search(a.get("onclick", ""))
        if not m:
            continue
        pro_idx = m.group(1)

        title = a.get_text(strip=True)
        tds = tr.select("td")
        period = tds[4].get_text(" ", strip=True) if len(tds) > 4 else ""

        if not title:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": pro_idx,
                "title": title,
                "url": DETAIL_URL_TMPL.format(pro_idx=pro_idx),
                "date": period,
                "image": None,
            }
        )
    return items
