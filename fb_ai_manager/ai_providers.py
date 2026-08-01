"""Gọi API của các nhà cung cấp AI (Groq, Gemini, Claude) để sinh nội dung bài viết."""
import requests

TIMEOUT = 60


class AIProviderError(Exception):
    pass


def generate_post(provider: str, api_key: str, prompt: str) -> str:
    provider = (provider or "").lower().strip()
    if not api_key:
        raise AIProviderError(f"Chưa nhập API key cho {provider}.")

    system_prompt = (
        "Bạn là trợ lý viết bài đăng Facebook. Viết một bài đăng ngắn gọn, tự nhiên, "
        "hấp dẫn bằng tiếng Việt (trừ khi người dùng yêu cầu ngôn ngữ khác). "
        "Không thêm giải thích, chỉ trả về nội dung bài đăng."
    )

    if provider == "groq":
        return _call_groq(api_key, system_prompt, prompt)
    if provider == "gemini":
        return _call_gemini(api_key, system_prompt, prompt)
    if provider == "claude":
        return _call_claude(api_key, system_prompt, prompt)
    raise AIProviderError(f"Không hỗ trợ nhà cung cấp AI: {provider}")


def _post_json(url: str, **kwargs) -> requests.Response:
    try:
        return requests.post(url, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as exc:
        raise AIProviderError(f"Không kết nối được tới AI: {exc}") from exc


def _call_groq(api_key: str, system_prompt: str, prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
    }
    resp = _post_json(url, headers=headers, json=payload)
    if not resp.ok:
        raise AIProviderError(f"Groq lỗi ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _call_gemini(api_key: str, system_prompt: str, prompt: str) -> str:
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.8},
    }
    resp = _post_json(url, json=payload)
    if not resp.ok:
        raise AIProviderError(f"Gemini lỗi ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as exc:
        raise AIProviderError(f"Gemini trả về phản hồi không hợp lệ: {data}") from exc


def _call_claude(api_key: str, system_prompt: str, prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "claude-sonnet-5",
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = _post_json(url, headers=headers, json=payload)
    if not resp.ok:
        raise AIProviderError(f"Claude lỗi ({resp.status_code}): {resp.text[:300]}")
    data = resp.json()
    try:
        return data["content"][0]["text"].strip()
    except (KeyError, IndexError) as exc:
        raise AIProviderError(f"Claude trả về phản hồi không hợp lệ: {data}") from exc
