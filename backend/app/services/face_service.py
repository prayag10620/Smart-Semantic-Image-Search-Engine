# backend/face_engine.py
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis

class FaceEngine:
    def __init__(self, db_client, references_dir=".data/faces"):
        self.db = db_client
        self.references_dir = references_dir
        
        print("⏳ Loading AI Models...")
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        # 1. Try Loading from DB
        print("🔄 Checking Database for known faces...")
        self.known_names, self.known_embeddings = self.db.load_all_references()

        # 2. If DB is empty, Scan Folder
        if not self.known_names:
            print("⚠️ DB empty! Scanning 'faces/' folder...")
            self._ingest_references_from_disk()
        else:
            print(f"✅ Loaded {len(self.known_names)} people from Database.")
            
        # Convert list to numpy array for fast calculation
        self.known_embeddings = np.array(self.known_embeddings)

    def _ingest_references_from_disk(self):
        """One-time setup: Reads images and saves to DB."""
        if not os.path.exists(self.references_dir):
            os.makedirs(self.references_dir)
            return

        for file in os.listdir(self.references_dir):
            if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                name = os.path.splitext(file)[0]
                img_path = os.path.join(self.references_dir, file)
                
                img = cv2.imread(img_path)
                faces = self.app.get(img)
                
                if len(faces) > 0:
                    embedding = faces[0].normed_embedding
                    
                    # SAVE TO DB INSTANTLY
                    self.db.save_reference_face(name, embedding)
                    
                    # Update local memory
                    self.known_names.append(name)
                    self.known_embeddings.append(embedding)
                    print(f"   💾 Saved to DB: {name}")

    def detect_and_recognize(self, image_path):
        """Identifies people in a new photo."""
        img = cv2.imread(image_path)
        if img is None: return []

        faces = self.app.get(img)
        found_names = []

        if len(self.known_embeddings) == 0:
            return []

        for face in faces:
            # Compare against all known vectors
            sims = np.dot(self.known_embeddings, face.normed_embedding)
            best_idx = np.argmax(sims)
            
            if sims[best_idx] > 0.5:
                found_names.append(self.known_names[best_idx])
        
        return list(set(found_names))
    
    def register_new_face(self, name: str, image_path: str):
        """
        Manually adds a specific image as a reference for a person.
        Strict Mode: Fails if 0 faces or >1 face found.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image file.")

        faces = self.app.get(img)

        if len(faces) == 0:
            raise ValueError(f"❌ No face detected in image. Please use a clear photo.")
        
        if len(faces) > 1:
            # For reference data, we want certainty. Reject group photos.
            raise ValueError(f"❌ Multiple faces detected. Please use a solo photo for registration.")

        # Get the embedding
        embedding = faces[0].normed_embedding
        
        # 1. Save to DB
        self.db.save_reference_face(name, embedding.tolist())
        
        # 2. Update In-Memory Lists (so we don't need to restart server)
        self.known_names.append(name)
        if len(self.known_embeddings) > 0:
            self.known_embeddings = np.vstack([self.known_embeddings, embedding])
        else:
            self.known_embeddings = np.array([embedding])
            
        return True