# Function Calling vs Structured Output vs JSON Mode

## 1. Function Calling

Function calling is a capability that allows Large Language Models (LLMs) to interact with external tools and functions.

The model does not execute functions itself. Instead, it decides:

- Which function should be called
- What arguments should be provided

The application then executes the function locally or through an external service and sends the result back to the model.

---

## Function Calling Flow


User Request
|
v
LLM analyzes request
|
v
Model selects function
|
v
Function name + arguments
|
v
Application executes function
|
v
Function result returned to model
|
v
LLM generates final response


---

## Example of Function Calling

User request:


Calculate 25 multiplied by 4


The model generates a function call:

```json
{
  "name": "calculate",
  "arguments": {
    "operation": "multiply",
    "number1": 25,
    "number2": 4
  }
}

The application executes:

calculate(
    operation="multiply",
    number1=25,
    number2=4
)

Function result:

{
  "result": 100
}

The model then creates the final answer:

The result is 100.
When to Use Function Calling

Use function calling when the model needs to perform actions or access external systems.

Examples:

Calling APIs
Searching databases
Performing calculations
Getting real-time information
Sending emails
Booking services

Common applications:

Banking assistants
Shopping agents
Weather applications
Calendar assistants
Customer support agents
2. Structured Output

Structured output means forcing the model response to follow a predefined schema.

The purpose is to get reliable and predictable data from the model.

The model only generates information. It does not execute any external function.

Example of Structured Output

User:

Extract information from this resume

Expected response:

{
  "name": "Ali",
  "skills": [
    "Python",
    "NLP"
  ],
  "experience": 2
}

The output follows a fixed structure, making it easy for another program to process.

When to Use Structured Output

Use structured output when:

You need consistent responses
You are extracting information
You are creating database records
You need API-compatible responses

Examples:

Resume parsing
Invoice extraction
Document classification
Data extraction systems
3. JSON Mode

JSON mode tells the model to return a valid JSON response.

It only guarantees that the response is valid JSON.

It does not enforce a specific schema.

Example of JSON Mode

Prompt:

Return user information in JSON format

Possible response:

{
  "name": "Sara",
  "age": 20
}

Another response could be:

{
  "username": "Sara",
  "years": 20
}

Both are valid JSON, but the structure is different.

When to Use JSON Mode

Use JSON mode when:

You only need valid JSON
The structure is flexible
You are quickly building prototypes

Examples:

Simple data exchange
Basic automation scripts
Quick experiments
Function Calling vs Structured Output vs JSON Mode
Feature	Function Calling	Structured Output	JSON Mode
Main Purpose	Execute actions	Generate fixed data format	Generate JSON data
Calls external functions	Yes	No	No
Uses JSON schema	Yes	Yes	No
Schema enforcement	High	Very High	Low
Database/API access	Yes	No	No
Best for actions	Yes	No	No
Best for extraction	Sometimes	Yes	Sometimes
Choosing the Right Approach
Use Function Calling When:

The model needs to interact with external tools.

Example:

Get the current weather

The model can call:

get_weather()
Use Structured Output When:

You need information in a fixed format.

Example:

Extract name, email, and skills from this document
Use JSON Mode When:

You only need machine-readable JSON.

Example:

Return this answer as JSON
Summary

Function calling connects an LLM with external tools and allows it to perform actions.

Structured output ensures the model response follows a predefined schema.

JSON mode only ensures that the response is valid JSON without enforcing a strict structure.

Decision guide:

Need the model to perform an action → Function Calling
Need reliable structured information → Structured Output
Need simple JSON response → JSON Mode