class DummyLock:
    """A no-op context manager for tests."""
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class DummyResp:
    """Simulates a requests.Response object."""
    def __init__(self, json_data=None, status=200):
        self._json = json_data or {}
        self.status_code = status

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def make_http_get(route_to_response):
    """
    route_to_response: dict {url: DummyResp}
    Returns a fake requests.get function.
    """
    def _get(url, timeout=None):
        if url not in route_to_response:
            raise Exception(f"Unexpected GET {url}")
        return route_to_response[url]
    return _get
