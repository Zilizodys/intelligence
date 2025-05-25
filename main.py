from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import generator, chat
import os

app = FastAPI(
    title="Odys.ai Travel API",
    description="API de génération de programmes de voyage IA",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(generator.router, prefix="/api/v1", tags=["generator"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Odys.ai Travel"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)