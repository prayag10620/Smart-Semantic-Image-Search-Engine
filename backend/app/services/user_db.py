# backend/app/services/user_db.py
from sqlalchemy import create_engine, Column, Integer, String # type: ignore
from sqlalchemy.orm import sessionmaker, declarative_base # type: ignore
from app.core.config import settings

Base = declarative_base()

# 1. Define User Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# 2. Setup SQLite Engine
engine = create_engine(settings.SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create Tables (Run this on import)
Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()