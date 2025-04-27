# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from slowapi import Limiter, _rate_limit_exceeded_handler # Optional Rate Limiting
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

from app.core.config import settings, logger
from app.api.api_v1.api import api_router
from app.db.base import Base  # Import Base for metadata
from app.db.session import AsyncSessionLocal, engine # Import SessionLocal for startup event
from app.db import init_db # Import the init_db function

# Optional Rate Limiting Setup
# limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # Add other FastAPI parameters like version, description etc.
    )

# Optional Rate Limiting Middleware
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# IMPORTANT: For production, restrict this to your actual frontend domain!
origins = [
    "http://localhost:5173", # Your frontend development server
    # Add your production frontend URL here later, e.g., "https://your-frontend.com"
]
# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"], # Allows all methods
        allow_headers=["*"], # Allows all headers
    )

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- Event Handlers ---

@app.on_event("startup")
async def on_startup():
    """
    Actions to perform on application startup.
    - Initialize database (create tables if they don't exist)
    - Create first superuser if needed
    """
    logger.info("Starting up TwinSecure AI Backend...")
    # Note: In a production setup with Alembic, you might run migrations
    # separately before starting the app, instead of create_all.
    # However, create_all is safe as it won't modify existing tables.
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    # logger.info("Database tables checked/created.")

    # Initialize DB and create superuser if necessary
    # This requires a synchronous session for the initial check/creation
    # For simplicity here, we might call a synchronous helper or adjust init_db
    # Or handle superuser creation via a separate script/command
    logger.info("Attempting to initialize database and create superuser...")
    # await init_db.init_db() # Make init_db async if needed or use sync version
    # For now, we assume Alembic handles table creation and superuser is managed separately or via a startup script.
    logger.info("Startup complete. Database connection assumed ready.")


@app.on_event("shutdown")
async def on_shutdown():
    """
    Actions to perform on application shutdown.
    """
    logger.info("Shutting down TwinSecure AI Backend...")
    # Clean up resources, close connections if necessary
    # await engine.dispose() # Dispose of the engine's connection pool
    logger.info("Shutdown complete.")

# --- Health Check Endpoint ---

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    # Add database connectivity check if desired
    # try:
    #     async with SessionLocal() as db:
    #         await db.execute(text("SELECT 1"))
    #     db_status = "ok"
    # except Exception as e:
    #     logger.error(f"Health check DB connection error: {e}")
    #     db_status = "error"
    return {"status": "ok"} #, "database": db_status}


# Root endpoint (optional)
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint providing basic info.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# --- Example of adding Alembic commands (optional, usually run from CLI) ---
# You could potentially expose migration commands via API endpoints for specific use cases,
# but this is generally discouraged for security reasons.
# It's better to run `alembic upgrade head` during deployment.

