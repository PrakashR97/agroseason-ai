"""Thin clients for Serper.dev and OpenAI. Tests replace the factories with mocks."""
from __future__ import annotations

import json
import time

import httpx

from app.config import get_settings


class ProviderError(Exception):
    pass


class NotConfigured(ProviderError):
    pass


def _post_with_retry(url: str, headers: dict, payload: dict, attempts: int = 3) -> dict:
    s = get_settings()
    delay = 1.0
    last: Exception | None = None
    for i in range(attempts):
        try:
            r = httpx.post(url, headers=headers, json=payload, timeout=s.http_timeout_seconds * 2)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                last = ProviderError(f"HTTP {r.status_code}")
            else:
                raise ProviderError(f"HTTP {r.status_code}")
        except httpx.HTTPError as e:
            last = e
        if i < attempts - 1:
            time.sleep(delay)
            delay *= 2
    raise ProviderError(f"Request failed after {attempts} attempts: {last}")


class SerperClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise NotConfigured("SERPER_API_KEY is not configured")
        self.headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    def search(self, query: str, num: int = 8) -> list[dict]:
        data = _post_with_retry("https://google.serper.dev/search", self.headers,
                                {"q": query, "gl": "in", "num": num})
        return data.get("organic", [])

    def images(self, query: str, num: int = 10) -> list[dict]:
        data = _post_with_retry("https://google.serper.dev/images", self.headers,
                                {"q": query, "gl": "in", "num": num})
        return data.get("images", [])


class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise NotConfigured("OPENAI_API_KEY is not configured")
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self.model = model

    def extract_json(self, system: str, user: str) -> tuple[dict, int, int]:
        """Returns (parsed_json, prompt_tokens, completion_tokens)."""
        data = _post_with_retry("https://api.openai.com/v1/chat/completions", self.headers, {
            "model": self.model, "temperature": 0, "max_tokens": 2000,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        })
        try:
            parsed = json.loads(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ProviderError("Model returned invalid JSON") from e
        usage = data.get("usage", {})
        return parsed, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def get_serper() -> SerperClient:
    return SerperClient(get_settings().serper_api_key)


def get_llm() -> OpenAIClient:
    s = get_settings()
    return OpenAIClient(s.openai_api_key, s.openai_model)
