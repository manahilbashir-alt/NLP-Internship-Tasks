"""
Day 10 - Function Calling
Task 3: Complete Function Calling Loop

Flow:
User -> Model -> Function Call -> Local Execution -> Function Result -> Final Answer
"""


import os
from datetime import datetime

from dotenv import load_dotenv
from google import genai

from tools_definition import tools


# Load API key
load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------
# Custom Functions
# -----------------------------


def get_current_time(location):

    try:
        current_time = datetime.now().strftime("%H:%M:%S")

        return {
            "location": location,
            "time": current_time
        }

    except Exception as e:

        return {
            "error": str(e)
        }



def calculate(operation, number1, number2):

    try:

        if operation == "add":
            result = number1 + number2

        elif operation == "subtract":
            result = number1 - number2

        elif operation == "multiply":
            result = number1 * number2

        elif operation == "divide":

            if number2 == 0:
                return {
                    "error": "Cannot divide by zero"
                }

            result = number1 / number2

        else:

            return {
                "error": "Invalid operation"
            }


        return {
            "result": result
        }


    except Exception as e:

        return {
            "error": str(e)
        }



def search_database(query, category):

    database = {

        "users": [
            {
                "name": "Ali",
                "role": "Developer"
            },
            {
                "name": "Sara",
                "role": "Designer"
            }
        ],


        "products": [
            {
                "name": "Laptop",
                "price": 1200
            },
            {
                "name": "Phone",
                "price": 800
            }
        ],


        "orders": [
            {
                "id": 101,
                "status": "Completed"
            }
        ]

    }


    try:

        records = database.get(category, [])


        results = [

            item

            for item in records

            if query.lower() in str(item).lower()

        ]


        return {

            "results": results

        }


    except Exception as e:

        return {

            "error": str(e)

        }



def format_currency(amount, currency):

    symbols = {

        "USD": "$",
        "EUR": "€",
        "PKR": "Rs."

    }


    try:

        symbol = symbols.get(currency, "")


        return {

            "formatted": f"{symbol}{amount:,.2f}"

        }


    except Exception as e:

        return {

            "error": str(e)

        }



# -----------------------------
# Function Executor
# -----------------------------


def execute_function(function_name, arguments):


    available_functions = {


        "get_current_time": get_current_time,

        "calculate": calculate,

        "search_database": search_database,

        "format_currency": format_currency


    }


    if function_name not in available_functions:

        return {

            "error": "Function not found"

        }


    try:

        return available_functions[function_name](**arguments)


    except TypeError as e:

        return {

            "error": f"Invalid arguments: {str(e)}"

        }



# -----------------------------
# Convert Tools for Gemini
# -----------------------------


gemini_tools = [

    {

        "function_declarations": [

            tool["function"]

            for tool in tools

        ]

    }

]



# -----------------------------
# Function Calling Loop
# -----------------------------


def run_agent(user_prompt):


    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=user_prompt,

        config={

            "tools": gemini_tools

        }

    )


    # If model calls a function

    if response.function_calls:


        function_call = response.function_calls[0]


        function_name = function_call.name


        arguments = dict(function_call.args)



        print("\nTool Selected:")

        print(function_name)



        print("\nArguments:")

        print(arguments)



        # Execute function locally

        result = execute_function(

            function_name,

            arguments

        )



        print("\nTool Result:")

        print(result)



        # Send result back to model

        second_response = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=[

                user_prompt,


                {

                    "role": "tool",

                    "parts": [

                        {

                            "function_response": {

                                "name": function_name,

                                "response": result

                            }

                        }

                    ]

                }

            ],


            config={

                "tools": gemini_tools

            }

        )


        if second_response.text:

            return second_response.text


        else:

            return f"The function {function_name} returned: {result}"



    # Model answered without function call

    else:

        return response.text



# -----------------------------
# Main
# -----------------------------


if __name__ == "__main__":


    question = input(

        "Ask something: "

    )


    answer = run_agent(question)


    print("\nFinal Answer:")

    print(answer)