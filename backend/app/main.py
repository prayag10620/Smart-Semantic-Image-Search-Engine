# backend/app/main.py
from fastapi import FastAPI #type:ignore
from contextlib import asynccontextmanager
import uvicorn

from app.api import routes_search, routes_ingest , routes_faces  ,routes_auth
from app.dependencies import init_resources

# Lifespan handles startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    init_resources()
    yield
    # Shutdown: Clean up (if needed)
    print("🛑 Shutting down...")

app = FastAPI(title="Smart Image Search", lifespan=lifespan)

# Register the Routes
app.include_router(routes_search.router, prefix="/search", tags=["Search"])
app.include_router(routes_ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(routes_faces.router,prefix ="/face",tags=["Face Resgister"])
app.include_router(routes_auth.router,prefix = "/api", tags=["User Login/Signup"])

@app.get("/")
def root():
    return {"message": "Image Search API is running. Go to /docs for Swagger UI."}

if __name__ == "__main__":
    uvicorn.run(host="localhost",port="8000")