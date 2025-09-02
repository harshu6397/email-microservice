from fastapi import HTTPException, status
from typing import Optional


class EmailServiceException(Exception):
    """Base exception for email service."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class SMTPConnectionError(EmailServiceException):
    """Raised when SMTP connection fails."""
    pass


class EmailSendError(EmailServiceException):
    """Raised when email sending fails."""
    pass


class TemplateNotFoundError(EmailServiceException):
    """Raised when email template is not found."""
    pass


class InvalidEmailError(EmailServiceException):
    """Raised when email validation fails."""
    pass


def handle_email_service_exception(exc: EmailServiceException) -> HTTPException:
    """Convert email service exceptions to HTTP exceptions."""
    
    if isinstance(exc, SMTPConnectionError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "SMTP connection failed", "message": exc.message}
        )
    
    if isinstance(exc, TemplateNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Template not found", "message": exc.message}
        )
    
    if isinstance(exc, InvalidEmailError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid email", "message": exc.message}
        )
    
    # Default to internal server error
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error": "Email service error", "message": exc.message}
    )
