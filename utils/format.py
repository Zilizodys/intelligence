from typing import Dict, List, Any
from datetime import datetime, date
import json

class DataFormatter:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Nettoie le texte en supprimant les caractères spéciaux et en normalisant les espaces
        """
        if not text:
            return ""
        return " ".join(text.split())

    @staticmethod
    def format_date(date_str: str) -> date:
        """
        Convertit une chaîne de date en objet date
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Format de date invalide: {date_str}")

    @staticmethod
    def format_time(time_str: str) -> datetime.time:
        """
        Convertit une chaîne d'heure en objet time
        """
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise ValueError(f"Format d'heure invalide: {time_str}")

    @staticmethod
    def format_currency(amount: float, currency: str = "EUR") -> str:
        """
        Formate un montant avec le symbole de la devise
        """
        currency_symbols = {
            "EUR": "€",
            "USD": "$",
            "GBP": "£"
        }
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{amount:.2f}"

    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Vérifie si un dictionnaire contient tous les champs requis
        """
        return all(field in data for field in required_fields)

    @staticmethod
    def format_duration(hours: float) -> str:
        """
        Formate une durée en heures et minutes
        """
        whole_hours = int(hours)
        minutes = int((hours - whole_hours) * 60)
        if whole_hours == 0:
            return f"{minutes}min"
        return f"{whole_hours}h{minutes:02d}" 