# backend/ai_engine.py
from sentence_transformers import SentenceTransformer
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

class AIEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚙️ AI Engine utilizing: {self.device}")

        # 1. Load CLIP Model (For Vector Search)
        # 'clip-ViT-B-32' outputs a 512-dimensional vector
        print("⏳ Loading CLIP Model...")
        self.clip_model = SentenceTransformer('clip-ViT-B-32', device=self.device)

        # 2. Load VLM Model (For Image Captioning - Optional but powerful)
        print("⏳ Loading BLIP Captioning Model...")
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)

    def generate_embedding(self, image_path):
        """Converts image to a 512-dim vector for search."""
        try:
            img = Image.open(image_path)
            # CLIP handles the preprocessing internally
            vector = self.clip_model.encode(img)
            return vector.tolist() # Convert numpy -> list for DB
        except Exception as e:
            print(f"❌ Error embedding {image_path}: {e}")
            return [0.0] * 512

    def generate_caption(self, image_path):
        """Creates a text description of the image."""
        try:
            img = Image.open(image_path).convert('RGB')
            
            # Prepare inputs
            inputs = self.blip_processor(img, return_tensors="pt").to(self.device)
            
            # Generate caption
            out = self.blip_model.generate(**inputs, max_new_tokens=50)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            
            return caption
        except Exception as e:
            print(f"❌ Error captioning {image_path}: {e}")
            return ""
        
    def generate_text_embedding(self, text_query):
        """Converts a search phrase (e.g. 'party at night') to a vector."""
        # CLIP can encode text directly
        vector = self.clip_model.encode(text_query)
        return vector.tolist()