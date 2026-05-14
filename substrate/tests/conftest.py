from typing import Callable, Dict

import pytest
from fastapi.testclient import TestClient

from accounts import auth, models
from accounts.main import app


@pytest.fixture(autouse=True)
def _reset_state():
    """Clear users + tokens between tests so order does not matter."""
    models.store.reset()
    models.seed(models.store)
    auth._clear_tokens()
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    r = client.post(
        "/auth/login",
        json={"username": "root", "password": "root123"},
    )
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture()
def user_token(client: TestClient) -> str:
    r = client.post(
        "/auth/login",
        json={"username": "alice", "password": "alice123"},
    )
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture()
def auth_header() -> Callable[[str], Dict[str, str]]:
    def _h(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}
    return _h
