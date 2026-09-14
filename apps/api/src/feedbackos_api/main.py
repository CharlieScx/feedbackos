from typing import Literal

from fastapi import FastAPI, Response
from pydantic import BaseModel

from feedbackos_api.config import get_settings

settings = get_settings()

app = FastAPI(
    title="FeedbackOS API",
    debug=settings.debug is True,
)


class HealthResponse(BaseModel):
    service: Literal["feedbackos-api"] = "feedbackos-api"
    status: Literal["ok"] = "ok"


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health(response: Response) -> HealthResponse:
    response.headers["Cache-Control"] = "no-store"
    return HealthResponse()
