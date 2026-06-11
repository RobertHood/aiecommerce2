import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ServiceError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status


def request_json(method, url, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            details = json.loads(exc.read().decode("utf-8"))
            message = details.get("error", str(exc))
        except json.JSONDecodeError:
            message = str(exc)
        raise ServiceError(message, status=exc.code) from exc
    except URLError as exc:
        raise ServiceError(f"Service unavailable: {exc.reason}") from exc
