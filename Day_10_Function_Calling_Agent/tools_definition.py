"""
Day 10 - Function Calling
Task 2: Custom Tools with JSON Schemas

Defines 4 tools:
1. get_current_time
2. calculate
3. search_database
4. format_currency
"""


# Tool definitions using JSON Schema
tools = [

    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time for a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or country name to get the current time for."
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform basic mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Mathematical operation to perform.",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide"
                        ]
                    },

                    "number1": {
                        "type": "number",
                        "description": "First number."
                    },

                    "number2": {
                        "type": "number",
                        "description": "Second number."
                    }
                },

                "required": [
                    "operation",
                    "number1",
                    "number2"
                ]
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search a mock database and return matching records.",
            "parameters": {
                "type": "object",
                "properties": {

                    "query": {
                        "type": "string",
                        "description": "Search keyword."
                    },

                    "category": {
                        "type": "string",
                        "description": "Category to search in.",
                        "enum": [
                            "users",
                            "products",
                            "orders"
                        ]
                    }

                },

                "required": [
                    "query",
                    "category"
                ]
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "format_currency",
            "description": "Convert a number into formatted currency.",
            "parameters": {
                "type": "object",
                "properties": {

                    "amount": {
                        "type": "number",
                        "description": "Amount to format."
                    },

                    "currency": {
                        "type": "string",
                        "description": "Currency code like USD, EUR, PKR.",
                        "enum": [
                            "USD",
                            "EUR",
                            "PKR"
                        ]
                    }

                },

                "required": [
                    "amount",
                    "currency"
                ]
            }
        }
    }

]


# Display tool schemas
if __name__ == "__main__":

    import json

    print(
        json.dumps(
            tools,
            indent=4
        )
    )