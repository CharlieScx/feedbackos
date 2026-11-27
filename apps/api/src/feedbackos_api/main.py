from typing import Any, Literal, cast

from fastapi import FastAPI, Response
from pydantic import BaseModel

from feedbackos_api.auth_routes import router as auth_router
from feedbackos_api.config import get_settings
from feedbackos_api.contracts import (
    API_ERROR_RESPONSES,
    SuccessResponse,
    additional_openapi_schemas,
)
from feedbackos_api.errors import install_exception_handlers
from feedbackos_api.workspace_routes import router as workspace_router

settings = get_settings()


class FeedbackOSApp(FastAPI):
    def openapi(self) -> dict[str, Any]:
        document = super().openapi()
        components = cast(dict[str, Any], document.setdefault("components", {}))
        schemas = cast(dict[str, Any], components.setdefault("schemas", {}))
        schemas.update(additional_openapi_schemas())
        return document


app = FeedbackOSApp(
    title="FeedbackOS API",
    debug=settings.debug is True,
    responses=API_ERROR_RESPONSES,
)
install_exception_handlers(app)
app.include_router(auth_router)
app.include_router(workspace_router)


class HealthData(BaseModel):
    service: Literal["feedbackos-api"] = "feedbackos-api"
    status: Literal["ok"] = "ok"


class HealthResponse(SuccessResponse[HealthData]):
    pass


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health(response: Response) -> HealthResponse:
    response.headers["Cache-Control"] = "no-store"
    return HealthResponse(data=HealthData())
