from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date

class Destination(BaseModel):
    city: str
    country: str
    duration_days: int = Field(ge=1, le=30)

class TravelRequest(BaseModel):
    destinations: List[Destination]
    start_date: date
    end_date: date
    budget: float = Field(gt=0)
    mood: str = Field(..., description="Ambiance souhaitée (romantique, aventure, culture, etc.)")
    travel_style: Optional[str] = Field(None, description="Style de voyage (luxe, économique, aventure, etc.)")
    interests: Optional[List[str]] = Field(None, description="Centres d'intérêt (culture, gastronomie, nature, etc.)")
    group_size: int = Field(ge=1, le=20)
    special_requirements: Optional[str] = None
    preferred_accommodation_type: Optional[str] = None
    preferred_transportation: Optional[str] = None

class ProgramRequest(BaseModel):
    type: Literal["mono", "multi"]
    start_date: date
    end_date: date
    destinations: List[Destination]
    mood: str = Field(..., description="Ambiance souhaitée (romantique, aventure, culture, etc.)")
    budget: float = Field(gt=0)
    group_size: int = Field(ge=1, le=20)
    special_requirements: Optional[str] = None 