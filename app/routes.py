# app/routes.py
import uuid
from fastapi import APIRouter, Header, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from app.core.redis import idempotency_manager
from app.services.worker import process_notification_task

# Initialize the router
router = APIRouter(prefix="/api/v1", tags=["Notifications"])

class NotificationPayload(BaseModel):
    """
    Schema for the incoming notification request.
    Strict typing ensures we receive exactly what we expect from the client.
    """
    user_id: str
    recipient_email: EmailStr
    template_name: str
    template_data: Dict[str, Any]
    provider_override: Optional[str] = None  # Allow client to force a specific provider

class NotificationResponse(BaseModel):
    """
    Standardized response schema for successful requests.
    """
    status: str
    message: str
    tracking_id: str

@router.post("/notify", response_model=NotificationResponse, status_code=202)
async def send_notification(
    payload: NotificationPayload,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str = Header(..., description="Unique key to prevent duplicate processing")
):
    """
    Dispatch a notification via email.
    Returns 202 Accepted immediately and processes the actual sending in the background.
    """
    
    # 1. Check for Idempotency hit
    cached_result = await idempotency_manager.get_cached_response(x_idempotency_key)
    
    if cached_result:
        # Return the cached successful response immediately to save resources
        return NotificationResponse(**cached_result)

    # 2. Generate a tracking ID for system observability
    tracking_id = str(uuid.uuid4())

    # 3. Formulate the initial success response
    response_data = {
        "status": "processing",
        "message": "Notification queued successfully.",
        "tracking_id": tracking_id
    }

    # 4. Save to Redis to prevent future duplicates with this exact key
    await idempotency_manager.save_response(x_idempotency_key, response_data)

    # 5. Delegate the rendering and HTTP requests to a background worker
    background_tasks.add_task(
        process_notification_task,
        recipient=payload.recipient_email,
        template_name=payload.template_name,
        template_data=payload.template_data,
        tracking_id=tracking_id,
        provider_override=payload.provider_override
    )

    return response_data