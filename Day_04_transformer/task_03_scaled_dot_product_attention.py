import numpy as np


def softmax(x):
    """Compute row-wise softmax."""
    x = x - np.max(x, axis=-1, keepdims=True)
    exp_values = np.exp(x)
    return exp_values / np.sum(exp_values, axis=-1, keepdims=True)


def scaled_dot_product_attention(Q, K, V):
    """Compute Scaled Dot-Product Attention."""

    # Input validation
    if Q.shape[1] != K.shape[1]:
        raise ValueError("Q and K must have the same feature dimension.")

    if K.shape[0] != V.shape[0]:
        raise ValueError("K and V must have the same number of rows.")

    print("=" * 65)
    print("INPUT MATRICES")
    print("=" * 65)

    print("\nQuery Matrix (Q)")
    print(Q)

    print("\nKey Matrix (K)")
    print(K)

    print("\nValue Matrix (V)")
    print(V)

    # Step 1
    scores = np.matmul(Q, K.T)

    print("\n" + "=" * 65)
    print("STEP 1: Q × Kᵀ")
    print(scores)

    # Step 2
    dk = K.shape[1]
    scaled_scores = scores / np.sqrt(dk)

    print("\n" + "=" * 65)
    print("STEP 2: Scaled Scores")
    print(scaled_scores)

    # Step 3
    attention_weights = softmax(scaled_scores)

    print("\n" + "=" * 65)
    print("STEP 3: Attention Weights")
    print(attention_weights)

    print("\nRow Sum Check (Should Equal 1)")
    print(np.sum(attention_weights, axis=1))

    # Step 4
    output = np.matmul(attention_weights, V)

    print("\n" + "=" * 65)
    print("STEP 4: Final Attention Output")
    print(output)

    print("=" * 65)

    return output, attention_weights


def main():

    Q = np.array([
        [1, 0],
        [0, 1]
    ], dtype=float)

    K = np.array([
        [1, 0],
        [0, 1]
    ], dtype=float)

    V = np.array([
        [10, 20],
        [30, 40]
    ], dtype=float)

    output, weights = scaled_dot_product_attention(Q, K, V)

    print("\nReturned Attention Output")
    print(output)

    print("\nReturned Attention Weights")
    print(weights)


if __name__ == "__main__":
    main()