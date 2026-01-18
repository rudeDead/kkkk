"""
Project Notes API Endpoints
CRUD operations for project notes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Optional
from uuid import UUID

from app.database import get_db, get_service_db
from app.core.dependencies import get_current_active_user
from app.models.note import NoteCreate, NoteUpdate, NoteResponse, NotesListResponse

router = APIRouter(prefix="/projects/{project_id}/notes", tags=["notes"])

@router.get("", response_model=NotesListResponse)
async def get_project_notes(
    project_id: str,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all notes for a project"""
    try:
        query = db.table("project_notes").select("*, users!created_by_id(name, email)").eq("project_id", project_id)
        
        if category:
            query = query.eq("category", category)
        
        query = query.order("created_at", desc=True)
        
        response = query.execute()
        
        notes = []
        for row in (response.data or []):
            user_data = row.get("users") or {}
            notes.append(NoteResponse(
                id=row['id'],
                project_id=row['project_id'],
                title=row['title'],
                content=row['content'],
                category=row['category'],
                created_by_id=row['created_by_id'],
                created_by_name=user_data.get('name'),
                created_by_email=user_data.get('email'),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return NotesListResponse(notes=notes, total=len(notes))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notes: {str(e)}"
        )

@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    project_id: str,
    note: NoteCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create a new note for a project"""
    try:
        # Verify project exists
        project_check = db.table("projects").select("id").eq("id", project_id).execute()
        
        if not project_check.data or len(project_check.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Create note
        new_note = {
            "project_id": project_id,
            "title": note.title,
            "content": note.content,
            "category": note.category,
            "created_by_id": current_user["id"]
        }
        
        response = db.table("project_notes").insert(new_note).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create note"
            )
        
        row = response.data[0]
        
        # Get creator info
        user_response = db.table("users").select("name, email").eq("id", current_user["id"]).execute()
        user_data = user_response.data[0] if user_response.data else {}
        
        return NoteResponse(
            id=row['id'],
            project_id=row['project_id'],
            title=row['title'],
            content=row['content'],
            category=row['category'],
            created_by_id=row['created_by_id'],
            created_by_name=user_data.get('name'),
            created_by_email=user_data.get('email'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create note: {str(e)}"
        )

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    project_id: str,
    note_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get a specific note"""
    try:
        response = db.table("project_notes").select("*, users!created_by_id(name, email)").eq("id", note_id).eq("project_id", project_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        row = response.data[0]
        user_data = row.get("users") or {}
        
        return NoteResponse(
            id=row['id'],
            project_id=row['project_id'],
            title=row['title'],
            content=row['content'],
            category=row['category'],
            created_by_id=row['created_by_id'],
            created_by_name=user_data.get('name'),
            created_by_email=user_data.get('email'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch note: {str(e)}"
        )

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    project_id: str,
    note_id: str,
    note: NoteUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Update a note"""
    try:
        # Check if note exists and belongs to project
        existing = db.table("project_notes").select("*").eq("id", note_id).eq("project_id", project_id).execute()
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        # Build update data
        update_data = {}
        
        if note.title is not None:
            update_data["title"] = note.title
        if note.content is not None:
            update_data["content"] = note.content
        if note.category is not None:
            update_data["category"] = note.category
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        response = db.table("project_notes").update(update_data).eq("id", note_id).eq("project_id", project_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update note"
            )
        
        row = response.data[0]
        
        # Get creator info
        user_response = db.table("users").select("name, email").eq("id", row['created_by_id']).execute()
        user_data = user_response.data[0] if user_response.data else {}
        
        return NoteResponse(
            id=row['id'],
            project_id=row['project_id'],
            title=row['title'],
            content=row['content'],
            category=row['category'],
            created_by_id=row['created_by_id'],
            created_by_name=user_data.get('name'),
            created_by_email=user_data.get('email'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update note: {str(e)}"
        )

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    project_id: str,
    note_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Delete a note"""
    try:
        # Check if exists
        existing = db.table("project_notes").select("id").eq("id", note_id).eq("project_id", project_id).execute()
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        db.table("project_notes").delete().eq("id", note_id).eq("project_id", project_id).execute()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete note: {str(e)}"
        )
