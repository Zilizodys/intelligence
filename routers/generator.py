from fastapi import APIRouter, HTTPException
from schemas.request import TravelRequest, ProgramRequest
from schemas.response import TravelProgram, ProgramResponse, Activity
from agents.router import RouterAgent
from utils.llm import LLMService
from utils.services import ExternalServices
from datetime import datetime, timedelta
import os
import json
import traceback

router = APIRouter()

# Initialisation des services
llm_service = LLMService()
router_agent = RouterAgent(llm_service)
external_services = ExternalServices()

@router.post("/generate-program", response_model=TravelProgram)
async def generate_travel_program(request: TravelRequest):
    """
    Génère un programme de voyage personnalisé basé sur les critères fournis
    """
    try:
        # Vérification de la clé API
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="La clé API OpenAI n'est pas configurée"
            )

        # Génération du programme
        program = await router_agent.generate_travel_program(request)
        return program

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du programme: {str(e)}"
        )

@router.post("/generate-program-v2", response_model=ProgramResponse)
async def generate_program(request: ProgramRequest):
    """
    Nouvelle version de la génération de programme avec orchestration des services externes
    """
    try:
        # 1. Génération de l'itinéraire de base
        itinerary = await router_agent.planner.create_itinerary(request)
        
        # 2. Enrichissement des activités pour chaque destination
        for destination in itinerary["destinations"]:
            # Calcul du budget par jour pour cette destination
            days_count = len(destination["days"])
            daily_budget = request.budget / sum(d.duration_days for d in request.destinations)
            
            # Pour chaque jour
            for day in destination["days"]:
                # Récupération des activités depuis les sources externes
                supabase_activities = await external_services.get_supabase_activities(
                    destination["name"],
                    request.mood,
                    daily_budget
                )
                
                viator_activities = await external_services.get_viator_activities(
                    destination["name"],
                    day["date"]
                )
                
                # Fusion des activités
                all_activities = supabase_activities + viator_activities
                
                # Si pas d'activités trouvées, on utilise le LLM pour en générer
                if not all_activities:
                    prompt = f"""
                    Génère 3 activités pour {destination["name"]} le {day["date"]}
                    Style: {request.mood}
                    Budget: {daily_budget}
                    """
                    llm_activities = await llm_service.generate_structured_response(prompt)
                    all_activities = llm_activities.get("activities", [])
                
                # Sélection et enrichissement des activités via LLM
                if all_activities:
                    prompt = f"""
                    Sélectionne et enrichis 3 activités parmi la liste suivante pour {destination["name"]}:
                    {json.dumps(all_activities, indent=2)}
                    
                    Critères:
                    - Style: {request.mood}
                    - Budget par jour: {daily_budget}
                    - Date: {day["date"]}
                    """
                    
                    selected_activities = await llm_service.generate_structured_response(prompt)
                    day["activities"] = [
                        Activity(
                            name=act["name"],
                            description=act["description"],
                            duration_hours=act["duration_hours"],
                            cost=act["cost"],
                            location=act["location"],
                            category=act["category"],
                            booking_url=act.get("booking_url"),
                            source=act.get("source", "llm")
                        )
                        for act in selected_activities.get("activities", [])
                    ]
            
            # 3. Ajout de l'hébergement
            lodging = await external_services.find_lodging(
                destination["name"],
                destination["start_date"],
                destination["end_date"],
                daily_budget * days_count
            )
            destination["accommodation"] = lodging
            
            # 4. Ajout des transports
            if request.type == "multi":
                # Transport d'arrivée
                transport_in = await external_services.find_transport(
                    "ORIGIN",  # À remplacer par la ville d'origine
                    destination["name"],
                    destination["start_date"]
                )
                destination["transport_in"] = transport_in
                
                # Transport de départ
                transport_out = await external_services.find_transport(
                    destination["name"],
                    "DESTINATION",  # À remplacer par la prochaine destination
                    destination["end_date"]
                )
                destination["transport_out"] = transport_out
        
        # 5. Calcul du coût total
        total_cost = sum(
            sum(act["cost"] for act in day["activities"])
            for dest in itinerary["destinations"]
            for day in dest["days"]
        ) + sum(
            dest["accommodation"]["price_per_night"] * len(dest["days"])
            for dest in itinerary["destinations"]
        )
        
        # 6. Création de la réponse
        return ProgramResponse(
            destinations=itinerary["destinations"],
            total_cost=total_cost,
            currency="EUR",
            generated_at=datetime.now().isoformat(),
            version="2.0",
            metadata={
                "sources_used": ["supabase", "viator", "llm"],
                "activities_count": sum(
                    len(day["activities"])
                    for dest in itinerary["destinations"]
                    for day in dest["days"]
                )
            }
        )

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du programme: {str(e)}"
        )

@router.post("/generate-structured-text")
async def generate_structured_text(request: TravelRequest):
    """
    Génère un programme de voyage structuré (texte/Markdown) pour la première destination
    """
    try:
        program_text = await router_agent.generate_structured_text_program(request)
        return {"program": program_text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du programme structuré : {str(e)}"
        ) 