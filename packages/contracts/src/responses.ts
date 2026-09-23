import type { components } from "./schema";

export type ApiErrorCode = components["schemas"]["ErrorCode"];
export type ApiErrorResponse = components["schemas"]["ErrorResponse"];
export type PaginationMeta = components["schemas"]["PaginationMeta"];

export interface ApiSuccess<T> {
  data: T;
}

export interface PaginatedResponse<T> extends ApiSuccess<T[]> {
  pagination: PaginationMeta;
}

const API_ERROR_CODES = [
  "authentication_failed",
  "access_denied",
  "resource_not_found",
  "request_invalid",
  "file_invalid",
  "conflict",
  "idempotency_conflict",
  "retryable_failure",
  "internal_error",
] as const satisfies readonly ApiErrorCode[];

export function isApiErrorCode(value: unknown): value is ApiErrorCode {
  return (
    typeof value === "string" &&
    (API_ERROR_CODES as readonly string[]).includes(value)
  );
}

export function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (typeof value !== "object" || value === null || !("error" in value)) {
    return false;
  }

  const error = value.error;
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    isApiErrorCode(error.code) &&
    "message" in error &&
    typeof error.message === "string" &&
    "retryable" in error &&
    typeof error.retryable === "boolean" &&
    "field_errors" in error &&
    Array.isArray(error.field_errors)
  );
}
