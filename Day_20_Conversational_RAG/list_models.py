from dotenv import load_dotenv
load_dotenv("/home/pb/Documents/AI-Engineering/day18_RAG_Pipeline/.env")

from google import genai

client = genai.Client()

for model in client.models.list():
    print(model.name)