from qdrant_client import QdrantClient, models
from typing import List, Any ,Tuple
import uuid

class VectorDB:
    def __init__(self):
        # Initialize Local Qdrant
        self.client = QdrantClient(host = "localhost",port=6333)
        self.collection_name = "my_photos"

        # Ensure Collection Exists
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=512, 
                    distance=models.Distance.COSINE
                ),
            )
            print(f"📦 Created collection: {self.collection_name}")

    def save_reference_face(self, name: str, embedding: List[float]):
        """Stores a known person's face signature."""
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={"name": name}
                )
            ]
        )
        print(f"👤 Saved reference face for: {name}")

    def load_all_references(self) -> Tuple[List[str], List[List[float]]]:
        """
        Fetches all known faces from DB on startup.
        Returns: (List of Names, List of Embeddings)
        """
        # We assume you have fewer than 2000 reference people.
        # scroll() is efficient for dumping data.
        response = self.client.scroll(
            collection_name=self.collection_name,
            limit=2000,
            with_payload=True,
            with_vectors=True
        )
        
        # response is a tuple: (list_of_points, next_page_offset)
        points = response[0]
        
        names = []
        embeddings = []
        
        for point in points:
            if point.payload and 'name' in point.payload:
                names.append(point.payload['name'])
                embeddings.append(point.vector)
            
        return names, embeddings

    def save_image(self, image_path: str, vector: List[float], people: List[str], caption: str):
        """
        Saves the image data + metadata.
        """
        point_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "path": image_path,
                        "people": people,
                        "caption": caption
                    }
                )
            ]
        )
        print(f"💾 Saved: {image_path}")

    def search_hybrid(self, query_vector: List[float], must_contain_people: List[str] = []) -> List[Any]:
        """
        Performs vector search with metadata filtering using the NEW API.
        """
        search_filter = None

        # Build Filter (If specific people are requested)
        if must_contain_people:
            conditions = [
                models.FieldCondition(
                    key="people", 
                    match=models.MatchValue(value=person)
                ) for person in must_contain_people
            ]
            search_filter = models.Filter(must=conditions)

        # --- THE FIX: Use query_points() instead of search() ---
        # This matches the documentation link you provided.
        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=search_filter,
            limit=10
        )
        
        # The new API returns an object with a .points attribute
        return result.points