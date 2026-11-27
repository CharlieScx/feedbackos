from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, SecretStr

from feedbackos_api.auth import AuthService, IssuedSession, UserIdentity, get_auth_service
from feedbackos_api.config import Settings, get_settings
from feedbackos_api.contracts import ErrorCode, SuccessResponse
from feedbackos_api.errors import ApiException, PrivateRoute


class AuthRoute(PrivateRoute):
    failure_message = "Authentication request failed"


router = APIRouter(prefix="/auth", tags=["auth"], route_class=AuthRoute)
Auth = Annotated[AuthService, Depends(get_auth_service)]
AppSettings = Annotated[Settings, Depends(get_settings)]


class Credentials(BaseModel):
    email: str
    password: SecretStr


class CurrentUser(BaseModel):
    id: UUID
    email: str


class CurrentUserResponse(SuccessResponse[CurrentUser]):
    pass


def require_trusted_origin(request: Request, settings: AppSettings) -> None:
    origins = request.headers.getlist("origin")
    allowed = {str(origin).removesuffix("/") for origin in settings.allowed_origins}
    if len(origins) != 1 or origins[0] not in allowed:
        raise ApiException(ErrorCode.ACCESS_DENIED)


def _cookie_name(settings: Settings) -> str:
    return "__Host-feedbackos_session" if settings.cookie_secure else "feedbackos_session"


def require_current_user(request: Request, auth: Auth, settings: AppSettings) -> UserIdentity:
    user = auth.resolve_session(request.cookies.get(_cookie_name(settings)))
    if user is None:
        raise ApiException(ErrorCode.AUTHENTICATION_FAILED)
    return user


def _user_response(user: UserIdentity) -> CurrentUserResponse:
    return CurrentUserResponse(data=CurrentUser(id=user.id, email=user.email))


def _session_response(
    issued: IssuedSession, response: Response, settings: Settings
) -> CurrentUserResponse:
    response.set_cookie(
        key=_cookie_name(settings),
        value=issued.token.get_secret_value(),
        expires=issued.expires_at,
        path="/",
        secure=settings.cookie_secure is True,
        httponly=True,
        samesite="lax",
    )
    return _user_response(issued.user)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_trusted_origin)],
)
def register(
    credentials: Credentials, response: Response, auth: Auth, settings: AppSettings
) -> CurrentUserResponse:
    issued = auth.register(credentials.email, credentials.password.get_secret_value())
    return _session_response(issued, response, settings)


@router.post("/login", dependencies=[Depends(require_trusted_origin)])
def login(
    credentials: Credentials, response: Response, auth: Auth, settings: AppSettings
) -> CurrentUserResponse:
    issued = auth.login(credentials.email, credentials.password.get_secret_value())
    return _session_response(issued, response, settings)


@router.get("/me")
def current_user(
    user: Annotated[UserIdentity, Depends(require_current_user)],
) -> CurrentUserResponse:
    return _user_response(user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_trusted_origin)],
)
def logout(request: Request, auth: Auth, settings: AppSettings) -> Response:
    cookie = _cookie_name(settings)
    auth.revoke_session(request.cookies.get(cookie))
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        cookie, path="/", secure=settings.cookie_secure is True, httponly=True, samesite="lax"
    )
    return response
