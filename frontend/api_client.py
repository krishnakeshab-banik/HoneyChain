"""HTTP helpers for the Streamlit UI. No page logic lives here."""

from __future__ import annotations

from typing import Any

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"


def _handle(response: requests.Response) -> Any:
    response.raise_for_status()
    if response.status_code == 204 or not response.content:
        return None
    if "application/json" in response.headers.get("content-type", ""):
        return response.json()
    return response.content


def api_get(path: str, timeout: int = 8) -> Any:
    try:
        return _handle(requests.get(f"{API_BASE_URL}{path}", timeout=timeout))
    except requests.HTTPError as error:
        detail = _error_detail(error)
        st.error(detail)
        return None
    except requests.RequestException as error:
        st.error("HoneyChain cannot reach the backend API. Start FastAPI first.")
        st.caption(f"Technical detail: {error}")
        return None


def api_send(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=8,
        )
        return _handle(response)
    except requests.HTTPError as error:
        st.error(_error_detail(error))
        return None
    except requests.RequestException as error:
        st.error("HoneyChain cannot reach the backend API. Start FastAPI first.")
        st.caption(f"Technical detail: {error}")
        return None


def _error_detail(error: requests.HTTPError) -> str:
    if error.response is None:
        return str(error)
    try:
        body = error.response.json()
        detail = body.get("detail", body)
        return f"API {error.response.status_code}: {detail}"
    except ValueError:
        return f"API {error.response.status_code}: {error.response.text}"
