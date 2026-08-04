import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API Key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Strict System Prompt
system_prompt = """
You are an AI assistant.

Rules:
1. Return ONLY valid JSON.
2. Do not write explanations.
3. Do not use Markdown.
4. Follow the schema exactly.
5. Do not add extra keys.
6. Do not remove required keys.

JSON Schema:
{
    "topic": "string",
    "definition": "string",
    "example": "string"
}
"""

# User Message
user_message = types.Content(
    role="user",
    parts=[
        types.Part.from_text(
            text="Explain tokenization."
        )
    ]
)

# Generate Response
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=[user_message],
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

response_text = response.text.strip()

print("\nRaw Response:\n")
print(response_text)

try:
    data = json.loads(response_text)

    required_keys = {"topic", "definition", "example"}

    if set(data.keys()) != required_keys:
        raise ValueError("JSON schema does not match.")

    print("\n Valid JSON")
    print(json.dumps(data, indent=4))

except json.JSONDecodeError:
    print("\n Invalid JSON returned by the model.")

except ValueError as e:
    print(f"\n {e}")