# Feedback System Setup

The TaleHopper app includes a user feedback system that allows users to send feedback directly to you via email using Twilio SendGrid.

## Features

- **Simple feedback form**: Users can submit feedback with an optional email for follow-up
- **Rate limiting**: Prevents spam with 1 submissions per minute per IP
- **Internationalization**: Supports English and French
- **Graceful fallback**: If email isn't configured, feedback is logged to console
- **Clean UI**: Modal popup with responsive design

## Setup Instructions

### 1. Get Twilio SendGrid Account

1. Sign up at [https://sendgrid.com/](https://sendgrid.com/)
2. Verify your account and complete setup
3. Create an API key:
   - Go to Settings > API Keys
   - Click "Create API Key"
   - Choose "Restricted Access" and give it "Mail Send" permissions
   - Copy the API key (you won't see it again!)

### 2. Configure Environment Variables

Add these variables to your `backend/.env` file:

```bash
# Feedback settings
SENDGRID_API_KEY="your_sendgrid_api_key_here"
FEEDBACK_EMAIL="your.email@example.com"
```

### 3. Verify Sender Domain (Optional but Recommended)

For production use, verify your domain with SendGrid:
1. Go to Settings > Sender Authentication
2. Follow the domain verification process
3. Update the `from_email` in `backend/app/services/feedback_service.py` to use your verified domain

### 4. Install Dependencies

The SendGrid dependency is already added to `requirements.txt`. Install it with:

```bash
cd backend
pip install -r requirements.txt
```

### 5. Test the System

1. Start your backend server
2. Start your frontend
3. Click the "Feedback" button in the bottom right
4. Submit a test message
5. Check your email or server logs

## How It Works

### Frontend
- **FeedbackModal**: React component with form validation
- **API Integration**: Calls `/feedback` endpoint
- **User Experience**: Clean modal with success/error states

### Backend
- **Rate Limited**: 5 submissions per minute per IP
- **Validation**: Message length and content validation
- **Email Service**: SendGrid integration with HTML formatting
- **Fallback**: Logs to console if email not configured

### Email Format
Feedback emails include:
- User's message (formatted)
- User's email (if provided)
- Timestamp
- Clean HTML formatting

## Troubleshooting

### Feedback not sending emails
1. Check that `SENDGRID_API_KEY` is set correctly
2. Check that `FEEDBACK_EMAIL` is set to your email
3. Verify SendGrid API key has "Mail Send" permissions
4. Check server logs for error messages

### Rate limiting issues
- Users are limited to 5 feedback submissions per minute
- This prevents spam but may need adjustment for your use case
- Modify the limit in `backend/app/api/routes/feedback.py`

### Frontend not showing feedback button
- Check that translations are loaded correctly
- Verify the feedback button styling isn't conflicting with other elements

## Customization

### Change rate limits
Edit `backend/app/api/routes/feedback.py`:
```python
@limiter.limit("10/minute")  # Change from 5/minute to 10/minute
```

### Modify email template
Edit `backend/app/services/feedback_service.py` in the `_format_email_body` method.

### Change feedback button position
Edit the footer styles in `frontend/src/App.tsx`.

### Add more form fields
1. Update `FeedbackRequest` schema in `backend/app/schemas/feedback.py`
2. Update the frontend form in `frontend/src/components/FeedbackModal.tsx`
3. Update email template to include new fields

## Security Notes

- API keys should never be committed to version control
- Rate limiting helps prevent abuse
- Input validation prevents malicious content
- SendGrid handles email delivery securely

## Future Enhancements

- **SMS notifications**: Use Twilio SMS API for instant notifications
- **Feedback dashboard**: Create an admin interface to view feedback
- **Categories**: Add feedback categories (bug, feature request, etc.)
- **File attachments**: Allow users to attach screenshots
- **Auto-responses**: Send confirmation emails to users
