from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.endpoints import analyses
from src.core.config import settings
from src.core.database import init_db
from src.api.endpoints import analyses, projects, suggestions
from src.api.middleware import setup_middleware
from src.api.exceptions import setup_exception_handlers

import logging

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Starting MCP Code Analyzer...")
    await init_db()
    logger.info("Database initialized")

    # Load ML models (future)
    # await load_models()

    yield

    # Shutdown
    logger.info("Shutting down MCP Code Analyzer...")
    # Cleanup connections
    # await cleanup_connections()

app = FastAPI(
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(
    projects.router,
    prefix=f"{settings.api_prefix}/projects",
    tags=["projects"]
)
app.include_router(
    analyses.router,
    prefix=f"{settings.api_prefix}/analyses",
    tags=["analyses"]
)
app.include_router(
    suggestions.router,
    prefix=f"{settings.api_prefix}/suggestions",
    tags=["suggestions"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        - **status**: Service health status
        - **version**: Application version
        - **database**: Database connection status
    """
    # Check database connection
    try:
        from sqlalchemy import text
        from src.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status
    }