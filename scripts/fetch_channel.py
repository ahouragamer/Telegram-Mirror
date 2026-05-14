import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_message(el):
    msg = {}

    msg_id = el.get("data-post", "")
    msg["id"] = msg_id

    date_el = el.select_one(".tgme_widget_message_date time")
    if date_el:
        msg["date_raw"] = date_el.get("datetime", "")
        try:
            dt = datetime.fromisoformat(msg["date_raw"].replace("Z", "+00:00"))
            msg["date"] = dt.strftime("%H:%M · %d %b %Y")
        except Exception:
            msg["date"] = msg["date_raw"]
    else:
        msg["date"] = ""
        msg["date_raw"] = ""

    views_el = el.select_one(".tgme_widget_message_views")
    msg["views"] = views_el.get_text(strip=True) if views_el else ""

    # ── متن + لینک‌های امبد شده ──
    text_el = el.select_one(".tgme_widget_message_text")
    if text_el:
        # کلون می‌کنیم تا DOM اصلی رو خراب نکنیم
        import copy
        text_clone = copy.copy(text_el)
        # هر لینک رو به فرمت "متن (url)" تبدیل می‌کنیم
        for a in text_clone.find_all("a"):
            href = a.get("href", "").strip()
            link_text = a.get_text(strip=True)
            if href and href != link_text:
                a.replace_with(f"{link_text} ({href})")
            elif href:
                a.replace_with(href)
        msg["text"] = text_clone.get_text(separator="\n", strip=True)
    else:
        msg["text"] = ""

    # Album (multiple photos)
    album_photos = el.select(".tgme_widget_message_photo_wrap")
    msg["album"] = []
    for ph in album_photos:
        style = ph.get("style", "")
        m = re.search(r"url\('(.+?)'\)", style)
        if m:
            msg["album"].append(m.group(1))

    # Single photo
    photo_el = el.select_one(".tgme_widget_message_photo_wrap")
    if photo_el:
        style = photo_el.get("style", "")
        m = re.search(r"url\('(.+?)'\)", style)
        msg["photo"] = m.group(1) if m else ""
    else:
        msg["photo"] = ""

    # Video
    video_el = el.select_one("video")
    msg["video"] = video_el.get("src", "") if video_el else ""

    # Video thumbnail
    if video_el:
        thumb = el.select_one(".tgme_widget_message_video_thumb")
        if thumb:
            style = thumb.get("style", "")
            m = re.search(r"url\('(.+?)'\)", style)
            msg["video_thumb"] = m.group(1) if m else ""
        else:
            msg["video_thumb"] = ""
        duration_el = el.select_one(".tgme_widget_message_video_duration")
        msg["video_duration"] = duration_el.get_text(strip=True) if duration_el else ""
    else:
        msg["video_thumb"] = ""
        msg["video_duration"] = ""

    # Document
    doc_el = el.select_one(".tgme_widget_message_document")
    if doc_el:
        title_el = doc_el.select_one(".tgme_widget_message_document_title")
        extra_el = doc_el.select_one(".tgme_widget_message_document_extra")
        msg["doc_title"] = title_el.get_text(strip=True) if title_el else ""
        msg["doc_extra"] = extra_el.get_text(strip=True) if extra_el else ""
        link_wrap = el.select_one("a.tgme_widget_message_document_wrap, a[href*='tg_file']")
        msg["doc_url"] = link_wrap.get("href", "") if link_wrap else ""
    else:
        msg["doc_title"] = ""
        msg["doc_extra"] = ""
        msg["doc_url"] = ""

    # Audio
    audio_el = el.select_one("audio")
    msg["audio_url"] = audio_el.get("src", "") if audio_el else ""

    # Forwarded
    fwd_el = el.select_one(".tgme_widget_message_forwarded_from")
    msg["forwarded_from"] = fwd_el.get_text(strip=True) if fwd_el else ""

    # Poll
    poll_el = el.select_one(".tgme_widget_message_poll")
    if poll_el:
        q = poll_el.select_one(".tgme_widget_message_poll_question")
        opts = poll_el.select(".tgme_widget_message_poll_option_text")
        msg["poll_question"] = q.get_text(strip=True) if q else ""
        msg["poll_options"] = [o.get_text(strip=True) for o in opts]
    else:
        msg["poll_question"] = ""
        msg["poll_options"] = []

    # Reactions
    reactions = []
    for r in el.select(".tgme_widget_message_reaction"):
        emoji_el = r.select_one(".tgme_widget_message_reaction_emoji")
        count_el = r.select_one(".tgme_widget_message_reaction_count")
        if emoji_el:
            emoji = emoji_el.get_text(strip=True)
            count = count_el.get_text(strip=True) if count_el else ""
            reactions.append(f"{emoji} {count}".strip())
    msg["reactions"] = reactions

    msg_url_el = el.select_one(".tgme_widget_message_date")
    msg["url"] = msg_url_el.get("href", "") if msg_url_el else ""

    return msg


