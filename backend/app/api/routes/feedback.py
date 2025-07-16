import logging
from fastapi import APIRouter, HTTPException, Request, status
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import feedback_service
from app.core.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
@limiter.limit("1/minute")  # Allow 1 feedback submission per minute per IP
async def submit_feedback(request: Request, feedback: FeedbackRequest):
    """ Submit user feedback """
    try:
        # Validate feedback message
        if not feedback.message or not feedback.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback message cannot be empty"
            )

        if len(feedback.message.strip()) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback message too long (max 5000 characters)"
            )

        # Send the feedback
        success = await feedback_service.send_feedback_email(feedback)
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Thank you for your feedback! We'll review it soon."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send feedback. Please try again later."
            )
            
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in feedback submission: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

