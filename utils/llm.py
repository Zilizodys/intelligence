from typing import Dict, Any
import httpx
import re

class LLMService:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model

    async def generate_response(self, prompt: str, system_message: str = None) -> str:
        """
        Génère une réponse à partir d'un prompt en utilisant Ollama (Mistral 7B)
        """
        full_prompt = (system_message + "\n" if system_message else "") + prompt
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json()["response"]

    async def generate_structured_response(self, prompt: str, system_message: str = None) -> Dict[str, Any]:
        """
        Génère une réponse structurée en JSON à partir d'un prompt
        """
        system_msg = system_message or "Tu es un assistant spécialisé dans la génération de programmes de voyage. Réponds toujours en JSON valide."
        response = await self.generate_response(prompt, system_msg)
        import json
        # Extraction du premier bloc JSON valide
        match = re.search(r'({[\s\S]*})', response)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        raise Exception("La réponse n'est pas un JSON valide") 