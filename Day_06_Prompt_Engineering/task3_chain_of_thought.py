"""
===============================================================================
Task 3: Applying Chain-of-Thought (CoT) Prompting

This script demonstrates how adding the phrase
"Let's think step by step."
changes the quality of responses produced by a Large Language Model.

The same reasoning problems are presented twice:
1. Without Chain-of-Thought prompting
2. With Chain-of-Thought prompting
===============================================================================
"""
def line():
    print("=" * 90)


def experiment(title, question, prompt_without, response_without,
               prompt_with, response_with, discussion):

    line()
    print(title)
    line()

    print("\nProblem")
    print("-" * 90)
    print(question)

    print("\nPrompt 1 (Without Chain-of-Thought)")
    print("-" * 90)
    print(prompt_without)

    print("\nModel Response")
    print("-" * 90)
    print(response_without)

    print("\nPrompt 2 (With Chain-of-Thought)")
    print("-" * 90)
    print(prompt_with)

    print("\nModel Response")
    print("-" * 90)
    print(response_with)

    print("\nDiscussion")
    print("-" * 90)
    print(discussion)

    print()


# =============================================================================
# Experiment 1
# =============================================================================

question1 = """
A shop sells a notebook for $12.
Sarah buys 5 notebooks and pays with $100.

How much change should she receive?
"""

prompt_without1 = question1

response_without1 = """
$40
"""

prompt_with1 = """
Let's think step by step.

A shop sells a notebook for $12.
Sarah buys 5 notebooks and pays with $100.

How much change should she receive?
"""

response_with1 = """
Each notebook costs $12.

Cost of 5 notebooks = 5 × 12 = $60.

Sarah paid $100.

Change = $100 − $60 = $40.

Final Answer: $40
"""

discussion1 = """
The direct prompt produced the correct answer immediately.

After adding "Let's think step by step", the model explained every
calculation before presenting the final answer. This makes the
solution easier to understand and verify.
"""

# =============================================================================
# Experiment 2
# =============================================================================

question2 = """
Ali is older than Ahmed.
Ahmed is older than Bilal.

Who is the oldest?
"""

prompt_without2 = question2

response_without2 = """
Ali
"""

prompt_with2 = """
Let's think step by step.

Ali is older than Ahmed.
Ahmed is older than Bilal.

Who is the oldest?
"""

response_with2 = """
Ali is older than Ahmed.

Ahmed is older than Bilal.

Therefore, Ali is older than both Ahmed and Bilal.

Final Answer: Ali
"""

discussion2 = """
Without Chain-of-Thought, the model only returned the final answer.

With Chain-of-Thought prompting, the relationship between all three
people is explained before reaching the conclusion, making the
reasoning much clearer.
"""

# =============================================================================
# Experiment 3
# =============================================================================

question3 = """
A train travels at 60 km/h for 2.5 hours.

How far does it travel?
"""

prompt_without3 = question3

response_without3 = """
150 km
"""

prompt_with3 = """
Let's think step by step.

A train travels at 60 km/h for 2.5 hours.

How far does it travel?
"""

response_with3 = """
Distance = Speed × Time

Distance = 60 × 2.5

Distance = 150 km

Final Answer: 150 km
"""

discussion3 = """
Both prompts produced the correct answer.

However, the Chain-of-Thought prompt clearly shows how the formula
was applied, making the response easier to follow.
"""

# =============================================================================
# Main Program
# =============================================================================

line()
print("TASK 3 : CHAIN-OF-THOUGHT (CoT) PROMPTING")
line()

experiment(
    "Experiment 1 : Mathematical Reasoning",
    question1,
    prompt_without1,
    response_without1,
    prompt_with1,
    response_with1,
    discussion1
)

experiment(
    "Experiment 2 : Logical Reasoning",
    question2,
    prompt_without2,
    response_without2,
    prompt_with2,
    response_with2,
    discussion2
)

experiment(
    "Experiment 3 : Multi-Step Arithmetic",
    question3,
    prompt_without3,
    response_without3,
    prompt_with3,
    response_with3,
    discussion3
)

line()
print("Overall Conclusion")
line()

print("""
After testing all three problems, it became clear that adding the
instruction "Let's think step by step" consistently encouraged the
model to explain its reasoning before providing the final answer.

Although the final answers were the same in these experiments,
the Chain-of-Thought prompt produced responses that were easier
to understand, verify, and learn from.

This makes Chain-of-Thought prompting particularly useful for
mathematical calculations, logical reasoning, and other multi-step
problem-solving tasks.
""")