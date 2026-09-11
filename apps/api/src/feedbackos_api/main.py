from fastapi import FastAPI

from feedbackos_api.config import get_settings

settings = get_settings()

app = FastAPI(
    title="FeedbackOS API",
    debug=settings.debug is True,
)
