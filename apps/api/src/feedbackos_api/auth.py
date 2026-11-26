from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from hmac import digest
from re import compile
from secrets import token_urlsafe
from unicodedata import normalize
from uuid import UUID

from argon2 import PasswordHasher, profiles
from argon2.exceptions import InvalidHashError, VerificationError
from email_validator import EmailNotValidError, validate_email
from pydantic import SecretStr
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session as DBSession

from feedbackos_api.config import get_settings
from feedbackos_api.contracts import ErrorCode, FieldError
from feedbackos_api.database import Database, get_database
from feedbackos_api.errors import ApiException
from feedbackos_api.models import Session, User

PASSWORD_MIN_LENGTH = 15
PASSWORD_MAX_LENGTH = 128
SESSION_TTL = timedelta(days=7)
_TOKEN_PATTERN = compile(r"[A-Za-z0-9_-]{43}")  # token_urlsafe(32) without padding
_PASSWORD_HASHER = PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)


@dataclass(frozen=True, slots=True)
class UserIdentity:
    id: UUID
    email: str


@dataclass(frozen=True, slots=True)
class IssuedSession:
    user: UserIdentity
    token: SecretStr
    expires_at: datetime


def normalize_email(email: str) -> str:
    try:
        validated = validate_email(
            email.strip(), check_deliverability=False, allow_smtputf8=False
        )
    except EmailNotValidError:
        raise ApiException(
            ErrorCode.REQUEST_INVALID, field_errors=[FieldError(field="email", code="invalid")]
        ) from None
    assert validated.ascii_email is not None  # SMTPUTF8 is disabled.
    return validated.ascii_email.lower()


class AuthService:
    def __init__(self, database: Database, session_secret: SecretStr) -> None:
        self._database = database
        self._session_key = session_secret.get_secret_value().encode("utf-8")
        self._dummy_password_hash = _PASSWORD_HASHER.hash(token_urlsafe(32))

    def register(self, email: str, password: str) -> IssuedSession:
        email = normalize_email(email)
        password = normalize("NFC", password)
        if not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH or password.isspace():
            raise ApiException(
                ErrorCode.REQUEST_INVALID,
                field_errors=[FieldError(field="password", code="invalid_length_or_blank")],
            )
        try:
            password_hash = _PASSWORD_HASHER.hash(password)
        except UnicodeEncodeError:
            raise ApiException(
                ErrorCode.REQUEST_INVALID,
                field_errors=[FieldError(field="password", code="invalid_unicode")],
            ) from None

        with self._database.transaction() as db_session:
            user_id = db_session.scalar(
                insert(User)
                .values(email=email, password_hash=password_hash)
                .on_conflict_do_nothing(index_elements=[User.email])
                .returning(User.id)
            )
            if user_id is None:
                raise ApiException(ErrorCode.CONFLICT)
            return self._issue(db_session, UserIdentity(id=user_id, email=email))

    def login(self, email: str, password: str) -> IssuedSession:
        try:
            email = normalize_email(email)
        except ApiException:
            raise ApiException(ErrorCode.AUTHENTICATION_FAILED) from None
        password = normalize("NFC", password)
        if len(password) > PASSWORD_MAX_LENGTH:
            raise ApiException(ErrorCode.AUTHENTICATION_FAILED)

        with self._database.transaction() as db_session:
            user = db_session.execute(
                select(User.id, User.password_hash).where(User.email == email)
            ).one_or_none()

        password_hash = user.password_hash if user is not None else self._dummy_password_hash
        try:
            _PASSWORD_HASHER.verify(password_hash, password)
        except (VerificationError, InvalidHashError, UnicodeEncodeError):
            raise ApiException(ErrorCode.AUTHENTICATION_FAILED) from None
        if user is None:
            raise ApiException(ErrorCode.AUTHENTICATION_FAILED)

        with self._database.transaction() as db_session:
            return self._issue(db_session, UserIdentity(id=user.id, email=email))

    def resolve_session(self, token: str | None) -> UserIdentity | None:
        if token is None or _TOKEN_PATTERN.fullmatch(token) is None:
            return None
        with self._database.transaction() as db_session:
            user = db_session.execute(
                select(User.id, User.email)
                .join(Session, Session.user_id == User.id)
                .where(
                    Session.token_hash == self._token_hash(token),
                    Session.revoked_at.is_(None),
                    Session.expires_at > func.now(),
                )
            ).one_or_none()
            return UserIdentity(id=user.id, email=user.email) if user is not None else None

    def revoke_session(self, token: str | None) -> None:
        if token is None or _TOKEN_PATTERN.fullmatch(token) is None:
            return
        with self._database.transaction() as db_session:
            db_session.execute(
                update(Session)
                .where(Session.token_hash == self._token_hash(token), Session.revoked_at.is_(None))
                .values(revoked_at=func.now())
            )

    def _issue(self, db_session: DBSession, user: UserIdentity) -> IssuedSession:
        token = token_urlsafe(32)
        expires_at = datetime.now(UTC) + SESSION_TTL
        db_session.add(
            Session(user_id=user.id, token_hash=self._token_hash(token), expires_at=expires_at)
        )
        return IssuedSession(user=user, token=SecretStr(token), expires_at=expires_at)

    def _token_hash(self, token: str) -> str:
        return digest(self._session_key, token.encode("ascii"), "sha256").hex()


@lru_cache
def get_auth_service() -> AuthService:
    session_secret = get_settings().session_secret
    assert session_secret is not None
    return AuthService(get_database(), session_secret)
