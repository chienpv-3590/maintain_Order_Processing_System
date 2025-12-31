"""Notification Service - handles sending notifications"""

from typing import List
from datetime import datetime

from domain.events.user_events import UserRegistered, UserAuthenticated
from domain.events.order_events import OrderCreated, OrderStatusUpdated
from infrastructure.logging.logger import ILogger


class NotificationService:
    """
    Application service for sending notifications.
    
    Responsibilities:
    - Send welcome emails
    - Send order confirmations
    - Send order status updates
    - Handle notification events
    """
    
    def __init__(self, logger: ILogger):
        """
        Initialize NotificationService.
        
        Args:
            logger: Logger for notification tracking
        """
        self._logger = logger
    
    def send_welcome_email(self, user_name: str, user_email: str) -> None:
        """
        Send welcome email to new user.
        
        Args:
            user_name: User's name
            user_email: User's email
        """
        message = f"Welcome {user_name}! Thanks for joining our platform."
        
        # In production, integrate with email service (SMTP, SendGrid, etc.)
        print(f"EMAIL SENT to {user_email}: {message}")
        
        self._logger.info(
            f"Welcome email sent to {user_email}",
            {"email": user_email, "name": user_name}
        )
    
    def send_order_confirmation(
        self, 
        user_email: str, 
        order_id: int, 
        total: float
    ) -> None:
        """
        Send order confirmation email.
        
        Args:
            user_email: User's email
            order_id: Order ID
            total: Order total amount
        """
        message = f"Order #{order_id} confirmed! Total: ${total:.2f}"
        
        # In production, use email template
        print(f"EMAIL SENT to {user_email}: {message}")
        
        self._logger.info(
            f"Order confirmation sent to {user_email}",
            {"email": user_email, "order_id": order_id, "total": total}
        )
    
    def send_order_status_update(
        self, 
        user_email: str, 
        order_id: int, 
        status: str
    ) -> None:
        """
        Send order status update notification.
        
        Args:
            user_email: User's email
            order_id: Order ID
            status: New order status
        """
        message = f"Your order #{order_id} status updated to: {status}"
        
        print(f"EMAIL SENT to {user_email}: {message}")
        
        self._logger.info(
            f"Order status update sent to {user_email}",
            {"email": user_email, "order_id": order_id, "status": status}
        )
    
    def send_low_stock_alert(self, product_name: str, stock: int, admin_emails: List[str]) -> None:
        """
        Send low stock alert to admins.
        
        Args:
            product_name: Product name
            stock: Current stock level
            admin_emails: List of admin emails
        """
        message = f"LOW STOCK ALERT: {product_name} has only {stock} units remaining"
        
        for email in admin_emails:
            print(f"EMAIL SENT to {email}: {message}")
        
        self._logger.warning(
            f"Low stock alert sent for {product_name}",
            {"product": product_name, "stock": stock, "recipients": len(admin_emails)}
        )


# Event Handlers (to be wired with event bus)
class NotificationEventHandlers:
    """Event handlers for notification service"""
    
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service
    
    def handle_user_registered(self, event: UserRegistered) -> None:
        """Handle UserRegistered event"""
        self._notification_service.send_welcome_email(
            event.name,
            event.email
        )
    
    def handle_order_created(self, event) -> None:
        """Handle OrderCreated event"""
        # Note: Would need user email from event or fetch from repository
        # self._notification_service.send_order_confirmation(
        #     user_email, event.order_id, event.total
        # )
        pass
    
    def handle_order_status_updated(self, event) -> None:
        """Handle OrderStatusUpdated event"""
        # self._notification_service.send_order_status_update(
        #     user_email, event.order_id, event.new_status
        # )
        pass
