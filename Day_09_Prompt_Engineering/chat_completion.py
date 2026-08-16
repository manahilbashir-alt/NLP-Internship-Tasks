import os
from dotenv import load_dotenv
from google import genai

from prompt_builder import PromptBuilder


# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Create Prompt Builder
builder = PromptBuilder("prompts")

print("=" * 50)
print("      Prompt Engineering Demo")
print("=" * 50)

# Choose task
print("\nAvailable Tasks:")
print("1. summarization")
print("2. sentiment_analysis")
print("3. entity_extraction")
print("4. code_generation")
print("5. data_transformation")
print("6. few_shot")
print("7. persona")
print("8. production_prompt")

task = input("\nEnter task name: ").strip()

# User input
user_text = input("\nEnter your text/request:\n")

# Extra input for persona prompt
if task == "persona":
    persona = input("Enter Persona (e.g., Cybersecurity Expert): ")

    prompt = builder.build_prompt(
        task=task,
        persona=persona,
        input_text=user_text
    )

# Extra input for temperature prompt
elif task == "temperature":
    creativity = input("Creativity Level (Low/Medium/High): ")

    prompt = builder.build_prompt(
        task=task,
        creativity_level=creativity,
        input_text=user_text
    )

# All other prompts
else:
    prompt = builder.build_prompt(
        task=task,
        input_text=user_text
    )

# Send prompt to Gemini
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

# Display response
print("\n" + "=" * 50)
print("AI Response")
print("=" * 50)

print(response.text)