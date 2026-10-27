import os

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")
TIMEOUT_SECONDS = 10


class ApiClient:
    def __init__(self, base_url, session):
        self.base_url = base_url.rstrip("/")
        self.session = session

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", TIMEOUT_SECONDS)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


@pytest.fixture(scope="session")
def api():
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"Accept": "application/json"})
    yield ApiClient(BASE_URL, session)
    session.close()


@pytest.fixture
def new_post():
    return {"title": "QA test post", "body": "Created by the automated test suite", "userId": 1}
