import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = "Explain Natural Language Processing in simple words."

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

print("Response:\n")
print(response.text)

print("\nUsage Information:\n")

if hasattr(response, "usage_metadata") and response.usage_metadata:
    usage = response.usage_metadata

    print("Prompt Tokens:", usage.prompt_token_count)
    print("Completion Tokens:", usage.candidates_token_count)
    print("Total Tokens:", usage.total_token_count)
else:
    print("Usage metadata is not available.")