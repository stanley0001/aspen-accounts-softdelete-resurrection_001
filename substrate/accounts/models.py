from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class User:
    username: str
    password: str
    email: str = ""
    org_name: str = ""
    display_name: str = ""
    role: str = "USER"
    is_admin: bool = False
    deleted_at: Optional[str] = None
    deletion_reason: Optional[str] = None
    restored_at: Optional[str] = None
    restored_by: Optional[str] = None


class UserStore:
    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def add(self, user: User) -> None:
        self._users[user.username] = user

    def get(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def list_active(self) -> List[User]:
        return [u for u in self._users.values() if u.deleted_at is None]

    def list_all(self) -> List[User]:
        return list(self._users.values())

    def reset(self) -> None:
        self._users.clear()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def seed(target: UserStore) -> None:
    target.add(User(
        username="root",
        password="root123",
        email="root@accounts.local",
        org_name="Platform",
        display_name="Root Admin",
        role="ADMIN",
        is_admin=True,
    ))
    target.add(User(
        username="alice",
        password="alice123",
        email="alice@accounts.local",
        org_name="Acme",
        display_name="Alice",
        role="USER",
        is_admin=False,
    ))
    target.add(User(
        username="bob",
        password="bob123",
        email="bob@accounts.local",
        org_name="Acme",
        display_name="Bob",
        role="USER",
        is_admin=False,
    ))
    # carla is an already-soft-deleted account, the canonical resurrection target
    target.add(User(
        username="carla",
        password="carla123",
        email="carla@accounts.local",
        org_name="Acme",
        display_name="Carla",
        role="USER",
        is_admin=False,
        deleted_at="2025-09-12T10:14:00+00:00",
        deletion_reason="account closure requested",
    ))


store = UserStore()
seed(store)
