# 📧 Email Service Microservice

A modern, feature-rich FastAPI microservice for sending emails with template management, MongoDB persistence, and an interactive web dashboard.

## ✨ Features

### Core Email Features
- 📨 Send plain text emails
- 🎨 Send HTML emails with rich formatting
- 📎 Send emails with attachments
- 🎯 Template-based emails with variable substitution
- 🔐 Password-protected API documentation
- ✅ Async email sending for high performance
- 🏥 Health check endpoint with SMTP connectivity verification
- 📝 Comprehensive error handling and logging

### Template & Variable Management
- 📋 Dynamic template management via MongoDB
- 🔄 Auto-load templates from filesystem on startup
- 🎭 Jinja2 template engine with custom MongoDB loader
- 🏷️ Template variable extraction and auto-filling in UI
- ✏️ Create, edit, and delete templates from dashboard
- 💾 Template persistence in MongoDB

### Email History & Tracking
- 📊 Complete email send history with timestamps
- 📧 Track recipients, subject, and content
- 🎯 Log template name and variables used
- 👁️ Detailed view with email preview
- 🔄 Resend previous emails with one click
- 💾 Full HTML body storage for historical reference

### Web Dashboard
- 🎯 Beautiful, modern UI for email composition
- 🔐 HTTP Basic authentication for security
- 📝 Compose emails with template selection
- 👥 Easy recipient management with tags
- 👁️ Real-time email preview
- 📋 Template management (CRUD operations)
- 📊 Email send history with details
- 🔄 Quick resend functionality
- 📱 Responsive design

## Architecture

```
email-microservice/
├── main.py                 # FastAPI application entry point
├── api/
│   └── index.py           # Vercel serverless handler
├── app/
│   ├── config/
│   │   └── settings.py    # Configuration management
│   ├── controllers/
│   │   └── email_controller.py  # Business logic
│   ├── core/
│   │   ├── auth.py        # Authentication (HTTP Basic Auth)
│   │   ├── database.py    # MongoDB connection
│   │   ├── exceptions.py  # Custom exceptions
│   │   ├── history.py     # Email history tracking
│   │   └── logging.py     # Logging configuration
│   ├── models/
│   │   └── email.py       # Pydantic models
│   ├── routers/
│   │   ├── email.py       # Email sending endpoints
│   │   └── dashboard.py   # Dashboard API endpoints
│   ├── services/
│   │   └── email_service.py  # Email sending service
│   ├── templates/
│   │   ├── dashboard.html    # Web dashboard UI
│   │   └── *.html            # Email templates
│   └── migrations/
│       └── load_templates.py # Template migration script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
DEFAULT_FROM_EMAIL=your_email@gmail.com
DEFAULT_FROM_NAME=Email Service

# MongoDB Configuration
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=email_service

# API Documentation Security
DOCS_PASSWORD=your_secure_password_here

# API Configuration (optional)
API_TITLE=Email Service
API_DESCRIPTION=A modern email microservice
API_VERSION=1.0.0
```

### 3. Run the Service

**Development:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🚀 Quick Start

1. **Access the Dashboard:**
   - Navigate to `http://localhost:8000/dashboard`
   - Login with your configured password

2. **Send Your First Email:**
   - Enter recipient email(s)
   - Add subject and message
   - Click "🚀 Send Email"

3. **Use Templates:**
   - Select a template from the dropdown
   - Template variables will auto-populate as input fields
   - Fill in the variable values
   - Send the email

4. **View History:**
   - Check "Send History" panel for all sent emails
   - Click "View Details" to see full email content
   - Use "🔄 Resend Email" to resend to same recipients

## API Endpoints

### Email Sending
- `POST /email/send` - Send plain text email
- `POST /email/send-html` - Send HTML email with optional variable substitution
- `POST /email/send-template` - Send email using MongoDB template

