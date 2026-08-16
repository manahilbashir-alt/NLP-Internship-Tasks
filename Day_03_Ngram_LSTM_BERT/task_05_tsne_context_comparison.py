import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sentence_transformers import SentenceTransformer
from gensim.models import Word2Vec
import numpy as np
import os


os.makedirs(
    "outputs",
    exist_ok=True
)


sentences = [

    "I deposited money in the bank.",
    "The bank approved my loan.",
    "She works at a bank.",

    "I sat near the bank of the river.",
    "The boat reached the river bank.",
    "We walked along the bank of the stream."

]


labels = [

    "Finance",
    "Finance",
    "Finance",

    "River",
    "River",
    "River"

]



# ---------------------------------
# Word2Vec Static Embeddings
# ---------------------------------

word2vec_model = Word2Vec.load(
    "word2vec.model"
)



def get_word2vec_sentence_vector(sentence):

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



static_vectors = []


for sentence in sentences:

    static_vectors.append(
        get_word2vec_sentence_vector(sentence)
    )


static_vectors = np.array(
    static_vectors
)



# ---------------------------------
# Transformer Embeddings
# ---------------------------------

transformer_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


transformer_vectors = transformer_model.encode(
    sentences
)



# ---------------------------------
# t-SNE
# ---------------------------------

def reduce_dimension(vectors):

    tsne = TSNE(
        n_components=2,
        random_state=42,
        perplexity=2
    )


    return tsne.fit_transform(
        vectors
    )



static_2d = reduce_dimension(
    static_vectors
)


transformer_2d = reduce_dimension(
    transformer_vectors
)



# ---------------------------------
# Plot Function
# ---------------------------------

def plot_embeddings(
        points,
        title,
        filename):


    plt.figure(
        figsize=(8,6)
    )


    for i in range(len(points)):

        plt.scatter(
            points[i][0],
            points[i][1]
        )


        plt.text(
            points[i][0],
            points[i][1],
            labels[i]
        )


    plt.title(title)

    plt.xlabel(
        "Dimension 1"
    )

    plt.ylabel(
        "Dimension 2"
    )


    plt.grid()


    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )


    plt.close()



plot_embeddings(
    static_2d,
    "t-SNE: Word2Vec Static Embeddings",
    "outputs/tsne_word2vec.png"
)



plot_embeddings(
    transformer_2d,
    "t-SNE: Transformer Contextual Embeddings",
    "outputs/tsne_transformer.png"
)



with open(
    "outputs/tsne_results.txt",
    "w",
    encoding="utf-8"
) as file:


    file.write(
        "t-SNE Embedding Comparison\n\n"
    )


    file.write(
        "Word2Vec = Static Embedding\n"
    )

    file.write(
        "Transformer = Contextual Embedding\n"
    )


print("Completed Successfully!")

print(
    "Saved:"
)

print(
    "outputs/tsne_word2vec.png"
)

print(
    "outputs/tsne_transformer.png"
)

print(
    "outputs/tsne_results.txt"
)