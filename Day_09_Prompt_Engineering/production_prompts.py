import os
from dotenv import load_dotenv
from google import genai

# Load API Key
load_dotenv()

# Create Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
structured_json_prompt = """
Generate the response ONLY in the following JSON format.

{
  "name": "",
  "age": 0,
  "city": ""
}

Input:
Ali is 20 years old and lives in Lahore.
"""

unstructured_text_prompt = """
Extract the following information from the text.

Return ONLY JSON.

Text:
Ali is a Computer Science student at FAST University. He lives in Lahore and is interested in NLP.

Required Fields:
- Name
- University
- City
- Interest
"""

code_generation_prompt = """
Write a Python function to check whether a number is prime.

Requirements:
- Use functions.
- Add comments.
- Include an example.
"""

document_summary_prompt = """
Summarize the following document in 5 bullet points.

Document:
Natural Language Processing (NLP) is a branch of Artificial Intelligence that enables computers to understand, interpret, and generate human language. It is widely used in chatbots, translation systems, speech recognition, sentiment analysis, and text summarization.
"""
prompt = structured_json_prompt

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

print("\n===== PROMPT =====\n")
print(prompt)

print("\n===== RESPONSE =====\n")
print(response.text)