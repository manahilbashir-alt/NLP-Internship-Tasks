from collections import defaultdict
import random
import re

with open("../data/input_corpus.txt", "r", encoding="utf-8") as file:
    corpus = file.read().lower()

corpus = re.sub(r"#+", " ", corpus)
corpus = re.sub(r"domain:", " ", corpus)
corpus = re.sub(r"[^a-z\s]", " ", corpus)
corpus = re.sub(r"\s+", " ", corpus).strip()

tokens = corpus.split()

print("=" * 60)
print("CORPUS INFORMATION")
print("=" * 60)
print("Total Tokens      :", len(tokens))

vocabulary = sorted(set(tokens))
V = len(vocabulary)

print("Vocabulary Size   :", V)

print("\nFirst 20 Tokens")
print(tokens[:20])

bigram_counts = defaultdict(int)
unigram_counts = defaultdict(int)

for i in range(len(tokens) - 1):
    w1 = tokens[i]
    w2 = tokens[i + 1]
    bigram_counts[(w1, w2)] += 1
    unigram_counts[w1] += 1

print("\nUnique Bigrams:", len(bigram_counts))

def bigram_probability(word1, word2):
    return (bigram_counts[(word1, word2)] + 1) / (unigram_counts[word1] + V)

def next_word_distribution(word):
    distribution = {}

    for next_word in vocabulary:
        distribution[next_word] = bigram_probability(word, next_word)

    return sorted(distribution.items(), key=lambda x: x[1], reverse=True)

print("\n" + "=" * 60)
print("NEXT WORD PROBABILITIES")
print("=" * 60)

test_word = input("\nEnter a word: ").lower()

if test_word in vocabulary:

    predictions = next_word_distribution(test_word)

    print("\nTop 10 Predictions\n")

    for word, prob in predictions[:10]:
        print(f"{word:<20} {prob:.6f}")

else:
    print("Word not found.")

def generate_text(start_word, length=20):

    if start_word not in vocabulary:
        return "Starting word not found."

    sentence = [start_word]
    current = start_word

    for _ in range(length):

        predictions = next_word_distribution(current)

        next_word = predictions[0][0]

        sentence.append(next_word)

        current = next_word

    return " ".join(sentence)

print("\n" + "=" * 60)
print("GENERATED TEXT")
print("=" * 60)

start = input("\nEnter starting word: ").lower()

print("\nGenerated Text\n")
print(generate_text(start))

trigram_counts = defaultdict(int)
bigram_prefix_counts = defaultdict(int)

for i in range(len(tokens) - 2):

    w1 = tokens[i]
    w2 = tokens[i + 1]
    w3 = tokens[i + 2]

    trigram_counts[(w1, w2, w3)] += 1
    bigram_prefix_counts[(w1, w2)] += 1

print("\n" + "=" * 60)
print("TRIGRAM MODEL")
print("=" * 60)

print("Unique Trigrams:", len(trigram_counts))

def trigram_probability(w1, w2, w3):
    return (trigram_counts[(w1, w2, w3)] + 1) / (bigram_prefix_counts[(w1, w2)] + V)

print("\nExample Trigram Probabilities\n")

count = 0

for trigram in trigram_counts:

    print(f"{trigram} --> {trigram_probability(trigram[0], trigram[1], trigram[2]):.6f}")

    count += 1

    if count == 10:
        break

print("\n" + "=" * 60)
print("OBSERVATIONS")
print("=" * 60)

print("""
1. Bigram predicts the next word using one previous word.

2. Trigram predicts the next word using the previous two words.

3. Laplace smoothing prevents zero probabilities for unseen word pairs.

4. The generated text follows the learned statistical patterns of the corpus.

5. N-gram models rely on a fixed context window.
   Bigram remembers only one previous word.
   Trigram remembers only two previous words.
   They cannot capture long-range dependencies in long sentences.
""")