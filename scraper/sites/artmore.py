from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

SITE_KEY = "artmore"
SITE_LABEL = "아트모아"

LIST_URL = "https://www.artmore.kr/sub/recruit/search_list.do"
BASE_URL = "https://www.artmore.kr"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for tr in soup.select("table.jobs_sch_tb tbody > tr"):
        a = tr.select_one("a.jobs_title")
        if not a or not a.get("href"):
            continue

        company_el = tr.select_one("p.jobs_cname")
        company = ""
        if company_el:
            company = company_el.find(string=True, recursive=False)
            company = company.strip() if company else ""

        state_el = a.select_one("span.jobs_list_state")
        state_text = state_el.get_text(strip=True) if state_el else ""
        title = a.get_text(strip=True)
        if state_text and title.startswith(state_text):
            title = title[len(state_text):].strip()

        workplace_el = tr.select_one("span.jobs_wkplace")
        workplace = workplace_el.get_text(strip=True) if workplace_el else ""

        date_el = tr.select_one("p.jobs_regi_stt-time")
        date = date_el.get_text(strip=True).replace("등록", "").strip() if date_el else ""

        href = a["href"]
        url = href if href.startswith("http") else BASE_URL + href
        rec_idx = parse_qs(urlparse(url).query).get("rec_idx", [None])[0]
        if not title or not rec_idx:
            continue

        full_title = f"[{company}] {title}" if company else title
        if workplace:
            full_title = f"{full_title} ({workplace})"

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": rec_idx,
                "title": full_title,
                "url": url,
                "date": date,
                "image": None,
            }
        )
    return items
