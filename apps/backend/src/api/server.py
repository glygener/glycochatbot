from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth, chat, health, sessions, status
from session.db import init_db

app = FastAPI(
    title="GlyGen Chatbot API",
    description="RAG chatbot for Essentials of Glycobiology with session memory.",
    version="0.3.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "GlyGen Chatbot API",
        "health": "/health",
        "docs": "/docs",
        "ui": "http://127.0.0.1:8501",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(status.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(chat.router)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "api.server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