def fetch_channel(channel, count):
    messages = []
    channel_info = {"name": channel, "title": "", "description": "", "avatar": "", "members": ""}
    base_url = f"https://t.me/s/{channel}"
    before = None

    print(f"[+] Fetching @{channel}")

    while len(messages) < count:
        url = base_url if before is None else f"{base_url}?before={before}"
        print(f"    → {url}")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"[!] Error fetching URL: {e}")
            break

        try:
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            print(f"[!] Error parsing HTML: {e}")
            break

        if before is None:
            try:
                title_el = soup.select_one(".tgme_channel_info_header_title")
                if title_el:
                    channel_info["title"] = title_el.get_text(strip=True)
                desc_el = soup.select_one(".tgme_channel_info_description")
                if desc_el:
                    channel_info["description"] = desc_el.get_text(strip=True)
                avatar_el = soup.select_one(".tgme_page_photo_image img, .tgme_channel_info_header_image img")
                if avatar_el:
                    channel_info["avatar"] = avatar_el.get("src", "")
                members_el = soup.select_one(".tgme_channel_info_counter .counter_value")
                if members_el:
                    channel_info["members"] = members_el.get_text(strip=True)
                print(f"[+] Channel: {channel_info['title']} ({channel_info['members']} members)")
            except Exception as e:
                print(f"[!] Error parsing channel info: {e}")

        try:
            bubbles = soup.select(".tgme_widget_message_wrap")
            if not bubbles:
                print("[!] No messages found.")
                break

            page_messages = []
            for b in bubbles:
                inner = b.select_one(".tgme_widget_message")
                if inner:
                    page_messages.append(parse_message(inner))

            if not page_messages:
                break

            messages = page_messages + messages
            ids = [int(m["id"].split("/")[-1]) for m in page_messages if m["id"]]
            if not ids:
                break
            before = min(ids)

            if len(messages) >= count:
                break

            time.sleep(0.8)
        except Exception as e:
            print(f"[!] Error processing messages: {e}")
            break

    messages = messages[-count:]
    print(f"[+] Got {len(messages)} messages")
    return messages, channel_info


def fetch_single_post(channel: str, post_id: str):
    """یه پست خاص رو با ID اون می‌خونه"""
    next_id = int(post_id) + 1
    url = f"https://t.me/s/{channel}?before={next_id}"
    print(f"[+] Fetching single post: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Error fetching page: {e}")
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "lxml")

    # پیدا کردن پست با data-post
    target = f"{channel}/{post_id}"
    el = soup.find(attrs={"data-post": target})
    if not el:
        el = soup.find(attrs={"data-post": post_id})
    if not el:
        all_posts = soup.select(".tgme_widget_message")
        if all_posts:
            el = all_posts[-1]
            print(f"[~] Exact post not found, using last post on page")
        else:
            print(f"[!] Post {post_id} not found. Channel may be private or post deleted.")
            sys.exit(1)

    # اطلاعات کانال
    channel_info = {"name": channel, "title": "", "description": "", "avatar": "", "members": ""}
    title_el = soup.select_one(".tgme_channel_info_header_title")
    if title_el:
        channel_info["title"] = title_el.get_text(strip=True)
    avatar_el = soup.select_one(".tgme_page_photo_image img, .tgme_channel_info_header_image img")
    if avatar_el:
        channel_info["avatar"] = avatar_el.get("src", "")
    members_el = soup.select_one(".tgme_channel_info_counter .counter_value")
    if members_el:
        channel_info["members"] = members_el.get_text(strip=True)

    return [parse_message(el)], channel_info


