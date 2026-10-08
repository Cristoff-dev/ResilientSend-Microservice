# app/services/worker.py
import logging
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.services.notifications.email_resend import ResendProvider
from app.services.notifications.email_sendgrid import SendGridProvider
from app.services.notifications.sms_twilio import TwilioProvider

logger = logging.getLogger(__name__)

# Pre-load the Jinja2 environment to cache templates in RAM.
template_env = Environment(loader=FileSystemLoader("app/templates"), enable_async=True)

# Initialize all available notification strategies
resend_provider = ResendProvider()
sendgrid_provider = SendGridProvider()
twilio_provider = TwilioProvider()

async def process_notification_task(
    recipient: str, 
    template_name: str, 
    template_data: Dict[str, Any], 
    tracking_id: str,
    provider_override: Optional[str] = None
) -> None:
    """
    Background worker that handles HTML rendering, dynamic routing (SMS vs Email), 
    and executes the failover logic.
    """
    logger.info(f"[{tracking_id}] Worker initiated for template: {template_name}")
    
    try:
        # 1. Render dynamic content (used as HTML for emails or plain text for SMS)
        template = template_env.get_template(f"{template_name}.html")
        content = await template.render_async(**template_data)
        subject = template_data.get("subject", "Automated Notification")

        # 2. Strategy Selection (Routing)
        if provider_override and provider_override.lower() == "sms":
            # --- SMS Flow ---
            try:
                await twilio_provider.send(recipient, subject, content)
                logger.info(f"[{tracking_id}] SMS completed successfully via Twilio.")
            except Exception as sms_error:
                # In a production environment, you could add a fallback SMS provider here (e.g., Plivo, MessageBird)
                logger.error(f"[{tracking_id}] SMS Provider failed: {sms_error}. No fallback configured.")
        
        else:
            # --- Email Flow with Failover ---
            try:
                await resend_provider.send(recipient, subject, content)
                logger.info(f"[{tracking_id}] Email completed via Primary Provider (Resend).")
                
            except Exception as primary_error:
                logger.error(f"[{tracking_id}] Primary Provider failed: {primary_error}. Triggering Failover.")
                
                await sendgrid_provider.send(recipient, subject, content)
                logger.info(f"[{tracking_id}] Email salvaged via Fallback Provider (SendGrid).")
                
    except TemplateNotFound:
        logger.error(f"[{tracking_id}] Template '{template_name}.html' missing from directory.")
    except Exception as critical_error:
        logger.critical(f"[{tracking_id}] Total system failure during notification process: {critical_error}")