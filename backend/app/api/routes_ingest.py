# backend/app/api/routes_ingest.py
import os
import shutil
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends #type:ignore
from pydantic import BaseModel #type:ignore

from app.dependencies import get_ingest_service
from app.services.ingestion_service import IngestionService
from app.core.config import settings

router = APIRouter()

# Configuration (Ideally moved to core/config.py)
# UPLOAD_DIR = "./data/uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

class FolderRequest(BaseModel):
    path: str

@router.post("/upload")
async def upload_image(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingest_service)
):
    try:
        # Save file to disk
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger Service in background
        background_tasks.add_task(service.process_image, file_path)
        
        return {"status": "queued", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/folder")
async def scan_folder(
    background_tasks: BackgroundTasks, 
    request: FolderRequest,
    service: IngestionService = Depends(get_ingest_service)
):
    if not os.path.exists(request.path):
        raise HTTPException(status_code=404, detail="Folder path not found")
        
    background_tasks.add_task(service.process_folder, request.path)
    
    return {"status": "queued", "path": request.path}