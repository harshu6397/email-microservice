from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.core.auth import verify_docs_access
from app.core.logging import get_logger
from app.core.database import get_db
from app.core.history import load_history, get_history_detail

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["Dashboard"])


class TemplateModel(BaseModel):
    name: str
    content: str


@router.get("/templates")
async def get_templates(credentials=Depends(verify_docs_access)):
    """Get all templates from MongoDB."""
    try:
        db = get_db()
        templates = await db.email_templates.find().to_list(None)
        
        # Convert ObjectId to string
        for template in templates:
            if "_id" in template:
                template["_id"] = str(template["_id"])
        
        return templates
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load templates"
        )


@router.get("/templates/{template_name}")
async def get_template(template_name: str, credentials=Depends(verify_docs_access)):
    """Get a specific template from MongoDB."""
    try:
        db = get_db()
        template = await db.email_templates.find_one({"name": template_name})
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_name}' not found"
            )
        
        template["_id"] = str(template["_id"])
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template"
        )


@router.post("/templates")
async def create_template(template: TemplateModel, credentials=Depends(verify_docs_access)):
    """Create a new template in MongoDB."""
    try:
        db = get_db()
        
        # Check if template already exists
        existing = await db.email_templates.find_one({"name": template.name})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Template '{template.name}' already exists"
            )
        
        template_doc = {
            "name": template.name,
            "content": template.content,
            "created_at": datetime.utcnow()
        }
        
        result = await db.email_templates.insert_one(template_doc)
        logger.info(f"Template created: {template.name}")
        
        return {
            "success": True,
            "message": "Template created successfully",
            "template": {"_id": str(result.inserted_id), **template_doc}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )


@router.put("/templates/{template_name}")
async def update_template(template_name: str, template: TemplateModel, credentials=Depends(verify_docs_access)):
    """Update an existing template in MongoDB."""
    try:
        db = get_db()
        
        result = await db.email_templates.update_one(
            {"name": template_name},
            {"$set": {
                "name": template.name,
                "content": template.content,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_name}' not found"
            )
        
        logger.info(f"Template updated: {template_name}")
        
        return {
            "success": True,
            "message": "Template updated successfully",
            "template": {"name": template.name, "content": template.content}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )


@router.delete("/templates/{template_name}")
async def delete_template(template_name: str, credentials=Depends(verify_docs_access)):
    """Delete a template from MongoDB."""
    try:
        db = get_db()
        
        result = await db.email_templates.delete_one({"name": template_name})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_name}' not found"
            )
        
        logger.info(f"Template deleted: {template_name}")
        
        return {
            "success": True,
            "message": "Template deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )


@router.get("/send-history")
async def get_send_history(credentials=Depends(verify_docs_access)):
    """Get email send history from MongoDB."""
    return await load_history(limit=50)


@router.get("/send-history/{email_id}")
async def get_send_history_detail(email_id: str, credentials=Depends(verify_docs_access)):
    """Get detailed information about a specific email from history."""
    try:
        detail = await get_history_detail(email_id)
        
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email history with ID '{email_id}' not found"
            )
        
        return detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get history detail"
        )
