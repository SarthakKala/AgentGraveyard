from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analytics_router, failures_router, sdk_router, wisdom_router
from api.websocket import router as websocket_router
from db.database import Base, engine
from memory.pinecone_client import initialize_pinecone

app = FastAPI(title="Agent Graveyard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sdk_router)
app.include_router(failures_router)
app.include_router(analytics_router)
app.include_router(wisdom_router)
app.include_router(websocket_router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    initialize_pinecone()


@app.get("/health")
def health():
    return {"status": "ok"}
