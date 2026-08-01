"""fb_ai_manager — công cụ local dùng AI (Groq/Gemini/Claude) để viết và đăng bài
lên Facebook Page. Chạy hoàn toàn trên máy bạn, không có bên thứ ba nào khác
nhìn thấy API key hay Facebook token của bạn (đều lưu trong data/fb_ai_manager.db).
"""
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash

from db import init_db, get_conn
from ai_providers import generate_post, AIProviderError
from facebook_api import verify_page, post_to_page, FacebookAPIError
from scheduler import start_scheduler

app = Flask(__name__)
app.secret_key = os.environ.get("FB_AI_MANAGER_SECRET", "dev-local-only-secret")

PROVIDERS = ["groq", "gemini", "claude"]


@app.route("/")
def dashboard():
    with get_conn() as conn:
        pages = conn.execute("SELECT * FROM pages ORDER BY label").fetchall()
        recent_posts = conn.execute(
            """
            SELECT posts.*, pages.label AS page_label
            FROM posts JOIN pages ON pages.id = posts.page_row_id
            ORDER BY posts.created_at DESC LIMIT 10
            """
        ).fetchall()
    return render_template("dashboard.html", pages=pages, recent_posts=recent_posts)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        form_type = request.form.get("form_type")
        with get_conn() as conn:
            if form_type == "ai_key":
                provider = request.form.get("provider")
                api_key = request.form.get("api_key", "").strip()
                if provider not in PROVIDERS or not api_key:
                    flash("Vui lòng chọn nhà cung cấp AI và nhập API key.", "error")
                else:
                    conn.execute(
                        """
                        INSERT INTO ai_keys (provider, api_key, updated_at) VALUES (?, ?, ?)
                        ON CONFLICT(provider) DO UPDATE SET api_key=excluded.api_key, updated_at=excluded.updated_at
                        """,
                        (provider, api_key, datetime.utcnow().isoformat()),
                    )
                    flash(f"Đã lưu API key cho {provider}.", "success")

            elif form_type == "add_page":
                label = request.form.get("label", "").strip()
                page_id = request.form.get("page_id", "").strip()
                access_token = request.form.get("access_token", "").strip()
                if not (label and page_id and access_token):
                    flash("Vui lòng điền đủ tên gợi nhớ, Page ID và Access Token.", "error")
                else:
                    try:
                        verify_page(page_id, access_token)
                    except FacebookAPIError as exc:
                        flash(f"Không thể xác thực trang: {exc}", "error")
                    else:
                        conn.execute(
                            "INSERT INTO pages (label, page_id, access_token) VALUES (?, ?, ?)",
                            (label, page_id, access_token),
                        )
                        flash(f'Đã thêm trang "{label}".', "success")

            elif form_type == "delete_page":
                page_row_id = request.form.get("page_row_id")
                conn.execute("DELETE FROM pages WHERE id = ?", (page_row_id,))
                flash("Đã xóa trang.", "success")

        return redirect(url_for("settings"))

    with get_conn() as conn:
        ai_keys = {row["provider"]: row["api_key"] for row in conn.execute("SELECT * FROM ai_keys")}
        pages = conn.execute("SELECT * FROM pages ORDER BY label").fetchall()
    return render_template("settings.html", providers=PROVIDERS, ai_keys=ai_keys, pages=pages)


@app.route("/generate", methods=["GET", "POST"])
def generate():
    with get_conn() as conn:
        ai_keys = {row["provider"]: row["api_key"] for row in conn.execute("SELECT * FROM ai_keys")}
        pages = conn.execute("SELECT * FROM pages ORDER BY label").fetchall()

    generated_content = None
    form_values = {"provider": "groq", "prompt": "", "page_row_id": "", "scheduled_at": ""}

    if request.method == "POST":
        action = request.form.get("action")
        provider = request.form.get("provider", "")
        prompt = request.form.get("prompt", "").strip()
        edited_content = request.form.get("edited_content", "").strip()
        page_row_id = request.form.get("page_row_id", "")
        scheduled_at = request.form.get("scheduled_at", "").strip()
        form_values = {
            "provider": provider,
            "prompt": prompt,
            "page_row_id": page_row_id,
            "scheduled_at": scheduled_at,
        }

        if action == "generate":
            if not prompt:
                flash("Vui lòng nhập chủ đề / yêu cầu nội dung.", "error")
            else:
                try:
                    generated_content = generate_post(provider, ai_keys.get(provider, ""), prompt)
                except AIProviderError as exc:
                    flash(str(exc), "error")

        elif action in ("post_now", "schedule"):
            if not page_row_id:
                flash("Vui lòng chọn trang Facebook để đăng.", "error")
            elif not edited_content:
                flash("Nội dung bài viết đang trống.", "error")
            else:
                generated_content = edited_content
                with get_conn() as conn:
                    page = conn.execute("SELECT * FROM pages WHERE id = ?", (page_row_id,)).fetchone()
                    if not page:
                        flash("Không tìm thấy trang đã chọn.", "error")
                    elif action == "post_now":
                        try:
                            fb_post_id = post_to_page(page["page_id"], page["access_token"], edited_content)
                        except FacebookAPIError as exc:
                            conn.execute(
                                """INSERT INTO posts
                                   (page_row_id, content, ai_provider, prompt, status, error)
                                   VALUES (?, ?, ?, ?, 'failed', ?)""",
                                (page_row_id, edited_content, provider, prompt, str(exc)),
                            )
                            flash(f"Đăng bài thất bại: {exc}", "error")
                        else:
                            conn.execute(
                                """INSERT INTO posts
                                   (page_row_id, content, ai_provider, prompt, status, posted_at, fb_post_id)
                                   VALUES (?, ?, ?, ?, 'posted', ?, ?)""",
                                (page_row_id, edited_content, provider, prompt,
                                 datetime.utcnow().isoformat(), fb_post_id),
                            )
                            flash("Đã đăng bài lên Facebook thành công!", "success")
                            return redirect(url_for("history"))
                    else:  # schedule
                        if not scheduled_at:
                            flash("Vui lòng chọn thời gian lên lịch.", "error")
                        else:
                            conn.execute(
                                """INSERT INTO posts
                                   (page_row_id, content, ai_provider, prompt, status, scheduled_at)
                                   VALUES (?, ?, ?, ?, 'scheduled', ?)""",
                                (page_row_id, edited_content, provider, prompt, scheduled_at),
                            )
                            flash("Đã lên lịch đăng bài.", "success")
                            return redirect(url_for("history"))

    return render_template(
        "generate.html",
        providers=PROVIDERS,
        ai_keys=ai_keys,
        pages=pages,
        generated_content=generated_content,
        form_values=form_values,
    )


@app.route("/history")
def history():
    with get_conn() as conn:
        posts = conn.execute(
            """
            SELECT posts.*, pages.label AS page_label
            FROM posts JOIN pages ON pages.id = posts.page_row_id
            ORDER BY posts.created_at DESC
            """
        ).fetchall()
    return render_template("history.html", posts=posts)


@app.route("/history/<int:post_id>/cancel", methods=["POST"])
def cancel_scheduled(post_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE posts SET status='cancelled' WHERE id = ? AND status = 'scheduled'",
            (post_id,),
        )
    flash("Đã hủy bài đã lên lịch.", "success")
    return redirect(url_for("history"))


def create_app():
    init_db()
    start_scheduler()
    return app


if __name__ == "__main__":
    create_app()
    app.run(host="127.0.0.1", port=5050, debug=False)
