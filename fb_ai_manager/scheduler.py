"""Luồng nền: kiểm tra bài đã lên lịch và tự đăng khi tới giờ."""
import threading
from datetime import datetime

from db import get_conn
from facebook_api import post_to_page, FacebookAPIError

CHECK_INTERVAL_SECONDS = 30


def _publish_due_posts():
    # scheduled_at đến từ <input type="datetime-local"> nên là giờ local, không kèm timezone.
    # So sánh bằng giờ local của máy chạy tool cho khớp.
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
    with get_conn() as conn:
        due = conn.execute(
            """
            SELECT posts.id, posts.content, pages.page_id, pages.access_token
            FROM posts JOIN pages ON pages.id = posts.page_row_id
            WHERE posts.status = 'scheduled' AND posts.scheduled_at <= ?
            """,
            (now_iso,),
        ).fetchall()

        for row in due:
            try:
                fb_post_id = post_to_page(row["page_id"], row["access_token"], row["content"])
                conn.execute(
                    "UPDATE posts SET status='posted', posted_at=?, fb_post_id=?, error=NULL WHERE id=?",
                    (datetime.now().isoformat(), fb_post_id, row["id"]),
                )
            except FacebookAPIError as exc:
                conn.execute(
                    "UPDATE posts SET status='failed', error=? WHERE id=?",
                    (str(exc), row["id"]),
                )


def _loop(stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            _publish_due_posts()
        except Exception as exc:  # noqa: BLE001 - nền chạy độc lập, không được để crash luồng
            print(f"[scheduler] lỗi khi kiểm tra bài lên lịch: {exc}")
        stop_event.wait(CHECK_INTERVAL_SECONDS)


def start_scheduler() -> threading.Event:
    stop_event = threading.Event()
    thread = threading.Thread(target=_loop, args=(stop_event,), daemon=True)
    thread.start()
    return stop_event
