# app/services/notifications/base.py
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class NotificationProvider(ABC):
    """
    Abstract Base Class defining the contract for all notification strategies.
    Ensures polymorphic behavior for seamless failover implementations.
    """
    
    @abstractmethod
    async def send(self, recipient: str, subject: str, content: str) -> bool:
        """
        Dispatches the notification asynchronously.
        
        Args:
            recipient (str): The target email address or phone number.
            subject (str): The subject line or SMS header.
            content (str): The rendered HTML body or text payload.
            
        Returns:
            bool: True if the dispatch was successfully acknowledged by the API.
            
        Raises:
            Exception: Network timeouts or HTTP 500 errors to be caught by the failover mechanism.
        """
        pass