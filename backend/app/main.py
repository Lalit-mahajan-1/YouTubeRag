from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.rag import router as rag_router
from app.api.routes.youtube import router as youtube_router
from app.core.config import settings
from app.core.logger import get_logger
from app.db.database import Base, engine
from app.api.routes.notes import router as notes_router

# Import services to trigger singleton init on startup
from app.services.embedding_service import embedding_service  # noqa
from app.services.llm_service import llm_service  # noqa

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting YouTube RAG API...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Ready")
    yield
    await engine.dispose()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(youtube_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(notes_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "healthy"}