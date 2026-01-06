# backend/app/api/routes_faces.py
import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List

from app.dependencies import get_face_engine
from app.services.face_service import FaceEngine
from app.core.config import settings

router = APIRouter()

@router.post("/register")
async def register_face(
    name: str = Form(...), # User types "Rahul"
    files: List[UploadFile] = File(...), # User uploads 1 or 5 photos
    face_engine: FaceEngine = Depends(get_face_engine)
):
    """
    Upload photos to register/improve a person's recognition.
    You can upload multiple photos of 'Rahul' to improve accuracy.
    """
    results = []
    
    # Create a temp folder for processing
    temp_dir = os.path.join(settings.DATA_DIR, "temp_reg")
    os.makedirs(temp_dir, exist_ok=True)

    for file in files:
        try:
            # Save temp file
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Register using our Updated Engine
            face_engine.register_new_face(name, file_path)
            
            results.append(f"✅ {file.filename}: Registered successfully")
            
            # Cleanup temp file
            os.remove(file_path)
            
        except ValueError as e:
            results.append(f"❌ {file.filename}: {str(e)}")
        except Exception as e:
            results.append(f"❌ {file.filename}: Unexpected Error {str(e)}")

    return {
        "person": name,
        "summary": results,
        "total_references_now": face_engine.known_names.count(name)
    }

@router.get("/list")
async def list_people(face_engine: FaceEngine = Depends(get_face_engine)):
    """Return a list of all known people and how many reference photos they have."""
    from collections import Counter
    counts = Counter(face_engine.known_names)
    return {"people": counts}