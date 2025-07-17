from pydantic import BaseModel
from typing import Optional


class FeedbackRequest(BaseModel):
    message: str
    # we care more about gathering feedback than the email, so let's not
    # validate it with EmailStr and just use a simple string:
    email: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    message: str
