from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException

from accounts.auth import current_user, require_admin
from accounts.models import User, now_iso, store
from accounts.schemas import AccountView, DeleteRequest, RestoreRequest


router = APIRouter(prefix="/accounts", tags=["accounts"])


def _view(user: User) -> AccountView:
    return AccountView(
        username=user.username,
        email=user.email,
        org_name=user.org_name,
        display_name=user.display_name,
        role=user.role,
        is_admin=user.is_admin,
        deleted_at=user.deleted_at,
        deletion_reason=user.deletion_reason,
        restored_at=user.restored_at,
        restored_by=user.restored_by,
    )


@router.get("", response_model=List[AccountView])
def list_accounts(caller: User = Depends(current_user)) -> List[AccountView]:
    require_admin(caller)
    return [_view(u) for u in store.list_active()]


@router.get("/{username}", response_model=AccountView)
def get_account(username: str, caller: User = Depends(current_user)) -> AccountView:
    require_admin(caller)
    target = store.get(username)
    if target is None:
        raise HTTPException(status_code=404, detail="not found")
    return _view(target)


@router.patch("/{username}", response_model=AccountView)
def update_account(
    username: str,
    payload: Dict[str, Any] = Body(...),
    caller: User = Depends(current_user),
) -> AccountView:
    require_admin(caller)
    target = store.get(username)
    if target is None:
        raise HTTPException(status_code=404, detail="not found")
    for key, value in payload.items():
        if hasattr(target, key):
            setattr(target, key, value)
    return _view(target)


@router.delete("/{username}", response_model=AccountView)
def soft_delete_account(
    username: str,
    payload: DeleteRequest,
    caller: User = Depends(current_user),
) -> AccountView:
    require_admin(caller)
    target = store.get(username)
    if target is None:
        raise HTTPException(status_code=404, detail="not found")
    if target.deleted_at is not None:
        raise HTTPException(status_code=409, detail="already deleted")
    target.deleted_at = now_iso()
    target.deletion_reason = payload.reason
    target.restored_at = None
    target.restored_by = None
    return _view(target)


@router.post("/{username}/restore", response_model=AccountView)
def restore_account(
    username: str,
    payload: RestoreRequest,
    caller: User = Depends(current_user),
) -> AccountView:
    require_admin(caller)
    target = store.get(username)
    if target is None:
        raise HTTPException(status_code=404, detail="not found")
    if target.deleted_at is None:
        raise HTTPException(status_code=409, detail="account is not deleted")
    target.deleted_at = None
    target.deletion_reason = None
    target.restored_at = now_iso()
    target.restored_by = caller.username
    return _view(target)
