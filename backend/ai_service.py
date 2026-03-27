import vertexai
from vertexai.generative_models import GenerativeModel
import os

# Initialize Vertex AI
# These variables will be set in your Vertex AI / Google Cloud environment
project_id = os.getenv("GCP_PROJECT_ID", "your-project-id")
location = os.getenv("GCP_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

model = GenerativeModel("gemini-1.5-flash")

def ai_generate_summary(news_text: str):
    response = model.generate_content(f"Summarize this financial news in 2 sentences: {news_text}")
    return response.text

def ai_generate_analysis_steps(news_text: str):
    prompt = f"Provide a 3-step logical analysis of how this news affects the market: {news_text}"
    response = model.generate_content(prompt)
    return response.text

def ai_get_sentiment(news_text: str):
    prompt = f"Analyze the market sentiment of this text. Return ONLY a number between 0 and 100: {news_text}"
    response = model.generate_content(prompt)
    # Strip any non-numeric characters the AI might add
    return int(''.join(filter(str.isdigit, response.text)))