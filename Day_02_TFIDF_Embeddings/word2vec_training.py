import re
from gensim.models import Word2Vec


def preprocess_text(text):
    text = text.lower()

    sentences = re.split(r"[.!?]", text)

    processed_sentences = []

    for sentence in sentences:
        sentence = re.sub(r"[^a-z\s]", "", sentence)

        words = sentence.split()

        if len(words) > 1:
            processed_sentences.append(words)

    return processed_sentences


def train_skipgram(sentences):

    model = Word2Vec(
        sentences=sentences,
        vector_size=100,
        window=5,
        min_count=1,
        sg=1,
        epochs=50
    )

    return model


def main():

    print("Reading corpus...")

    with open("input_corpus.txt", "r", encoding="utf-8") as file:
        text = file.read()

    sentences = preprocess_text(text)

    print(f"Total Sentences : {len(sentences)}")

    print("Training Word2Vec model...")

    model = train_skipgram(sentences)

    model.save("word2vec.model")

    print("\nTraining completed successfully.")
    print("Model saved as word2vec.model")


if __name__ == "__main__":
    main()