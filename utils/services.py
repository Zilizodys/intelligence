from typing import List, Dict, Any
import httpx
from datetime import date
import os

class ExternalServices:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.viator_api_key = os.getenv("VIATOR_API_KEY")

    async def get_supabase_activities(self, destination: str, mood: str, budget: float) -> List[Dict[str, Any]]:
        """
        Récupère les activités depuis Supabase
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/activities",
                    params={
                        "destination": destination,
                        "mood": mood,
                        "max_budget": budget
                    },
                    headers={"apikey": self.supabase_key}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Erreur Supabase: {str(e)}")
            return []

    async def get_viator_activities(self, destination: str, date: date) -> List[Dict[str, Any]]:
        """
        Récupère les activités depuis Viator
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.viator.com/v1/products",
                    params={
                        "destId": destination,
                        "date": date.isoformat()
                    },
                    headers={"exp-api-key": self.viator_api_key}
                )
                response.raise_for_status()
                return response.json().get("products", [])
        except Exception as e:
            print(f"Erreur Viator: {str(e)}")
            return []

    async def find_lodging(self, destination: str, check_in: date, check_out: date, budget: float) -> Dict[str, Any]:
        """
        Simule la recherche d'hébergement (à remplacer par un vrai service)
        """
        return {
            "name": f"Hôtel {destination}",
            "type": "hotel",
            "location": destination,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "price_per_night": budget / 2,
            "booking_url": "https://example.com"
        }

    async def find_transport(self, from_city: str, to_city: str, date: date) -> Dict[str, Any]:
        """
        Simule la recherche de transport (à remplacer par un vrai service)
        """
        return {
            "type": "train",
            "from_location": from_city,
            "to_location": to_city,
            "departure_time": "10:00",
            "arrival_time": "12:00",
            "cost": 50.0,
            "booking_url": "https://example.com"
        } 