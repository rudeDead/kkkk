"""
Project Notes Models
Pydantic schemas for project notes
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class NoteCategory(str):
    """Note category enum"""
    GENERAL = "general"
    MEETING = "meeting"
    TECHNICAL = "technical"
    FEEDBACK = "feedback"

class NoteBase(BaseModel):
    """Base note schema"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: str = Field(default="general")

class NoteCreate(NoteBase):
    """Schema for creating a note"""
    pass

class NoteUpdate(BaseModel):
    """Schema for updating a note"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None

class NoteResponse(NoteBase):
    """Schema for note response"""
    id: UUID
    project_id: UUID
    created_by_id: UUID
    created_by_name: Optional[str] = None
    created_by_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotesListResponse(BaseModel):
    """Schema for notes list response"""
    notes: list[NoteResponse]
    total: int
