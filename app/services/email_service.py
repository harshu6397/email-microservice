import aiosmtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from jinja2 import Environment, BaseLoader, TemplateNotFound, Template
import os

from app.config.settings import settings
from app.models.email import EmailRequest, HTMLEmailRequest, TemplateEmailRequest, EmailType
from app.core.exceptions import (
    SMTPConnectionError, 
    EmailSendError, 
    TemplateNotFoundError,
    InvalidEmailError
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoDBTemplateLoader(BaseLoader):
    """Jinja2 template loader that loads templates from MongoDB."""
    
    async def get_source(self, environment, template_name):
        """Load template from MongoDB."""
        try:
            from app.core.database import get_db
            db = get_db()
            
            template_doc = await db.email_templates.find_one({"name": template_name})
            if not template_doc:
                raise TemplateNotFound(template_name)
            
            source = template_doc["content"]
            
            # Return (source, filename, uptodate_func)
            # The uptodate function is used for checking if template needs reload
            def uptodate():
                return False  # Always reload from DB
            
            return source, None, uptodate
        except Exception as e:
            logger.error(f"Failed to load template from MongoDB: {e}")
            raise TemplateNotFound(template_name)


class EmailService:
    """Email service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.default_from_email = settings.default_from_email
        self.default_from_name = settings.default_from_name
        
        # Initialize Jinja2 environment with MongoDB loader
        self.jinja_env = Environment(loader=MongoDBTemplateLoader())
    
    async def _create_smtp_client(self) -> aiosmtplib.SMTP:
        """Create and configure SMTP client."""
        try:
            # Create SMTP client with proper TLS configuration
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=False,  # Don't start TLS automatically
                use_tls=False     # We'll manually start TLS after connecting
            )
            
            # Connect to the server
            await smtp.connect()
            
            # Start TLS if required
            if self.smtp_use_tls:
                await smtp.starttls()
            
            # Login with credentials
            await smtp.login(self.smtp_username, self.smtp_password)
            return smtp
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            raise SMTPConnectionError(f"Failed to connect to SMTP server: {str(e)}")
    
    def _create_message(
        self,
        to: List[str],
        subject: str,
        body: str,
        body_type: str = "plain",
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> MIMEMultipart:
        """Create email message."""
        
        # Set from address
        from_addr = from_email or self.default_from_email
        sender_name = from_name or self.default_from_name
        from_header = f"{sender_name} <{from_addr}>"
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = from_header
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        
        # Attach body
        msg.attach(MIMEText(body, body_type))
        
        return msg
    
    async def send_email(self, email_request: EmailRequest) -> str:
        """Send a plain text or HTML email."""
        try:
            logger.info(f"Sending email to: {email_request.to}")
            
            # Create message
            body_type = "html" if email_request.email_type == EmailType.HTML else "plain"
            msg = self._create_message(
                to=email_request.to,
                subject=email_request.subject,
                body=email_request.body,
                body_type=body_type,
                cc=email_request.cc,
                bcc=email_request.bcc,
                from_email=email_request.from_email,
                from_name=email_request.from_name
            )
            
            # Send email
            smtp = await self._create_smtp_client()
            
            # Combine all recipients
            all_recipients = email_request.to[:]
            if email_request.cc:
                all_recipients.extend(email_request.cc)
            if email_request.bcc:
                all_recipients.extend(email_request.bcc)
            
            await smtp.send_message(msg, recipients=all_recipients)
            await smtp.quit()
            
            email_id = str(uuid.uuid4())
            logger.info(f"Email sent successfully with ID: {email_id}")
            return email_id
            
        except SMTPConnectionError:
            raise
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise EmailSendError(f"Failed to send email: {str(e)}")
    
    async def send_html_email(self, email_request: HTMLEmailRequest) -> str:
        """Send an HTML email with optional text fallback."""
        try:
            logger.info(f"Sending HTML email to: {email_request.to}")
            
            # Render HTML body if variables are provided
            html_body = email_request.html_body
            if email_request.variables:
                try:
                    # Create a Jinja2 template from the HTML body string
                    template = self.jinja_env.from_string(html_body)
                    html_body = template.render(**email_request.variables)
                except Exception as e:
                    logger.error(f"Failed to render template with variables: {e}")
                    raise EmailSendError(f"Failed to render template with variables: {str(e)}")
            
            # Create multipart message
            from_addr = email_request.from_email or self.default_from_email
            sender_name = email_request.from_name or self.default_from_name
            from_header = f"{sender_name} <{from_addr}>"
            
            msg = MIMEMultipart("alternative")
            msg["From"] = from_header
            msg["To"] = ", ".join(email_request.to)
            msg["Subject"] = email_request.subject
            
            if email_request.cc:
                msg["Cc"] = ", ".join(email_request.cc)
            
            # Add text version if provided
            if email_request.text_body:
                text_part = MIMEText(email_request.text_body, "plain")
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)
            
            # Send email
            smtp = await self._create_smtp_client()
            
            # Combine all recipients
            all_recipients = email_request.to[:]
            if email_request.cc:
                all_recipients.extend(email_request.cc)
            if email_request.bcc:
                all_recipients.extend(email_request.bcc)
            
            await smtp.send_message(msg, recipients=all_recipients)
            await smtp.quit()
            
            email_id = str(uuid.uuid4())
            logger.info(f"HTML email sent successfully with ID: {email_id}")
            return email_id
            
        except SMTPConnectionError:
            raise
        except Exception as e:
            logger.error(f"Failed to send HTML email: {str(e)}")
            raise EmailSendError(f"Failed to send HTML email: {str(e)}")
    
    async def send_template_email(self, email_request: TemplateEmailRequest) -> str:
        """Send an email using a MongoDB template."""
        try:
            logger.info(f"Sending template email '{email_request.template_name}' to: {email_request.to}")
            
            # Load template from MongoDB
            try:
                template = self.jinja_env.get_template(email_request.template_name)
                html_body = template.render(**email_request.template_data)
            except TemplateNotFound:
                raise TemplateNotFoundError(f"Template '{email_request.template_name}' not found in database")
            
            # Create HTML email request
            html_request = HTMLEmailRequest(
                to=email_request.to,
                subject=email_request.subject,
                html_body=html_body,
                cc=email_request.cc,
                bcc=email_request.bcc,
                from_email=email_request.from_email,
                from_name=email_request.from_name
            )
            
            return await self.send_html_email(html_request)
            
        except (SMTPConnectionError, TemplateNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            raise EmailSendError(f"Failed to send template email: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            smtp = await self._create_smtp_client()
            await smtp.quit()
            return True
        except Exception:
            return False


# Global email service instance
email_service = EmailService()
