from gensim.models import Word2Vec


def load_model():
    return Word2Vec.load("word2vec.model")


def polysemy_test(model, word):

    print("=" * 60)
    print("POLYSEMY TEST")
    print("=" * 60)

    if word not in model.wv:
        print(f"'{word}' not found in the vocabulary.")
        return

    print(f"\nWord: {word}")

    print("\nFirst 10 values of its embedding:\n")
    print(model.wv[word][:10])

    print("\nObservation:")
    print("Word2Vec stores only one vector for each word.")
    print("If a word has multiple meanings,")
    print("the same embedding is used for every meaning.")
    print("This is one limitation of traditional Word2Vec models.")


def main():

    print("Loading Word2Vec model...\n")

    model = load_model()

    polysemy_test(model, "bank")


if __name__ == "__main__":
    main()