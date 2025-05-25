from typing import List
from schemas.response import Activity, Accommodation, DestinationPlan
from utils.llm import LLMService
import re

class CuratorAgent:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def enhance_activities(self, destination_plan: DestinationPlan, interests: List[str], budget: float) -> List[Activity]:
        """
        Enrichit les activités pour une destination via Ollama
        """
        prompt = f"""
        Pour la destination {destination_plan.city}, propose 3 activités par jour en JSON, adaptées aux intérêts suivants : {', '.join(interests)} et au budget {budget}.
        Chaque activité doit obligatoirement contenir les champs suivants :
        - name (str)
        - description (str)
        - duration_hours (float)
        - cost (float)
        - location (str)
        - category (str)
        N'utilise que les clés : name, description, duration_hours, cost, location, category. Pas d'autres clés.
        Format attendu : {{ "activities": [ {{ "name": ..., "description": ..., "duration_hours": ..., "cost": ..., "location": ..., "category": ... }} ] }}
        Réponds uniquement avec le JSON.
        """
        response = await self.llm_service.generate_structured_response(prompt)
        activities = []
        for act in response.get("activities", []):
            # Mapping ultra-générique des clés pour le nom
            name = (
                act.get("name")
                or act.get("activity_name")
                or act.get("activity")
                or act.get("title")
                or act.get("nom")
                or act.get("libelle")
            )
            if not name:
                continue
            activity_data = {
                "name": name,
                "description": act.get("description") or act.get("desc") or act.get("details") or act.get("texte") or name,
                "duration_hours": 1.0,
                "cost": 0.0,
                "location": act.get("location") or act.get("lieu") or destination_plan.city,
                "category": act.get("category") or act.get("type") or "général"
            }
            # Parsing duration
            duration = act.get("duration_hours") or act.get("duration") or act.get("duree")
            if duration:
                try:
                    if isinstance(duration, str):
                        if "hour" in duration or "heure" in duration:
                            match = re.search(r"(\d+(?:[\.,]\d+)?)", duration)
                            if match:
                                duration = float(match.group(1).replace(',', '.'))
                            else:
                                duration = 8.0
                        elif "day" in duration or "journée" in duration:
                            duration = 8.0
                        else:
                            duration = 1.0
                    activity_data["duration_hours"] = float(duration)
                except Exception:
                    pass
            cost = act.get("cost") or act.get("price") or act.get("prix")
            if cost:
                try:
                    activity_data["cost"] = float(cost)
                except Exception:
                    pass
            # Ajoute uniquement l'objet bien formaté
            activities.append(Activity(**activity_data))
        # Fallback si aucune activité valide
        if not activities:
            activities.append(Activity(
                name="Découverte libre",
                description="Journée libre pour explorer la ville.",
                duration_hours=4.0,
                cost=0.0,
                location=destination_plan.city,
                category="général"
            ))
        return activities

    async def find_accommodations(self, destination_plan: DestinationPlan, budget: float, style: str) -> List[Accommodation]:
        """
        Trouve des hébergements via Ollama
        """
        prompt = f"""
        Propose 1 hébergement pour {destination_plan.city} du {destination_plan.days[0].date} au {destination_plan.days[-1].date}, style : {style}, budget total : {budget}.
        Format attendu : {{ "accommodations": [ {{ "name": ..., "type": ..., "location": ..., "check_in": ..., "check_out": ..., "price_per_night": ..., "booking_url": ... }} ] }}
        """
        response = await self.llm_service.generate_structured_response(prompt)
        return [Accommodation(**acc) for acc in response.get("accommodations", [])]

    async def generate_structured_day_plan(self, destination_plan: DestinationPlan, interests: List[str], budget: float) -> str:
        """
        Génère un programme texte structuré jour par jour pour une destination via Ollama
        """
        prompt = f"""
Pour la destination {destination_plan.city}, génère un programme de voyage structuré jour par jour pour un groupe de {len(destination_plan.days)} jours.
Pour chaque jour, propose :
- Une activité le matin
- Un restaurant pour le midi
- Une ou deux activités l'après-midi
- Un restaurant pour le soir
- Une activité le soir

Présente chaque jour ainsi :

Jour X ({destination_plan.city})
Matin : ...
Déjeuner : ...
Après-midi : ...
Soir : ...
Nuit : ...

Sois synthétique, va à la ligne pour chaque section, et ne donne que le programme sans texte autour.
Centres d'intérêt : {', '.join(interests)}
Budget total : {budget} €
"""
        response = await self.llm_service.generate_response(prompt)
        return response 