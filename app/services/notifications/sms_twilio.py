# app/services/notifications/sms_twilio.py
import httpx
import logging
from app.services.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)

class TwilioProvider(NotificationProvider):
    """
    SMS notification strategy utilizing the Twilio REST API.
    Designed for time-sensitive alerts like 2FA codes or critical system failures.
    """
    
    def __init__(self, account_sid: str = "mock_sid", auth_token: str = "mock_token", from_number: str = "+1234567890"):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        # Standard Twilio API endpoint for message creation
        self.endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

    async def send(self, recipient: str, subject: str, content: str) -> bool:
        """
        Dispatches an SMS message. Note: The 'subject' parameter is prepended 
        to the content since SMS does not support native subject lines.
        """
        
        # Strip HTML tags if any, or assume 'content' is plain text for SMS
        # Prepending subject to mimic standard alert formats (e.g., "URGENT: Server Down")
        sms_body = f"{subject}: {content}" if subject else content

        # Twilio uses form-encoded data, not JSON
        payload = {
            "To": recipient,
            "From": self.from_number,
            "Body": sms_body
        }

        # Twilio requires Basic Authentication
        auth = (self.account_sid, self.auth_token)

        async with httpx.AsyncClient(timeout=5.0) as client:
            logger.info(f"[TwilioProvider] Attempting to dispatch SMS to {recipient}")
            
            # Simulated HTTP POST for portfolio demonstration
            # In production: 
            # response = await client.post(self.endpoint, data=payload, auth=auth)
            # response.raise_for_status()
            
            # Simulating a failure scenario to demonstrate resilience
            if "fail_twilio" in content.lower():
                raise httpx.RequestError("Simulated connection drop to Twilio API.")
                
            logger.info("[TwilioProvider] SMS dispatched successfully.")
            return True