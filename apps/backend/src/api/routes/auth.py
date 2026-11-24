from fastapi import APIRouter, Depends, HTTPException

from api.auth import create_access_token, get_current_user
from api.schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from session.users import UserRecord, UserStore

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _user_response(user: UserRecord) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        is_enabled=user.is_enabled,
    )


def _auth_response(user: UserRecord) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user),
        user=_user_response(user),
    )


def _require_enabled(user: UserRecord) -> UserRecord:
    if not user.is_enabled:
        raise HTTPException(
            status_code=403,
            detail=(
                "Your User ID does not have access to this application. "
                "Contact your system administrator to enable your account."
            ),
        )
    return user


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest) -> AuthResponse:
    try:
        user = UserStore().register(
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest) -> AuthResponse:
    store = UserStore()
    user = store.get_by_username(request.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Username not found. Please register at /register.")
    _require_enabled(user)
    if request.browser_id:
        store.touch_browser(request.browser_id, user.user_id)
    return _auth_response(user)


@router.get("/me", response_model=UserResponse)
def me(user: UserRecord = Depends(get_current_user)) -> UserResponse:
    _require_enabled(user)
    return _user_response(user)
