"""
Day 2 Task 2

TF-IDF Retrieval System
(Using own TF-IDF implementation)
"""

from tfidf_from_scratch import (
    build_bow_matrix,
    compute_tf,
    compute_idf,
    compute_tfidf,
    simple_word_tokenize
)
import math
def build_query_vector(query, vocab, idf):

    tokens = simple_word_tokenize(query)

    total_words = len(tokens)

    tf = {}

    for word in tokens:

        if word not in tf:
            tf[word] = 0

        tf[word] += 1

    # TF
    for word in tf:

        tf[word] = tf[word] / total_words

    # TF-IDF
    vector = []

    for word in vocab:

        if word in tf:

            vector.append(tf[word] * idf.get(word, 0))

        else:

            vector.append(0)

    return vector
def build_document_vectors(vocab, tfidf_list):

    vectors = []

    for tfidf in tfidf_list:

        vector = []

        for word in vocab:

            vector.append(tfidf.get(word, 0))

        vectors.append(vector)

    return vectors
def cosine_similarity(vector1, vector2):

    dot_product = 0

    for i in range(len(vector1)):

        dot_product += vector1[i] * vector2[i]

    magnitude1 = 0

    for value in vector1:

        magnitude1 += value ** 2

    magnitude1 = math.sqrt(magnitude1)

    magnitude2 = 0

    for value in vector2:

        magnitude2 += value ** 2

    magnitude2 = math.sqrt(magnitude2)

    if magnitude1 == 0 or magnitude2 == 0:

        return 0

    return dot_product / (magnitude1 * magnitude2)
def retrieve_documents(query, sentences, vocab, tfidf_list, idf):

    query_vector = build_query_vector(query, vocab, idf)

    document_vectors = build_document_vectors(vocab, tfidf_list)

    scores = []

    for i in range(len(document_vectors)):

        score = cosine_similarity(
            query_vector,
            document_vectors[i]
        )

        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    return scores
if __name__ == "__main__":

    with open("outputs/cleaned_corpus.txt", "r", encoding="utf-8") as f:

        text = f.read()

    (
        sentences,
        sentences_tokens,
        vocab,
        bow_dicts,
        matrix
    ) = build_bow_matrix(text)

    tf = compute_tf(sentences_tokens)

    idf = compute_idf(sentences_tokens)

    tfidf = compute_tfidf(tf, idf)

    query = input("Enter your search query: ")

    results = retrieve_documents(
        query,
        sentences,
        vocab,
        tfidf,
        idf
    )

    print("\nTop Matching Documents\n")

    for index, score in results[:5]:

        print("-" * 70)
        print("Similarity :", round(score, 4))
        print("Document :", sentences[index])                