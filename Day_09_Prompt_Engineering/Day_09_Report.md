# Day 09 – Prompt Engineering

## Objective

The objective of this task was to understand Prompt Engineering techniques and implement a reusable prompt library for Large Language Models (LLMs). The project demonstrates how prompts can be separated from application logic, making AI systems easier to maintain, extend, and reuse.

---

# Tasks Completed

## 1. Prompt Template Library

Created reusable prompt templates for the following NLP tasks:

- Summarization
- Entity Extraction
- Sentiment Analysis
- Code Generation
- Data Transformation
- Few-Shot Prompting
- Persona Prompting
- Temperature-Based Prompting
- Production Prompt Template

Each prompt was stored in a separate Markdown (.md) file.

---

## 2. System Prompt

Designed a reusable system prompt defining:

- AI role
- Objectives
- Instructions
- Constraints
- Response style

This system prompt is shared across all tasks.

---

## 3. Prompt Builder

Implemented a reusable PromptBuilder class.

Responsibilities:

- Load prompt templates from the prompts folder
- Replace placeholders such as:

  - {input_text}
  - {persona}
  - {creativity_level}

- Combine the system prompt and task prompt
- Return the final prompt ready for Gemini API

---

## 4. Gemini Integration

Integrated the prompt builder with the Gemini API.

Instead of hardcoding prompts inside Python code, prompts are dynamically loaded from Markdown files.

---

## 5. Supported Prompting Techniques

Implemented the following prompt engineering techniques:

- Role Prompting
- Instruction Prompting
- Constraint Prompting
- Structured Output Prompting
- Few-Shot Prompting
- Persona Prompting
- Production Prompt Design

---

# Project Structure

```

Day_09_Prompt_Engineering/

├── prompts/
│ ├── system_prompt.md
│ ├── summarization.md
│ ├── entity_extraction.md
│ ├── sentiment_analysis.md
│ ├── code_generation.md
│ ├── data_transformation.md
│ ├── few_shot.md
│ ├── persona.md
│ ├── temperature.md
│ └── production_prompt.md
│
├── prompt_builder.py
├── chat_completion.py
├── .env
├── README.md

```

---

# Workflow

User Input

↓

Prompt Builder

↓

System Prompt + Task Prompt

↓

Final Prompt

↓

Gemini API

↓

AI Response

---

# Learning Outcomes

Through this implementation I learned:

- Difference between system prompts and user prompts.
- How reusable prompt templates improve maintainability.
- Importance of separating prompt design from application logic.
- How PromptBuilder dynamically constructs prompts.
- How Gemini API processes structured prompts.
- Practical Prompt Engineering techniques used in production AI applications.

---

# Conclusion

This project demonstrates a modular Prompt Engineering workflow where prompt templates are maintained separately from the application code. The implementation improves reusability, scalability, and maintainability while following software engineering best practices for AI-powered applications.