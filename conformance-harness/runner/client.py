import httpx


class ConformanceClient:

    def __init__(self, base_url: str, verify_ssl: bool = False):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            verify=verify_ssl,
            timeout=30.0,
            headers={
                "Content-Type": "application/json"
            }
        )

    def get(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        response = self.client.get(url, **kwargs)
        response.raise_for_status()
        return response

    def post(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        response = self.client.post(url, **kwargs)
        response.raise_for_status()
        return response

    def close(self):
        self.client.close()