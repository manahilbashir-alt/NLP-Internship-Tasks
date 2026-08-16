class ReActAgent:

    def __init__(self):

        # Simulated Weather Database
        self.weather_database = {
            "lahore": {
                "temperature": "34°C",
                "condition": "Sunny",
                "humidity": "48%"
            },

            "karachi": {
                "temperature": "31°C",
                "condition": "Cloudy",
                "humidity": "70%"
            },

            "islamabad": {
                "temperature": "29°C",
                "condition": "Rainy",
                "humidity": "82%"
            }
        }

       
        self.currency_database = {

            ("USD", "PKR"): 284.50,
            ("EUR", "PKR"): 331.20,
            ("SAR", "PKR"): 75.80

        }
    def reason(self, query):

        query = query.lower()

        if "weather" in query:
            return "weather"

        elif "convert" in query:
            return "currency"

        elif any(operator in query for operator in ["+", "-", "*", "/", "calculate"]):
            return "calculator"

        else:
            return "unknown"
    def choose_tool(self, tool_name):

        if tool_name == "weather":
            return self.weather_tool

        elif tool_name == "currency":
            return self.currency_tool

        elif tool_name == "calculator":
            return self.calculator_tool

        return None

    # ============================================================
    # Weather Tool
    # ============================================================

    def weather_tool(self, city):

        city = city.lower()

        if city in self.weather_database:
            return self.weather_database[city]

        return "City not found."

    # ============================================================
    # Currency Tool
    # ============================================================

    def currency_tool(self, amount, from_currency, to_currency):

        key = (from_currency.upper(), to_currency.upper())

        if key not in self.currency_database:
            return "Currency pair not available."

        rate = self.currency_database[key]

        return round(amount * rate, 2)

    # ============================================================
    # Calculator Tool
    # ============================================================

    def calculator_tool(self, expression):

        try:
            return eval(expression)

        except Exception:
            return "Invalid Expression"

    # ============================================================
    # STEP 3 : Execute
    # ============================================================

    def execute(self, query):

        print("=" * 80)
        print("USER QUERY")
        print("=" * 80)
        print(query)

        tool_needed = self.reason(query)

        print("\nREASON")
        print("-" * 80)

        if tool_needed == "weather":
            print("The query requires current weather information.")

        elif tool_needed == "currency":
            print("The query requires currency conversion.")

        elif tool_needed == "calculator":
            print("The query requires mathematical calculation.")

        else:
            print("No suitable tool found.")

        tool = self.choose_tool(tool_needed)

        if tool is None:
            print("\nFINAL RESPONSE")
            print("I cannot answer this query.")
            return

        print("\nACTION")
        print("-" * 80)

        # Weather Example
        if tool_needed == "weather":

            city = "lahore"

            print(f"Calling Weather Tool for '{city.title()}'...")

            observation = tool(city)

            print("\nOBSERVATION")
            print(observation)

            print("\nFINAL RESPONSE")

            print(
                f"The weather in {city.title()} is "
                f"{observation['condition']} with a temperature of "
                f"{observation['temperature']} and humidity of "
                f"{observation['humidity']}."
            )

        # Currency Example
        elif tool_needed == "currency":

            amount = 100
            from_currency = "USD"
            to_currency = "PKR"

            print(
                f"Calling Currency Tool for "
                f"{amount} {from_currency} -> {to_currency}"
            )

            observation = tool(amount, from_currency, to_currency)

            print("\nOBSERVATION")
            print(observation)

            print("\nFINAL RESPONSE")

            print(
                f"{amount} {from_currency} is approximately "
                f"{observation} {to_currency}."
            )

        # Calculator Example
        elif tool_needed == "calculator":

            expression = "(145*28)+760"

            print(f"Calling Calculator Tool for {expression}")

            observation = tool(expression)

            print("\nOBSERVATION")
            print(observation)

            print("\nFINAL RESPONSE")

            print(f"The result of {expression} is {observation}.")
agent = ReActAgent()
agent.execute("What is the weather in Lahore today?")

print("\n\n")
agent.execute("Convert 100 USD to PKR")

print("\n\n")

agent.execute("Calculate (145*28)+760")