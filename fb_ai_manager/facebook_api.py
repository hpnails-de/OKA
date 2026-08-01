"""Đăng bài lên Facebook Page qua Graph API."""
import requests

GRAPH_VERSION = "v19.0"
TIMEOUT = 30


class FacebookAPIError(Exception):
    pass


def verify_page(page_id: str, access_token: str) -> dict:
    """Kiểm tra token hợp lệ và trả về tên trang."""
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}"
    try:
        resp = requests.get(url, params={"fields": "id,name", "access_token": access_token}, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        raise FacebookAPIError(f"Không kết nối được tới Facebook: {exc}") from exc
    if not resp.ok:
        raise FacebookAPIError(_extract_error(resp))
    return resp.json()


def post_to_page(page_id: str, access_token: str, message: str) -> str:
    """Đăng bài lên Facebook Page. Trả về fb post id."""
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/feed"
    try:
        resp = requests.post(
            url,
            data={"message": message, "access_token": access_token},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        raise FacebookAPIError(f"Không kết nối được tới Facebook: {exc}") from exc
    if not resp.ok:
        raise FacebookAPIError(_extract_error(resp))
    data = resp.json()
    post_id = data.get("id")
    if not post_id:
        raise FacebookAPIError(f"Facebook không trả về post id: {data}")
    return post_id


def _extract_error(resp) -> str:
    try:
        data = resp.json()
        err = data.get("error", {})
        return f"Facebook lỗi ({resp.status_code}): {err.get('message', resp.text[:300])}"
    except ValueError:
        return f"Facebook lỗi ({resp.status_code}): {resp.text[:300]}"
