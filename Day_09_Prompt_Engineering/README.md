# Prompt Engineering Library

## Overview

This project demonstrates a modular Prompt Engineering framework using Google's Gemini API.

Instead of hardcoding prompts inside Python files, prompt templates are stored as separate Markdown files and dynamically combined using a reusable PromptBuilder.

---

## Features

- Reusable prompt templates
- Modular Prompt Builder
- Gemini API integration
- Dynamic placeholder replacement
- Professional prompt engineering techniques
- Easy to extend with new prompt templates

---

## Project Structure

```
Day_09_Prompt_Engineering/

├── prompts/
├── prompt_builder.py
├── chat_completion.py
├── requirements.txt
├── README.md
└── .env
```

---

## Prompt Templates

The project includes prompts for:

- Summarization
- Entity Extraction
- Sentiment Analysis
- Code Generation
- Data Transformation
- Few-Shot Prompting
- Persona Prompting
- Temperature Prompting
- Production Prompt

---

## How It Works

1. User selects a task.
2. PromptBuilder loads the system prompt.
3. PromptBuilder loads the selected task prompt.
4. Placeholders are replaced with user input.
5. The final prompt is sent to Gemini.
6. Gemini generates the response.

---

## Technologies Used

- Python
- Google Gemini API
- python-dotenv
- Markdown
- Prompt Engineering
