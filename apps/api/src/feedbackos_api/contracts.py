from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import ceil
from typing import Any

from pydantic import BaseModel, Field


class SuccessResponse[T](BaseModel):
    data: T


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)

    @classmethod
    def from_total(cls, *, page: int, page_size: int, total: int) -> PaginationMeta:
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if total else 0,
        )


class PaginatedResponse[T](BaseModel):
    data: list[T]
    pagination: PaginationMeta


class ErrorCode(StrEnum):
    AUTHENTICATION_FAILED = "authentication_failed"
    ACCESS_DENIED = "access_denied"
    RESOURCE_NOT_FOUND = "resource_not_found"
    REQUEST_INVALID = "request_invalid"
    FILE_INVALID = "file_invalid"
    CONFLICT = "conflict"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    RETRYABLE_FAILURE = "retryable_failure"
    INTERNAL_ERROR = "internal_error"


class FieldError(BaseModel):
    field: str
    code: str


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str
    retryable: bool
    field_errors: list[FieldError]


class ErrorResponse(BaseModel):
    error: ErrorDetail


@dataclass(frozen=True, slots=True)
class ErrorDefinition:
    status_code: int
    message: str
    retryable: bool = False


ERROR_DEFINITIONS: dict[ErrorCode, ErrorDefinition] = {
    ErrorCode.AUTHENTICATION_FAILED: ErrorDefinition(401, "认证失败，请重新登录"),
    ErrorCode.ACCESS_DENIED: ErrorDefinition(403, "没有执行此操作的权限"),
    ErrorCode.RESOURCE_NOT_FOUND: ErrorDefinition(404, "资源不存在"),
    ErrorCode.REQUEST_INVALID: ErrorDefinition(422, "请求内容无效，请检查后重试"),
    ErrorCode.FILE_INVALID: ErrorDefinition(422, "文件无效，请检查类型、大小或内容"),
    ErrorCode.CONFLICT: ErrorDefinition(409, "当前请求与资源状态冲突"),
    ErrorCode.IDEMPOTENCY_CONFLICT: ErrorDefinition(409, "该请求标识已用于其他文件"),
    ErrorCode.RETRYABLE_FAILURE: ErrorDefinition(503, "服务暂时不可用，请稍后重试", True),
    ErrorCode.INTERNAL_ERROR: ErrorDefinition(500, "服务暂时无法完成请求"),
}


API_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse, "description": "认证失败"},
    403: {"model": ErrorResponse, "description": "无权访问"},
    404: {"model": ErrorResponse, "description": "资源不存在或不可见"},
    409: {"model": ErrorResponse, "description": "资源或幂等键冲突"},
    422: {"model": ErrorResponse, "description": "请求或文件无效"},
    500: {"model": ErrorResponse, "description": "未预期的安全错误响应"},
    503: {"model": ErrorResponse, "description": "可重试的临时失败"},
}


def additional_openapi_schemas() -> dict[str, dict[str, Any]]:
    schema = PaginatedResponse[Any].model_json_schema(
        ref_template="#/components/schemas/{model}",
    )
    definitions = schema.pop("$defs", {})
    schema["title"] = "PaginatedResponse"
    return {**definitions, "PaginatedResponse": schema}
