import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import os


os.makedirs(
    "outputs",
    exist_ok=True
)


sequence_length = 60
embedding_size = 10


x = torch.randn(
    sequence_length,
    1,
    embedding_size,
    requires_grad=True
)


print("Input Shape:")
print(x.shape)



class SimpleLSTM(nn.Module):

    def __init__(self):

        super().__init__()

        self.lstm = nn.LSTM(
            input_size=embedding_size,
            hidden_size=20,
            num_layers=1
        )

        self.fc = nn.Linear(
            20,
            1
        )


    def forward(self, x):

        output, (hidden, cell) = self.lstm(x)

        prediction = self.fc(
            output[-1]
        )

        return prediction, output



model = SimpleLSTM()


print("\nModel:")
print(model)



prediction, hidden_states = model(x)


print("\nPrediction:")
print(prediction)


print("\nHidden State Shape:")
print(hidden_states.shape)



target = torch.tensor(
    [[1.0]]
)


loss_function = nn.MSELoss()


loss = loss_function(
    prediction,
    target
)


print("\nLoss:")
print(loss.item())


loss.backward()


print("\nBackward propagation completed")



gradient_values = []


for timestep in range(sequence_length):

    gradient = x.grad[timestep].abs().mean()

    gradient_values.append(
        gradient.item()
    )



print("\nGradient Values:")

for i, value in enumerate(gradient_values):

    print(
        f"Token {i+1}: {value}"
    )



plt.figure(
    figsize=(10,5)
)


plt.plot(
    range(1, sequence_length+1),
    gradient_values,
    marker="o"
)


plt.xlabel(
    "Token Position"
)

plt.ylabel(
    "Gradient Magnitude"
)

plt.title(
    "Gradient Flow Across LSTM Timesteps"
)


plt.grid()



plt.savefig(
    "outputs/lstm_gradient.png",
    dpi=300,
    bbox_inches="tight"
)


plt.close()



with open(
    "outputs/lstm_gradient_results.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "LSTM Gradient Flow Experiment\n\n"
    )

    file.write(
        f"Sequence Length: {sequence_length}\n"
    )

    file.write(
        f"Embedding Size: {embedding_size}\n"
    )

    file.write(
        f"Loss: {loss.item()}\n\n"
    )


    file.write(
        "Gradient Values:\n"
    )


    for i, value in enumerate(gradient_values):

        file.write(
            f"Token {i+1}: {value}\n"
        )



print("\nSaved:")
print("outputs/lstm_gradient.png")
print("outputs/lstm_gradient_results.txt")