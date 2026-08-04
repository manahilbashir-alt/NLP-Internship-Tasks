import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API Key
load_dotenv()

# Create Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

persona = "technical"

personas = {
    "formal": """
You are a formal AI assistant.
Use professional language.
Give clear, polite, and concise answers.
""",

    "casual": """
You are a friendly AI assistant.
Use simple, conversational language.
Keep responses relaxed and easy to understand.
""",

    "technical": """
You are an expert software engineer and NLP specialist.
Provide detailed technical explanations.
Use appropriate programming terminology and examples.
"""
}

prompt = """
Explain what tokenization is.
"""

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=personas[persona],
        temperature=0.5
    )
)

print("=" * 60)
print(f"SELECTED PERSONA: {persona.upper()}")
print("=" * 60)

print("\nSystem Prompt:")
print(personas[persona])

print("\nAI Response:\n")
print(response.text)