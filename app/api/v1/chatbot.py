"""
HR Chatbot API Endpoints
Uses OpenRouter API with Meta Llama for HR queries
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.dependencies import get_current_active_user
from app.config import settings
import httpx
import os
from typing import List, Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# System prompt for HR chatbot
SYSTEM_PROMPT = """You are QKREW HR Assistant, a helpful AI chatbot for QKREW Software Technologies.

QKREW is a modern software development company with a comprehensive employee management system. You help employees with HR-related queries.

Key Information:
- Company: QKREW Software Technologies
- Hierarchy: L1 (CEO) to L13 (Junior Developer)
- Leave Types: Casual, Sick, Earned, Maternity, Paternity, Unpaid
- Leave Workflow: Employee → HR Review → L7 Team Lead → L6 Architect (if conflicts)
- Software Requests: Employees can request software/tools with business justification
- Notice Period: Employees submit resignation with handover process
- Events: Company organizes team building, training, workshops, and social events
- Incidents: Critical issues are tracked and assigned to team members
- Projects: Managed by Project Managers (L3-L5), Principal Architects (L6), Team Leads (L7)

You should:
1. Answer HR policy questions clearly and concisely
2. Guide users on how to use the QKREW system
3. Be professional but friendly
4. If you don't know something, admit it and suggest contacting HR directly
5. Keep responses brief and actionable

Do not:
- Make up policies or procedures
- Provide personal advice
- Discuss confidential employee information
"""


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_active_user)
):
    """Send message to HR chatbot"""
    
    try:
        api_key = settings.OPENROUTER_API_KEY
        logger.info(f"API Key present: {bool(api_key)}")
        logger.info(f"API Key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
        
        logger.info(f"Sending message to OpenRouter: {chat_message.message[:50]}...")
        
        # Call OpenRouter API with Meta Llama
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "QKREW HR Chatbot"
                },
                json={
                    "model": "mistralai/devstral-2512:free",  # Free Google Gemini model - better availability
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": chat_message.message
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            logger.info(f"OpenRouter response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"OpenRouter API error: {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenRouter API error: {error_text}"
                )
            
            result = response.json()
            bot_response = result["choices"][0]["message"]["content"]
            
            logger.info(f"Bot response received: {bot_response[:50]}...")
            
            from datetime import datetime
            return ChatResponse(
                response=bot_response,
                timestamp=datetime.utcnow().isoformat()
            )
            
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {str(e)}")
        raise HTTPException(status_code=504, detail="Request timeout - AI service took too long")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except KeyError as e:
        logger.error(f"KeyError in response parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invalid response from AI service: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/chat/history")
async def get_chat_history(
    current_user: dict = Depends(get_current_active_user)
):
    """Get chat history (placeholder - implement if needed)"""
    return {
        "messages": [],
        "note": "Chat history not persisted in this version"
    }
