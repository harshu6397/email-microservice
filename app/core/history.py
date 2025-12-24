import uuid
from datetime import datetime
from typing import List, Any, Dict
from pymongo import DESCENDING

from app.core.logging import get_logger
from app.core.database import get_db

logger = get_logger(__name__)


async def add_email_to_history(
    to: List[str],
    subject: str,
    email_id: str = None,
    status: str = "sent",
    template_name: str = None,
    template_variables: Dict[str, Any] = None,
    recipients_count: int = None,
    html_body: str = None
) -> str:
    """Add an email send event to history with detailed information."""
    try:
        db = get_db()
        
        if not email_id:
            email_id = str(uuid.uuid4())
        
        if recipients_count is None:
            recipients_count = len(to) if to else 0
        
        history_item = {
            "_id": email_id,
            "to": to,
            "recipients_count": recipients_count,
            "subject": subject,
            "timestamp": datetime.utcnow(),
            "status": status,
            "template_name": template_name,
            "template_variables": template_variables or {},
            "html_body_preview": html_body[:500] if html_body else None,  # Store first 500 chars for preview
            "html_body_full": html_body  # Store full HTML for detailed view
        }
        
        await db.email_history.insert_one(history_item)
        logger.info(f"Email logged to history: {email_id}")
        return email_id
        
    except Exception as e:
        logger.error(f"Failed to add email to history: {e}")
        return email_id or str(uuid.uuid4())


async def get_send_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Get send history."""
    try:
        db = get_db()
        
        history = await db.email_history.find()\
            .sort("timestamp", DESCENDING)\
            .limit(limit)\
            .to_list(limit)
        
        # Convert ObjectId and datetime to strings for JSON serialization
        for item in history:
            item["_id"] = str(item.get("_id", ""))
            if isinstance(item.get("timestamp"), datetime):
                item["timestamp"] = item["timestamp"].isoformat()
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get send history: {e}")
        return []


async def get_history_detail(email_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific email from history."""
    try:
        db = get_db()
        
        item = await db.email_history.find_one({"_id": email_id})
        
        if not item:
            return None
        
        # Convert ObjectId and datetime to strings for JSON serialization
        item["_id"] = str(item.get("_id", ""))
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].isoformat()
        
        return item
        
    except Exception as e:
        logger.error(f"Failed to get history detail: {e}")
        return None


async def load_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Load email send history (alias for get_send_history)."""
    return await get_send_history(limit)