# backend/app/api/routes_search.py
from fastapi import APIRouter, Depends, Query #type:ignore
from typing import List
from pydantic import BaseModel #type:ignore

from app.dependencies import get_db, get_agent
from app.services.db_service import VectorDB
from app.services.agent import SearchAgent
from app.services.ai_service import AIEngine # We need this to embed the query

router = APIRouter()

# Response Model
class SearchResponse(BaseModel):
    image_path: str
    score: float
    people: List[str]
    caption: str

@router.get("/", response_model=List[SearchResponse])
async def search_images(
    q: str = Query(..., description="Natural language search query"),
    db: VectorDB = Depends(get_db),
    agent: SearchAgent = Depends(get_agent)
):
    # 1. Agent Analysis
    intent = agent.parse_query(q)
    target_people = intent.get('people', [])
    visual_query = intent.get('visual_query', q)

    # 2. Convert text to vector (We can instantiate a temporary AIEngine or reuse one)
    # Optimization: It's better to make AIEngine a dependency too, but for now:
    # We will assume db.search_hybrid handles the embedding or we pass an embedder.
    # Let's assume AIEngine is handled inside the Service layer in a real production app.
    # For this tutorial, let's grab the global AI engine from dependencies to be safe:
    from app.dependencies import ingest_service_instance 
    ai_engine = ingest_service_instance.ai_engine 
    
    query_vector = ai_engine.generate_text_embedding(visual_query)

    # 3. Perform Search
    results = db.search_hybrid(query_vector, target_people)

    # 4. Format Output
    response_data = []
    for point in results:
        response_data.append(SearchResponse(
            image_path=point.payload['path'],
            score=point.score,
            people=point.payload['people'],
            caption=point.payload.get('caption', '')
        ))

    return response_data