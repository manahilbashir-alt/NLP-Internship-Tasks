from gensim.models import Word2Vec

# Load the trained model
model = Word2Vec.load("word2vec.model")

print("Model loaded successfully!")
print("-" * 50)

# Test nearest neighbor queries
test_words = ["exoplanet", "planet", "star", "water"]

for word in test_words:
    if word in model.wv:
        print(f"\nNearest neighbors of '{word}':")

        for similar_word, score in model.wv.most_similar(word, topn=5):
            print(f"{similar_word:15} {score:.4f}")

    else:
        print(f"\n'{word}' not found in the vocabulary.")
print("\n" + "=" * 50)
print("WORD ANALOGY TEST")
print("=" * 50)

try:
    result = model.wv.most_similar(
        positive=["planet", "water"],
        negative=["earth"],
        topn=5
    )

    print("\nAnalogy: planet - earth + water")

    for word, score in result:
        print(f"{word:15} {score:.4f}")

except KeyError as e:
    print("Analogy could not be performed.")
    print(e)    
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

print("\n" + "=" * 50)
print("WORD2VEC SIMILARITY")
print("=" * 50)

pairs = [
    ("planet", "exoplanets"),
    ("star", "stars"),
    ("virus", "deaths"),
    ("python", "code"),
    ("generator", "iterator")
]


def get_sentence_vector(text):
    words = text.lower().split()

    vectors = []

    for word in words:
        if word in model.wv:
            vectors.append(model.wv[word])

    if len(vectors) == 0:
        return None

    return np.mean(vectors, axis=0)


for first, second in pairs:

    vector1 = get_sentence_vector(first)
    vector2 = get_sentence_vector(second)

    if vector1 is not None and vector2 is not None:

        similarity = cosine_similarity([vector1], [vector2])[0][0]

        print(f"{first:15} <--> {second:15} {similarity:.4f}")

    else:

        print(f"{first:15} <--> {second:15} Not Found")        
