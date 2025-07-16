from pydantic import BaseModel, EmailStr
from typing import Optional


class FeedbackRequest(BaseModel):
    message: str
    email: Optional[EmailStr] = None


class FeedbackResponse(BaseModel):
    success: bool
    message: str
