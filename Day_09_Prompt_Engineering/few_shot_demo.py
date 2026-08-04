import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API Key
load_dotenv()

# Create Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# System Instruction
system_prompt = """
You are an AI assistant.

Always answer in the same format as the examples.
"""

# Few-Shot Conversation
contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="What is NLP?")]
    ),
    types.Content(
        role="model",
        parts=[types.Part.from_text(
            text="NLP stands for Natural Language Processing. It enables computers to understand and process human language."
        )]
    ),
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="What is Machine Learning?")]
    ),
    types.Content(
        role="model",
        parts=[types.Part.from_text(
            text="Machine Learning is a branch of Artificial Intelligence that enables computers to learn from data without being explicitly programmed."
        )]
    ),
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="What is Tokenization?")]
    )
]

# Generate Response
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=contents,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print("\n===== RESPONSE =====\n")
print(response.text)