class PromptTemplateLibrary:

    """
    A reusable collection of prompt templates.

    Every method returns a formatted prompt that can be
    directly used with any Large Language Model.
    """

    def __init__(self):

        self.author = "Manahil Bashir"

        self.version = "1.0"

        self.total_templates = 5
    def _header(self, role):

        return (
            f"You are an experienced {role}.\n"
            "Follow the instructions carefully.\n\n"
        )
    def summarization(
        self,
        text,
        summary_type="paragraph",
        max_words=100
    ):

        prompt = self._header("document summarizer")

        prompt += (
            f"Summarize the following text.\n\n"

            f"Summary Type : {summary_type}\n"

            f"Maximum Length : {max_words} words\n\n"

            "Text\n"
            "----\n"

            f"{text}\n\n"

            "Instructions\n"
            "------------\n"

            "- Keep the important information.\n"

            "- Remove unnecessary details.\n"

            "- Do not change the original meaning.\n"

            "- Use simple and professional English.\n\n"

            "Summary\n"
        )

        return prompt
    def entity_extraction(
        self,
        text,
        entity_types=None
    ):

        if entity_types is None:

            entity_types = [

                "Person",

                "Organization",

                "Location",

                "Date"

            ]

        prompt = self._header("Named Entity Recognition specialist")

        prompt += (

            "Extract the entities from the given text.\n\n"

            "Return only the requested categories.\n\n"

            "Entity Types\n"

            "------------\n"

        )

        for entity in entity_types:

            prompt += f"- {entity}\n"

        prompt += (

            "\nText\n"

            "----\n"

            f"{text}\n\n"

            "Output Format\n"

            "-------------\n"

        )

        for entity in entity_types:

            prompt += f"{entity}:\n"

        return prompt
    def sentiment_analysis(self, text):

        prompt = self._header("sentiment analysis expert")

        prompt += (

            "Analyze the sentiment of the following text.\n\n"

            "Return\n"

            "- Sentiment\n"

            "- Confidence Score\n"

            "- Short Explanation\n\n"

            "Text\n"

            "----\n"

            f"{text}\n\n"

            "Output Format\n"

            "-------------\n"

            "Sentiment:\n"

            "Confidence:\n"

            "Reason:\n"

        )

        return prompt
    def code_generation(

        self,

        language,

        task,

        include_comments=True,

        include_example=True

    ):

        prompt = self._header(f"{language} software developer")

        prompt += (

            f"Write a {language} program.\n\n"

            f"Task\n"

            "----\n"

            f"{task}\n\n"

            "Requirements\n"

            "------------\n"

            "- Use functions\n"

            "- Follow clean coding practices\n"

            "- Handle invalid input\n"

        )

        if include_comments:

            prompt += "- Add meaningful comments\n"

        if include_example:

            prompt += "- Include sample input and output\n"

        prompt += "\nCode\n"

        return prompt
    # ===========================================================
    # Template 5
    # Data Transformation
    # ===========================================================

    def data_transformation(
        self,
        data,
        source_format,
        target_format
    ):

        prompt = self._header("data transformation specialist")

        prompt += (

            f"Convert the following data from "

            f"{source_format} to {target_format}.\n\n"

            "Requirements\n"

            "------------\n"

            "- Preserve all information.\n"

            "- Do not modify the values.\n"

            "- Return only the converted data.\n\n"

            "Input Data\n"

            "----------\n"

            f"{data}\n\n"

            "Converted Data\n"

        )

        return prompt

    # ===========================================================
    # Display Available Templates
    # ===========================================================

    def show_templates(self):

        print("=" * 70)
        print("AVAILABLE PROMPT TEMPLATES")
        print("=" * 70)

        templates = [

            "1. Summarization",

            "2. Entity Extraction",

            "3. Sentiment Analysis",

            "4. Code Generation",

            "5. Data Transformation"

        ]

        for template in templates:
            print(template)

        print()
    def preview(self, prompt):

        print("=" * 70)
        print("PROMPT TEMPLATE")
        print("=" * 70)
        print(prompt)
        print("=" * 70) 
library = PromptTemplateLibrary()

library.show_templates()
article = """
Artificial Intelligence has transformed many industries by
automating repetitive tasks and improving decision making.
Machine learning models are increasingly used in healthcare,
finance, education, and cybersecurity.
"""

summary_prompt = library.summarization(
    text=article,
    summary_type="bullet points",
    max_words=80
)

library.preview(summary_prompt)
text = """
Sundar Pichai is the CEO of Google.
He visited Islamabad in July 2025.
"""

entity_prompt = library.entity_extraction(text)

library.preview(entity_prompt)
review = """
The phone's performance is excellent,
but the battery life is disappointing.
"""

sentiment_prompt = library.sentiment_analysis(review)

library.preview(sentiment_prompt)
code_prompt = library.code_generation(

    language="Python",

    task="Create a Student Management System using classes."

)

library.preview(code_prompt)
csv_data = """
Name,Age
Ali,20
Sara,21
"""

transform_prompt = library.data_transformation(

    data=csv_data,

    source_format="CSV",

    target_format="JSON"

)

library.preview(transform_prompt)           