def parse_post_url(url: str):
    """لینک پست رو به channel و post_id تبدیل می‌کنه"""
    url = url.strip().rstrip("/").split("?")[0]
    m = re.search(r"t(?:elegram)?\.me/([^/]+)/(\d+)", url)
    if m:
        return m.group(1), m.group(2)
    return None, None


def escape_md(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def download_box(post_url: str, label: str, extra: str = "") -> list:
    """
    باکس دانلود با لینک پست در code block
    کاربر کپی می‌کنه و توی اکشن ⬇️ Download Telegram Post paste می‌کنه
    """
    lines = []
    lines.append('<table><tr><td>')
    lines.append(f'<b>⬇️ {label}</b>')
    if extra:
        lines.append(f'<br/><sub>{extra}</sub>')
    lines.append('<br/><br/>')
    lines.append('<sub>📋 لینک پست را کپی کن، سپس برو <b>Actions ← ⬇️ Download Telegram Post</b> و paste کن:</sub>')
    lines.append('</td></tr>')
    lines.append('<tr><td>')
    lines.append(f'\n```\n{post_url}\n```\n')
    lines.append('</td></tr></table>')
    lines.append('')
    return lines


def render_message_md(m):
    lines = []

    lines.append('<table width="100%">')
    lines.append('<tr><td width="100%">')
    lines.append("")

    # ── فوروارد ──
    if m.get("forwarded_from"):
        lines.append(f"> ↪ **فوروارد از:** {escape_md(m['forwarded_from'])}")
        lines.append("")

    # ── آلبوم ──
    if m.get("album") and len(m["album"]) > 1:
        for ph in m["album"]:
            lines.append(f'<a href="{ph}"><img src="{ph}" width="400"/></a>')
            lines.append("<br/>")
        lines.append("")
    elif m.get("photo"):
        ph = m["photo"]
        lines.append(f'<a href="{ph}"><img src="{ph}" width="400"/></a>')
        lines.append("")

    # ── ویدیو ──
    if m.get("video"):
        thumb = m.get("video_thumb", "")
        duration = m.get("video_duration", "")
        post_url = m.get("url", "")
        if thumb:
            play_badge = "https://img.shields.io/badge/%E2%96%B6%EF%B8%8F_Play-000000?style=for-the-badge"
            lines.append(f'<a href="{post_url}"><img src="{thumb}" width="400"/></a><br/>')
            lines.append(f'<a href="{post_url}"><img src="{play_badge}" height="80"/></a>')
            lines.append("")
        extra = f"🕐 {duration}" if duration else ""
        lines.extend(download_box(post_url, "دانلود ویدیو", extra))

    # ── صدا ──
    if m.get("audio_url"):
        post_url = m.get("url", "")
        lines.extend(download_box(post_url, "دانلود فایل صوتی"))

    # ── فایل/سند ──
    if m.get("doc_title"):
        post_url = m.get("url", "")
        doc_title = escape_md(m["doc_title"])
        doc_extra = escape_md(m.get("doc_extra", ""))
        lines.extend(download_box(post_url, f"دانلود فایل — {doc_title}", doc_extra))

    # ── نظرسنجی ──
    if m.get("poll_question"):
        lines.append(f'📊 **{escape_md(m["poll_question"])}**')
        lines.append("")
        for opt in m.get("poll_options", []):
            lines.append(f"▫️ {escape_md(opt)}")
        lines.append("")

    # ── متن (با لینک‌های امبد) ──
    if m.get("text"):
        text = escape_md(m["text"])
        wrapped = "<br/>".join(text.split("\n"))
        lines.append(wrapped)
        lines.append("")

    # ── ری‌اکشن‌ها ──
    if m.get("reactions"):
        lines.append("&nbsp;&nbsp;".join(m["reactions"]))
        lines.append("")

    # ── فوتر ──
    footer_parts = []
    if m.get("views"):
        footer_parts.append(f"👁 **{m['views']}**")
    if m.get("date") and m.get("url"):
        footer_parts.append(f'[🕐 {m["date"]}]({m["url"]})')
    elif m.get("date"):
        footer_parts.append(f'🕐 {m["date"]}')

    if footer_parts:
        lines.append("<sub>" + " &nbsp;·&nbsp; ".join(footer_parts) + "</sub>")

    lines.append("")
    lines.append("</td></tr>")
    lines.append("</table>")
    lines.append("")

    return "\n".join(lines)


def render_markdown(messages, channel_info, channel, fetch_time):
    lines = []

    title = channel_info.get("title") or f"@{channel}"
    members = channel_info.get("members", "")
    desc = channel_info.get("description", "")
    avatar = channel_info.get("avatar", "")

    lines.append('<div align="center">')
    lines.append("")
    if avatar:
        lines.append(f'<img src="{avatar}" width="80" height="80"/>')
        lines.append("")
    lines.append(f"# 📡 {escape_md(title)}")
    lines.append("")

    meta = [f"**@{channel}**"]
    if members:
        meta.append(f"👥 **{members}** عضو")
    lines.append(" &nbsp;·&nbsp; ".join(meta))
    lines.append("")

    if desc:
        lines.append(f"*{escape_md(desc)}*")
        lines.append("")

    lines.append(f"🕐 آپدیت: `{fetch_time}` &nbsp;·&nbsp; 📨 **{len(messages)}** پیام")
    lines.append("")
    lines.append(f'[![باز در تلگرام](https://img.shields.io/badge/باز_کردن_در_تلگرام-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/{channel})')
    lines.append("")
    lines.append("</div>")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── پیام‌ها — جدیدترین اول ──
    for m in reversed(messages):
        lines.append(render_message_md(m))

    lines.append("---")
    lines.append("")
    lines.append('<div align="center">')
    lines.append(f"<sub>ساخته شده با ❤️ توسط TG Mirror &nbsp;·&nbsp; {fetch_time}</sub>")
    lines.append("</div>")

    return "\n".join(lines)


def main():
    try:
        parser = argparse.ArgumentParser(description="Fetch Telegram channel messages")
        parser.add_argument("--channel", required=True, help="Channel username (without @)")
        parser.add_argument("--count", type=int, default=100, help="Number of messages to fetch")
        parser.add_argument("--post", default="", help="لینک یا ID پست خاص (اختیاری)")
        args = parser.parse_args()

        channel = args.channel.lstrip("@").strip()
        if not channel:
            print("[!] Error: Channel name is empty")
            sys.exit(1)

        # ── حالت پست خاص ──
        if args.post:
            post_input = args.post.strip()
            # اگه لینک کامل بود parse کن
            if "t.me" in post_input:
                parsed_channel, post_id = parse_post_url(post_input)
                if parsed_channel:
                    channel = parsed_channel
                else:
                    print(f"[!] Cannot parse post URL: {post_input}")
                    sys.exit(1)
            else:
                # فقط عدد ID وارد شده
                post_id = post_input

            print(f"[*] Single post mode: @{channel}/{post_id}")
            messages, channel_info = fetch_single_post(channel, post_id)
        else:
            # ── حالت عادی — کل کانال ──
            count = max(10, min(args.count, 200))
            print(f"[*] Parameters: channel=@{channel}, count={count}")
            messages, channel_info = fetch_channel(channel, count)

        if not messages:
            print("[!] No messages fetched.")
            sys.exit(1)

        now = datetime.utcnow()
        fetch_time = now.strftime("%Y-%m-%d %H:%M UTC")
        file_date = now.strftime("%Y-%m-%d_%H-%M")

        md = render_markdown(messages, channel_info, channel, fetch_time)

        out_dir = Path("channels")
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[!] Error creating directory: {e}")
            sys.exit(1)

        # اگه پست خاص بود اسم فایل متفاوته
        if args.post:
            filename = f"{channel}_post{post_id}_{file_date}.md"
        else:
            filename = f"{channel}_{file_date}.md"

        out_file = out_dir / filename

        try:
            out_file.write_text(md, encoding="utf-8")
            file_size = out_file.stat().st_size
            print(f"[✓] Saved: {out_file} ({file_size} bytes)")
        except Exception as e:
            print(f"[!] Error writing file: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
