import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


prompt = """
Write a short motivational message for computer science students.
"""


experiments = [
    {
        "name": "Experiment 1: Low Creativity",
        "temperature": 0.2,
        "top_p": 0.5,
        "max_tokens": 50
    },
    {
        "name": "Experiment 2: Balanced",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 100
    },
    {
        "name": "Experiment 3: High Creativity",
        "temperature": 1.2,
        "top_p": 1.0,
        "max_tokens": 150
    }
]


for exp in experiments:

    print("\n" + "=" * 50)
    print(exp["name"])
    print("=" * 50)

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=exp["temperature"],
            top_p=exp["top_p"],
            max_output_tokens=exp["max_tokens"]
        )
    )

    print(response.text)