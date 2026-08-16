# Task 6: Prompting Best Practices

## Introduction

Prompt engineering is the process of designing instructions that help a Large Language Model (LLM) generate accurate, relevant, and well-structured responses. Small changes in the wording or structure of a prompt can significantly affect the quality of the output.

In this task, I explored ten practical prompting techniques and compared a simple prompt with an improved version to understand how prompt design influences the final response.

---

# 1. Be Clear and Specific

A vague prompt often leads to vague answers. Clearly describing the task helps the model understand exactly what is expected.

### Before

```text
Tell me about Python.
```

### After

```text
Explain Python programming for a beginner in less than 200 words. Include its main features and two real-world applications.
```

### Why it is better

The improved prompt defines the audience, length, and topics to include, resulting in a more focused response.

---

# 2. Assign a Role

Giving the model a role helps it respond from a particular perspective.

### Before

```text
Explain machine learning.
```

### After

```text
You are a university professor. Explain machine learning to first-year computer science students using simple language and examples.
```

### Why it is better

The explanation becomes more educational, structured, and easier to understand.

---

# 3. Provide Context

Adding context reduces ambiguity and improves relevance.

### Before

```text
Write an email.
```

### After

```text
Write a professional email to my project supervisor requesting a two-day extension because I was ill.
```

### Why it is better

The model understands the situation and produces a response that matches the intended purpose.

---

# 4. Clearly Define the Task

Instead of asking for something broad, describe the exact action you want.

### Before

```text
Analyze this article.
```

### After

```text
Read the article and identify its main argument, supporting evidence, and final conclusion.
```

### Why it is better

Breaking the task into smaller objectives produces a more organized response.

---

# 5. Specify the Output Format

Defining the expected format makes responses easier to read and process.

### Before

```text
List the advantages of AI.
```

### After

```text
List five advantages of Artificial Intelligence in a table with two columns: Advantage and Explanation.
```

### Why it is better

The response becomes consistent and well organized.

---

# 6. Add Constraints

Constraints help control the length, style, and detail of the response.

### Before

```text
Write about climate change.
```

### After

```text
Write a 150-word summary of climate change using simple English suitable for high school students.
```

### Why it is better

The response matches the required audience and length.

---

# 7. Include Examples

Examples help the model understand the desired style or pattern.

### Before

```text
Classify the sentiment.
```

### After

```text
Example:

Sentence: "The food was amazing."

Sentiment: Positive

Now classify:

Sentence: "The service was disappointing."
```

### Why it is better

The example guides the model toward the expected output format.

---

# 8. Break Complex Tasks into Steps

Complex problems are easier to solve when divided into smaller parts.

### Before

```text
Solve this math problem.
```

### After

```text
Solve the following problem step by step. Show each calculation before giving the final answer.
```

### Why it is better

The reasoning process becomes transparent and easier to verify.

---

# 9. Request Structured Reasoning

Encouraging the model to explain its reasoning often improves response quality.

### Before

```text
Who is older?

Ali is older than Ahmed.
Ahmed is older than Bilal.
```

### After

```text
Let's think step by step.

Ali is older than Ahmed.
Ahmed is older than Bilal.

Who is the oldest?
```

### Why it is better

The model explains the logical relationships before reaching the conclusion.

---

# 10. Review and Refine the Prompt

Prompt engineering is an iterative process. Small improvements often produce noticeably better results.

### Before

```text
Explain neural networks.
```

### After

```text
Explain neural networks for a beginner. Use simple language, include one real-life analogy, and keep the explanation under 250 words.
```

### Why it is better

The refined prompt produces a response that is clearer, more engaging, and appropriate for the intended audience.

---

# Summary

| Best Practice | Benefit |
|--------------|---------|
| Be specific | Produces focused responses |
| Assign a role | Matches the desired perspective |
| Provide context | Improves relevance |
| Define the task | Reduces ambiguity |
| Specify output format | Produces organized responses |
| Add constraints | Controls style and length |
| Include examples | Improves consistency |
| Break tasks into steps | Helps solve complex problems |
| Encourage reasoning | Makes answers more transparent |
| Refine prompts | Improves overall quality |

---

# Conclusion

This task demonstrates that effective prompt engineering is not only about asking a question but also about providing clear instructions, sufficient context, and a well-defined structure. Throughout these examples, the improved prompts consistently produced responses that were more accurate, organized, and easier to understand than the original versions.

These best practices can be applied across a wide range of NLP tasks, including summarization, text generation, sentiment analysis, information extraction, and code generation. As Large Language Models continue to evolve, carefully designed prompts remain one of the most effective ways to improve the quality and reliability of AI-generated responses.