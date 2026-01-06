# backend/app/services/agent_service.py
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.core.config import settings

# 1. Define the Expected Output Structure (Pydantic)
class SearchIntent(BaseModel):
    people: List[str] = Field(description="List of known names found in the query")
    visual_query: str = Field(description="Visual scene description for CLIP, without names")

class SearchAgent:
    def __init__(self, known_people: List[str]):
        self.known_people = known_people
        
        # 2. Select the Model based on Config
        if settings.LLM_PROVIDER == "groq":
            print("🚀 Using Groq (Cloud) for Agent")
            self.llm = ChatGroq(
                temperature=0, 
                model_name=settings.GROQ_MODEL, 
                api_key=settings.GROQ_API_KEY
            )
        else:
            print("🦙 Using Ollama (Local) for Agent")
            self.llm = ChatOllama(
                model=settings.OLLAMA_MODEL, 
                base_url=settings.OLLAMA_BASE_URL,
                format="json" # Native JSON mode for Ollama
            )

        # 3. Create the Prompt Template
        # We inject the 'format_instructions' automatically
        self.parser = JsonOutputParser(pydantic_object=SearchIntent)
        
        template = """
        You are a smart search engine for a personal photo gallery.
        
        CONTEXT:
        The database contains photos of these specific people: {known_people}
        
        USER QUERY: {query}
        
        INSTRUCTIONS:
        1. Identify if any of the 'known_people' are mentioned. Map variations (e.g., "my best friend") to the closest name if obvious.
        2. Create a 'visual_query' for a CLIP model. This should describe the SCENE, ACTIONS, and OBJECTS, but remove the specific names.
        
        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["query"],
            partial_variables={"known_people": str(self.known_people), "format_instructions": self.parser.get_format_instructions()}
        )

        # 4. Connect the Chain (Prompt -> LLM -> Parser)
        self.chain = self.prompt | self.llm | self.parser

    def parse_query(self, user_query: str):
        """
        Input: "Pic of me and Rahul eating"
        Output: {'people': ['me', 'rahul'], 'visual_query': 'people eating food'}
        """
        try:
            # Invoke the chain
            result = self.chain.invoke({"query": user_query})
            return result
        except Exception as e:
            print(f"⚠️ Agent Error: {e}")
            # Fallback
            return {"people": [], "visual_query": user_query}