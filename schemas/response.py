from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, time

class Activity(BaseModel):
    name: str
    description: Optional[str] = None
    duration_hours: Optional[float] = 1.0
    cost: Optional[float] = 0.0
    location: Optional[str] = None
    category: Optional[str] = "général"
    booking_url: Optional[str] = None
    source: str = "llm"  # llm, supabase, viator

    def __init__(self, **data):
        # Si description n'est pas fournie, utiliser le nom
        if "description" not in data:
            data["description"] = data.get("name", "")
        # Si location n'est pas fournie, utiliser une valeur par défaut
        if "location" not in data:
            data["location"] = "Non spécifié"
        super().__init__(**data)

class Accommodation(BaseModel):
    name: str
    type: str
    location: str
    check_in: date
    check_out: date
    price_per_night: float
    booking_url: Optional[str] = None

class Transportation(BaseModel):
    type: str
    from_location: str
    to_location: str
    departure_time: time
    arrival_time: time
    cost: float
    booking_url: Optional[str] = None

class DayPlan(BaseModel):
    date: date
    activities: List[Activity]
    meals: List[str]
    notes: Optional[str] = None

class DestinationPlan(BaseModel):
    city: str
    country: str
    days: List[DayPlan]
    accommodations: List[Accommodation]
    transportation: List[Transportation]

class TravelProgram(BaseModel):
    destinations: List[DestinationPlan]
    total_cost: float
    currency: str = "EUR"
    generated_at: str
    version: str = "1.0"

class ProgramResponse(BaseModel):
    destinations: List[Dict[str, Any]]  # Structure flexible pour le frontend
    total_cost: float
    currency: str = "EUR"
    generated_at: str
    version: str = "1.0"
    metadata: Dict[str, Any] = {}  # Informations supplémentaires (statistiques, sources, etc.) 