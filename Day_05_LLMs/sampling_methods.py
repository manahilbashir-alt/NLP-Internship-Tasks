import numpy as np


np.random.seed(42)


tokens = [
    "cat",
    "dog",
    "bird",
    "car",
    "tree",
    "house",
    "computer",
    "book"
]


logits = np.array([
    4.8,
    4.2,
    3.5,
    2.8,
    2.0,
    1.4,
    0.9,
    0.3
])


def softmax(values):

    values = values - np.max(values)

    exp_values = np.exp(values)

    return exp_values / np.sum(exp_values)



def temperature_sampling(logits, temperature):

    adjusted_logits = logits / temperature

    probabilities = softmax(adjusted_logits)

    chosen_index = np.random.choice(
        len(tokens),
        p=probabilities
    )

    return tokens[chosen_index], probabilities



def top_k_sampling(logits, k):

    top_indices = np.argsort(logits)[-k:]

    top_logits = logits[top_indices]

    probabilities = softmax(top_logits)

    chosen_index = np.random.choice(
        top_indices,
        p=probabilities
    )

    return tokens[chosen_index]



def top_p_sampling(logits, p):

    probabilities = softmax(logits)

    sorted_indices = np.argsort(
        probabilities
    )[::-1]


    sorted_probabilities = probabilities[
        sorted_indices
    ]


    cumulative_probability = np.cumsum(
        sorted_probabilities
    )


    selected_indices = []

    for index, probability in zip(
        sorted_indices,
        cumulative_probability
    ):

        selected_indices.append(index)

        if probability >= p:
            break


    selected_logits = logits[selected_indices]

    selected_probabilities = softmax(
        selected_logits
    )


    chosen_index = np.random.choice(
        selected_indices,
        p=selected_probabilities
    )


    return tokens[chosen_index]



def main():

    print("=" * 60)
    print("VOCABULARY WITH LOGITS")
    print("=" * 60)


    for word, score in zip(tokens, logits):
        print(
            f"{word:12} {score}"
        )


    print("\nTemperature Sampling")

    for temperature in [0.5, 1.0, 2.0]:

        word, probabilities = temperature_sampling(
            logits,
            temperature
        )

        print(
            f"\nTemperature {temperature}"
        )

        print(
            "Selected:",
            word
        )


    print("\nTop-k Sampling")


    for k in [2,3,5]:

        print(
            f"Top-{k}:",
            top_k_sampling(logits,k)
        )


    print("\nTop-p Sampling")


    for p in [0.70,0.85,0.95]:

        print(
            f"Top-p {p}:",
            top_p_sampling(logits,p)
        )



if __name__ == "__main__":
    main()