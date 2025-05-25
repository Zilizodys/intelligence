from typing import List
from schemas.response import Transportation, DestinationPlan
from utils.llm import LLMService

class BookerAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def find_transportation(self, from_destination: DestinationPlan, to_destination: DestinationPlan, budget: float, preferred_type: str = None) -> List[Transportation]:
        """
        Génère des options de transport via Ollama
        """
        prompt = f"""
        Propose 1 option de transport de {from_destination.city} à {to_destination.city} pour un budget de {budget}.
        Format attendu : {{ "transportation": [ {{ "type": ..., "from_location": ..., "to_location": ..., "departure_time": ..., "arrival_time": ..., "cost": ..., "booking_url": ... }} ] }}
        """
        response = await self.llm_service.generate_structured_response(prompt)
        return [Transportation(**trans) for trans in response.get("transportation", [])]

    async def optimize_transportation(self, transportation_options: List[Transportation], criteria: str = "cost") -> Transportation:
        if not transportation_options:
            return None
        if criteria == "cost":
            return min(transportation_options, key=lambda x: x.cost)
        elif criteria == "duration":
            return min(transportation_options, key=lambda x: (x.arrival_time.hour - x.departure_time.hour))
        else:
            return transportation_options[0] 