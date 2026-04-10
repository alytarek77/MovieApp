import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def generate_recommendaton_ai(mood, genre):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")

    client = genai.Client(api_key=api_key)

    # Added instruction to return JSON so your JSON.loads doesn't break
    prompt = f"""
    You are a JSON generator. Based on the mood '{mood}' and the genre '{genre}', 
    recommend 3 movies.
    
    IMPORTANT: You must respond ONLY with a valid JSON object. 
    Do not include markdown formatting like ```json or any introductory text.
    
    Strict JSON structure:
    {{
        "recommendation": "Movie Title (Year) - A short description of why it fits."
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash", # Note: ensure your model name is correct
        contents=prompt
    )

    return response.text