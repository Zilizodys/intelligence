from typing import List, Dict, Any
from schemas.request import TravelRequest
from schemas.response import TravelProgram
from agents.planner import PlannerAgent
from agents.curator import CuratorAgent
from agents.booker import BookerAgent
from utils.llm import LLMService
from datetime import datetime

class AgentManager:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.planner = PlannerAgent(llm_service)
        self.curator = CuratorAgent(llm_service)
        self.booker = BookerAgent(llm_service)
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

    async def process_message(self, session_id: str, message: str, context: Dict[str, Any] = None) -> str:
        """
        Traite un message utilisateur et génère une réponse appropriée
        """
        # Initialiser ou récupérer l'historique de conversation
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        # Ajouter le message de l'utilisateur à l'historique
        self.conversations[session_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Analyser l'intention du message
        intent_prompt = f"""
        Analyse le message suivant et détermine l'intention principale :
        Message: {message}
        
        Réponds avec un seul mot parmi :
        - PROGRAM : demande de génération/modification de programme
        - INFO : demande d'information sur une destination/activité
        - BOOKING : demande de réservation
        - OTHER : autre type de demande
        """
        intent = await self.llm_service.generate_response(intent_prompt)

        # Générer une réponse appropriée selon l'intention
        if "PROGRAM" in intent.upper():
            response = await self._handle_program_request(message, context)
        elif "INFO" in intent.upper():
            response = await self._handle_info_request(message)
        elif "BOOKING" in intent.upper():
            response = await self._handle_booking_request(message)
        else:
            response = await self._handle_general_request(message)

        # Ajouter la réponse à l'historique
        self.conversations[session_id].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return response

    async def _handle_program_request(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Gère les demandes liées à la génération ou modification de programme
        """
        prompt = f"""
        En tant qu'expert en voyages, réponds à la demande suivante concernant un programme de voyage :
        {message}
        
        Si la demande nécessite des modifications au programme, explique les changements proposés.
        Si c'est une nouvelle demande, propose une structure de programme adaptée.
        """
        return await self.llm_service.generate_response(prompt)

    async def _handle_info_request(self, message: str) -> str:
        """
        Gère les demandes d'information sur les destinations ou activités
        """
        prompt = f"""
        En tant qu'expert en voyages, fournis des informations détaillées sur :
        {message}
        
        Inclus des détails pratiques, des conseils et des recommandations.
        """
        return await self.llm_service.generate_response(prompt)

    async def _handle_booking_request(self, message: str) -> str:
        """
        Gère les demandes de réservation
        """
        prompt = f"""
        En tant qu'expert en voyages, explique le processus de réservation pour :
        {message}
        
        Fournis des étapes claires et des conseils pratiques.
        """
        return await self.llm_service.generate_response(prompt)

    async def _handle_general_request(self, message: str) -> str:
        """
        Gère les autres types de demandes
        """
        prompt = f"""
        En tant qu'expert en voyages, réponds de manière professionnelle et utile à :
        {message}
        """
        return await self.llm_service.generate_response(prompt)

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Récupère l'historique des conversations pour une session donnée
        """
        return self.conversations.get(session_id, []) 