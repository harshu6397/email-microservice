from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum


class EmailType(str, Enum):
    PLAIN = "plain"
    HTML = "html"


class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    email_type: EmailType = EmailType.PLAIN


class HTMLEmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    html_body: str
    text_body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None


class TemplateEmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    template_name: str
    template_data: Dict[str, Any] = {}
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None


class EmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
