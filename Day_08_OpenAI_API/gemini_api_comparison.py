import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -------------------------------
# Method 1: Generate Content API
# -------------------------------

print("===== Generate Content API =====")

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Explain machine learning in simple words."
)

print(response.text)



# -------------------------------
# Method 2: Chat API
# -------------------------------

print("\n===== Chat API =====")

chat = client.chats.create(
    model="gemini-flash-latest"
)

response = chat.send_message(
    "What are the main applications of machine learning?"
)

print(response.text)