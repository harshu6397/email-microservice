from fastapi import HTTPException
from typing import List
import datetime

from app.models.email import (
    EmailRequest, 
    HTMLEmailRequest, 
    TemplateEmailRequest, 
    EmailResponse,
    HealthResponse
)
from app.services.email_service import email_service
from app.core.exceptions import (
    EmailServiceException, 
    handle_email_service_exception
)
from app.core.logging import get_logger
from app.core.history import add_email_to_history
from app.config.settings import settings

logger = get_logger(__name__)


class EmailController:
    """Controller for email operations."""
    
    @staticmethod
    async def send_email(email_request: EmailRequest) -> EmailResponse:
        """Send a plain text or HTML email."""
        try:
            email_id = await email_service.send_email(email_request)
            await add_email_to_history(email_request.to, email_request.subject, email_id)
            return EmailResponse(
                success=True,
                message="Email sent successfully",
                email_id=email_id
            )
        except EmailServiceException as e:
            logger.error(f"Email service error: {e.message}")
            raise handle_email_service_exception(e)
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Internal server error", "message": "Failed to send email"}
            )
    
    @staticmethod
    async def send_html_email(email_request: HTMLEmailRequest) -> EmailResponse:
        """Send an HTML email."""
        try:
            email_id = await email_service.send_html_email(email_request)
            
            # Add to history with detailed information
            await add_email_to_history(
                to=email_request.to,
                subject=email_request.subject,
                email_id=email_id,
                template_name=email_request.template_name,
                template_variables=email_request.variables,
                recipients_count=len(email_request.to),
                html_body=email_request.html_body
            )
            
            return EmailResponse(
                success=True,
                message="HTML email sent successfully",
                email_id=email_id
            )
        except EmailServiceException as e:
            logger.error(f"Email service error: {e.message}")
            raise handle_email_service_exception(e)
        except Exception as e:
            logger.error(f"Unexpected error sending HTML email: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Internal server error", "message": "Failed to send HTML email"}
            )
    
    @staticmethod
    async def send_template_email(email_request: TemplateEmailRequest) -> EmailResponse:
        """Send a template-based email."""
        try:
            email_id = await email_service.send_template_email(email_request)
            await add_email_to_history(email_request.to, email_request.subject, email_id)
            return EmailResponse(
                success=True,
                message="Template email sent successfully",
                email_id=email_id
            )
        except EmailServiceException as e:
            logger.error(f"Email service error: {e.message}")
            raise handle_email_service_exception(e)
        except Exception as e:
            logger.error(f"Unexpected error sending template email: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Internal server error", "message": "Failed to send template email"}
            )
    
    @staticmethod
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        try:
            # Test SMTP connection
            smtp_healthy = await email_service.test_connection()
            
            status = "healthy" if smtp_healthy else "unhealthy"
            
            return HealthResponse(
                status=status,
                service=settings.api_title,
                version=settings.api_version,
                timestamp=datetime.datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return HealthResponse(
                status="unhealthy",
                service=settings.api_title,
                version=settings.api_version,
                timestamp=datetime.datetime.utcnow().isoformat()
            )
