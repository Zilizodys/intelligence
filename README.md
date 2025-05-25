# Odys.ai - Générateur de Programmes de Voyage IA

Ce projet est une API FastAPI qui génère des programmes de voyage personnalisés en utilisant l'IA.

## Fonctionnalités

- Génération de programmes de voyage multi-destinations
- Planification d'itinéraires détaillés
- Suggestions d'activités personnalisées
- Recherche d'hébergements
- Optimisation des transports
- Gestion du budget

## Prérequis

- Python 3.11+
- Clé API OpenAI

## Installation

1. Cloner le repository :
```bash
git clone [URL_DU_REPO]
cd odys-ai
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
# ou
.\venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env et ajouter votre clé API OpenAI
```

## Utilisation

1. Démarrer le serveur :
```bash
uvicorn main:app --reload
```

2. Accéder à la documentation API :
```
http://localhost:8000/docs
```

## Structure du Projet

```
.
├── main.py                 # Point d'entrée de l'application
├── routers/
│   └── generator.py        # Endpoint de génération de programme
├── schemas/
│   ├── request.py         # Schémas de requête
│   └── response.py        # Schémas de réponse
├── agents/
│   ├── planner.py         # Agent de planification
│   ├── curator.py         # Agent de curation
│   ├── booker.py          # Agent de réservation
│   └── router.py          # Agent de routage
└── utils/
    ├── llm.py             # Utilitaires LLM
    └── format.py          # Utilitaires de formatage
```

## API Endpoints

### POST /api/v1/generate-program

Génère un programme de voyage personnalisé.

**Requête :**
```json
{
  "destinations": [
    {
      "city": "Paris",
      "country": "France",
      "duration_days": 3
    }
  ],
  "start_date": "2024-06-01",
  "end_date": "2024-06-03",
  "budget": 2000,
  "travel_style": "luxe",
  "interests": ["culture", "gastronomie"],
  "group_size": 2
}
```

## Licence

MIT 