### Dashboard
- `GET /api/templates` - Get all templates
- `GET /api/templates/{template_name}` - Get specific template
- `POST /api/templates` - Create new template
- `PUT /api/templates/{template_name}` - Update template
- `DELETE /api/templates/{template_name}` - Delete template
- `GET /api/send-history` - Get email send history
- `GET /api/send-history/{email_id}` - Get detailed email info

### Documentation
- `GET /docs` - Swagger UI (password protected)
- `GET /redoc` - ReDoc (password protected)
- `GET /openapi.json` - OpenAPI schema (password protected)

### Health
- `GET /health` - Service health check

## API Documentation

Once the service is running, access interactive API documentation at:

- **Swagger UI:** `http://localhost:8000/docs`
  - Interactive API explorer
  - Try out endpoints
  - View request/response schemas

- **ReDoc:** `http://localhost:8000/redoc`
  - Beautiful API documentation
  - Offline-friendly

Both require your `DOCS_PASSWORD` for access.

## Request Examples

### Send HTML Email with Variables

```bash
curl -X POST "http://localhost:8000/email/send-html" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Welcome",
    "html_body": "<h1>Hello {{ user_name }}</h1><p>Welcome!</p>",
    "variables": {
      "user_name": "John Doe"
    }
  }'
```

### Send Template-Based Email

```bash
curl -X POST "http://localhost:8000/email/send-template" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Account Verification",
    "template_name": "email_verification",
    "template_data": {
      "user_name": "John",
      "verification_url": "https://example.com/verify?token=xyz"
    }
  }'
```

## Template Variables

Templates use Jinja2 syntax for variables:

```html
<h1>Hello {{ user_name or "Friend" }}!</h1>
<p>Your reset link: <a href="{{ reset_url }}">Click here</a></p>
<p>This link expires in {{ expiry_time or "1 hour" }}</p>
```

Variables with `or` provide default values if not supplied.

## Database

### MongoDB Collections

**email_templates**
- Stores all email templates
- Fields: name, content, created_at

**email_history**
- Tracks all sent emails
- Fields: to, subject, template_name, template_variables, recipients_count, html_body_full, html_body_preview, timestamp, status

## Deployment

### Vercel
The service includes `api/index.py` for Vercel serverless deployment:

```bash
vercel deploy
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Traditional Server
```bash
# Install
pip install -r requirements.txt

# Run with gunicorn for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Security Considerations

- ✅ HTTP Basic Auth for API documentation
- ✅ Email validation for all recipients
- ✅ Environment variables for sensitive data
- ✅ CORS middleware (configure for production)
- ✅ SMTP credentials never exposed in logs
- ⚠️ Configure SMTP_USE_TLS=true in production
- ⚠️ Use strong DOCS_PASSWORD
- ⚠️ Restrict CORS origins in production

## Troubleshooting

### MongoDB Connection Issues
- Verify MONGO_URL is correct
- Check MongoDB cluster IP whitelist
- Ensure MONGO_DB name exists

### SMTP Connection Errors
- Verify SMTP credentials
- Check firewall rules for port 587
- For Gmail, use App Password (not regular password)
- Ensure SMTP_USE_TLS=true

### Template Not Found
- Template names are case-sensitive
- Check if template exists in MongoDB
- Use dashboard to view available templates

### Variables Not Substituting
- Verify variable names match template syntax
- Check escaping in template HTML
- Use Jinja2 syntax: `{{ variable_name }}`

## Development

### Project Structure
The project follows a clean architecture pattern with separation of concerns:
- Controllers handle request validation
- Services contain business logic
- Models define data structures
- Routers define API endpoints
- Core modules handle cross-cutting concerns

### Adding New Features
1. Create models in `app/models/`
2. Implement logic in `app/services/`
3. Add controller methods in `app/controllers/`
4. Create routes in `app/routers/`
5. Update documentation

## License

MIT License

## Support

For issues, questions, or contributions, please refer to the project documentation.

---

**Built with:** FastAPI, MongoDB, Jinja2, aiosmtplib
