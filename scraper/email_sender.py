import os
import smtplib
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _item_html(item: dict) -> str:
    title = item.get("title", "")
    url = item.get("url", "#")
    date = item.get("date") or ""
    image = item.get("image")

    image_html = ""
    if image:
        image_html = (
            f'<img src="{image}" alt="" '
            f'style="max-width:240px;max-height:240px;display:block;'
            f'margin:6px 0;border-radius:6px;">'
        )

    return f"""
    <div style="margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #eee;">
      {image_html}
      <a href="{url}" style="font-size:15px;font-weight:600;color:#1a0dab;text-decoration:none;">{title}</a>
      <div style="font-size:12px;color:#888;margin-top:2px;">{date}</div>
    </div>
    """


def build_email_html(items_by_site: dict) -> str:
    sections = []
    for site_label, items in items_by_site.items():
        items_html = "".join(_item_html(i) for i in items)
        sections.append(
            f'<h3 style="font-size:16px;margin:20px 0 8px;">{site_label} ({len(items)}건)</h3>'
            f"{items_html}"
        )
    body = "".join(sections)
    return f"""
    <html><body style="font-family:-apple-system,sans-serif;max-width:640px;margin:0 auto;">
      <h2 style="font-size:18px;">새로운 공모/지원사업/교육 알림</h2>
      {body}
    </body></html>
    """


def send_email(subject: str, html_body: str, to_addr: str = None) -> None:
    from_addr = os.environ["EMAIL_ADDRESS"]
    app_password = os.environ["EMAIL_APP_PASSWORD"]
    to_addr = to_addr or os.environ.get("ALERT_TO_EMAIL", from_addr)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(from_addr, app_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())


def group_by_site(items: list) -> dict:
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get("site_label", item.get("site"))].append(item)
    return dict(grouped)
