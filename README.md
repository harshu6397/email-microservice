# Email Service

A microservice for sending emails using FastAPI.

## Features

- Send plain text emails
- Send HTML emails
- Send emails with attachments
- Template-based emails
- Gmail SMTP support
- Health check endpoint
- Async email sending
- Proper error handling and logging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your email configuration:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
DEFAULT_FROM_EMAIL=your_email@gmail.com
DEFAULT_FROM_NAME=Email Service
```

3. Run the service:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /email/send` - Send email
- `POST /email/send-html` - Send HTML email
- `POST /email/send-template` - Send template-based email

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
