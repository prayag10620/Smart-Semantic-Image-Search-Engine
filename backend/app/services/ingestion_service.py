# backend/ingestion_service.py
import os
import shutil
from app.services.ai_service import AIEngine
from app.services.face_service import FaceEngine
from app.services.db_service import VectorDB

class IngestionService:
    def __init__(self, db: VectorDB, face_engine: FaceEngine, ai_engine: AIEngine):
        self.db = db
        self.face_engine = face_engine
        self.ai_engine = ai_engine

    def process_image(self, image_path: str):
        """
        Runs the full pipeline on a single image.
        1. Detect Faces
        2. Generate CLIP Vector
        3. Generate Caption
        4. Save to DB
        """
        try:
            print(f"⚡ Processing: {image_path}")
            
            # A. Detect Faces
            people = self.face_engine.detect_and_recognize(image_path)
            print("People Face: ",people)
            # B. Generate Vector (Visual)
            vector = self.ai_engine.generate_embedding(image_path)

            # C. Generate Caption (Text)
            caption = self.ai_engine.generate_caption(image_path)
            print("Caption: " , caption)

            # D. Save to DB
            self.db.save_image(image_path, vector, people, caption)
            
            return True
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
            return False

    def process_folder(self, folder_path: str):
        """Scans a directory recursively."""
        if not os.path.exists(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            return

        count = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    full_path = os.path.join(root, file)
                    self.process_image(full_path)
                    count += 1
        print(f"✅ Batch Ingestion Complete. Processed {count} images.")