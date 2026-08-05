"""
Day 10 - Function Calling
Task 5: Robust Error Handling
"""


from function_calling_loop import execute_function



# -----------------------------
# Test invalid arguments
# -----------------------------

def test_invalid_arguments():

    print("\n--- Invalid Arguments Test ---")


    result = execute_function(

        "calculate",

        {
            "operation": "multiply",
            "number1": "abc",
            "number2": 10
        }

    )


    print(result)



# -----------------------------
# Test function error
# -----------------------------

def test_function_error():

    print("\n--- Function Error Test ---")


    result = execute_function(

        "calculate",

        {
            "operation": "divide",
            "number1": 10,
            "number2": 0
        }

    )


    print(result)



# -----------------------------
# Test unknown function
# -----------------------------

def test_unknown_function():

    print("\n--- Unknown Function Test ---")


    result = execute_function(

        "unknown_tool",

        {}

    )


    print(result)



# -----------------------------
# Main
# -----------------------------


if __name__ == "__main__":


    test_invalid_arguments()

    test_function_error()

    test_unknown_function()