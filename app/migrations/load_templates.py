import os
import asyncio
from pathlib import Path
from datetime import datetime

from app.config.settings import settings
from app.core.database import connect_db, disconnect_db, get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


async def load_templates_from_files():
    """Load all HTML templates from the templates folder into MongoDB."""
    try:
        await connect_db()
        db = get_db()
        
        # Clear existing templates
        await db.email_templates.delete_many({})
        logger.info("Cleared existing templates from MongoDB")
        
        # Load all HTML files from templates directory
        template_files = [
            "welcome.html",
            "email_verification.html",
            "password_reset.html",
            "newsletter.html",
            "notification.html",
            "promotional.html",
        ]
        
        for filename in template_files:
            filepath = os.path.join(TEMPLATES_DIR, filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"Template file not found: {filepath}")
                continue
            
            # Read template content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create template name from filename (remove .html)
            template_name = filename.replace('.html', '')
            
            # Create template document
            template_doc = {
                "name": template_name,
                "filename": filename,
                "content": content,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "type": "html"
            }
            
            # Insert or update template
            await db.email_templates.update_one(
                {"name": template_name},
                {"$set": template_doc},
                upsert=True
            )
            
            logger.info(f"Loaded template: {template_name}")
        
        logger.info("✅ All templates loaded into MongoDB successfully!")
        
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        raise
    finally:
        await disconnect_db()


async def migrate():
    """Run migration."""
    await load_templates_from_files()


if __name__ == "__main__":
    asyncio.run(migrate())
