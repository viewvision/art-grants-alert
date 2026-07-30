import html

import requests

SITE_KEY = "nabi"
SITE_LABEL = "아트센터 나비미술관"

API_URL = "https://www.nabi.or.kr/proc/board_list.php"
BASE_URL = "https://www.nabi.or.kr"
DETAIL_URL_TMPL = BASE_URL + "/page/board_view.php?brd_idx={brd_idx}&brd_id=academy"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
PAYLOAD = {"brd_id": "academy", "brd_lang": "KR", "brd_category": "", "size": "20", "page": "1"}


def fetch() -> list:
    resp = requests.post(API_URL, data=PAYLOAD, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for row in data.get("list", []):
        brd_idx = row.get("brd_idx")
        title = html.unescape((row.get("brd_title") or "").strip())
        if not brd_idx or not title:
            continue

        thumb = row.get("brd_thumb")
        image = BASE_URL + thumb if thumb else None

        sdate = row.get("brd_sdate", "")
        edate = row.get("brd_edate", "")
        date = f"{sdate} ~ {edate}" if sdate or edate else ""

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": brd_idx,
                "title": title,
                "url": DETAIL_URL_TMPL.format(brd_idx=brd_idx),
                "date": date,
                "image": image,
            }
        )
    return items
