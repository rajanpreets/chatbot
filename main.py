from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from groq import Groq
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
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

SUPPORTED_MODELS = [
    "mixtral-8x7b-32768",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma-7b-it"
]

class DrugRequest(BaseModel):
    drugs: List[str]

class NewsItem(BaseModel):
    summary: str
    url: str

class DrugAnalysisResponse(BaseModel):
    molecule: str
    latest_summary: str
    moa: str
    regulatory_news: List[NewsItem]
    clinical_news: List[NewsItem]
    commercial_news: List[NewsItem]

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
            model=SUPPORTED_MODELS[1],
            temperature=0.1,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error summarizing content: {e}"

def get_latest_summary(drug: str) -> str:
    try:
        params = {
            "api_key": SERPAPI_API_KEY,
            "engine": "google",
            "q": f"{drug} latest drug developments 2024",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": 1
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get('organic_results', [])
        
        if not organic_results:
            return "No recent information found"
            
        top_result = organic_results[0]
        link = top_result.get('link')
        text = get_visible_text(link)
        
        if "Error" in text:
            return "Information unavailable - could not fetch source"
            
        return summarize_content(
            text, 
            "Extract the most recent and important information about this drug in 3 bullet points. Focus on updates from the last 12 months."
        )
        
    except Exception as e:
        return f"Error retrieving summary: {str(e)}"

def categorize_news(summary: str) -> str:
    return summarize_content(
        summary,
        "Classify this news into ONLY ONE of these categories: Clinical, Regulatory, Commercial. Respond only with the category name."
    )

def extract_moa(drug_name: str, summaries: List[str]) -> str:
    return summarize_content(
        "\n".join(summaries),
        f"Identify the mechanism of action for {drug_name} from these news summaries. Respond concisely in one sentence."
    )

@app.post("/analyze", response_model=List[DrugAnalysisResponse])
async def analyze_drugs(request: DrugRequest):
    try:
        all_data = []
        
        for drug in request.drugs:
            clinical, regulatory, commercial = [], [], []
            summaries = []
            
            latest_summary = get_latest_summary(drug)
            
            news_params = {
                "api_key": SERPAPI_API_KEY,
                "engine": "google",
                "q": f"{drug} pharmaceutical news",
                "google_domain": "google.com",
                "gl": "us",
                "hl": "en",
                "tbm": "nws",
                "tbs": "qdr:m",
                "num": 5
            }
            
            news_search = GoogleSearch(news_params)
            news_results = news_search.get_dict().get('news_results', [])
            
            for item in news_results[:5]:
                link = item.get('link')
                news_text = get_visible_text(link)
                
                if "Error" not in news_text:
                    news_summary = summarize_content(
                        news_text,
                        "Summarize this pharmaceutical news in 3 bullet points focusing on drug development aspects."
                    )
                    summaries.append(news_summary)
                    
                    category = categorize_news(news_summary)
                    news_item = {
                        "summary": news_summary,
                        "url": link
                    }
                    if category == 'Clinical':
                        clinical.append(news_item)
                    elif category == 'Regulatory':
                        regulatory.append(news_item)
                    elif category == 'Commercial':
                        commercial.append(news_item)

            moa = extract_moa(drug, summaries) if summaries else "MoA not available"
            
            all_data.append({
                "molecule": drug,
                "latest_summary": latest_summary,
                "moa": moa,
                "regulatory_news": regulatory,
                "clinical_news": clinical,
                "commercial_news": commercial
            })
        
        return all_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
