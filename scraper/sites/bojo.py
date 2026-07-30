import requests

SITE_KEY = "bojo"
SITE_LABEL = "e나라도움(보조금통합포털)"

DATA_URL = "https://www.bojo.go.kr/aa/getAA001000DataSet.do"
DETAIL_URL_TMPL = "https://www.bojo.go.kr/ia/getIA005100Popup.do?nttId={ntt_id}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch() -> list:
    resp = requests.post(DATA_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for item in data.get("newTaskVOList", []):
        ntt_id = item.get("nttId")
        title = item.get("pblancNm") or item.get("pssrpNm")
        if not ntt_id or not title:
            continue

        begin = item.get("rceptBeginDe") or ""
        end = item.get("rceptEndDe") or ""
        date = f"{begin} ~ {end}" if begin or end else ""

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": str(ntt_id),
                "title": title,
                "url": DETAIL_URL_TMPL.format(ntt_id=ntt_id),
                "date": date,
                "image": None,
            }
        )
    return items
