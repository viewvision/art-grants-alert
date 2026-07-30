import requests
from bs4 import BeautifulSoup

SITE_KEY = "arko_education"
SITE_LABEL = "한국문화예술위원회(교육)"

LIST_URL = "https://arko.or.kr/infra/exevshedBoard/list?category=education"
BASE_URL = "https://arko.or.kr"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch() -> list:
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    items = []
    for li in soup.select("ul.newImgBoardList > li"):
        link_el = li.select_one("a.btn.blank")
        if not link_el or not link_el.get("href"):
            continue
        href = link_el["href"]
        url = href if href.startswith("http") else BASE_URL + href

        head_el = li.select_one("div.head")
        title = ""
        if head_el:
            edu_span = head_el.select_one("span.edu")
            if edu_span:
                edu_span.extract()
            title = head_el.get_text(strip=True)

        date = ""
        for row in li.select(".txtWrap ul > li"):
            tit_el = row.select_one("span.tit")
            txt_el = row.select_one("span.txt")
            if tit_el and txt_el and "교육기간" in tit_el.get_text(strip=True):
                date = txt_el.get_text(strip=True)
                break

        img_el = li.select_one("div.img img")
        image = None
        if img_el and img_el.get("src"):
            src = img_el["src"]
            image = src if src.startswith("http") else BASE_URL + src

        if not title:
            continue

        items.append(
            {
                "site": SITE_KEY,
                "site_label": SITE_LABEL,
                "id": href,
                "title": title,
                "url": url,
                "date": date,
                "image": image,
            }
        )
    return items
