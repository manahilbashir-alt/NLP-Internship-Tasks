import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API Key
load_dotenv()

# Create Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Prompt
prompt = """
Write a short paragraph about Artificial Intelligence.
"""

low_temp_response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.2
    )
)

high_temp_response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.9
    )
)

print("=" * 60)
print("LOW TEMPERATURE (0.2)")
print("=" * 60)
print(low_temp_response.text)

print("\n" + "=" * 60)
print("HIGH TEMPERATURE (0.9)")
print("=" * 60)
print(high_temp_response.text)

print("\n" + "=" * 60)
print("WHEN TO USE EACH TEMPERATURE")
print("=" * 60)

print("""
Temperature = 0.0 - 0.3
Use for:
- JSON Generation
- Information Extraction
- Code Generation
- Data Processing

Temperature = 0.4 - 0.7
Use for:
- General Chat
- Question Answering
- Summarization

Temperature = 0.8 - 1.0
Use for:
- Story Writing
- Brainstorming
- Creative Content
- Marketing Ideas
""")