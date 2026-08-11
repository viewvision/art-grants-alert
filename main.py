from datetime import date

from scraper.sites import SITE_MODULES
from scraper.filters import load_config, filter_items
from scraper.state import load_state, save_state, find_new_items, update_state
from scraper.dashboard import (
    load_matched_items,
    merge_matched_items,
    save_matched_items,
    write_dashboard,
    dedupe_by_title,
)
from scraper.email_sender import build_email_html, group_by_site, send_email


def main():
    today = date.today().isoformat()
    config = load_config()
    state = load_state()

    all_items = []
    for mod in SITE_MODULES:
        try:
            items = mod.fetch()
        except Exception as e:
            print(f"[WARN] {mod.SITE_KEY} fetch failed: {e}")
            continue
        print(f"[INFO] {mod.SITE_KEY}: {len(items)}건 수집")
        all_items.extend(items)

    new_items = find_new_items(all_items, state, today)
    state = update_state(all_items, state, today)
    save_state(state)
    print(f"[INFO] 신규 글: {len(new_items)}건 (전체 수집: {len(all_items)}건)")

    new_matched = filter_items(new_items, config)
    new_matched = dedupe_by_title(new_matched)
    for item in new_matched:
        item["first_seen"] = today

    matched_existing = load_matched_items()
    already_shown_titles = {"".join(i.get("title", "").split()) for i in matched_existing}
    new_matched = [
        i for i in new_matched if "".join(i.get("title", "").split()) not in already_shown_titles
    ]
    print(f"[INFO] 필터 통과 신규 글: {len(new_matched)}건 (사이트 간 중복 제거 후)")

    if new_matched:
        matched_merged = merge_matched_items(matched_existing, new_matched)
        save_matched_items(matched_merged)
        write_dashboard(matched_merged)

        html_body = build_email_html(group_by_site(new_matched))
        send_email(f"[공모/지원사업 알림] 새 글 {len(new_matched)}건", html_body)
        print(f"[INFO] 이메일 발송 완료 ({len(new_matched)}건)")
    else:
        print("[INFO] 새로 알릴 항목 없음")


if __name__ == "__main__":
    main()
