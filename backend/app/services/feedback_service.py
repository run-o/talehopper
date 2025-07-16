import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings
from app.schemas.feedback import FeedbackRequest

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self):
        self.sendgrid_client = None
        if settings.SENDGRID_API_KEY:
            self.sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    async def send_feedback_email(self, feedback: FeedbackRequest) -> bool:
        """ Send feedback email via SendGrid """
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured - feedback will be logged only")
            self._log_feedback(feedback)
            return True
        
        if not settings.FEEDBACK_EMAIL_TO or not settings.FEEDBACK_EMAIL_FROM:
            logger.error("Feedback email fields not configured")
            return False
        
        try:
            # Create email content
            subject = "TaleHopper Feedback"
            
            # Format the email body
            email_body = self._format_email_body(feedback)
            
            message = Mail(
                from_email=settings.FEEDBACK_EMAIL_FROM,
                to_emails=settings.FEEDBACK_EMAIL_TO,
                subject=subject,
                html_content=email_body
            )
            
            # Send the email
            response = self.sendgrid_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Feedback email sent successfully. Status: {response.status_code}")
                return True
            else:
                logger.error(f"Failed to send feedback email. Status: {response.status_code}")
                return False
                
        except Exception as exc:
            logger.error(f"Error sending feedback email: {str(exc)}")
            # Still log the feedback even if email fails
            self._log_feedback(feedback)
            return False
    
    def _format_email_body(self, feedback: FeedbackRequest) -> str:
        """Format the feedback into a nice HTML email"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #007bff;">New TaleHopper Feedback</h2>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3>Feedback Message:</h3>
                <p style="white-space: pre-wrap;">{feedback.message}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <p><strong>User Email:</strong> {feedback.email if feedback.email else 'Not provided'}</p>
                <p><strong>Timestamp:</strong> {timestamp}</p>
            </div>
            
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This feedback was submitted through the TaleHopper application.
            </p>
        </body>
        </html>
        """
        
        return html_content
    
    def _log_feedback(self, feedback: FeedbackRequest):
        """Log feedback to console/logs when email is not available"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.info(f"""
        === NEW FEEDBACK RECEIVED ===
        Timestamp: {timestamp}
        User Email: {feedback.email if feedback.email else 'Not provided'}
        Message: {feedback.message}
        ============================
        """)


# Global instance
feedback_service = FeedbackService()
