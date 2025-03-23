from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from groq import Groq  # Changed import
import os
from typing import List, Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # Changed client initialization
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Available Groq models (choose one)
SUPPORTED_MODELS = [
    "mixtral-8x7b-32768",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma-7b-it"
]

class DrugRequest(BaseModel):
    drugs: List[str]

class DrugAnalysisResponse(BaseModel):
    molecule: str
    latest_summary: str
    moa: str
    regulatory_news: str
    clinical_news: str
    commercial_news: str

def get_visible_text(url: str) -> str:
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error fetching text: {e}"

def summarize_content(text: str, prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            model=SUPPORTED_MODELS[1],  # Using llama3-70b-8192
            temperature=0.1,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error summarizing content: {e}"

# Rest of the functions remain the same as original...

@app.post("/analyze", response_model=List[DrugAnalysisResponse])
async def analyze_drugs(request: DrugRequest):
    # Implementation remains the same...
    # (Only the OpenAI calls were replaced in summarize_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
