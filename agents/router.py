from typing import List
from schemas.request import TravelRequest
from schemas.response import TravelProgram, DestinationPlan
from agents.planner import PlannerAgent
from agents.curator import CuratorAgent
from agents.booker import BookerAgent
from utils.llm import LLMService
from datetime import datetime

class RouterAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.planner = PlannerAgent(llm_service)
        self.curator = CuratorAgent(llm_service)
        self.booker = BookerAgent(llm_service)

    async def generate_travel_program(self, request: TravelRequest) -> TravelProgram:
        """
        Orchestration complète avec appels LLM (Ollama) à chaque étape
        """
        destination_plans = await self.planner.create_itinerary(request)
        for i, plan in enumerate(destination_plans):
            # Enrichissement des activités
            enhanced_activities = await self.curator.enhance_activities(
                plan,
                getattr(request, 'interests', [getattr(request, 'mood', '')]),
                request.budget
            )
            for day in plan.days:
                day.activities = enhanced_activities
            # Hébergement
            accommodations = await self.curator.find_accommodations(
                plan,
                request.budget,
                getattr(request, 'mood', getattr(request, 'travel_style', ''))
            )
            plan.accommodations = accommodations
            # Transport
            if i < len(destination_plans) - 1:
                transportation_options = await self.booker.find_transportation(
                    plan,
                    destination_plans[i + 1],
                    request.budget,
                    None
                )
                best_transport = await self.booker.optimize_transportation(
                    transportation_options,
                    "cost"
                )
                if best_transport:
                    plan.transportation.append(best_transport)
        total_cost = sum(
            sum(acc.price_per_night for acc in plan.accommodations) +
            sum(trans.cost for trans in plan.transportation) +
            sum(activity.cost for day in plan.days for activity in day.activities)
            for plan in destination_plans
        )
        return TravelProgram(
            destinations=destination_plans,
            total_cost=total_cost,
            currency="EUR",
            generated_at=datetime.now().isoformat(),
            version="1.0"
        )

    async def generate_structured_text_program(self, request: TravelRequest) -> str:
        """
        Orchestration pour générer un programme texte structuré (Markdown ou texte clair) pour la première destination
        """
        destination_plans = await self.planner.create_itinerary(request)
        if not destination_plans:
            return "Aucune destination trouvée."
        plan = destination_plans[0]
        # On utilise mood comme valeur par défaut pour interests et travel_style
        interests = request.interests or [request.mood]
        budget = request.budget
        # Appel à l'agent curator pour générer le texte structuré
        program_text = await self.curator.generate_structured_day_plan(plan, interests, budget)
        return program_text 