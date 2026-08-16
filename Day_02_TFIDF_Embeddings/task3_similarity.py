from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(text1, text2):

    documents = [text1, text2]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0],
        tfidf_matrix[1]
    )

    return similarity[0][0]


def evaluate_pairs(pairs):

    print("=" * 60)
    print("TF-IDF SIMILARITY")
    print("=" * 60)

    for first, second in pairs:

        score = calculate_similarity(first, second)

        print(f"\nText 1 : {first}")
        print(f"Text 2 : {second}")
        print(f"Similarity Score : {score:.4f}")


def main():

    sentence_pairs = [
        ("rocky planet", "terrestrial planet"),
        ("space research", "astronomy study"),
        ("hot lava", "magma surface"),
        ("water ice", "frozen water"),
        ("gas planet", "gaseous planet")
    ]

    evaluate_pairs(sentence_pairs)


if __name__ == "__main__":
    main()