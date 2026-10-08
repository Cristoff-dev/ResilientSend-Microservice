# app/services/notifications/email_resend.py
import httpx
import logging
from app.services.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)

class ResendProvider(NotificationProvider):
    """
    Primary email strategy utilizing the Resend REST API.
    Configured with strict timeouts to ensure rapid failover switching.
    """
    
    def __init__(self, api_key: str = "mock_api_key"):
        self.api_key = api_key
        self.endpoint = "https://api.resend.com/emails"

    async def send(self, recipient: str, subject: str, content: str) -> bool:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": "notifications@yourdomain.com",
            "to": recipient,
            "subject": subject,
            "html": content
        }

        # Context manager for the HTTP client ensures connections are closed
        async with httpx.AsyncClient(timeout=5.0) as client:
            logger.info(f"[ResendProvider] Attempting to dispatch email to {recipient}")
            
            # Simulated HTTP POST for portfolio demonstration
            # In production: response = await client.post(self.endpoint, json=payload, headers=headers)
            # response.raise_for_status()
            
            # Simulating a failure scenario to demonstrate the failover in action
            if "fail_resend" in content.lower():
                raise httpx.RequestError("Simulated connection drop to Resend API.")
                
            logger.info("[ResendProvider] Email dispatched successfully.")
            return True