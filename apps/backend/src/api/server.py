from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chat, health, sessions, status

app = FastAPI(
    title="GlyGen Chatbot API",
    description="RAG chatbot for Essentials of Glycobiology with session memory.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(status.router)
app.include_router(sessions.router)
app.include_router(chat.router)
