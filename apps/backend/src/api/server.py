from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chat, health, sessions, status

app = FastAPI(
    title="GlyGen Chatbot API",
    description="RAG chatbot for Essentials of Glycobiology with session memory.",
    version="0.2.0",
)


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
app.include_router(sessions.router)
app.include_router(chat.router)


def main() -> None:
    import uvicorn
    from pathlib import Path

    project = Path(__file__).resolve().parents[4]
    uvicorn.run(
        "api.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[
            str(project / "apps" / "backend" / "src"),
            str(project / "packages"),
            str(project / "config"),
            str(project / "prompts"),
        ],
    )


if __name__ == "__main__":
    main()
