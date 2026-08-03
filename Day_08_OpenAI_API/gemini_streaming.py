import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


prompt = """
Explain Artificial Intelligence in simple words.
Give examples.
"""


# -------------------------------
# Normal Response (Non Streaming)
# -------------------------------

print("===== Normal Response =====\n")

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

print(response.text)



# -------------------------------
# Streaming Response
# -------------------------------

print("\n\n===== Streaming Response =====\n")

stream = client.models.generate_content_stream(
    model="gemini-flash-latest",
    contents=prompt
)

for chunk in stream:
    print(chunk.text, end="", flush=True)

print("\n\nStreaming Completed!")