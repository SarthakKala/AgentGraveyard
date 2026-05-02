from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analytics_router, failures_router, sdk_router, wisdom_router
from api.websocket import router as websocket_router
from db.database import Base, database_health_check, engine
from memory.pinecone_client import initialize_pinecone, pinecone_health_check

API_VERSION = "0.1.1"

app = FastAPI(title="Agent Graveyard API", version=API_VERSION)

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
    db_h = database_health_check()
    pc_h = pinecone_health_check()
    if not db_h["ok"]:
        overall = "unhealthy"
    elif not pc_h["ok"]:
        overall = "degraded"
    else:
        overall = "ok"
    return {
        "status": overall,
        "version": API_VERSION,
        "checks": {
            "database": {"ok": db_h["ok"], "detail": db_h["detail"]},
            "pinecone": {"ok": pc_h["ok"], "detail": pc_h["detail"]},
        },
    }
