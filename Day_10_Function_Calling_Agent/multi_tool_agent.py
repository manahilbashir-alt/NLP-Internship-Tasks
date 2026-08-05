"""
Day 10 - Function Calling
Task 4: Multi Tool Agent

Flow:

User
 |
Model
 |
Tool 1
 |
Result
 |
Tool 2
 |
Result
 |
Final Answer
"""


import os
import json

from dotenv import load_dotenv
from google import genai

from tools_definition import tools
from function_calling_loop import execute_function


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



# Gemini tool format

gemini_tools = [

    {
        "function_declarations": [

            tool["function"]

            for tool in tools

        ]
    }

]



def multi_tool_agent(question):


    messages = [
        question
    ]


    for step in range(3):


        response = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=messages,

            config={
                "tools": gemini_tools
            }

        )


        if not response.function_calls:

            return response.text



        function_call = response.function_calls[0]


        function_name = function_call.name


        arguments = dict(function_call.args)



        print("\nCalling Tool:")
        print(function_name)


        print("Arguments:")
        print(arguments)



        result = execute_function(

            function_name,

            arguments

        )


        print("\nResult:")
        print(result)



        messages.append(

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

        )


    return "Maximum tool calls reached"



if __name__ == "__main__":


    question = input(
        "Ask something complex: "
    )


    answer = multi_tool_agent(question)


    print("\nFinal Answer:")
    print(answer)