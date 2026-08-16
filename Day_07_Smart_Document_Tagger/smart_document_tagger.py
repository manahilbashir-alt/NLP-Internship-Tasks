import json
import re
import os

from dotenv import load_dotenv

load_dotenv()
import nltk
from google import genai
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Download NLTK Resources
# -----------------------------
nltk.download("stopwords")
nltk.download("wordnet")

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


# -----------------------------
# Read Document
# -----------------------------
def read_document(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# -----------------------------
# NLP Preprocessing
# -----------------------------
def preprocess_text(text):

    text = text.lower()

    text = re.sub(r"[^a-zA-Z ]", "", text)

    words = text.split()

    cleaned_words = []

    for word in words:

        if word not in STOP_WORDS:

            cleaned_words.append(
                LEMMATIZER.lemmatize(word)
            )

    return cleaned_words


# -----------------------------
# TF-IDF Keywords
# -----------------------------
def get_tfidf_keywords(text, top_k=8):

    vectorizer = TfidfVectorizer(stop_words="english")

    matrix = vectorizer.fit_transform([text])

    scores = matrix.toarray()[0]

    words = vectorizer.get_feature_names_out()

    ranking = sorted(
        zip(words, scores),
        key=lambda x: x[1],
        reverse=True
    )

    keywords = []

    for word, score in ranking[:top_k]:
        keywords.append(word)

    return keywords


# -----------------------------
# Embedding Keywords
# -----------------------------
def get_embedding_keywords(text, top_k=8):

    model = SentenceTransformer("all-MiniLM-L6-v2")

    vocabulary = list(set(preprocess_text(text)))

    document_embedding = model.encode([text])

    word_embeddings = model.encode(vocabulary)

    similarity = cosine_similarity(
        document_embedding,
        word_embeddings
    )[0]

    ranking = sorted(
        zip(vocabulary, similarity),
        key=lambda x: x[1],
        reverse=True
    )

    keywords = []

    for word, score in ranking[:top_k]:
        keywords.append(word)

    return keywords


# -----------------------------
# Prompt
# -----------------------------
def build_prompt(document, tfidf_keywords, embedding_keywords):

    prompt = f"""
You are an intelligent semantic document tagger.

Example 1

Document:
The patient has diabetes and high blood pressure.

Tags:
["Healthcare","Medicine"]

--------------------------------

Example 2

Document:
Convolutional Neural Networks improve image recognition.

Tags:
["Artificial Intelligence","Computer Vision"]

--------------------------------

Now classify the following document.

Document:
{document}

TF-IDF Keywords:
{tfidf_keywords}

Embedding Keywords:
{embedding_keywords}

Return ONLY valid JSON.

Example:

{{
    "semantic_tags": [
        "Artificial Intelligence",
        "Natural Language Processing",
        "Machine Learning"
    ]
}}

Do not return markdown.
Do not explain anything.
"""

    return prompt


# -----------------------------
# Gemini API
# -----------------------------
def call_llm(prompt):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    text = response.text.strip()

    # Remove markdown if Gemini returns it
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        return json.loads(text)

    except Exception:
        return {
            "semantic_tags": [
                "Artificial Intelligence",
                "Natural Language Processing"
            ]
        }
def save_output(document,
                tfidf_keywords,
                embedding_keywords,
                semantic_tags):

    result = {

        "document": document,

        "tfidf_keywords": tfidf_keywords,

        "embedding_keywords": embedding_keywords,

        "semantic_tags": semantic_tags

    }

    with open("output.json",
              "w",
              encoding="utf-8") as file:

        json.dump(
            result,
            file,
            indent=4
        )

    return result

def main():

    print("Reading document...")

    document = read_document("sample_document.txt")

    print("Extracting TF-IDF keywords...")

    tfidf_keywords = get_tfidf_keywords(document)

    print("Extracting embedding keywords...")

    embedding_keywords = get_embedding_keywords(document)

    print("Sending prompt to Gemini...")

    prompt = build_prompt(
        document,
        tfidf_keywords,
        embedding_keywords
    )

    llm_output = call_llm(prompt)

    result = save_output(
        document,
        tfidf_keywords,
        embedding_keywords,
        llm_output["semantic_tags"]
    )

    print("\nCompleted Successfully!\n")

    print(json.dumps(result, indent=4))
if __name__ == "__main__":
    main()    