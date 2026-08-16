import torch
from transformers import BertTokenizer, BertModel
from torch.nn.functional import cosine_similarity


tokenizer = BertTokenizer.from_pretrained(
    "bert-base-uncased"
)

model = BertModel.from_pretrained(
    "bert-base-uncased"
)

model.eval()


sentence1 = "I deposited money in the bank."

sentence2 = "I sat near the bank of the river."


def get_word_embedding(sentence, target_word):

    inputs = tokenizer(
        sentence,
        return_tensors="pt"
    )

    tokens = tokenizer.convert_ids_to_tokens(
        inputs["input_ids"][0]
    )

    with torch.no_grad():

        outputs = model(**inputs)


    hidden_states = outputs.last_hidden_state[0]


    target_tokens = tokenizer.tokenize(
        target_word
    )


    for i in range(len(tokens)):

        if tokens[i:i+len(target_tokens)] == target_tokens:

            word_vector = hidden_states[i]

            return word_vector, tokens


    return None, tokens



bank_vector_1, tokens1 = get_word_embedding(
    sentence1,
    "bank"
)


bank_vector_2, tokens2 = get_word_embedding(
    sentence2,
    "bank"
)



print("="*60)
print("BERT CONTEXTUAL EMBEDDING TEST")
print("="*60)


print("\nSentence 1:")
print(sentence1)

print("Tokens:")
print(tokens1)


print("\nSentence 2:")
print(sentence2)

print("Tokens:")
print(tokens2)



print("\nEmbedding Shape:")
print(bank_vector_1.shape)



print("\nFirst 10 values:")
print("\nFinancial Bank:")
print(bank_vector_1[:10])

print("\nRiver Bank:")
print(bank_vector_2[:10])



similarity = cosine_similarity(
    bank_vector_1.unsqueeze(0),
    bank_vector_2.unsqueeze(0)
)


difference = torch.sum(
    torch.abs(
        bank_vector_1 - bank_vector_2
    )
)


print("\n" + "="*60)

print("Cosine Similarity:")
print(similarity.item())


print("\nVector Difference:")
print(difference.item())


print("\nObservation:")

if similarity.item() < 1:

    print(
        "BERT generated different embeddings "
        "for the same word because the context is different."
    )

else:

    print(
        "Embeddings are identical."
    )


with open(
    "outputs/bert_polysemy_results.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "BERT Contextual Embedding Test\n\n"
    )

    file.write(
        f"Sentence 1: {sentence1}\n"
    )

    file.write(
        f"Sentence 2: {sentence2}\n\n"
    )

    file.write(
        f"Cosine Similarity: {similarity.item()}\n"
    )

    file.write(
        f"Vector Difference: {difference.item()}\n"
    )
