from typing import List
from schemas.request import TravelRequest
from schemas.response import DayPlan, DestinationPlan, Activity
from utils.llm import LLMService
from datetime import timedelta

class PlannerAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def create_itinerary(self, request: TravelRequest) -> List[DestinationPlan]:
        """
        Crée un itinéraire détaillé pour chaque destination en utilisant Ollama
        """
        destination_plans = []
        for destination in request.destinations:
            prompt = f"""
            Génère un programme de voyage structuré en JSON pour {destination.city}, {destination.country} sur {destination.duration_days} jours.
            Dates: {request.start_date} à {request.end_date}
            Mood: {request.mood}
            Budget: {request.budget}
            Groupe: {request.group_size}
            
            Pour chaque activité, fournis obligatoirement :
            - name (str) : nom de l'activité
            - description (str) : description courte
            - duration_hours (float) : durée en heures
            - cost (float) : coût en euros
            - location (str) : lieu précis
            - category (str) : type d'activité
            
            Format attendu : {{ "days": [ {{ "date": ..., "activities": [ {{ "name": ..., "description": ..., "duration_hours": ..., "cost": ..., "location": ..., "category": ... }} ] }} ] }}
            """
            response = await self.llm_service.generate_structured_response(prompt)
            day_plans = []
            current_date = request.start_date
            for day in response["days"]:
                activities = []
                for act in day.get("activities", []):
                    activity = Activity(
                        name=act.get("name", "Activité non spécifiée"),
                        description=act.get("description", act.get("name", "Activité non spécifiée")),
                        duration_hours=float(act.get("duration_hours", 1.0)),
                        cost=float(act.get("cost", 0.0)),
                        location=act.get("location", destination.city),
                        category=act.get("category", "général")
                    )
                    activities.append(activity)
                
                day_plan = DayPlan(
                    date=current_date,
                    activities=activities,
                    meals=day.get("meals", []),
                    notes=day.get("notes")
                )
                day_plans.append(day_plan)
                current_date += timedelta(days=1)
            
            destination_plan = DestinationPlan(
                city=destination.city,
                country=destination.country,
                days=day_plans,
                accommodations=[],
                transportation=[]
            )
            destination_plans.append(destination_plan)
        return destination_plans 