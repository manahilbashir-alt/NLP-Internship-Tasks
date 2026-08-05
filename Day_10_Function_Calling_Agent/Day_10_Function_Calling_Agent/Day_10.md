# Day 10 - Function Calling Agent

## Overview

In Day 10, I studied and implemented Function Calling with Large Language Models (LLMs).

Function calling allows an LLM to interact with external tools and functions by selecting appropriate functions, generating arguments, and using the returned results to produce final responses.

---

# Tasks Completed

## 1. Function Calling Specification Study

Studied:

- Function calling concept
- Tools array structure
- Function definitions
- JSON schema for function parameters
- Tool selection process
- Function execution workflow

The complete explanation is available in:


function_calling_basics.md


---

# 2. Custom Tool Definitions

Implemented four custom tools with proper JSON schemas:

## get_current_time

Purpose:

- Returns current time information for a location.

Parameters:

```json
{
  "location": "string"
}
calculate

Purpose:

Performs mathematical calculations.

Supported operations:

Addition
Subtraction
Multiplication
Division

Parameters:

{
  "operation": "string",
  "number1": "number",
  "number2": "number"
}
search_database

Purpose:

Searches a mock database.

Supported categories:

Users
Products
Orders

Parameters:

{
  "query": "string",
  "category": "string"
}
format_currency

Purpose:

Converts numbers into formatted currency values.

Supported currencies:

USD
EUR
PKR

Parameters:

{
  "amount": "number",
  "currency": "string"
}

Implementation:

tools_definition.py
3. Complete Function Calling Loop

Implemented the complete function calling workflow:

User Request
      |
      v
LLM analyzes request
      |
      v
Model selects tool
      |
      v
Function call with arguments
      |
      v
Local function execution
      |
      v
Function result returned
      |
      v
LLM generates final response

Implementation:

function_calling_loop.py
4. Multi-Tool Agent

Implemented an agent capable of using multiple tools together.

Example workflow:

User request:

Find product price and calculate discount

Agent can:

Search database
Perform calculation
Format final result

Tools can be chained together to solve complex tasks.

5. Error Handling

Implemented robust error handling for:

Invalid arguments
Incorrect data types
Division by zero
Unknown functions
Function execution failures
Model responses without function calls

Implementation:

error_handling.py
6. Function Calling vs Structured Output vs JSON Mode

Documented the differences between:

Function Calling

Used when an LLM needs to perform actions using external tools.

Examples:

Calling APIs
Database search
Calculations
Structured Output

Used when the model must return information in a fixed schema.

Examples:

Resume extraction
Document parsing
Data extraction
JSON Mode

Used when only valid JSON output is required without strict schema enforcement.

Examples:

Simple data exchange
Flexible JSON responses

Documentation:

function_calling_vs_json.md
Project Structure
Day_10_Function_Calling_Agent

│
├── Day_10.md
├── function_calling_basics.md
├── function_calling_vs_json.md
├── tools_definition.py
├── function_calling_loop.py
└── error_handling.py
Key Learnings
How LLMs interact with external tools
How to define functions using JSON schemas
How to execute model-selected functions locally
How to build tool-using AI agents
How to handle function calling failures
Difference between function calling, structured output, and JSON mode
Conclusion

Day 10 focused on building a Function Calling Agent that connects an LLM with external tools.