from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from gensim.models import Word2Vec
import numpy as np
import os


os.makedirs(
    "outputs",
    exist_ok=True
)


tests = {

    "Synonym Test": [
        "The movie was very good.",
        "The film was very excellent."
    ],

    "Polysemy Test": [
        "I deposited money in the bank.",
        "I sat near the bank of the river."
    ]

}



# -----------------------------
# TF-IDF
# -----------------------------

def tfidf_similarity(sentences):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(
        sentences
    )

    return cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]



# -----------------------------
# N-Gram
# -----------------------------

def ngram_similarity(sentences):

    vectorizer = CountVectorizer(
        ngram_range=(1,2)
    )

    vectors = vectorizer.fit_transform(
        sentences
    )

    return cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]



# -----------------------------
# Word2Vec
# -----------------------------

word2vec_model = Word2Vec.load(
    "word2vec.model"
)



def sentence_vector(sentence):

    words = sentence.lower().split()

    vectors = []


    for word in words:

        word = word.strip(".,!?")

        if word in word2vec_model.wv:

            vectors.append(
                word2vec_model.wv[word]
            )


    if len(vectors) == 0:

        return np.zeros(
            word2vec_model.vector_size
        )


    return np.mean(
        vectors,
        axis=0
    )



def word2vec_similarity(sentences):

    vector1 = sentence_vector(
        sentences[0]
    )

    vector2 = sentence_vector(
        sentences[1]
    )


    return cosine_similarity(
        [vector1],
        [vector2]
    )[0][0]



# -----------------------------
# Transformer
# -----------------------------

transformer_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)



def transformer_similarity(sentences):

    embeddings = transformer_model.encode(
        sentences
    )


    return cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]



# -----------------------------
# Main Comparison
# -----------------------------

results = []


for name, sentences in tests.items():


    tfidf_score = tfidf_similarity(
        sentences
    )


    ngram_score = ngram_similarity(
        sentences
    )


    word2vec_score = word2vec_similarity(
        sentences
    )


    transformer_score = transformer_similarity(
        sentences
    )


    results.append(
        [
            name,
            round(tfidf_score,4),
            round(word2vec_score,4),
            round(ngram_score,4),
            round(transformer_score,4)
        ]
    )



print("\nFINAL COMPARISON TABLE")
print("-"*75)


print(
    f"{'Test':20} {'TF-IDF':12} {'Word2Vec':12} {'N-Gram':12} {'Transformer'}"
)



for row in results:

    print(
        f"{row[0]:20} {row[1]:12} {row[2]:12} {row[3]:12} {row[4]}"
    )



with open(
    "outputs/similarity_comparison.txt",
    "w",
    encoding="utf-8"
) as file:


    file.write(
        "TF-IDF vs Word2Vec vs N-Gram vs Transformer\n\n"
    )


    for row in results:

        file.write(
            str(row) + "\n"
        )



print("\nSaved:")
print("outputs/similarity_comparison.txt")