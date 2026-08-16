import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Structured prompt
prompt = """
Explain what tokenization is.

Include:
1. A simple definition
2. One real-world example
3. Why tokenization is important in NLP
"""

# Send request
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

# Print the generated response
print(response.text)

# Print the complete response object
print("\n\n===== FULL RESPONSE =====\n")
print(response)