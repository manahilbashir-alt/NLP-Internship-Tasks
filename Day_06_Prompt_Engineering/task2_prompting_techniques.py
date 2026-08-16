"""
===============================================================================
Task 2: Comparison of Zero-Shot, One-Shot, and Few-Shot Prompting
Internship: NLP / LLM Engineering
===============================================================================

Objective:
To implement and compare Zero-Shot, One-Shot, and Few-Shot prompting
techniques on three NLP tasks:
    1. Sentiment Classification
    2. Named Entity Extraction
    3. Text Generation

===============================================================================
"""


def print_separator():
    print("=" * 90)


def display_experiment(title, input_text, prompts):
    """
    Display an experiment with different prompting techniques.
    """
    print_separator()
    print(title)
    print_separator()

    print("\nInput:")
    print("-" * 90)
    print(input_text)

    for technique, details in prompts.items():
        print("\n" + "-" * 90)
        print(f"{technique}")
        print("-" * 90)

        print("\nPrompt:")
        print(details["prompt"])

        print("\nExpected Output:")
        print(details["output"])


# =============================================================================
# Experiment 1 : Sentiment Classification
# =============================================================================

classification_input = """
Sentence:
"I absolutely loved this movie. The acting was fantastic."
"""

classification_prompts = {

    "Zero-Shot Prompting": {

        "prompt": """
Classify the sentiment of the following sentence.

Return only:
Positive, Negative, or Neutral.
""",

        "output": """
Positive
"""
    },

    "One-Shot Prompting": {

        "prompt": """
Example

Sentence:
"The food was terrible."

Sentiment:
Negative

Now classify:

"I absolutely loved this movie. The acting was fantastic."

Return only:
Positive, Negative, or Neutral.
""",

        "output": """
Positive
"""
    },

    "Few-Shot Prompting": {

        "prompt": """
Sentence:
"The weather is amazing."

Sentiment:
Positive

Sentence:
"The service was horrible."

Sentiment:
Negative

Sentence:
"The lecture was okay."

Sentiment:
Neutral

Now classify:

"I absolutely loved this movie. The acting was fantastic."

Return only:
Positive, Negative, or Neutral.
""",

        "output": """
Positive
"""
    }

}


# =============================================================================
# Experiment 2 : Named Entity Extraction
# =============================================================================

entity_input = """
Sentence:
Sundar Pichai is the CEO of Google and lives in California.
"""

entity_prompts = {

    "Zero-Shot Prompting": {

        "prompt": """
Extract all named entities.

Return them under:

Person
Organization
Location
""",

        "output": """
Person:
Sundar Pichai

Organization:
Google

Location:
California
"""
    },

    "One-Shot Prompting": {

        "prompt": """
Example

Sentence:
Ali studies at FAST University in Lahore.

Output

Person:
Ali

Organization:
FAST University

Location:
Lahore

Now extract entities from:

Sundar Pichai is the CEO of Google and lives in California.
""",

        "output": """
Person:
Sundar Pichai

Organization:
Google

Location:
California
"""
    },

    "Few-Shot Prompting": {

        "prompt": """
Sentence:
Sara works at Microsoft in Seattle.

Person:
Sara

Organization:
Microsoft

Location:
Seattle

Sentence:
Ahmed studies at FAST University in Islamabad.

Person:
Ahmed

Organization:
FAST University

Location:
Islamabad

Now extract entities from:

Sundar Pichai is the CEO of Google and lives in California.
""",

        "output": """
Person:
Sundar Pichai

Organization:
Google

Location:
California
"""
    }

}


# =============================================================================
# Experiment 3 : Text Generation
# =============================================================================

generation_input = """
Task:
Write a professional email requesting a project deadline extension.
"""

generation_prompts = {

    "Zero-Shot Prompting": {

        "prompt": """
Write a professional email requesting a project deadline extension.
""",

        "output": """
A formal email requesting additional time to complete the project.
"""
    },

    "One-Shot Prompting": {

        "prompt": """
Example

Write a professional leave request email.

Now write a professional email requesting a project deadline extension.
""",

        "output": """
A well-structured professional email with an appropriate subject,
greeting, reason for extension, and closing.
"""
    },

    "Few-Shot Prompting": {

        "prompt": """
Example 1
Write a professional internship acceptance email.

Example 2
Write a professional meeting request email.

Example 3
Write a formal leave application.

Now write a professional email requesting a project deadline extension.
""",

        "output": """
A highly professional email following a consistent formal style.
"""
    }

}


# =============================================================================
# Main Program
# =============================================================================

print_separator()
print("TASK 2 : COMPARISON OF PROMPTING TECHNIQUES")
print_separator()

display_experiment(
    "Experiment 1 : Sentiment Classification",
    classification_input,
    classification_prompts
)

display_experiment(
    "Experiment 2 : Named Entity Extraction",
    entity_input,
    entity_prompts
)

display_experiment(
    "Experiment 3 : Text Generation",
    generation_input,
    generation_prompts
)

print_separator()
print("Summary")
print_separator()

print("""
Observations

• Zero-Shot Prompting works well for straightforward tasks but may produce
  inconsistent formatting.

• One-Shot Prompting improves response consistency by providing a single
  demonstration.

• Few-Shot Prompting achieves the highest accuracy and consistency by
  allowing the model to infer the expected response pattern from multiple
  examples.

Conclusion

Prompt engineering significantly influences the quality of outputs generated
by Large Language Models. As the number of examples increases, the model
better understands the desired structure and style of the response.
""")