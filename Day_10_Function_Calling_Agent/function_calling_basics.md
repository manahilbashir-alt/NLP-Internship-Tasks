# Function Calling Specification

## 1. Introduction

Function calling is a capability that allows a Large Language Model (LLM) to interact with external functions, APIs, databases, or tools.

Instead of generating only text, the model can decide when it needs an external tool, generate structured arguments, and request the application to execute that function.

The complete workflow:

```
User Request
      |
      v
LLM receives available tools
      |
      v
LLM selects required function
      |
      v
Application executes function
      |
      v
Function result sent back to LLM
      |
      v
LLM generates final response
```

---

# 2. Tools Array Structure

The `tools` parameter contains a list of functions available to the model.

Each tool has:

* type
* function definition
* function name
* description
* parameters (JSON Schema)

Example:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current time for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
]
```

---

# 3. Tool Object Fields

## type

Defines the type of tool.

Currently the main supported type is:

```
function
```

Example:

```json
{
    "type": "function"
}
```

---

## function

Contains the function metadata.

It includes:

### name

The unique function identifier.

Example:

```json
"name": "calculate"
```

The application uses this name to execute the correct function.

---

### description

Explains what the function does.

Example:

```json
"description": "Performs mathematical calculations"
```

The model uses this description to decide when the function should be called.

---

### parameters

Defines the input format using JSON Schema.

Example:

```json
"parameters": {
    "type": "object",
    "properties": {
        "number1": {
            "type": "number"
        },
        "number2": {
            "type": "number"
        }
    }
}
```

---

# 4. JSON Schema for Function Definitions

JSON Schema defines:

* data type
* available fields
* required arguments
* validation rules

Example:

```json
{
    "type": "object",
    "properties": {
        "amount": {
            "type": "number",
            "description": "Amount to convert"
        },
        "currency": {
            "type": "string",
            "description": "Target currency"
        }
    },
    "required": [
        "amount",
        "currency"
    ]
}
```

---

# 5. Common JSON Schema Types

## String

Used for text values.

Example:

```json
{
"type":"string"
}
```

---

## Number

Used for numerical values.

Example:

```json
{
"type":"number"
}
```

---

## Integer

Used for whole numbers.

Example:

```json
{
"type":"integer"
}
```

---

## Boolean

Used for true/false values.

Example:

```json
{
"type":"boolean"
}
```

---

## Array

Used for lists.

Example:

```json
{
"type":"array"
}
```

---

## Object

Used for structured data.

Example:

```json
{
"type":"object"
}
```

---

# 6. tool_choice Parameter

The `tool_choice` parameter controls how the model uses tools.

There are three common modes:

---

# 6.1 Auto

The model decides whether to call a function.

Example:

```python
tool_choice="auto"
```

Behavior:

* Model can call a tool
* Model can answer normally

Example:

User:

```
What is the weather today?
```

Model:

```
Calls get_weather()
```

---

# 6.2 Required

The model must call a tool.

Example:

```python
tool_choice="required"
```

Used when an external function is always needed.

Example:

```
Calculate invoice total
```

The model must use the calculator function.

---

# 6.3 Specific Function

Force a particular function.

Example:

```python
tool_choice={
    "type":"function",
    "function":{
        "name":"calculate"
    }
}
```

The model must call:

```
calculate()
```

---

# 7. Function Calling Response Structure

When the model decides to call a function, it returns:

```json
{
    "tool_calls":[
        {
            "id":"call_123",
            "type":"function",
            "function":{
                "name":"calculate",
                "arguments":"{\"a\":10,\"b\":5}"
            }
        }
    ]
}
```

The application:

1. Reads function name
2. Parses arguments
3. Executes function
4. Sends result back

---

# 8. Sending Function Results Back

After execution:

```json
{
    "role":"tool",
    "tool_call_id":"call_123",
    "content":"15"
}
```

The model then generates the final natural language response.

Example:

```
The calculation result is 15.
```

---

# 9. Function Calling vs Normal Response

Without function calling:

```
User
 |
LLM
 |
Text Response
```

The model only generates text.

---

With function calling:

```
User
 |
LLM
 |
Function Call
 |
External Tool
 |
Result
 |
LLM Final Answer
```

The model can interact with external systems.

---

# Summary

Function calling provides:

* Structured interaction with external tools
* Reliable argument generation
* JSON schema validation
* Multi-step reasoning
* API/database integration

Important components:

| Component     | Purpose                     |
| ------------- | --------------------------- |
| tools         | Defines available functions |
| function.name | Function identifier         |
| description   | Helps model select tool     |
| parameters    | JSON Schema inputs          |
| tool_choice   | Controls tool usage         |
| tool result   | Sends execution output back |

Function calling turns an LLM into a tool-using agent.
