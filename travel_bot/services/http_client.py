"""
HTTP Client helper for Sayohatchi Bot.
Provides unified HTTP GET and POST methods.
Uses `requests` library when installed, with automatic fallback to standard library `urllib`.
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Check if requests library is installed
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    import urllib.error

    HAS_REQUESTS = False


class HttpResponse:
    """Standardized response wrapper."""

    def __init__(self, status_code: int, text: str, data: Any = None):
        self.status_code = status_code
        self.text = text
        self._data = data

    def json(self) -> Any:
        if self._data is not None:
            return self._data
        return json.loads(self.text)


def http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 12,
) -> HttpResponse:
    """Executes an HTTP GET request with timeout and error protection."""
    if headers is None:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = "SayohatchiTelegramBot/2.0"

    if HAS_REQUESTS:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        return HttpResponse(status_code=resp.status_code, text=resp.text)
    else:
        full_url = url
        if params:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}" if "?" not in url else f"{url}&{query_string}"

        req = urllib.request.Request(full_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                body = response.read().decode("utf-8")
                return HttpResponse(status_code=status_code, text=body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            return HttpResponse(status_code=e.code, text=body)
        except Exception as e:
            logger.error("HTTP GET error to %s: %s", full_url, e)
            raise


def http_post(
    url: str,
    json_data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 12,
) -> HttpResponse:
    """Executes an HTTP POST request with timeout and error protection."""
    if headers is None:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = "SayohatchiTelegramBot/2.0"

    if HAS_REQUESTS:
        resp = requests.post(
            url, json=json_data, data=data, headers=headers, timeout=timeout
        )
        return HttpResponse(status_code=resp.status_code, text=resp.text)
    else:
        post_bytes = None
        if json_data is not None:
            post_bytes = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        elif data is not None:
            post_bytes = urllib.parse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=post_bytes, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                body = response.read().decode("utf-8")
                return HttpResponse(status_code=status_code, text=body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            return HttpResponse(status_code=e.code, text=body)
        except Exception as e:
            logger.error("HTTP POST error to %s: %s", url, e)
            raise
