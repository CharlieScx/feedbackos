import type { ApiErrorCode } from "@feedbackos/contracts";

export type ApiErrorAction =
  | "authenticate"
  | "show-not-found"
  | "fix-file"
  | "replace-idempotency-key"
  | "retry"
  | "show-error";

export function getApiErrorAction(code: ApiErrorCode): ApiErrorAction {
  switch (code) {
    case "authentication_failed":
      return "authenticate";
    case "resource_not_found":
      return "show-not-found";
    case "file_invalid":
      return "fix-file";
    case "idempotency_conflict":
      return "replace-idempotency-key";
    case "retryable_failure":
      return "retry";
    default:
      return "show-error";
  }
}
