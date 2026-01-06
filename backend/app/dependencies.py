# backend/app/dependencies.py
from app.services.db_service import VectorDB
from app.services.ai_service import AIEngine
from app.services.face_service import FaceEngine
from app.services.ingestion_service import IngestionService
from app.services.agent import SearchAgent

# Global placeholders
db_instance = None
ingest_service_instance = None
agent_instance = None
face_engine = None

def get_face_engine():
    return face_engine

def get_db():
    return db_instance

def get_ingest_service():
    return ingest_service_instance

def get_agent():
    return agent_instance

def init_resources():
    """Initializes all heavy models. Called by main.py on startup."""
    global db_instance, ingest_service_instance, agent_instance , face_engine
    
    print("⏳ Initializing Global Services...")
    
    # 1. Load DB
    db_instance = VectorDB()
    
    # 2. Load Engines
    ai_engine = AIEngine()
    face_engine = FaceEngine(db_client=db_instance, references_dir="./data/faces")
    
    # 3. Create Services
    ingest_service_instance = IngestionService(db_instance, face_engine, ai_engine)
    
    # 4. Create Agent
    known_people = list(set(face_engine.known_names))
    agent_instance = SearchAgent(known_people=known_people)
    
    print("✅ All Systems Ready.")