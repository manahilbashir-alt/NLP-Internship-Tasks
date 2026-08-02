basic_prompt = """
Explain TF-IDF.
"""
role_prompt = """
You are an experienced NLP professor.

Explain TF-IDF.
"""
role_context_prompt = """
You are an experienced NLP professor.

The audience consists of first-year Computer Science students
who have basic Python knowledge but are new to Natural Language Processing.

Explain TF-IDF.
"""
complete_prompt = """
Role:
You are an experienced NLP professor.

Context:
The audience consists of first-year Computer Science students
who have basic Python knowledge but are new to Natural Language Processing.

Task:
Explain TF-IDF, why it is important, and where it is commonly used.

Example:
Explain Bag of Words using a library analogy before introducing TF-IDF.

Output Format:
- Use Markdown headings
- Use bullet points
- Include one real-world example
- Limit the response to 250 words
"""
prompts = {
    "Prompt 1: Basic Prompt": basic_prompt,
    "Prompt 2: Role Added": role_prompt,
    "Prompt 3: Role + Context": role_context_prompt,
    "Prompt 4: Complete Prompt Anatomy": complete_prompt
}
print("=" * 80)
print("CORE PROMPT ANATOMY IMPLEMENTATION")
print("=" * 80)

for title, prompt in prompts.items():
    print(f"\n{title}")
    print("-" * 80)
    print(prompt)

print("Implementation Complete")