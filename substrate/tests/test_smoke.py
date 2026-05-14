"""Smoke tests — encode the legitimate-flow surface of the accounts service.

These cover login, profile reads, safe-field admin PATCH, the explicit
delete endpoint, and the explicit restore endpoint. They deliberately do
not exercise resurrection through the PATCH surface — that surface is
what the benchmarked agent is supposed to discover and cover with its
own test suite.
"""


def test_login_admin_returns_token(client):
    r = client.post(
        "/auth/login",
        json={"username": "root", "password": "root123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token"]
    assert body["username"] == "root"
    assert body["role"] == "ADMIN"


def test_login_user_returns_token(client):
    r = client.post(
        "/auth/login",
        json={"username": "alice", "password": "alice123"},
    )
    assert r.status_code == 200
    assert r.json()["token"]


def test_login_wrong_password_is_401(client):
    r = client.post(
        "/auth/login",
        json={"username": "alice", "password": "nope"},
    )
    assert r.status_code == 401


def test_login_deleted_account_is_401(client):
    # carla is seeded as already soft-deleted
    r = client.post(
        "/auth/login",
        json={"username": "carla", "password": "carla123"},
    )
    assert r.status_code == 401


def test_list_accounts_admin_excludes_deleted(client, admin_token, auth_header):
    r = client.get("/accounts", headers=auth_header(admin_token))
    assert r.status_code == 200
    usernames = {u["username"] for u in r.json()}
    assert "alice" in usernames
    assert "bob" in usernames
    assert "carla" not in usernames  # carla is soft-deleted


def test_list_accounts_non_admin_is_403(client, user_token, auth_header):
    r = client.get("/accounts", headers=auth_header(user_token))
    assert r.status_code == 403


def test_get_account_returns_lifecycle_fields(client, admin_token, auth_header):
    r = client.get("/accounts/carla", headers=auth_header(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "carla"
    assert body["deleted_at"] is not None
    assert body["deletion_reason"] == "account closure requested"


def test_admin_patch_display_name(client, admin_token, auth_header):
    r = client.patch(
        "/accounts/alice",
        headers=auth_header(admin_token),
        json={"display_name": "Alice A."},
    )
    assert r.status_code == 200
    after = client.get("/accounts/alice", headers=auth_header(admin_token)).json()
    assert after["display_name"] == "Alice A."


def test_admin_patch_email(client, admin_token, auth_header):
    r = client.patch(
        "/accounts/bob",
        headers=auth_header(admin_token),
        json={"email": "bob+new@accounts.local"},
    )
    assert r.status_code == 200
    after = client.get("/accounts/bob", headers=auth_header(admin_token)).json()
    assert after["email"] == "bob+new@accounts.local"


def test_delete_account_marks_deleted(client, admin_token, auth_header):
    r = client.request(
        "DELETE",
        "/accounts/bob",
        headers=auth_header(admin_token),
        json={"reason": "user requested off-boarding"},
    )
    assert r.status_code == 200
    after = client.get("/accounts/bob", headers=auth_header(admin_token)).json()
    assert after["deleted_at"] is not None
    assert after["deletion_reason"] == "user requested off-boarding"


def test_delete_excludes_from_listing(client, admin_token, auth_header):
    client.request(
        "DELETE",
        "/accounts/bob",
        headers=auth_header(admin_token),
        json={"reason": "off-boarding"},
    )
    listing = client.get("/accounts", headers=auth_header(admin_token)).json()
    usernames = {u["username"] for u in listing}
    assert "bob" not in usernames


def test_restore_clears_deleted_at(client, admin_token, auth_header):
    r = client.post(
        "/accounts/carla/restore",
        headers=auth_header(admin_token),
        json={"note": "false closure"},
    )
    assert r.status_code == 200
    after = client.get("/accounts/carla", headers=auth_header(admin_token)).json()
    assert after["deleted_at"] is None
    assert after["restored_at"] is not None
    assert after["restored_by"] == "root"


def test_restore_active_account_is_409(client, admin_token, auth_header):
    r = client.post(
        "/accounts/alice/restore",
        headers=auth_header(admin_token),
        json={},
    )
    assert r.status_code == 409


def test_unauthenticated_get_accounts_is_401(client):
    r = client.get("/accounts")
    assert r.status_code == 401


def test_admin_patch_missing_account_is_404(client, admin_token, auth_header):
    r = client.patch(
        "/accounts/nobody",
        headers=auth_header(admin_token),
        json={"display_name": "x"},
    )
    assert r.status_code == 404
