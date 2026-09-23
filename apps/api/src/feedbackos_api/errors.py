from __future__ import annotations

from collections.abc import Mapping, Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from feedbackos_api.contracts import (
    ERROR_DEFINITIONS,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    FieldError,
)


class ApiException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        *,
        field_errors: Sequence[FieldError] = (),
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.field_errors = tuple(field_errors)
        self.headers = dict(headers) if headers else None


def error_response(
    code: ErrorCode,
    *,
    status_code: int | None = None,
    field_errors: Sequence[FieldError] = (),
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    definition = ERROR_DEFINITIONS[code]
    body = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=definition.message,
            retryable=definition.retryable,
            field_errors=list(field_errors),
        ),
    )
    return JSONResponse(
        status_code=status_code or definition.status_code,
        content=body.model_dump(mode="json"),
        headers=headers,
    )


def _field_errors(exc: RequestValidationError) -> list[FieldError]:
    errors: list[FieldError] = []
    for issue in exc.errors():
        location = issue.get("loc", ())
        field = ".".join(str(part) for part in location if part not in {"body", "query", "path"})
        errors.append(
            FieldError(
                field=field or "request",
                code=str(issue.get("type", "invalid")),
            ),
        )
    return errors


def _http_error_code(status_code: int) -> ErrorCode:
    if status_code == 401:
        return ErrorCode.AUTHENTICATION_FAILED
    if status_code == 403:
        return ErrorCode.ACCESS_DENIED
    if status_code == 404:
        return ErrorCode.RESOURCE_NOT_FOUND
    if status_code == 409:
        return ErrorCode.CONFLICT
    if status_code == 422:
        return ErrorCode.REQUEST_INVALID
    if status_code == 503:
        return ErrorCode.RETRYABLE_FAILURE
    return ErrorCode.INTERNAL_ERROR if status_code >= 500 else ErrorCode.REQUEST_INVALID


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiException)
    async def handle_api_exception(_request: Request, exc: ApiException) -> JSONResponse:
        return error_response(
            exc.code,
            field_errors=exc.field_errors,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return error_response(ErrorCode.REQUEST_INVALID, field_errors=_field_errors(exc))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return error_response(
            _http_error_code(exc.status_code),
            status_code=exc.status_code,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_request: Request, _exc: Exception) -> JSONResponse:
        return error_response(ErrorCode.INTERNAL_ERROR)
