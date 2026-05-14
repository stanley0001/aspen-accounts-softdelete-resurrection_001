from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str


class AccountView(BaseModel):
    username: str
    email: str
    org_name: str
    display_name: str
    role: str
    is_admin: bool
    deleted_at: Optional[str] = None
    deletion_reason: Optional[str] = None
    restored_at: Optional[str] = None
    restored_by: Optional[str] = None


class UserAdminUpdate(BaseModel):
    """Profile fields an admin can edit on any user. Lifecycle fields
    (deleted_at, deletion_reason, restored_at, restored_by) are intentionally
    excluded — those move only through the explicit delete / restore endpoints.
    """
    display_name: Optional[str] = None
    email: Optional[str] = None
    org_name: Optional[str] = None
    role: Optional[str] = None


class DeleteRequest(BaseModel):
    reason: str


class RestoreRequest(BaseModel):
    note: Optional[str] = None
