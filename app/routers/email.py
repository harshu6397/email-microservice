from fastapi import APIRouter, status
from typing import List

from app.models.email import (
    EmailRequest, 
    HTMLEmailRequest, 
    TemplateEmailRequest, 
    EmailResponse,
    HealthResponse
)
from app.controllers.email_controller import EmailController

router = APIRouter()


@router.post(
    "/send",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Email",
    description="Send a plain text or HTML email to one or more recipients."
)
async def send_email(email_request: EmailRequest) -> EmailResponse:
    """
    Send an email.
    
    - **to**: List of recipient email addresses
    - **subject**: Email subject
    - **body**: Email body content
    - **cc**: Optional list of CC recipients
    - **bcc**: Optional list of BCC recipients
    - **from_email**: Optional sender email (defaults to configured email)
    - **from_name**: Optional sender name (defaults to configured name)
    - **email_type**: Email type (plain or html)
    """
    return await EmailController.send_email(email_request)


@router.post(
    "/send-html",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Send HTML Email",
    description="Send an HTML email with optional text fallback."
)
async def send_html_email(email_request: HTMLEmailRequest) -> EmailResponse:
    """
    Send an HTML email.
    
    - **to**: List of recipient email addresses
    - **subject**: Email subject
    - **html_body**: HTML email body content
    - **text_body**: Optional plain text fallback
    - **cc**: Optional list of CC recipients
    - **bcc**: Optional list of BCC recipients
    - **from_email**: Optional sender email (defaults to configured email)
    - **from_name**: Optional sender name (defaults to configured name)
    """
    return await EmailController.send_html_email(email_request)


@router.post(
    "/send-template",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Template Email",
    description="Send an email using a Jinja2 template."
)
async def send_template_email(email_request: TemplateEmailRequest) -> EmailResponse:
    """
    Send a template-based email.
    
    - **to**: List of recipient email addresses
    - **subject**: Email subject
    - **template_name**: Name of the template file (without .html extension)
    - **template_data**: Data to populate the template
    - **cc**: Optional list of CC recipients
    - **bcc**: Optional list of BCC recipients
    - **from_email**: Optional sender email (defaults to configured email)
    - **from_name**: Optional sender name (defaults to configured name)
    """
    return await EmailController.send_template_email(email_request)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the email service."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the health status of the email service including SMTP connectivity.
    """
    return await EmailController.health_check()
