import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# Create Gemini client
client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1"}
)


def generate_answer(prompt):
    """
    Generate a grounded answer using Gemini
    Interactions API.
    """

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text