import requests
from typing import Any, Dict, Optional

__all__ = ["fetch", "fetch_text", "fetch_json"]


def fetch(url: str, params: Optional[Dict[str, Any]] = None,
          headers: Optional[Dict[str, str]] = None,
          timeout: int = 10) -> requests.Response:
    """Perform a GET request to *url* and return the ``requests.Response``.

    Args:
        url: Target URL.
        params: Optional query parameters.
        headers: Optional HTTP headers.
        timeout: Seconds to wait for a response before raising.

    Returns:
        The ``Response`` object.

    Raises:
        requests.RequestException: Propagated network‑related errors.
    """
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def fetch_text(url: str, **kwargs) -> str:
    """Convenience wrapper that returns the response body as plain text."""
    return fetch(url, **kwargs).text


def fetch_json(url: str, **kwargs) -> Any:
    """Convenience wrapper that parses the response as JSON and returns the object."""
    return fetch(url, **kwargs).json()