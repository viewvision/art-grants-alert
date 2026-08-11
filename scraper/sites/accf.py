import requests

SITE_KEY = "accf"
SITE_LABEL = "국립아시아문화전당재단 (기획 행사)"

API_URL = "https://www.accf.or.kr/main/api/v1/product/list"
DETAIL_URL_TMPL = "https://www.accf.or.kr/main/product/detail/ko/{seq_no}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
PARAMS = {
    "cpage": 1,
    "searchKeyword": "",
    "searchType": 1,
    "category": 16,  # 공연 및 행사 > 기획 행사
    "localeCookie": "",
    "status": "진행중",
}


def fetch() -> list:
    resp = requests.get(API_URL, params=PARAMS, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for row in data.get("list", []):
        seq_no = row.get("seq_no")
        title = (row.get("list_title") or "").strip()
        if not seq_no or not title:
            continue

        start_date = row.get("start_date_time") or ""
        end_date = row.get("end_date_time") or ""
        date = f"{start_date} ~ {end_date}" if start_date or end_date else ""

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": str(seq_no),
                "title": title,
                "url": DETAIL_URL_TMPL.format(seq_no=seq_no),
                "date": date,
                "image": row.get("verticalFilePath"),
            }
        )
    return items
