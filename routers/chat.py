from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from agents.manager import AgentManager
from utils.llm import LLMService
import uuid

router = APIRouter()

# Initialisation des services
llm_service = LLMService()
agent_manager = AgentManager(llm_service)

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Endpoint pour interagir avec l'agent manager via le chat
    """
    try:
        # Générer un nouveau session_id si non fourni
        session_id = message.session_id or str(uuid.uuid4())
        
        # Traiter le message
        response = await agent_manager.process_message(
            session_id=session_id,
            message=message.message,
            context=message.context
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message : {str(e)}"
        )

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Récupère l'historique des conversations pour une session donnée
    """
    try:
        history = agent_manager.get_conversation_history(session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'historique : {str(e)}"
        ) 